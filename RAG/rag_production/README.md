# Agentic RAG — Production Refactor

A production-grade Retrieval-Augmented Generation system built with
**LangChain · LangGraph · FastAPI · Streamlit**.

---

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
rag_production/
├── api/
│   ├── app.py                  # FastAPI factory + lifespan
│   ├── middleware/
│   │   └── exception_handlers.py
│   ├── routers/
│   │   ├── ingest_router.py
│   │   ├── query_router.py
│   │   └── observability_router.py
│   └── schemas/
│       └── schemas.py          # All Pydantic request/response models
│
├── core/
│   ├── config/settings.py      # pydantic-settings singleton
│   ├── exceptions/errors.py    # Custom exception hierarchy
│   └── state/rag_state.py      # LangGraph state schema
│
├── services/
│   ├── rag_orchestrator.py     # Application-level façade
│   ├── llm/llm_service.py
│   ├── ingestion/ingestion_service.py
│   ├── vectorstore/vectorstore_service.py
│   └── graph/
│       ├── graph_service.py    # LangGraph pipeline builder
│       └── rag_nodes.py        # retrieve_docs + generate_answer nodes
│
├── streamlit_app/
│   ├── app.py                  # Streamlit UI
│   └── api_client.py           # HTTP client for FastAPI
│
├── .env.example
└── requirements.txt
```

---

## Setup

```bash
# 1. Clone / unzip and enter the directory
cd rag_production

# 2. Create a virtual environment
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

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
