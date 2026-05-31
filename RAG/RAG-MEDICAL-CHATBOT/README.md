# RAG Medical Chatbot

FastAPI-based medical RAG chatbot with OpenTelemetry instrumentation and production-friendly health/metrics endpoints.

```bash
cd RAG-MEDICAL-CHATBOT
uv venv
source .venv/bin/activate
uv pip install -e .
```

## vim .env

```bash
# Required API keys
OPENAI_API_KEY=sk-proj-xxxx
HF_TOKEN=hf_xHWxxxxx
HUGGINGFACEHUB_API_TOKEN=hf_xHWxxxxx

# Optional runtime configuration
CHATBOT_DB_PATH=data/chat_history.db
SERVICE_VERSION=1.0.0
DEPLOYMENT_ENV=development

# Optional OpenTelemetry exporter endpoint
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318

HTTP_PROXY="http://proxy-xxx:3128"
HTTPS_PROXY="http://proxy-xxx:3128"
ALL_PROXY="http://proxy-xxx:3128"
http_proxy="http://proxy-xxx:3128"
https_proxy="http://proxy-xxx:3128"
all_proxy="http://proxy-xxx:3128"
NO_PROXY="localhost,127.0.0.1"

```

```bash
docker build --no-cache --build-arg USE_PROXY=false -t rag-medical-chatbot:latest .

docker run --rm -p 8000:8000 --env-file .env -e HTTP_PROXY= -e HTTPS_PROXY= -e ALL_PROXY= -e http_proxy= -e https_proxy= -e all_proxy= rag-medical-chatbot:latest

```

###  Open UI and API docs.

