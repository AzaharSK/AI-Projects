"""
RAGOrchestrator — application-level façade.

Single entry point consumed by FastAPI routers.
Owns the lifecycle of every service and keeps them in sync.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from src.services.ingestion.ingestion_service import IngestionService
from src.services.llm.llm_service import LLMService
from src.services.vectorstore.vectorstore_service import VectorStoreService
from src.services.graph.graph_service import GraphService

logger = logging.getLogger(__name__)


class RAGOrchestrator:
    """
    Coordinates ingestion → indexing → graph-build → query.

    Intended to be used as a FastAPI dependency (app-level singleton)::

        orchestrator = RAGOrchestrator()
        app.state.orchestrator = orchestrator
    """

    def __init__(self) -> None:
        self._llm_service = LLMService()
        self._ingestion = IngestionService()
        self._vectorstore = VectorStoreService()
        self._graph: Optional[GraphService] = None

        # runtime metrics
        self._ingest_count: int = 0
        self._query_count: int = 0
        self._total_query_ms: float = 0.0
        self._startup_ts: float = time.time()

    # ── properties ────────────────────────────────────────────────────────────

    @property
    def is_ready(self) -> bool:
        return (
            self._vectorstore.is_ready
            and self._graph is not None
            and self._graph.is_built
        )

    @property
    def vectorstore_metrics(self) -> dict:
        return self._vectorstore.metrics

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def ingest(self, sources: List[str]) -> Dict[str, Any]:
        """
        Load sources, chunk, index, and (re)build the graph.

        Args:
            sources: URLs, file paths, or directory paths.

        Returns:
            Summary dict with counts and timing.
        """
        t0 = time.perf_counter()

        chunks = self._ingestion.ingest(sources)
        self._vectorstore.build(chunks)

        retriever = self._vectorstore.get_retriever()
        llm = self._llm_service.llm

        if self._graph is None:
            self._graph = GraphService(retriever=retriever, llm=llm)
            self._graph.build()
        else:
            self._graph.rebuild(retriever=retriever)

        self._ingest_count += 1
        duration = round(time.perf_counter() - t0, 3)

        logger.info("Ingest complete: %d sources → %d chunks in %.3fs", len(sources), len(chunks), duration)
        return {
            "sources_processed": len(sources),
            "chunks_created": len(chunks),
            "duration_s": duration,
        }

    def query(self, question: str) -> Dict[str, Any]:
        """
        Run the RAG pipeline for a question.

        Returns:
            Dict with ``answer``, ``sources``, and ``latency_ms``.
        """
        t0 = time.perf_counter()
        result = self._graph.run(question)
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)

        self._query_count += 1
        self._total_query_ms += latency_ms

        sources = [
            {
                "content": doc.page_content[:300],
                "metadata": doc.metadata,
            }
            for doc in result.get("retrieved_docs", [])
        ]

        return {
            "answer": result.get("answer", ""),
            "sources": sources,
            "latency_ms": latency_ms,
        }

    def health(self) -> Dict[str, Any]:
        return {
            "status": "ok" if self.is_ready else "initialising",
            "is_ready": self.is_ready,
            "uptime_s": round(time.time() - self._startup_ts, 1),
        }

    def metrics(self) -> Dict[str, Any]:
        avg_latency = (
            round(self._total_query_ms / self._query_count, 1)
            if self._query_count
            else 0.0
        )
        return {
            "query_count": self._query_count,
            "ingest_count": self._ingest_count,
            "avg_latency_ms": avg_latency,
            "vectorstore": self._vectorstore.metrics,
        }
