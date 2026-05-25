"""
Document ingestion service.
Responsible for loading raw content from any supported source and chunking it.
Supported sources:
  - HTTP / HTTPS URLs  → WebBaseLoader
  - .txt file paths    → TextLoader
  - PDF file path      → PyPDFLoader
  - Directory path     → PyPDFDirectoryLoader (all PDFs inside)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Union

from langchain_community.document_loaders import (
    PyPDFDirectoryLoader,
    PyPDFLoader,
    TextLoader,
    WebBaseLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.config.settings import get_settings
from src.core.exceptions.errors import DocumentIngestionError, UnsupportedSourceError

logger = logging.getLogger(__name__)


class IngestionService:
    """
    Load and chunk documents from heterogeneous sources.

    Usage::

        svc = IngestionService()
        chunks = svc.ingest(["https://example.com", "/data/report.pdf"])
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        settings = get_settings()
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size or settings.chunk_size,
            chunk_overlap=chunk_overlap or settings.chunk_overlap,
            add_start_index=True,
        )

    # ── public ────────────────────────────────────────────────────────────────

    def ingest(self, sources: List[str]) -> List[Document]:
        """
        Full pipeline: load all sources → split into chunks.

        Args:
            sources: Mix of URLs, file paths, or directory paths.

        Returns:
            Flat list of chunked ``Document`` objects.
        """
        raw: List[Document] = []
        for src in sources:
            raw.extend(self._load_one(src))

        chunks = self._splitter.split_documents(raw)
        logger.info("Ingested %d sources → %d chunks", len(sources), len(chunks))
        return chunks

    # ── private loaders ───────────────────────────────────────────────────────

    def _load_one(self, source: str) -> List[Document]:
        """Dispatch a single source to the right loader."""
        if source.startswith(("http://", "https://")):
            return self._load_url(source)

        path = Path(source)
        if path.is_dir():
            return self._load_pdf_dir(path)
        if path.suffix.lower() == ".pdf":
            return self._load_pdf(path)
        if path.suffix.lower() == ".txt":
            return self._load_txt(path)

        raise UnsupportedSourceError(source)

    def _load_url(self, url: str) -> List[Document]:
        try:
            loader = WebBaseLoader(url)
            docs = loader.load()
            logger.debug("Loaded %d doc(s) from URL: %s", len(docs), url)
            return docs
        except Exception as exc:
            raise DocumentIngestionError(url, str(exc)) from exc

    def _load_pdf(self, path: Path) -> List[Document]:
        try:
            loader = PyPDFLoader(str(path))
            docs = loader.load()
            logger.debug("Loaded %d page(s) from PDF: %s", len(docs), path)
            return docs
        except Exception as exc:
            raise DocumentIngestionError(str(path), str(exc)) from exc

    def _load_pdf_dir(self, directory: Path) -> List[Document]:
        try:
            loader = PyPDFDirectoryLoader(str(directory))
            docs = loader.load()
            logger.debug("Loaded %d doc(s) from PDF dir: %s", len(docs), directory)
            return docs
        except Exception as exc:
            raise DocumentIngestionError(str(directory), str(exc)) from exc

    def _load_txt(self, path: Path) -> List[Document]:
        try:
            loader = TextLoader(str(path), encoding="utf-8")
            docs = loader.load()
            logger.debug("Loaded %d doc(s) from TXT: %s", len(docs), path)
            return docs
        except Exception as exc:
            raise DocumentIngestionError(str(path), str(exc)) from exc
