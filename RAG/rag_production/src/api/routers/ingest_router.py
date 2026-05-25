"""
/ingest  endpoint — trigger document ingestion and indexing.
"""

from fastapi import APIRouter, Request

from src.api.schemas.schemas import IngestRequest, IngestResponse

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("", response_model=IngestResponse, summary="Ingest documents into the RAG system")
async def ingest_documents(body: IngestRequest, request: Request) -> IngestResponse:
    """
    Load and index documents from the provided sources.

    Sources can be:
    - HTTP/HTTPS URLs
    - Absolute paths to `.txt` files
    - Absolute paths to directories containing PDFs
    - Absolute paths to individual `.pdf` files

    This rebuilds the vector store and recompiles the graph.
    Subsequent `/query` calls will use the new index.
    """
    orchestrator = request.app.state.orchestrator
    result = orchestrator.ingest(body.sources)
    return IngestResponse(**result)
