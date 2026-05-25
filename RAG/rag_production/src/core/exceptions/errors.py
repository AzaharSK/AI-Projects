"""
Centralised exception hierarchy.
Raise these; let FastAPI exception handlers translate them to HTTP responses.
"""


class RAGBaseError(Exception):
    """Root of all RAG-specific errors."""
    http_status: int = 500


class VectorStoreNotReadyError(RAGBaseError):
    """Raised when a query is attempted before the vector store is built."""
    http_status = 503
    def __init__(self) -> None:
        super().__init__("Vector store is not initialised. Ingest documents first.")


class DocumentIngestionError(RAGBaseError):
    """Raised when document loading or splitting fails."""
    http_status = 422
    def __init__(self, source: str, reason: str) -> None:
        super().__init__(f"Failed to ingest '{source}': {reason}")
        self.source = source
        self.reason = reason


class UnsupportedSourceError(RAGBaseError):
    """Raised for unknown / unsupported source types."""
    http_status = 422
    def __init__(self, source: str) -> None:
        super().__init__(
            f"Unsupported source: '{source}'. "
            "Provide an HTTP(S) URL, a .txt file path, or a PDF directory."
        )
        self.source = source


class GraphNotBuiltError(RAGBaseError):
    """Raised when the LangGraph pipeline hasn't been compiled yet."""
    http_status = 503
    def __init__(self) -> None:
        super().__init__("RAG graph is not built. Call build() first.")


class AnswerGenerationError(RAGBaseError):
    """Raised when the LLM fails to produce an answer."""
    http_status = 502
    def __init__(self, detail: str) -> None:
        super().__init__(f"Answer generation failed: {detail}")
