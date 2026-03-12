from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from sentence_transformers import CrossEncoder

from app.config import MODELS


@dataclass(frozen=True)
class RerankItem:
    id: str
    text: str
    meta: dict[str, object]


@dataclass(frozen=True)
class RerankResult:
    id: str
    score: float
    meta: dict[str, object]


_cross_encoder: CrossEncoder | None = None


def _get_cross_encoder() -> CrossEncoder:
    global _cross_encoder
    if _cross_encoder is None:
        # CURSOR: for hackathon, lazy-load; swap to fine-tuned checkpoints in self_improve.
        _cross_encoder = CrossEncoder(MODELS.cross_encoder_model)
    return _cross_encoder


def rerank(query: str, items: Sequence[RerankItem], top_k: int) -> list[RerankResult]:
    if not items:
        return []
    ce = _get_cross_encoder()
    pairs: list[tuple[str, str]] = [(query, item.text) for item in items]
    scores: List[float] = ce.predict(pairs).tolist()  # type: ignore[assignment]
    scored = [
        RerankResult(id=item.id, score=float(score), meta=item.meta)
        for item, score in zip(items, scores, strict=True)
    ]
    scored.sort(key=lambda r: r.score, reverse=True)
    return scored[: min(top_k, len(scored))]


__all__ = ["RerankItem", "RerankResult", "rerank"]

from sentence_transformers import CrossEncoder
from typing import List, Tuple
from app.config import CROSS_ENCODER_MODEL
import logging

logger = logging.getLogger(__name__)
_reranker = CrossEncoder(CROSS_ENCODER_MODEL)


def rerank(query: str, candidates: List[str]) -> List[Tuple[int, float]]:
    """
    candidates: list of passage strings
    returns: list of (orig_index, score) sorted descending
    """
    if not candidates:
        return []
    pairs = [(query, c) for c in candidates]
    scores = _reranker.predict(pairs, batch_size=8)
    indexed = list(enumerate(scores))
    indexed.sort(key=lambda x: x[1], reverse=True)
    return indexed

