"""
GPU-batched embedding with dynamic padding for 1000 QPS production scale.
"""
from __future__ import annotations

import asyncio
import logging
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    SentenceTransformer = None  # type: ignore
    ST_AVAILABLE = False


class BatchEmbedder:
    """GPU-batched sentence-transformers with dynamic padding."""

    def __init__(
        self,
        model_name: str = "all-mpnet-base-v2",
        device: Optional[str] = None,
        max_batch_size: int = 128,
    ) -> None:
        self.model_name = model_name
        self.max_batch_size = max_batch_size
        self._device = device
        self.model = self._load_model()
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=1000)

    def _load_model(self):  # type: ignore
        if not ST_AVAILABLE:
            return None
        if TORCH_AVAILABLE and torch.cuda.is_available() and self._device != "cpu":
            device = "cuda"
        else:
            device = "cpu"
        return SentenceTransformer(
            self.model_name,
            device=device,
        )

    def _split_into_batches(self, texts: List[str], size: int) -> List[List[str]]:
        batches: List[List[str]] = []
        for i in range(0, len(texts), size):
            batches.append(texts[i : i + size])
        return batches

    def embed_batch_sync(self, texts: List[str]) -> np.ndarray:
        """Synchronous GPU-batched embedding."""
        if not self.model:
            return np.zeros((len(texts), 768), dtype=np.float32)
        if len(texts) == 0:
            dim = self.model.get_sentence_embedding_dimension()
            return np.empty((0, dim), dtype=np.float32)
        batches = self._split_into_batches(texts, self.max_batch_size)
        embeddings = []
        for batch_texts in batches:
            emb = self.model.encode(
                batch_texts,
                batch_size=len(batch_texts),
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            embeddings.append(emb)
        return np.vstack(embeddings).astype(np.float32)

    async def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Async: run batch embedding in executor to avoid blocking."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.embed_batch_sync, texts)

    @property
    def dimension(self) -> int:
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        return 768
