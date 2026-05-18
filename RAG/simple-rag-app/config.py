import os
from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Enforces fail-fast system properties validation checks across system initializations."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    OPENAI_API_KEY: Optional[SecretStr] = Field(default=None)
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    CHROMA_DB_PATH: str = Field(default="./chroma_db")
    
    # Core Constants Config Management
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

settings = Settings()