"""
Production settings using pydantic-settings for env-based configuration.
All tunables live here — no magic strings scattered across the codebase.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM ──────────────────────────────────────────────────────────────────
    openai_api_key: str = Field(..., description="OpenAI API key")
    llm_model: str = Field("openai:gpt-4o", description="LangChain model string")
    llm_temperature: float = Field(0.0, ge=0.0, le=2.0)

    # ── Embeddings ────────────────────────────────────────────────────────────
    embedding_model: str = Field("text-embedding-3-small")

    # ── Document Processing ───────────────────────────────────────────────────
    chunk_size: int = Field(500, gt=0)
    chunk_overlap: int = Field(50, ge=0)
    retriever_k: int = Field(6, gt=0, description="Top-k docs to retrieve")

    # ── Default Sources ───────────────────────────────────────────────────────
    default_urls: List[str] = Field(
        default=[
            "https://lilianweng.github.io/posts/2023-06-23-agent/",
            "https://lilianweng.github.io/posts/2024-04-12-diffusion-video/",
        ]
    )

    # ── API Server ────────────────────────────────────────────────────────────
    api_host: str = Field("0.0.0.0")
    api_port: int = Field(8000, gt=0, lt=65535)
    api_prefix: str = Field("/api/v1")
    cors_origins: List[str] = Field(default=["*"])
    log_level: str = Field("INFO")

    # ── Streamlit ─────────────────────────────────────────────────────────────
    backend_url: str = Field("http://localhost:8000", description="FastAPI base URL")

    @field_validator("llm_temperature")
    @classmethod
    def clamp_temperature(cls, v: float) -> float:
        return max(0.0, min(2.0, v))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton settings — import this everywhere."""
    return Settings()
