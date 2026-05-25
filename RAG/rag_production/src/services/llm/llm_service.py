"""
LLM provider abstraction.
Swap the underlying model by changing settings — nothing else changes.
"""

from __future__ import annotations

import os
import logging
from functools import lru_cache

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from src.core.config.settings import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    """Thin factory/wrapper around the configured language model."""

    def __init__(self) -> None:
        settings = get_settings()
        os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
        self._model_string = settings.llm_model
        self._temperature = settings.llm_temperature
        self._llm: BaseChatModel | None = None

    # ── public ────────────────────────────────────────────────────────────────

    @property
    def llm(self) -> BaseChatModel:
        if self._llm is None:
            self._llm = self._build()
        return self._llm

    def _build(self) -> BaseChatModel:
        logger.info("Initialising LLM: %s (temp=%.2f)", self._model_string, self._temperature)
        return init_chat_model(self._model_string, temperature=self._temperature)


@lru_cache(maxsize=1)
def get_llm_service() -> LLMService:
    return LLMService()
