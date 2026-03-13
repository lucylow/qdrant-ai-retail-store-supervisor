"""
Async Redis client with connection pooling for 85% cache hit target.
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import timedelta
from typing import Any, Callable, Optional, Union

logger = logging.getLogger(__name__)

try:
    from redis.asyncio import Redis
    from redis.asyncio import ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    Redis = None  # type: ignore
    ConnectionPool = None  # type: ignore
    REDIS_AVAILABLE = False


class PerformanceCache:
    """Async Redis cache with fingerprint keys and get_or_set pattern."""

    def __init__(
        self,
        redis_url: str = "redis://localhost",
        default_ttl: Optional[timedelta] = None,
        max_connections: int = 20,
    ) -> None:
        self.redis_url = redis_url
        self.default_ttl = default_ttl or timedelta(minutes=30)
        self.max_connections = max_connections
        self._pool: Any = None
        self._redis: Any = None

    async def _client(self) -> Any:
        if self._redis is not None:
            return self._redis
        if not REDIS_AVAILABLE:
            return None
        self._pool = ConnectionPool.from_url(
            self.redis_url,
            max_connections=self.max_connections,
            decode_responses=True,
        )
        self._redis = Redis(connection_pool=self._pool)
        return self._redis

    def fingerprint(self, *args: Any, **kwargs: Any) -> str:
        """Deterministic cache key from inputs."""
        from app.cache.fingerprint import fingerprint as fp
        return fp(*args, **kwargs)

    def _serialize(self, value: Any) -> str:
        return json.dumps(value, default=str)

    def _deserialize(self, raw: str) -> Any:
        return json.loads(raw)

    async def get(self, key: str) -> Any:
        client = await self._client()
        if client is None:
            return None
        try:
            cached = await client.get(key)
            if cached is None:
                return None
            return self._deserialize(cached)
        except Exception as e:
            logger.debug("Cache get failed: %s", e)
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[timedelta, int]] = None,
    ) -> None:
        client = await self._client()
        if client is None:
            return
        try:
            ex = int(ttl.total_seconds()) if isinstance(ttl, timedelta) else (int(ttl) if ttl else int(self.default_ttl.total_seconds()))
            await client.setex(key, ex, self._serialize(value))
        except Exception as e:
            logger.debug("Cache set failed: %s", e)

    async def get_or_set(
        self,
        key: str,
        compute: Callable[[], Any],
        ttl: Optional[timedelta] = None,
    ) -> Any:
        """Cache with automatic computation + serialization. compute can be async."""
        cached = await self.get(key)
        if cached is not None:
            return cached
        if asyncio.iscoroutinefunction(compute):
            result = await compute()
        else:
            result = compute()
        await self.set(key, result, ttl=ttl or self.default_ttl)
        return result

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()
            self._redis = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
