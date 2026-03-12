from __future__ import annotations

from typing import Sequence

from app.data.episodic_memory import EpisodicMemoryStore


class EpisodicRetriever:
    """
    Thin wrapper around `EpisodicMemoryStore` for success-weighted retrieval.
    """

    def __init__(self, store: EpisodicMemoryStore | None = None) -> None:
        self.store = store or EpisodicMemoryStore()


__all__: Sequence[str] = ["EpisodicRetriever"]

