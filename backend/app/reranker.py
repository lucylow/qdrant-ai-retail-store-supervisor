from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple, Dict

from sentence_transformers import CrossEncoder

from app.config import MODELS


@dataclass(frozen=True)
class RerankItem:
    id: str
    text: str
    meta: Dict[str, object]


@dataclass(frozen=True)
class RerankResult:
    id: str
    score: float
    meta: Dict[str, object]


_cross_encoder: Optional[CrossEncoder] = None


def _get_cross_encoder() -> CrossEncoder:
    global _cross_encoder
    if _cross_encoder is None:
        # CURSOR: for hackathon, lazy-load; swap to fine-tuned checkpoints in self_improve.
        _cross_encoder = CrossEncoder(MODELS.cross_encoder_model)
    return _cross_encoder


def rerank(query: str, items: Sequence[RerankItem], top_k: int) -> List[RerankResult]:
    if not items:
        return []
    ce = _get_cross_encoder()
    pairs: List[Tuple[str, str]] = [(query, item.text) for item in items]
    scores: List[float] = ce.predict(pairs).tolist()  # type: ignore[assignment]
    scored = [
        RerankResult(id=item.id, score=float(score), meta=item.meta)
        for item, score in zip(items, scores)
    ]
    scored.sort(key=lambda r: r.score, reverse=True)
    return scored[: min(top_k, len(scored))]


__all__ = ["RerankItem", "RerankResult", "rerank"]

