"""
LangGraph node implementations.

1. retrieve_docs → fetch chunks
2. generate_answer → tool-enabled LLM response
"""

from __future__ import annotations

import logging
from typing import List

from langchain.tools import tool
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from src.core.exceptions.errors import AnswerGenerationError
from src.core.state.rag_state import RAGState

logger=logging.getLogger(__name__)

_SYSTEM_PROMPT="""
You are a precise RAG assistant.
Use retriever first for document questions.
Use wikipedia only for missing background knowledge.
Prefer retrieved context and cite sources.
Return concise answers.
"""

class RAGNodes:
    """
    Stateless LangGraph node handlers.

    Usage:
        nodes=RAGNodes(retriever,llm)
        builder.add_node("retriever",nodes.retrieve_docs)
        builder.add_node("responder",nodes.generate_answer)
    """

    def __init__(self,retriever,llm):
        self._retriever=retriever
        self._llm=llm.bind_tools(self._build_tools())

    def retrieve_docs(self,state:RAGState)->RAGState:
        docs:List[Document]=self._retriever.invoke(state.question)
        logger.debug("Retrieved %d docs for %.80s",len(docs),state.question)
        return RAGState(question=state.question,retrieved_docs=docs)

    def generate_answer(self,state:RAGState)->RAGState:
        try:
            context=self._format_docs(state.retrieved_docs)

            messages=[
                SystemMessage(content=_SYSTEM_PROMPT),
                HumanMessage(content=f"Context:\n{context}\n\nQuestion:\n{state.question}")
            ]

            result=self._llm.invoke(messages)

            answer=getattr(result,"content","")
            if isinstance(answer,list):
                answer=" ".join(str(x) for x in answer)

            answer=str(answer).strip()

            if not answer:
                raise AnswerGenerationError("Empty response")

            logger.debug("Generated answer %.120s",answer)

            return RAGState(
                question=state.question,
                retrieved_docs=state.retrieved_docs,
                answer=answer
            )

        except Exception as exc:
            logger.exception("Generation failed")
            raise AnswerGenerationError(str(exc)) from exc

    def _build_tools(self):
        retriever=self._retriever

        @tool
        def retriever_tool(query:str)->str:
            """Search ingested documents."""
            docs=retriever.invoke(query)
            if not docs:return "No relevant documents found."
            return self._format_docs(docs)

        wikipedia_tool=WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(top_k_results=3,lang="en")
        )

        return [retriever_tool,wikipedia_tool]

    @staticmethod
    def _format_docs(docs:List[Document])->str:
        return "\n\n".join(
            f"[{i}] {(d.metadata or {}).get('title') or (d.metadata or {}).get('source') or f'doc_{i}'}\n{d.page_content}"
            for i,d in enumerate(docs[:8],1)
        )