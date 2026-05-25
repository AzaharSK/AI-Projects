"""
FastAPI application factory.

Run with:
    uvicorn api.app:create_app --factory --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware.exception_handlers import generic_exception_handler, rag_exception_handler
from src.api.routers import ingest_router, observability_router, query_router
from src.core.config.settings import get_settings
from src.core.exceptions.errors import RAGBaseError
from src.services.rag_orchestrator import RAGOrchestrator

# ── logging ───────────────────────────────────────────────────────────────────

def _configure_logging(level: str) -> None:
    logging.basicConfig(
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


# ── lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Bootstrap the orchestrator on startup; clean up on shutdown."""
    settings = get_settings()
    _configure_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    logger.info("🚀 RAG API starting up …")
    orchestrator = RAGOrchestrator()

    # Auto-ingest default URLs so the system is ready immediately
    if settings.default_urls:
        logger.info("Auto-ingesting %d default source(s) …", len(settings.default_urls))
        try:
            summary = orchestrator.ingest(settings.default_urls)
            logger.info(
                "Auto-ingest done: %d chunks in %.2fs",
                summary["chunks_created"],
                summary["duration_s"],
            )
        except Exception:
            logger.exception("Auto-ingest failed — system will start without an index.")

    app.state.orchestrator = orchestrator
    logger.info("✅ RAG API ready.")
    yield
    logger.info("🛑 RAG API shutting down.")


# ── factory ───────────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Agentic RAG API",
        description=(
            "Production-grade Retrieval-Augmented Generation service.\n\n"
            "**Endpoints**\n"
            "- `POST /api/v1/ingest` — load & index documents\n"
            "- `POST /api/v1/query`  — ask a question\n"
            "- `GET  /health`        — liveness/readiness probe\n"
            "- `GET  /metrics`       — operational metrics\n"
        ),
        version="1.0.0",
        lifespan=_lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── exception handlers ────────────────────────────────────────────────────
    app.add_exception_handler(RAGBaseError, rag_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # ── routers ───────────────────────────────────────────────────────────────
    prefix = settings.api_prefix
    app.include_router(ingest_router.router, prefix=prefix)
    app.include_router(query_router.router, prefix=prefix)
    app.include_router(observability_router.router)  # /health and /metrics at root

    return app


# Allow `uvicorn api.app:app` too
app = create_app()
