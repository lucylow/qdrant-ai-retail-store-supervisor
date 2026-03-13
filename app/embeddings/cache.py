"""
Redis vector cache with fingerprint TTL for 85% cache hit target.
"""
from __future__ import annotations

import json
import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

try:
    from redis.asyncio import Redis
    REDIS_AVAILABLE = True
except ImportError:
    Redis = None  # type: ignore
    REDIS_AVAILABLE = False


class EmbeddingCache:
    """Redis-backed cache for embeddings and vector results; key = fingerprint, TTL in seconds."""

    def __init__(
        self,
        redis_url: str = "redis://localhost",
        default_ttl_s: int = 1800,
        key_prefix: str = "emb:",
    ) -> None:
        self.redis_url = redis_url
        self.default_ttl_s = default_ttl_s
        self.key_prefix = key_prefix
        self._redis: Optional[Any] = None

    async def _client(self) -> Any:
        if self._redis is not None:
            return self._redis
        if not REDIS_AVAILABLE:
            return None
        self._redis = Redis.from_url(self.redis_url, decode_responses=False)
        return self._redis

    def _key(self, fingerprint: str) -> str:
        return f"{self.key_prefix}{fingerprint}"

    async def get(self, fingerprint: str) -> Optional[List[float]]:
        """Return cached vector or None."""
        client = await self._client()
        if client is None:
            return None
        try:
            raw = await client.get(self._key(fingerprint))
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as e:
            logger.debug("Embedding cache get failed: %s", e)
            return None

    async def set(
        self,
        fingerprint: str,
        vector: List[float],
        ttl_s: Optional[int] = None,
    ) -> None:
        client = await self._client()
        if client is None:
            return
        try:
            key = self._key(fingerprint)
            await client.set(
                key,
                json.dumps(vector),
                ex=ttl_s or self.default_ttl_s,
            )
        except Exception as e:
            logger.debug("Embedding cache set failed: %s", e)

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()
            self._redis = None
