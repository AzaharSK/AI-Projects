from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class LLMProvider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"

class EmbeddingProvider(str, Enum):
    OPENAI = "openai"
    CHROMA = "chroma"
    NOMIC = "nomic"

class EmbeddingMetaResponse(BaseModel):
    name: str
    dimensions: int
    model_name: Optional[str]

class SystemCapabilitiesResponse(BaseModel):
    available_llms: Dict[str, str]
    available_embeddings: Dict[str, EmbeddingMetaResponse]

class QueryInputPayload(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000, description="The text question sent by user")
    embedding_model: EmbeddingProvider = Field(default=EmbeddingProvider.OPENAI)
    llm_model: LLMProvider = Field(default=LLMProvider.OPENAI)
    n_results: Optional[int] = Field(default=3, ge=1, le=10)

class QueryContextNode(BaseModel):
    passage_index: int
    text: str
    source: str

class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    source_passages: List[QueryContextNode]