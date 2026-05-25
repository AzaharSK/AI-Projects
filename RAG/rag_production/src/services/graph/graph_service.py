"""
LangGraph pipeline builder.

Wires nodes → edges → compiles a runnable graph.
The compiled graph is cached; call rebuild() to replace it after
re-ingestion / re-indexing.
"""

from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, StateGraph

from src.core.exceptions.errors import GraphNotBuiltError
from src.core.state.rag_state import RAGState
from src.services.graph.rag_nodes import RAGNodes

logger = logging.getLogger(__name__)


class GraphService:
    """
    Builds and runs the two-node RAG pipeline:

        [retrieve_docs] ──► [generate_answer] ──► END
    """

    def __init__(self, retriever: Any, llm: Any) -> None:
        self._retriever = retriever
        self._llm = llm
        self._graph = None

    # ── public ────────────────────────────────────────────────────────────────

    @property
    def is_built(self) -> bool:
        return self._graph is not None

    def build(self) -> None:
        """Compile the LangGraph pipeline. Idempotent."""
        nodes = RAGNodes(retriever=self._retriever, llm=self._llm)

        builder = StateGraph(RAGState)
        builder.add_node("retrieve_docs", nodes.retrieve_docs)
        builder.add_node("generate_answer", nodes.generate_answer)

        builder.set_entry_point("retrieve_docs")
        builder.add_edge("retrieve_docs", "generate_answer")
        builder.add_edge("generate_answer", END)

        self._graph = builder.compile()
        logger.info("LangGraph pipeline compiled successfully.")

    def rebuild(self, retriever: Any) -> None:
        """Replace the retriever (e.g. after re-ingestion) and recompile."""
        self._retriever = retriever
        self._graph = None
        self.build()

    def run(self, question: str) -> dict:
        """
        Execute the pipeline for a single question.

        Returns:
            Final ``RAGState`` as a dict with keys:
            ``question``, ``retrieved_docs``, ``answer``.
        """
        if self._graph is None:
            raise GraphNotBuiltError()

        initial_state = RAGState(question=question)
        return self._graph.invoke(initial_state)
