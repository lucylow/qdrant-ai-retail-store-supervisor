from __future__ import annotations

from typing import List, Sequence, Tuple

import torch
from sentence_transformers import CrossEncoder


class ProductionReranker:
    """
    Simple cross‑encoder wrapper with batched inference and a minimal
    fine‑tuning hook used by the training script.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        device: str | None = None,
        batch_size: int = 32,
    ) -> None:
        device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CrossEncoder(model_name, device=device)
        self.batch_size = batch_size

    def rerank(
        self,
        query: str,
        passages: Sequence[str],
        top_k: int = 10,
        max_passages: int = 100,
    ) -> List[Tuple[int, float]]:
        """
        Returns a list of (original_index, score) sorted descending by score.
        """
        if not passages:
            return []
        truncated = list(passages[:max_passages])
        pairs = [[query, passage] for passage in truncated]
        scores = self.model.predict(
            pairs,
            batch_size=self.batch_size,
            show_progress_bar=False,
        )
        indexed = list(enumerate(scores))
        ranked = sorted(indexed, key=lambda x: float(x[1]), reverse=True)[:top_k]
        return [(idx, float(score)) for idx, score in ranked]


__all__ = ["ProductionReranker"]

