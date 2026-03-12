from __future__ import annotations

from typing import Any, Dict, List

from app.context_engine import RetailContextBuilder
from app.generative_ai import RetailContentGenerator
from app.vector_store.retail_memory import RetailVectorMemory, RetailVectorSearchResult


class RetailCopilot:
    """
    Thin orchestrator that ties vector memory, context building and generation
    together for simple retail Q&A / content generation scenarios.
    """

    def __init__(
        self,
        vector_store: RetailVectorMemory | None = None,
        generator: RetailContentGenerator | None = None,
    ) -> None:
        self.vector_store = vector_store or RetailVectorMemory()
        self.generator = generator or RetailContentGenerator()
        self._context_builder = RetailContextBuilder()

    def _docs_to_product_list(
        self,
        docs: List[RetailVectorSearchResult],
    ) -> List[Dict[str, Any]]:
        products: List[Dict[str, Any]] = []
        for d in docs:
            payload = d.payload or {}
            products.append(payload)
        return products

    def answer(self, question: str, customer_profile: Dict[str, Any] | None = None) -> str:
        """
        High-level helper meant to mirror the simple example from the spec.

        It:
        - runs semantic product search for the question
        - builds a retail-flavored context
        - asks the generator for rich marketing content
        """
        docs = self.vector_store.search_products(question)
        products = self._docs_to_product_list(docs)
        context = self._context_builder.build_context(
            user_query=question,
            product_data=products,
            customer_profile=customer_profile or {},
            retrieved_docs=[],
        )
        return self.generator.generate_product_description(context)


__all__ = ["RetailCopilot"]

