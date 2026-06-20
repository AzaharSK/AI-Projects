import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from fastapi import FastAPI, File, Request, Response, UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
from opentelemetry import trace
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from app.common.logger import get_logger
from app.components.llm import load_llm
from app.components.pdf_loader import create_text_chunks, load_pdf_files
from app.components.retriever import create_qa_chain
from app.components.vector_store import save_vector_store
from app.database import ChatHistoryStore
from app.observability import instrument_fastapi_app, setup_observability
from app.schema import (
    AppMetricsResponse,
    ChatCompletionResponse,
    ChatQueryRequest,
    HealthResponse,
    LiveResponse,
    ReadyResponse,
)

load_dotenv()

APP_START_TIME = time.time()
logger = get_logger(__name__)

BUSINESS_QUERIES_TOTAL = Counter(
    "medical_chatbot_queries_total",
    "Total number of questions sent to the chatbot",
)
BUSINESS_QUERY_ERRORS_TOTAL = Counter(
    "medical_chatbot_query_errors_total",
    "Total number of failed query attempts",
)
BUSINESS_QUERY_LATENCY_SECONDS = Histogram(
    "medical_chatbot_query_latency_seconds",
    "Latency of chatbot responses in seconds",
    buckets=(0.1, 0.25, 0.5, 1, 2, 5, 10),
)
READINESS_GAUGE = Gauge(
    "medical_chatbot_readiness",
    "Readiness flag for chatbot dependencies",
)


def nl2br(value: str) -> Markup:
    return Markup(value.replace("\n", "<br>\n"))


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    setup_observability(service_name="rag-medical-chatbot")
    db_path = os.environ.get("CHATBOT_DB_PATH", "data/chat_history.db")
    fastapi_app.state.chat_store = ChatHistoryStore(db_path)
    fastapi_app.state.init_error = None
    fastapi_app.state.business_metrics = {
        "queries_total": 0,
        "queries_failed": 0,
        "last_query_time_utc": None,
        "last_error": None,
    }

    try:
        qa_chain = create_qa_chain()
        fastapi_app.state.qa_chain = qa_chain
        initialized = qa_chain is not None
        fastapi_app.state.vectorstore_ready = initialized
        fastapi_app.state.graph_ready = initialized
        if not initialized:
            fastapi_app.state.init_error = (
                "Startup could not initialize QA chain. "
                "Upload a PDF and verify OpenAI connectivity."
            )
    except Exception as exc:
        logger.exception("Failed during startup initialization: %s", exc)
        fastapi_app.state.qa_chain = None
        fastapi_app.state.vectorstore_ready = False
        fastapi_app.state.graph_ready = False
        fastapi_app.state.init_error = str(exc)

    ready_flag = int(
        bool(
            fastapi_app.state.vectorstore_ready
            and fastapi_app.state.graph_ready
        )
    )
    READINESS_GAUGE.set(ready_flag)
    yield


app = FastAPI(title="RAG Medical Chatbot", version="1.0.0", lifespan=lifespan)
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["nl2br"] = nl2br
tracer = trace.get_tracer(__name__)
instrument_fastapi_app(app)


def _get_or_create_session_id(request: Request) -> str:
    cookie_session_id = request.cookies.get("session_id")
    if cookie_session_id:
        return cookie_session_id
    return str(uuid.uuid4())


def _ready_state() -> bool:
    return bool(
        app.state.vectorstore_ready
        and app.state.graph_ready
        and app.state.qa_chain is not None
    )


def _refresh_chain_after_ingestion() -> None:
    documents = load_pdf_files()
    if not documents:
        raise RuntimeError("No PDF documents available for ingestion")

    text_chunks = create_text_chunks(documents)
    if not text_chunks:
        raise RuntimeError("Failed to create text chunks from uploaded PDFs")

    db = save_vector_store(text_chunks)
    if db is None:
        raise RuntimeError("Failed to save FAISS vectorstore")

    qa_chain = create_qa_chain()
    if qa_chain is None:
        raise RuntimeError("Failed to rebuild QA chain after ingestion")

    app.state.qa_chain = qa_chain
    app.state.vectorstore_ready = True
    app.state.graph_ready = True
    app.state.init_error = None
    READINESS_GAUGE.set(1)


