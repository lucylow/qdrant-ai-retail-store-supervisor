"""
Async search and scroll pagination for retrieval at scale.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, AsyncIterator, List, Optional

from app.data.async_qdrant import AsyncQdrant

logger = logging.getLogger(__name__)


class StreamingRetrieval:
    """Async search and scroll-based pagination over Qdrant collections."""

    def __init__(self, async_qdrant: Optional[AsyncQdrant] = None) -> None:
        self.qdrant = async_qdrant or AsyncQdrant()

    async def search(
        self,
        collection: str,
        query_vector: List[float],
        limit: int = 20,
        score_threshold: Optional[float] = None,
    ) -> List[Any]:
        return await self.qdrant.search(
            collection=collection,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )

    async def scroll_all(
        self,
        collection: str,
        batch_size: int = 100,
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> AsyncIterator[List[Any]]:
        """Async iterator over all points in collection via scroll."""
        offset = None
        while True:
            records, next_offset = await self.qdrant.scroll(
                collection=collection,
                limit=batch_size,
                offset=offset,
                with_payload=with_payload,
                with_vectors=with_vectors,
            )
            if not records:
                break
            yield records
            if next_offset is None:
                break
            offset = next_offset
