"""
LangGraph state schema.
Kept minimal — all fields that flow through the graph live here.
"""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field
from langchain_core.documents import Document


class RAGState(BaseModel):
    """Immutable-ish state threaded through the LangGraph nodes."""

    question: str = Field(..., description="User question")
    retrieved_docs: List[Document] = Field(
        default_factory=list,
        description="Documents fetched from the vector store / agent tools",
    )
    answer: str = Field(default="", description="Final generated answer")

    model_config = {"arbitrary_types_allowed": True}
