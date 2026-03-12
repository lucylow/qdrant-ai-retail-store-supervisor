from __future__ import annotations

from typing import Any, Iterable, List

from rag.context_selector import ContextSelector
from rag.retrieval_optimizer import RetrievalOptimizer
from vector_store.retail_vector_memory import RetailVectorMemory


class AgenticRAG:
    """
    Agentic RAG pipeline that:
    - rewrites queries
    - retrieves from Qdrant
    - selects context documents
    """

    def __init__(self) -> None:
        self.memory = RetailVectorMemory()
        self.context_selector = ContextSelector()
        self.query_optimizer = RetrievalOptimizer()

    def retrieve(self, query: str, collection: str = "retail_docs") -> List[Any]:
        improved_query = self.query_optimizer.adjust_query(query)

        docs = self.memory.search(collection, improved_query)

        context_docs = self.context_selector.score_documents(docs)

        return context_docs

    def build_context(self, docs: Iterable[Any], max_chars: int = 4000) -> str:
        """
        Compress selected docs into a single context string.
        """
        return self.query_optimizer.compress_context(docs, max_chars=max_chars)