def _attempt_initialize_chain() -> bool:
    if app.state.qa_chain is not None:
        return True

    try:
        qa_chain = create_qa_chain()
        app.state.qa_chain = qa_chain
        initialized = qa_chain is not None
        app.state.vectorstore_ready = initialized
        app.state.graph_ready = initialized
        app.state.init_error = None if initialized else (
            "QA chain initialization failed. "
            "Upload a PDF and verify OpenAI API connectivity."
        )
        READINESS_GAUGE.set(int(initialized))
        return initialized
    except Exception as exc:
        app.state.vectorstore_ready = False
        app.state.graph_ready = False
        app.state.init_error = str(exc)
        READINESS_GAUGE.set(0)
        logger.exception("Lazy QA initialization failed: %s", exc)
        return False


def _query_chatbot(user_input: str) -> str:
    start = time.perf_counter()
    BUSINESS_QUERIES_TOTAL.inc()
    app.state.business_metrics["queries_total"] += 1

    try:
        if app.state.qa_chain is None:
            logger.warning("QA chain is missing; attempting lazy initialization")
            _attempt_initialize_chain()

        if app.state.qa_chain is not None:
            with tracer.start_as_current_span("rag.query.invoke"):
                response = app.state.qa_chain.invoke({"query": user_input})
                result = response.get("result", "No response")
        else:
            logger.warning(
                "RAG index unavailable; using direct OpenAI response fallback"
            )
            llm = load_llm()
            if llm is None:
                raise RuntimeError(
                    "QA chain is not initialized and direct LLM fallback failed. "
                    "Upload a PDF to build vectorstore and verify OPENAI_API_KEY."
                )
            with tracer.start_as_current_span("llm.query.fallback"):
                llm_response = llm.invoke(user_input)
                result = getattr(llm_response, "content", str(llm_response))

        app.state.business_metrics["last_query_time_utc"] = (
            datetime.now(timezone.utc).isoformat()
        )
        return result
    except Exception as exc:
        BUSINESS_QUERY_ERRORS_TOTAL.inc()
        app.state.business_metrics["queries_failed"] += 1
        app.state.business_metrics["last_error"] = str(exc)
        logger.exception("Query failed: %s", exc)
        raise
    finally:
        BUSINESS_QUERY_LATENCY_SECONDS.observe(time.perf_counter() - start)


@app.get("/", name="index")
async def index(request: Request):
    session_id = _get_or_create_session_id(request)
    messages = app.state.chat_store.get_messages(session_id)
    upload_status = request.query_params.get("upload_status")
    upload_error = request.query_params.get("upload_error")
    response = templates.TemplateResponse(
        request,
        "index.html",
        {
            "messages": messages,
            "error": None,
            "upload_status": upload_status,
            "upload_error": upload_error,
        },
    )
    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,
        samesite="lax",
    )
    return response


@app.post("/", name="ask_web")
async def ask_web(request: Request):
    session_id = _get_or_create_session_id(request)
    form_data = await request.form()
    user_input = (form_data.get("prompt") or "").strip()

    if user_input:
        app.state.chat_store.add_message(session_id, "user", user_input)
        try:
            result = _query_chatbot(user_input)
            app.state.chat_store.add_message(session_id, "assistant", result)
        except Exception as exc:
            messages = app.state.chat_store.get_messages(session_id)
            response = templates.TemplateResponse(
                request,
                "index.html",
                {
                    "messages": messages,
                    "error": f"Error: {str(exc)}",
                },
            )
            response.set_cookie(
                "session_id", session_id, httponly=True, samesite="lax"
            )
            return response

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,
        samesite="lax",
    )
    return response


