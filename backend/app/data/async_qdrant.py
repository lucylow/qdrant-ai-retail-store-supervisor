"""
Async Qdrant client wrapper with batch operations for high throughput.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, List, Optional

from app.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)


class AsyncQdrant:
    """Async wrapper around Qdrant client using run_in_executor for batch operations."""

    def __init__(self) -> None:
        self._client = None
        self._loop = asyncio.get_event_loop()

    def _get_client(self):  # type: ignore
        if self._client is None:
            self._client = get_qdrant_client()
        return self._client

    async def search(
        self,
        collection: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
    ) -> List[Any]:
        def _run() -> Any:
            client = self._get_client()
            return client.search(
                collection_name=collection,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
            )

        return await self._loop.run_in_executor(None, _run)

    async def upsert(
        self,
        collection: str,
        points: List[Any],
    ) -> None:
        def _run() -> None:
            client = self._get_client()
            client.upsert(collection_name=collection, points=points)

        await self._loop.run_in_executor(None, _run)

    async def scroll(
        self,
        collection: str,
        limit: int = 100,
        offset: Optional[Any] = None,
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> tuple[List[Any], Optional[Any]]:
        def _run() -> Any:
            client = self._get_client()
            return client.scroll(
                collection_name=collection,
                limit=limit,
                offset=offset,
                with_payload=with_payload,
                with_vectors=with_vectors,
            )

        result = await self._loop.run_in_executor(None, _run)
        return (result[0], result[1] if len(result) > 1 else None)

    async def get_collections(self) -> List[str]:
        def _run() -> Any:
            return self._get_client().get_collections()

        resp = await self._loop.run_in_executor(None, _run)
        return [c.name for c in (resp.collections or [])]
