from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from rag.context_selector import ContextSelector
from rag.retrieval_optimizer import RetrievalOptimizer
from vector_store.retail_vector_memory import RetailVectorMemory

logger = logging.getLogger(__name__)


@dataclass
class RetrievalTrace:
    """Full audit trail for a single agentic retrieval cycle."""

    query: str
    rewritten_query: str = ""
    raw_doc_count: int = 0
    scored_doc_count: int = 0
    episodic_hits: int = 0
    confidence: float = 0.0
    latency_ms: float = 0.0
    fallback_used: bool = False
    steps: List[str] = field(default_factory=list)


@dataclass
class AgenticResult:
    """Return type wrapping context + provenance trace."""

    context: str
    docs: List[Any]
    trace: RetrievalTrace


class AgenticRAG:
    """
    Agentic RAG pipeline — multi-step retrieval with:
    - query rewriting & expansion
    - primary vector retrieval from Qdrant
    - episodic memory look-up (past successful solutions)
    - learnable context selection
    - confidence gating & fallback paths
    - full retrieval trace for observability
    """

    CONFIDENCE_THRESHOLD = 0.35

    def __init__(self) -> None:
        self.memory = RetailVectorMemory()
        self.context_selector = ContextSelector()
        self.query_optimizer = RetrievalOptimizer()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        collection: str = "retail_docs",
        top_k: int = 5,
        include_episodes: bool = True,
    ) -> List[Any]:
        """Backward-compatible retrieval returning ranked docs."""
        result = self.agentic_retrieve(
            query, collection=collection, top_k=top_k, include_episodes=include_episodes
        )
        return result.docs

    def agentic_retrieve(
        self,
        query: str,
        collection: str = "retail_docs",
        top_k: int = 5,
        include_episodes: bool = True,
    ) -> AgenticResult:
        """
        Full agentic retrieval cycle with trace.

        Steps:
        1. Rewrite / expand query
        2. Retrieve from primary collection
        3. Optionally retrieve episodic memory
        4. Merge & score
        5. Confidence gate — fallback if below threshold
        6. Return ranked docs + compressed context + trace
        """
        t0 = time.perf_counter()
        trace = RetrievalTrace(query=query)

        # 1 — Query rewriting
        improved_query = self.query_optimizer.adjust_query(query)
        trace.rewritten_query = improved_query
        trace.steps.append(f"query_rewrite: '{query}' → '{improved_query}'")

        # 2 — Primary retrieval
        raw_docs = self._safe_search(collection, improved_query, limit=top_k * 2)
        trace.raw_doc_count = len(raw_docs)
        trace.steps.append(f"primary_retrieval: {len(raw_docs)} docs from '{collection}'")

        # 3 — Episodic memory (past successes)
        episodic_docs: List[Any] = []
        if include_episodes:
            episodic_docs = self._safe_search("episodes", improved_query, limit=3)
            trace.episodic_hits = len(episodic_docs)
            trace.steps.append(f"episodic_lookup: {len(episodic_docs)} hits")

        # 4 — Merge & score
        merged = list(raw_docs) + list(episodic_docs)
        scored = self.context_selector.score_documents(merged, top_k=top_k)
        trace.scored_doc_count = len(scored)
        trace.steps.append(f"context_selection: kept {len(scored)}/{len(merged)}")

        # 5 — Confidence gate
        avg_score = self._avg_retrieval_score(scored)
        trace.confidence = avg_score
        if avg_score < self.CONFIDENCE_THRESHOLD and len(scored) > 0:
            trace.fallback_used = True
            trace.steps.append("fallback: low confidence — expanding search")
            fallback_docs = self._safe_search(collection, query, limit=top_k)
            scored = self.context_selector.score_documents(
                list(scored) + list(fallback_docs), top_k=top_k
            )
            trace.scored_doc_count = len(scored)

        # 6 — Build context
        context = self.build_context(scored)
        trace.latency_ms = (time.perf_counter() - t0) * 1000
        trace.steps.append(f"done: {trace.latency_ms:.1f}ms")

        logger.info(
            "AgenticRAG query=%r docs=%d confidence=%.2f latency=%.1fms fallback=%s",
            query,
            len(scored),
            avg_score,
            trace.latency_ms,
            trace.fallback_used,
        )

        return AgenticResult(context=context, docs=scored, trace=trace)

    def build_context(self, docs: Iterable[Any], max_chars: int = 4000) -> str:
        """Compress selected docs into a single context string."""
        return self.query_optimizer.compress_context(docs, max_chars=max_chars)

    def feedback(self, docs: Iterable[Any], reward: float) -> None:
        """Forward reward signal to the context selector for online learning."""
        self.context_selector.update_weights(docs, reward)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _safe_search(self, collection: str, query: str, limit: int = 5) -> List[Any]:
        try:
            return self.memory.search(collection, query, limit=limit)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Search failed on '%s': %s", collection, exc)
            return []

    @staticmethod
    def _avg_retrieval_score(docs: Iterable[Any]) -> float:
        scores = [float(getattr(d, "score", 0.0)) for d in docs]
        return sum(scores) / len(scores) if scores else 0.0