- UI: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`

### Validate service and probes.

## Notes

- `readiness` reflects whether startup initialization successfully created the RAG chain.
- If startup dependencies fail, `/readiness` and `/health` report degraded state.



```bash
curl http://localhost:8000/liveness
curl http://localhost:8000/readiness
curl http://localhost:8000/health
curl http://localhost:8000/app-metrics
curl http://localhost:8000/metrics
```

Upload your PDF from the web UI (Upload PDF button), then ask questions.


---------------------------------------------------------------------------------------

# Server Running

```bash
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2026-05-31 10:59:55,961 - INFO - app.observability - OTLP exporters are disabled (set OTEL_ENABLE_OTLP=true to enable).
2026-05-31 10:59:55,982 - INFO - app.components.retriever - Loading vector store for context
2026-05-31 10:59:55,983 - INFO - app.components.embeddings - Initializing OpenAI embedding model
2026-05-31 10:59:56,360 - INFO - app.components.embeddings - OpenAI embedding model loaded successfully
2026-05-31 10:59:56,361 - WARNING - app.components.vector_store - No vectore store found..
2026-05-31 10:59:56,361 - WARNING - app.components.retriever - Vector store missing and AUTO_BUILD_VECTORSTORE_ON_STARTUP is disabled. Upload a PDF to initialize retrieval.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
2026-05-31 11:00:03,317 - WARNING - app.application - QA chain is missing; attempting lazy initialization
2026-05-31 11:00:03,318 - INFO - app.components.retriever - Loading vector store for context
2026-05-31 11:00:03,318 - INFO - app.components.embeddings - Initializing OpenAI embedding model
2026-05-31 11:00:03,341 - INFO - app.components.embeddings - OpenAI embedding model loaded successfully
2026-05-31 11:00:03,341 - WARNING - app.components.vector_store - No vectore store found..
2026-05-31 11:00:03,341 - WARNING - app.components.retriever - Vector store missing and AUTO_BUILD_VECTORSTORE_ON_STARTUP is disabled. Upload a PDF to initialize retrieval.
2026-05-31 11:00:03,341 - WARNING - app.application - RAG index unavailable; using direct OpenAI response fallback
2026-05-31 11:00:03,341 - INFO - app.components.llm - Loading LLM from OpenAI...
2026-05-31 11:00:03,342 - INFO - langchain_openai.chat_models._client_utils - langchain-openai detected system proxy configuration and no explicit `http_socket_options` / `http_client` / `http_async_client` / `openai_proxy`; skipping the custom `httpx` transport so httpx's env-proxy auto-detection applies. Pass `http_socket_options=[...]` to opt back into kernel-level TCP keepalive tuning on top of the env proxy.
2026-05-31 11:00:03,363 - INFO - app.components.llm - LLM loaded successfully from OpenAI.
2026-05-31 11:00:08,076 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:     172.17.0.1:45980 - "POST / HTTP/1.1" 303 See Other
INFO:     172.17.0.1:45980 - "GET / HTTP/1.1" 200 OK
2026-05-31 11:00:58,845 - INFO - app.components.pdf_loader - Loading files from data/
2026-05-31 11:01:37,392 - INFO - app.components.pdf_loader - Sucesfully fetched 1518 documents
2026-05-31 11:01:37,392 - INFO - app.components.pdf_loader - Splitting 1518 documents into chunks
2026-05-31 11:01:38,126 - INFO - app.components.pdf_loader - Generated 14160 text chunks
2026-05-31 11:01:38,126 - INFO - app.components.vector_store - Generating your new vectorstore
2026-05-31 11:01:38,126 - INFO - app.components.embeddings - Initializing OpenAI embedding model
2026-05-31 11:01:38,145 - INFO - app.components.embeddings - OpenAI embedding model loaded successfully
2026-05-31 11:01:50,418 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:01:53,594 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:01:55,642 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:01:58,304 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:02:00,353 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:02:02,810 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:02:05,370 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:02:07,723 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:02:10,307 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:02:12,946 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:02:15,814 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:02:18,169 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:02:20,832 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:02:23,506 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:02:27,387 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:02:27,873 - INFO - faiss.loader - Loading faiss with AVX2 support.
2026-05-31 11:02:27,873 - INFO - faiss.loader - Could not load library with AVX2 support due to:
ModuleNotFoundError("No module named 'faiss.swigfaiss_avx2'")
2026-05-31 11:02:27,873 - INFO - faiss.loader - Loading faiss.
2026-05-31 11:02:27,909 - INFO - faiss.loader - Successfully loaded faiss.
2026-05-31 11:02:29,647 - INFO - app.components.vector_store - Saving vectorstoree
2026-05-31 11:02:29,794 - INFO - app.components.vector_store - Vectostore saved sucesfulyy...
2026-05-31 11:02:29,794 - INFO - app.components.retriever - Loading vector store for context
2026-05-31 11:02:29,794 - INFO - app.components.embeddings - Initializing OpenAI embedding model
2026-05-31 11:02:29,813 - INFO - app.components.embeddings - OpenAI embedding model loaded successfully
2026-05-31 11:02:29,813 - INFO - app.components.vector_store - Loading existing vectorstore...
2026-05-31 11:02:29,946 - INFO - app.components.llm - Loading LLM from OpenAI...
2026-05-31 11:02:29,947 - INFO - app.components.llm - LLM loaded successfully from OpenAI.
2026-05-31 11:02:29,948 - INFO - app.components.retriever - Successfully created the QA chain
2026-05-31 11:02:29,966 - INFO - app.application - Uploaded and ingested PDF: data/e41ebdc9-0b35-4269-9f3b-e301f0939535_The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf
INFO:     172.17.0.1:45990 - "POST /upload-pdf HTTP/1.1" 303 See Other
2026-05-31 11:02:31,278 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
2026-05-31 11:02:32,915 - INFO - httpx - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:     172.17.0.1:52842 - "POST / HTTP/1.1" 303 See Other
INFO:     172.17.0.1:52842 - "GET / HTTP/1.1" 200 OK

```
<img width="1198" height="1082" alt="image" src="https://github.com/user-attachments/assets/baa2cec1-8261-447d-b3c1-a12bc62408ff" />

## What Changed

- FastAPI endpoints
- Added OpenTelemetry SDK for traces, metrics, and logs
- Added Prometheus scrape endpoint
- Added health probe endpoints for container/orchestrator checks
- Added PDF upload UI and ingestion endpoint to rebuild FAISS vectorstore
- Added modular request/response models in `app/schema.py`
- Added SQLite-based chat persistence in `app/database.py`
- Switched local package workflow to `uv` and Docker runtime build to `pip`

## Architecture

```text
User/Web/API
   |
   v
FastAPI app (app/application.py)
  |-- RAG chain (LangChain + FAISS + OpenAI)
   |-- SQLite chat history (app/database.py)
   |-- Pydantic schemas (app/schema.py)
   |-- OpenTelemetry SDK (app/observability.py)
          |
          +--> OTLP traces/logs/metrics exporter
                 |
                 +--> Prometheus (metrics)
                 +--> OpenSearch (logs)
                 +--> Grafana/Datadog (dashboards + alerts)
