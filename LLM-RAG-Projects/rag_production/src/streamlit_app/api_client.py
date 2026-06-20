"""
Thin HTTP client for talking to the FastAPI backend.
All network calls go through here — Streamlit pages import this, never requests directly.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import ConnectionError, Timeout

logger = logging.getLogger(__name__)

_TIMEOUT = 120  # seconds — LLM calls can be slow


class APIClient:
    """
    Wrapper around the RAG FastAPI service.

    Args:
        base_url: Root URL of the FastAPI server, e.g. ``http://localhost:8000``.
    """

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.base_url = base_url.rstrip("/")
        self._prefix = f"{self.base_url}/api/v1"

    # ── helpers ───────────────────────────────────────────────────────────────

    def _post(self, path: str, payload: dict) -> Dict[str, Any]:
        url = f"{self._prefix}{path}"
        try:
            resp = requests.post(url, json=payload, timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except (ConnectionError, Timeout) as exc:
            raise RuntimeError(f"Cannot reach backend at {self.base_url}") from exc

    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except (ConnectionError, Timeout) as exc:
            raise RuntimeError(f"Cannot reach backend at {self.base_url}") from exc

    # ── public ────────────────────────────────────────────────────────────────

    def health(self) -> Dict[str, Any]:
        return self._get("/health")

    def metrics(self) -> Dict[str, Any]:
        return self._get("/app-metrics")

    def ingest(self, sources: List[str]) -> Dict[str, Any]:
        return self._post("/ingest", {"sources": sources})

    def query(self, question: str) -> Dict[str, Any]:
        return self._post("/query", {"question": question})
