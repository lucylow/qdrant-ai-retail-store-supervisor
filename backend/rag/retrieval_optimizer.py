from __future__ import annotations

from typing import Iterable, List, Any


class RetrievalOptimizer:
    """
    Query rewriting + scoring utilities to improve RAG retrieval quality.
    """

    def adjust_query(self, query: str) -> str:
        """
        Basic query expansion tailored to retail.

        This matches the requested behavior and can be extended with
        LLM-based rewriting or user-behavior signals.
        """
        expanded = query + " retail product sales promotion"
        return expanded

    def score_results(self, docs: Iterable[Any]) -> List[tuple[float, Any]]:
        """
        Attach a naive relevance score to docs, e.g. using their Qdrant score.
        """
        scored: List[tuple[float, Any]] = []
        for d in docs:
            score = float(getattr(d, "score", 0.0))
            scored.append((score, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

    def compress_context(self, docs: Iterable[Any], max_chars: int = 4000) -> str:
        """
        Very simple context compression: concatenate until budget is hit.
        """
        pieces: List[str] = []
        total = 0
        for d in docs:
            text = ""
            payload = getattr(d, "payload", None)
            if isinstance(payload, dict):
                text = str(payload.get("text", ""))
            else:
                text = str(d)
            if not text:
                continue
            if total + len(text) > max_chars:
                break
            pieces.append(text)
            total += len(text)
        return "\n".join(pieces)

