"""
Vector store service — FAISS-backed, thread-safe singleton.

Responsibilities:
  - Build an in-memory FAISS index from document chunks.
  - Expose a LangChain retriever consumed by the graph.
  - Track basic metrics (document count, last build time).
"""

from __future__ import annotations

import logging
import threading
import time
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import OpenAIEmbeddings

from src.core.config.settings import get_settings
from src.core.exceptions.errors import VectorStoreNotReadyError

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Manages the FAISS vector store lifecycle.

    Thread-safe: a ``threading.Lock`` guards index rebuild so that
    concurrent HTTP requests cannot corrupt the index mid-build.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._embeddings = OpenAIEmbeddings(model=settings.embedding_model)
        self._retriever_k: int = settings.retriever_k

        self._store: Optional[FAISS] = None
        self._retriever: Optional[VectorStoreRetriever] = None
        self._lock = threading.Lock()

        # metrics
        self._doc_count: int = 0
        self._chunk_count: int = 0
        self._last_build_ts: Optional[float] = None
        self._build_duration_s: Optional[float] = None

    # ── public ────────────────────────────────────────────────────────────────

    @property
    def is_ready(self) -> bool:
        return self._store is not None

    @property
    def metrics(self) -> dict:
        return {
            "is_ready": self.is_ready,
            "chunk_count": self._chunk_count,
            "last_build_ts": self._last_build_ts,
            "build_duration_s": self._build_duration_s,
        }

    def build(self, documents: List[Document]) -> None:
        """
        (Re)build the vector store from a list of chunked documents.
        Blocks the caller until the index is ready.
        """
        if not documents:
            raise ValueError("Cannot build vector store from an empty document list.")

        with self._lock:
            logger.info("Building FAISS index for %d chunks …", len(documents))
            t0 = time.perf_counter()
            self._store = FAISS.from_documents(documents, self._embeddings)
            self._retriever = self._store.as_retriever(
                search_kwargs={"k": self._retriever_k}
            )
            self._chunk_count = len(documents)
            self._last_build_ts = time.time()
            self._build_duration_s = round(time.perf_counter() - t0, 3)
            logger.info(
                "FAISS index ready — %d chunks in %.3fs",
                self._chunk_count,
                self._build_duration_s,
            )

    def get_retriever(self) -> VectorStoreRetriever:
        if self._retriever is None:
            raise VectorStoreNotReadyError()
        return self._retriever

    def similarity_search(self, query: str, k: int | None = None) -> List[Document]:
        if self._store is None:
            raise VectorStoreNotReadyError()
        return self._store.similarity_search(query, k=k or self._retriever_k)
