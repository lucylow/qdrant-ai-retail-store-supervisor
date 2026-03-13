"""
Parallel document processing for bulk ingestion into Qdrant.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, List, Optional

from app.data.async_qdrant import AsyncQdrant

logger = logging.getLogger(__name__)


class BulkIngest:
    """Parallel document processing and batch upsert to Qdrant."""

    def __init__(
        self,
        async_qdrant: Optional[AsyncQdrant] = None,
        embed_fn: Optional[Callable[[List[str]], Any]] = None,
        batch_size: int = 64,
        max_concurrent: int = 4,
    ) -> None:
        self.qdrant = async_qdrant or AsyncQdrant()
        self.embed_fn = embed_fn
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def ingest_documents(
        self,
        collection: str,
        documents: List[dict],
        id_field: str = "id",
        text_field: str = "text",
    ) -> int:
        """Embed and upsert documents in parallel batches. Returns count upserted."""
        if not documents:
            return 0
        if not self.embed_fn:
            logger.warning("No embed_fn; skipping vector ingestion")
            return 0

        total = 0
        for start in range(0, len(documents), self.batch_size):
            batch = documents[start : start + self.batch_size]
            texts = [d.get(text_field, "") for d in batch]
            ids = [d.get(id_field, start + i) for i, d in enumerate(batch)]

            async with self._semaphore:
                vectors = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda t=texts: self.embed_fn(t),
                )
                if hasattr(vectors, "tolist"):
                    vectors = vectors.tolist()
                elif hasattr(vectors, "__iter__") and vectors and not isinstance(vectors[0], (list, tuple)):
                    vectors = [[float(x) for x in v] for v in vectors]
                from qdrant_client.http import models as rest
                points = [
                    rest.PointStruct(
                        id=ids[i],
                        vector=vectors[i] if i < len(vectors) else vectors[0],
                        payload=dict(batch[i]),
                    )
                    for i in range(len(batch))
                ]
                await self.qdrant.upsert(collection, points)
                total += len(batch)
        return total
