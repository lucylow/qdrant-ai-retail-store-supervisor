"""
AsyncIO embedding queue for non-blocking batch submission.
"""
from __future__ import annotations

import asyncio
import logging
from typing import List, Optional

from app.embeddings.batch_embedder import BatchEmbedder

logger = logging.getLogger(__name__)


class AsyncEmbedder:
    """Queue-based async embedder: submit texts, get futures, batch when ready."""

    def __init__(
        self,
        embedder: Optional[BatchEmbedder] = None,
        max_batch_size: int = 128,
        max_wait_s: float = 0.05,
    ) -> None:
        self.embedder = embedder or BatchEmbedder()
        self.max_batch_size = max_batch_size
        self.max_wait_s = max_wait_s
        self._queue: List[str] = []
        self._futures: List[asyncio.Future] = []
        self._lock = asyncio.Lock()
        self._worker_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start background worker that flushes batches."""
        if self._worker_task is not None:
            return
        self._worker_task = asyncio.create_task(self._worker())

    async def _worker(self) -> None:
        while True:
            await asyncio.sleep(self.max_wait_s)
            async with self._lock:
                if len(self._queue) >= self.max_batch_size or (
                    self._queue and self._futures
                ):
                    batch = self._queue[: self.max_batch_size]
                    futures = self._futures[: len(batch)]
                    self._queue = self._queue[len(batch) :]
                    self._futures = self._futures[len(batch) :]
                else:
                    batch = []
                    futures = []
            if batch and futures:
                try:
                    emb = await self.embedder.embed_batch(batch)
                    for i, fut in enumerate(futures):
                        if not fut.done() and i < len(emb):
                            fut.set_result(emb[i])
                        elif not fut.done():
                            fut.set_exception(IndexError("embedding index"))
                except Exception as e:
                    for fut in futures:
                        if not fut.done():
                            fut.set_exception(e)

    async def embed(self, text: str) -> List[float]:
        """Submit one text; returns embedding when batch is processed."""
        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        async with self._lock:
            self._queue.append(text)
            self._futures.append(fut)
        result = await asyncio.wait_for(fut, timeout=30.0)
        return result.tolist() if hasattr(result, "tolist") else list(result)

    async def embed_many(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts in batches."""
        emb = await self.embedder.embed_batch(texts)
        return [emb[i].tolist() for i in range(len(emb))]
