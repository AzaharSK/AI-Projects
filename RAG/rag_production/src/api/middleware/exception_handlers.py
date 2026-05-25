"""
Global exception handlers — converts RAGBaseError subclasses to HTTP responses
so routers never need bare try/except.
"""

from __future__ import annotations

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.exceptions.errors import RAGBaseError

logger = logging.getLogger(__name__)


async def rag_exception_handler(request: Request, exc: RAGBaseError) -> JSONResponse:
    logger.error("RAG error on %s: %s", request.url, exc)
    return JSONResponse(
        status_code=exc.http_status,
        content={"detail": str(exc), "type": type(exc).__name__},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s", request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error.", "type": type(exc).__name__},
    )
