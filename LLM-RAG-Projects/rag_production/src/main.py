from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.routers.query_router import router as query_router
from src.api.routers.observability_router import router as observability_router
from src.api.routers.ingest_router import router as ingest_router

from src.services.rag_orchestrator import RAGOrchestrator


# optional tracing
try:
    from src.observability.tracing import setup_tracing
except:
    setup_tracing = None


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting application...")

    # initialize once
    app.state.orchestrator = RAGOrchestrator()

    if setup_tracing:
        setup_tracing(app)

    yield

    print("Shutting down...")


app = FastAPI( title="Enterprise RAG", version="1.0", lifespan=lifespan)

@app.get("/")
async def root():
    return {
        "service":"rag",
        "status":"running"
    }

app.include_router(query_router, prefix="/api/v1")
app.include_router(ingest_router, prefix="/api/v1")
app.include_router(observability_router)

Instrumentator().instrument(app).expose(app)

