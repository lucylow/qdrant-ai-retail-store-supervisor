# app/geospatial/eta_cache.py
import json
import os
from typing import Any, Optional

# Use redis.asyncio (redis >= 4.2); aioredis is deprecated
try:
    from redis.asyncio import Redis
except ImportError:
    Redis = None  # type: ignore[misc, assignment]

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_redis: Optional[Any] = None


async def get_redis() -> Optional[Any]:
    global _redis
    if Redis is None:
        return None
    if _redis is None:
        _redis = Redis.from_url(REDIS_URL)
    return _redis


async def set_eta_cache(
    intent_id: str, store_id: str, eta_seconds: int, ttl: int = 120
) -> None:
    r = await get_redis()
    if r is None:
        return
    key = f"eta:{intent_id}:{store_id}"
    await r.set(key, json.dumps({"eta": eta_seconds}), ex=ttl)


async def get_eta_cache(intent_id: str, store_id: str) -> Optional[dict]:
    r = await get_redis()
    if r is None:
        return None
    key = f"eta:{intent_id}:{store_id}"
    data = await r.get(key)
    if not data:
        return None
    return json.loads(data)
