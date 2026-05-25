# Agentic RAG — Production Refactor

A production-grade Retrieval-Augmented Generation system built with
**LangChain · LangGraph · FastAPI · Streamlit**.

- Ref: https://in.trip.com/hotels/list?city=1355&checkin=2026/5/25&checkout=2026/05/26
<img width="1791" height="980" alt="image" src="https://github.com/user-attachments/assets/c1577a7a-6bdf-4c42-856f-307eb717893f" />
<img width="1846" height="1099" alt="image" src="https://github.com/user-attachments/assets/582ef949-dcd3-4ed6-8b58-47b95c71417e" />



## API 

<img width="1790" height="751" alt="image" src="https://github.com/user-attachments/assets/9b398194-aa34-432e-8e53-00a95333b2ea" />

```
POST /api/v1/ingest
POST /api/v1/query

GET /health
GET /liveness
GET /readiness
GET /app-metrics
GET /metrics
```


where:

```
/health → aggregate app status
/liveness → process alive
/readiness → vectorstore/graph initialized
/app-metrics → your business metrics
/metrics → Prometheus scrape endpoint
```

## 1. Create virtual environment

```bash
uv venv
source .venv/bin/activate

uv add fastapi uvicorn celery redis
uv add prometheus-fastapi-instrumentator
uv add opentelemetry-api
uv add opentelemetry-sdk
uv add opentelemetry-instrumentation-fastapi
uv add opentelemetry-exporter-otlp
uv add structlog
uv add python-jose passlib
uv add slowapi
uv add httpx

uv add langchain
uv add langchain-community
uv add langchain-openai
uv add langgraph
uv add faiss-cpu
uv add pydantic
uv add python-dotenv
```

## 2. Start Redis

Required for:
- cache
- Celery broker
- task queue
- rate limit storage

Using Docker:

Terminal 1:
```bash
docker run -d --name redis -p 6379:6379 redis:7
docker ps  // Verify
docker start redis
```


## 3. Run Celery worker

Terminal 2:

```bash
source .venv/bin/activate

$ celery -A src.workers.celery_app:app worker --loglevel=info

 -------------- celery@c623lrd90445656 v5.6.3 (recovery)
--- ***** ----- 
-- ******* ---- Linux-6.8.0-111-generic-x86_64-with-glibc2.35 2026-05-25 13:06:19
- 
                
[tasks]
[2026-05-25 13:06:19,689: INFO/MainProcess] Connected to redis://localhost:6379/0
[2026-05-25 13:06:19,691: INFO/MainProcess] mingle: searching for neighbors
[2026-05-25 13:06:20,699: INFO/MainProcess] mingle: all alone
[2026-05-25 13:06:20,724: INFO/MainProcess] celery@c623lrd90445656 ready.
```

## 4. Start Fastapi server
Terminal 3:
```bash
uvicorn src.main:app --reload
```

## 5. Start streamlit UI:

Terminal 4:
```bash
streamlit run streamlit/app.py
```

## 6. Enable tracing

Run local Jaeger:
```bash
docker run -d \
-p 16686:16686 \
-p 4317:4317 \
jaegertracing/all-in-one
```

- Open: `http://localhost:16686`
- Once OpenTelemetry exporter config is added, traces appear automatically.

-------------

# For a complete production deployment later:

```bash
docker compose up --build
```
with:

- FastAPI container
- Redis container
- Celery worker
- Streamlit
- Prometheus
- Grafana
- Jaeger

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Streamlit UI                                │
│  streamlit_app/app.py  →  api_client.py  (HTTP)                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ REST / JSON
┌──────────────────────────────▼──────────────────────────────────────┐
│                        FastAPI  (api/)                              │
│                                                                     │
│  POST /api/v1/ingest   ─── ingest_router.py                        │
│  POST /api/v1/query    ─── query_router.py                         │
│  GET  /health          ─── observability_router.py                 │
│  GET  /metrics         ─── observability_router.py                 │
│                                                                     │
│  Middleware: CORS, global exception handlers                        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                     RAGOrchestrator (services/)                     │
│                                                                     │
│  IngestionService   →  VectorStoreService   →  GraphService         │
│  (load + chunk)         (FAISS index)           (LangGraph)         │
│                                                     │               │
│                                               RAGNodes              │
│                                          ┌── retrieve_docs          │
│                                          └── generate_answer        │
│                                              (ReAct: retriever      │
│                                               + Wikipedia)          │
└─────────────────────────────────────────────────────────────────────┘
```


```
POST /api/v1/ingest
       ↓
Celery queue
       ↓
