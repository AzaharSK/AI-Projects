import os
import logging
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any

from config import settings
from schema import EmbeddingProvider, LLMProvider
from models_factory import SimpleModelSelector

logger = logging.getLogger("RAG.Engine.CoreSystem")

class SimpleRAGSystem:
    """System orchestrator handling database vector persistence indexing and similarity evaluations."""
    
    def __init__(self, embedding_model: EmbeddingProvider, llm_model: LLMProvider):
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        
        # Initialize persistent store client parameters
        self.db = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self._setup_embedding_function()
        
        # Resolve modular generation components
        self.selector = SimpleModelSelector()
        self.llm_executor = self.selector.resolve_llm_client(self.llm_model)
        self.collection = self.setup_collection()

    def _setup_embedding_function(self):
        """Maps unified interaction pipelines onto different embedding providers."""
        if self.embedding_model == EmbeddingProvider.OPENAI:
            if not settings.OPENAI_API_KEY:
                raise ValueError("System Missing Token Variables: OpenAI embeddings require a configured API key.")
            self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY.get_secret_value(),
                model_name="text-embedding-3-small",
            )
        elif self.embedding_model == EmbeddingProvider.NOMIC:
            self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key="ollama",
                api_base=f"{settings.OLLAMA_BASE_URL}/v1",
                model_name="nomic-embed-text",
            )
        else: # Chroma Default
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    def setup_collection(self) -> chromadb.Collection:
        """Enforces schema rules and handles storage collection lifecycles safely."""
        collection_name = f"system_index_layer_{self.embedding_model.value}"
        return self.db.get_or_create_collection(
            name=collection_name, 
            embedding_function=self.embedding_fn
        )

    def add_documents(self, chunks: List[Dict[str, Any]]) -> bool:
        if not chunks:
            return False
        try:
            self.collection.add(
                ids=[c["id"] for c in chunks],
                documents=[c["text"] for c in chunks],
                metadatas=[c["metadata"] for c in chunks]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to index documents inside Chroma pipeline layers: {e}")
            return False

    def query_documents(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Queries database index vectors to extract contextually related text blocks."""
        try:
            results = self.collection.query(query_texts=[query], n_results=n_results)
            formatted_passages = []
            
            if results and 'documents' in results and results['documents']:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(documents)
                
                for idx, (doc_text, meta) in enumerate(zip(documents, metadatas)):
                    formatted_passages.append({
                        "passage_index": idx + 1,
                        "text": doc_text,
                        "source": meta.get("source", "unknown_boundary_context")
                    })
            return formatted_passages
        except Exception as e:
            logger.error(f"Similarity mapping traversal failed execution loop parameters: {e}")
            return []

    def generate_response(self, query: str, context_passages: List[Dict[str, Any]]) -> str:
        """Constructs an augmented context prompt payload, then routes it to your selected model client."""
        context_str = "\n---\n".join([f"Source [{p['source']}]: {p['text']}" for p in context_passages])
        
        augmented_prompt = (
            f"Context extracts source baseline definitions:\n{context_str}\n\n"
            f"User Evaluation Request Query: {query}\n\n"
            f"Synthesized Response:"
        )
        
        system_instruction = (
            "You are an enterprise AI assistant answering questions using only the provided context extracts.\n"
            "If the information is not present within the provided context definitions, reply explaining "
            "that the required data cannot be found within the indexed codebase parameters. Do not extrapolate."
        )
        
        return self.llm_executor(prompt=augmented_prompt, system_instruction=system_instruction)