```

        ## Project Tree and File Purpose

        ```text
        RAG-MEDICAL-CHATBOT/
        ├── Dockerfile
        ├── Jenkinsfile
        ├── FULL_DOCUMENTATION.md
        ├── requirements.txt
        ├── setup.py
        ├── app/
        │   ├── __init__.py
        │   ├── application.py
        │   ├── schema.py
        │   ├── database.py
        │   ├── observability.py
        │   ├── common/
        │   │   ├── __init__.py
        │   │   ├── logger.py
        │   │   └── custom_exception.py
        │   ├── components/
        │   │   ├── __init__.py
        │   │   ├── data_loader.py
        │   │   ├── pdf_loader.py
        │   │   ├── embeddings.py
        │   │   ├── vector_store.py
        │   │   ├── llm.py
        │   │   └── retriever.py
        │   ├── config/
        │   │   ├── __init__.py
        │   │   └── config.py
        │   └── templates/
        │       └── index.html
        ├── custom_jenkins/
        │   └── Dockerfile
        ├── data/
        └── vectorstore/
          └── db_faiss/
            └── index.faiss
        ```

        Top-level files and folders:

        - `Dockerfile`: container build definition for app runtime with uv + Uvicorn.
        - `Jenkinsfile`: CI/CD pipeline stages (clone, image build, scan, push, deploy).
        - `FULL_DOCUMENTATION.md`: extended setup and deployment notes.
        - `requirements.txt`: Python dependency list used by packaging and image builds.
        - `setup.py`: package metadata and editable install entrypoint.
        - `data/`: runtime data (including SQLite chat history db).
        - `vectorstore/db_faiss/`: persisted FAISS index for RAG retrieval.

        Application modules:

        - `app/application.py`: FastAPI app entrypoint, routes, health checks, business metrics, and Prometheus endpoint.
        - `app/schema.py`: Pydantic request/response models for API contracts.
        - `app/database.py`: SQLite-backed chat history storage by session id.
        - `app/observability.py`: OpenTelemetry SDK setup and FastAPI/log instrumentation.
        - `app/common/logger.py`: common logger setup.
        - `app/common/custom_exception.py`: custom exception utilities.
        - `app/components/data_loader.py`: source document loading utilities.
        - `app/components/pdf_loader.py`: PDF ingestion pipeline.
        - `app/components/embeddings.py`: embedding model setup.
        - `app/components/vector_store.py`: FAISS vector store load/save operations.
        - `app/components/llm.py`: LLM client initialization (OpenAI).
        - `app/components/retriever.py`: RAG retriever and QA chain construction.
        - `app/config/config.py`: environment-backed configuration constants.
        - `app/templates/index.html`: browser chat UI template.

## Endpoints

- `GET /` : Chat UI
- `POST /` : Submit chat prompt from UI
- `POST /chat` : JSON API for chat completions
- `POST /clear` : Clear session chat history
- `POST /upload-pdf` : Upload a PDF and rebuild/update FAISS vectorstore
- `GET /liveness` : Process alive check
- `GET /readiness` : Vectorstore/graph initialization check
- `GET /health` : Aggregate app health status
- `GET /app-metrics` : Business metrics snapshot
- `GET /metrics` : Prometheus scrape endpoint

## Request/Response Schema

All request/response models are centralized in:

- `app/schema.py`

Main models:

- `ChatQueryRequest`
- `ChatCompletionResponse`
- `LiveResponse`
- `ReadyResponse`
- `HealthResponse`
- `AppMetricsResponse`

## Database Handling

SQLite chat history store:

- module: `app/database.py`
- class: `ChatHistoryStore`
- default db path: `data/chat_history.db`
- configurable via env var: `CHATBOT_DB_PATH`

Each session is tracked by `session_id` (cookie for web flow, optional in `/chat` API).


## Observability Setup

The app initializes OpenTelemetry in `app/observability.py` and instruments FastAPI automatically.
OTLP export is disabled by default unless `OTEL_ENABLE_OTLP=true`.

Exported telemetry:

- traces: OTLP span exporter (when enabled)
- metrics: OTLP metric exporter (when enabled) + `/metrics` Prometheus endpoint
- logs: OTLP log exporter (when enabled) + logging instrumentation

Typical stack:

- Prometheus scrapes `/metrics`
- OpenSearch stores logs
- Grafana or Datadog visualizes dashboards and alerts