@app.post("/clear", name="clear_chat")
async def clear_chat(request: Request):
    session_id = _get_or_create_session_id(request)
    app.state.chat_store.clear_messages(session_id)
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,
        samesite="lax",
    )
    return response


@app.post("/upload-pdf", name="upload_pdf")
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    session_id = _get_or_create_session_id(request)

    original_name = file.filename or "uploaded.pdf"
    suffix = Path(original_name).suffix.lower()
    if suffix != ".pdf":
        response = RedirectResponse(
            url=f"/?upload_error={quote_plus('Only PDF files are accepted')}",
            status_code=303,
        )
        response.set_cookie(
            "session_id",
            session_id,
            httponly=True,
            samesite="lax",
        )
        return response

    safe_name = f"{uuid.uuid4()}_{Path(original_name).name}"
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    destination = data_dir / safe_name

    try:
        content = await file.read()
        if not content:
            raise RuntimeError("Uploaded file is empty")

        destination.write_bytes(content)
        _refresh_chain_after_ingestion()
        logger.info("Uploaded and ingested PDF: %s", destination)

        upload_message = quote_plus("PDF uploaded and vectorstore updated")
        response = RedirectResponse(
            url=f"/?upload_status={upload_message}",
            status_code=303,
        )
    except Exception as exc:
        logger.exception("PDF upload or ingestion failed: %s", exc)
        response = RedirectResponse(
            url=f"/?upload_error={quote_plus(str(exc))}",
            status_code=303,
        )

    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,
        samesite="lax",
    )
    return response


@app.post("/chat", response_model=ChatCompletionResponse)
async def chat_api(payload: ChatQueryRequest, request: Request):
    session_id = payload.session_id or _get_or_create_session_id(request)
    app.state.chat_store.add_message(session_id, "user", payload.query)
    result = _query_chatbot(payload.query)
    app.state.chat_store.add_message(session_id, "assistant", result)

    return ChatCompletionResponse(
        session_id=session_id,
        answer=result,
        messages=app.state.chat_store.get_messages(session_id),
    )


@app.get("/liveness", response_model=LiveResponse)
async def liveness() -> LiveResponse:
    return LiveResponse(
        status="alive",
        pid=os.getpid(),
        uptime_seconds=round(time.time() - APP_START_TIME, 3),
    )


@app.get("/readiness", response_model=ReadyResponse)
async def readiness() -> ReadyResponse:
    _attempt_initialize_chain()
    ready = _ready_state()
    READINESS_GAUGE.set(int(ready))
    return ReadyResponse(
        status="ready" if ready else "not_ready",
        ready=ready,
        vectorstore_initialized=bool(app.state.vectorstore_ready),
        graph_initialized=bool(app.state.graph_ready),
        init_error=app.state.init_error,
    )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    live = LiveResponse(
        status="alive",
        pid=os.getpid(),
        uptime_seconds=round(time.time() - APP_START_TIME, 3),
    )
    ready = await readiness()
    aggregate_ok = ready.ready

    return HealthResponse(
        status="ok" if aggregate_ok else "degraded",
        liveness=live,
        readiness=ready,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/app-metrics", response_model=AppMetricsResponse)
async def app_metrics() -> AppMetricsResponse:
    metrics = app.state.business_metrics
    return AppMetricsResponse(
        queries_total=metrics["queries_total"],
        queries_failed=metrics["queries_failed"],
        last_query_time_utc=metrics["last_query_time_utc"],
        last_error=metrics["last_error"],
    )


@app.get("/metrics")
async def metrics() -> Response:
    metrics_content = generate_latest().decode("utf-8")
    return PlainTextResponse(
        metrics_content,
        media_type=CONTENT_TYPE_LATEST,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
        },
    )
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.application:app", host="0.0.0.0", port=8000, reload=False)











