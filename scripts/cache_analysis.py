#!/usr/bin/env python3
"""
Cache hit/miss analysis and optimization suggestions.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from redis.asyncio import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


async def analyze(redis_url: str = "redis://localhost", key_prefix: str = "perf:") -> dict:
    if not REDIS_AVAILABLE:
        return {"error": "redis not available"}
    client = Redis.from_url(redis_url, decode_responses=True)
    try:
        info = await client.info("stats")
        keys = await client.keys(f"{key_prefix}*")
        return {
            "total_keys": len(keys),
            "redis_used_memory": info.get("used_memory_human", "N/A"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
        }
    finally:
        await client.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--redis-url", default="redis://localhost")
    ap.add_argument("--prefix", default="perf:")
    args = ap.parse_args()
    result = asyncio.run(analyze(args.redis_url, args.prefix))
    hits = result.get("keyspace_hits", 0) or 0
    misses = result.get("keyspace_misses", 0) or 0
    total = hits + misses
    hit_rate = hits / total if total else 0.0
    print(f"Keys: {result.get('total_keys', 0)} | Hit rate: {hit_rate:.1%} | Memory: {result.get('redis_used_memory', 'N/A')}")


if __name__ == "__main__":
    main()
