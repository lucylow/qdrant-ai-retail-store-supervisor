from __future__ import annotations

from typing import Any, Dict, List

from context_engine.context_builder import ContextBuilder
from rag.agentic_rag_pipeline import AgenticRAG
from reasoning.retail_reasoning_engine import RetailReasoningEngine
from vector_store.retail_vector_memory import RetailVectorMemory


class RetailCopilot:
    """
    Retail copilot that supports both:
    - existing context-building workflow (`run`)
    - agentic RAG + LLM answering (`answer`)
    """

    def __init__(self) -> None:
        self.memory = RetailVectorMemory()
        self.context_builder = ContextBuilder()

        # Agentic RAG + reasoning
        self.agentic_rag = AgenticRAG()
        self.reasoner = RetailReasoningEngine()

    # --- Existing API: keep for backwards compatibility ---

    def run(
        self,
        question: str,
        product_data: List[Dict[str, Any]],
        sales_data: List[Dict[str, Any]],
        collection: str = "retail_docs",
    ) -> str:
        docs = self.memory.search(collection, question)

        context = self.context_builder.build_context(
            question,
            product_data,
            sales_data,
            docs,
        )

        return context

    # --- New API: Agentic RAG + reasoning ---

    def answer(self, question: str, collection: str = "retail_docs") -> str:
        """
        High-level convenience method:
        - retrieves documents via AgenticRAG
        - builds a compressed context
        - calls the LLM reasoning engine
        """
        docs = self.agentic_rag.retrieve(question, collection=collection)
        context = self.agentic_rag.build_context(docs)
        return self.reasoner.answer(context, question=question)


