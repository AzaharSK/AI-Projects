import logging
from typing import Dict, Any, Callable, Optional
from openai import OpenAI
import requests

from config import settings
from schema import LLMProvider, EmbeddingProvider, EmbeddingMetaResponse

logger = logging.getLogger("RAG.Infrastructure.ModelSelector")

class SimpleModelSelector:
    """Manages system capabilities and handles vendor-agnostic generation client abstraction."""
    
    def __init__(self):
        self.llm_models: Dict[str, str] = {
            LLMProvider.OPENAI.value: "GPT-4 / Cloud Core API Engine",
            LLMProvider.OLLAMA.value: "Llama3 / Local System Compute Daemon"
        }
        
        self.embedding_models: Dict[str, Dict[str, Any]] = {
            EmbeddingProvider.OPENAI.value: {
                "name": "OpenAI Embeddings",
                "dimensions": 1536,
                "model_name": "text-embedding-3-small",
            },
            EmbeddingProvider.CHROMA.value: {
                "name": "Chroma Default MiniLM",
                "dimensions": 384,
                "model_name": "all-MiniLM-L6-v2"
            },
            EmbeddingProvider.NOMIC.value: {
                "name": "Nomic Embed Text",
                "dimensions": 768,
                "model_name": "nomic-embed-text",
            },
        }

    def get_system_capabilities(self) -> Dict[str, Any]:
        return {
            "available_llms": self.llm_models,
            "available_embeddings": {
                k: EmbeddingMetaResponse(**v) for k, v in self.embedding_models.items()
            }
        }

    def resolve_llm_client(self, provider: LLMProvider) -> Callable[[str, str], str]:
        """Factory Method returning unified programmatic wrappers independent of generation vendor type."""
        if provider == LLMProvider.OPENAI:
            if not settings.OPENAI_API_KEY:
                raise ValueError("Initialization Defect: OpenAI provider requires a valid system API Key.")
            
            client = OpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())
            
            def _openai_completion(prompt: str, system_instruction: str) -> str:
                logger.info("Executing completion request targeting openai matrix endpoint nodes.")
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0
                )
                return response.choices[0].message.content
            return _openai_completion

        elif provider == LLMProvider.OLLAMA:
            base_url = f"{settings.OLLAMA_BASE_URL}/v1"
            client = OpenAI(base_url=base_url, api_key="ollama")
            
            def _ollama_completion(prompt: str, system_instruction: str) -> str:
                logger.info("Executing loopback network complete logic targeting local Ollama client contexts.")
                try:
                    response = client.chat.completions.create(
                        model="llama3",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.0
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    raise RuntimeError(f"Ollama local container processing loop failure trace: {e}")
            return _ollama_completion

        raise NotImplementedError(f"Unsupported Provider: {provider}")