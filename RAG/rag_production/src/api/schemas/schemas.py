"""
Request / Response Pydantic models for all API endpoints.
Kept in one file so the Streamlit client can import them too (or mirror them).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


# ── Ingest ────────────────────────────────────────────────────────────────────

class IngestRequest(BaseModel):
    sources: List[str] = Field(
        ...,
        min_length=1,
        description="List of URLs, file paths, or PDF directory paths to ingest.",
        examples=[["https://example.com/doc", "/data/reports/"]],
    )


class IngestResponse(BaseModel):
    sources_processed: int
    chunks_created: int
    duration_s: float
    message: str = "Ingestion complete."


# ── Query ─────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class SourceDocument(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument] = Field(default_factory=list)
    latency_ms: float


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    is_ready: bool
    uptime_s: float


# ── Metrics ───────────────────────────────────────────────────────────────────

class VectorStoreMetrics(BaseModel):
    is_ready: bool
    chunk_count: int
    last_build_ts: Optional[float] = None
    build_duration_s: Optional[float] = None


class MetricsResponse(BaseModel):
    query_count: int
    ingest_count: int
    avg_latency_ms: float
    vectorstore: VectorStoreMetrics