worker
       ↓
vector build
       ↓
status endpoint
```


### Key design decisions

| Decision | Rationale |
|---|---|
| Services never import each other directly | Orchestrator owns wiring; avoids circular deps |
| `pydantic-settings` for config | Type-safe, env-file aware, cached singleton |
| Custom exception hierarchy | Single place to map errors → HTTP codes |
| `VectorStoreService` thread-safe lock | Prevents index corruption on concurrent ingests |
| `GraphService.rebuild()` | Hot-swap retriever post-ingest without restart |
| Streamlit `api_client.py` | All network calls isolated; easy to mock in tests |

---

## Directory layout

```
rag_production

├── pyproject.toml                # Project metadata, dependencies, build configuration
├── README.md                     # Setup guide, architecture, API usage
├── requirements.txt             # Python dependency list
├── uv.lock                      # Locked package versions for reproducible installs

├── src
│
│── main.py                      # Application entry point; starts FastAPI/services
│
│── api
│   │── app.py                   # FastAPI app creation and route registration
│   │── __init__.py              # Package initialization
│   │
│   ├── middleware
│   │   ├── exception_handlers.py # Global exception handlers and error responses
│   │   └── __init__.py
│   │
│   ├── routers
│   │   ├── ingest_router.py      # API endpoints for document ingestion
│   │   ├── observability_router.py # Health checks, metrics, monitoring endpoints
│   │   ├── query_router.py       # RAG query/chat endpoints
│   │   └── __init__.py
│   │
│   └── schemas
│       ├── schemas.py           # Pydantic request/response models
│       └── __init__.py
│
├── core
│   │── __init__.py
│   │
│   ├── config
│   │   ├── settings.py          # Environment variables and app config loading
│   │   └── __init__.py
│   │
│   ├── exceptions
│   │   ├── errors.py            # Custom exception definitions
│   │   └── __init__.py
│   │
│   └── state
│       ├── rag_state.py         # Shared state object for RAG workflow
│       └── __init__.py
│
├── services
│   │── __init__.py
│   │── rag_orchestrator.py      # Main coordinator connecting retrieval + LLM
│   │
│   ├── graph
│   │   ├── graph_service.py     # LangGraph workflow creation/execution
│   │   ├── rag_nodes.py         # Individual workflow nodes
│   │   └── __init__.py
│   │
│   ├── ingestion
│   │   ├── ingestion_service.py # Chunking, preprocessing and indexing logic
│   │   └── __init__.py
│   │
│   ├── llm
│   │   ├── llm_service.py       # LLM interaction abstraction
│   │   └── __init__.py
│   │
│   └── vectorstore
│       ├── vectorstore_service.py # FAISS/vector DB operations
│       └── __init__.py
│
├── streamlit_app
│   │── app.py                   # Streamlit UI entrypoint
│   │── api_client.py            # Connects UI with backend APIs
│   │── __init__.py
│   │
│   └── pages                    # Multi-page Streamlit screens
│
└── workers
    ├── celery_app.py            # Background task worker configuration
    └── __init__.py

├── test
│   └── test_redis.py            # Redis integration/unit tests

```

---

## Setup

```bash
# 1. Clone / unzip and enter the directory
cd rag_production

# 2. Create a virtual environment
source .venv/bin/activate

# 3. Install dependencies
uv add -r requirements.txt

# 4. Configure secrets
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...
```

---

## Run

### Start the FastAPI backend

```bash
# From the rag_production/ directory
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

The server auto-ingests the default URLs on startup.
Interactive API docs: http://localhost:8000/docs

### Start the Streamlit frontend

```bash
# In a second terminal, from rag_production/streamlit_app/
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## API reference

### `POST /api/v1/ingest`

```json
{
  "sources": [
    "https://example.com/article",
    "/absolute/path/to/docs/",
    "/absolute/path/to/file.pdf"
  ]
}
```

### `POST /api/v1/query`

```json
{ "question": "What is the agent loop in autonomous agents?" }
```

Response:
```json
{
  "answer": "…",
  "sources": [{ "content": "…", "metadata": {} }],
  "latency_ms": 1234.5
}
```

### `GET /health`

```json
{ "status": "ok", "is_ready": true, "uptime_s": 42.1 }
```

### `GET /metrics`

```json
{
  "query_count": 7,
  "ingest_count": 1,
  "avg_latency_ms": 2130.0,
  "vectorstore": {
    "is_ready": true,
    "chunk_count": 312,
    "last_build_ts": 1724000000.0,
    "build_duration_s": 3.14
  }
}
```
