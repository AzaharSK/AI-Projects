"""
/query  endpoint — run the RAG pipeline for a user question.
"""

from fastapi import APIRouter, HTTPException, Request

from src.api.schemas.schemas import QueryRequest, QueryResponse, SourceDocument

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("", response_model=QueryResponse, summary="Ask a question")
async def query(body: QueryRequest, request: Request) -> QueryResponse:
    """
    Run the agentic RAG pipeline against the current vector index.

    Returns the generated answer plus the source document passages
    that were retrieved (for transparency / citation).

    Raises **503** if no documents have been ingested yet.
    """
    orchestrator = request.app.state.orchestrator

    if not orchestrator.is_ready:
        raise HTTPException(
            status_code=503,
            detail="RAG system not ready. POST to /ingest first.",
        )

    result = orchestrator.query(body.question)
    sources = [SourceDocument(**s) for s in result["sources"]]

    return QueryResponse(
        answer=result["answer"],
        sources=sources,
        latency_ms=result["latency_ms"],
    )
