#!/usr/bin/env python3
"""
Prewarm cache with top queries for 85% hit rate target.
Usage: python scripts/cache_prewarm.py --top-queries 1000
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure app is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.cache.redis_client import PerformanceCache
from app.cache.prewarm import PrewarmCache


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top-queries", type=int, default=1000)
    ap.add_argument("--redis-url", default="redis://localhost")
    args = ap.parse_args()

    cache = PerformanceCache(redis_url=args.redis_url)

    async def compute(query: str) -> dict:
        return {"query": query, "cached": True}

    prewarm = PrewarmCache(cache=cache, compute_fn=compute, top_n=args.top_queries)
    queries = [f"retail query {i} Coop Migros" for i in range(args.top_queries)]
    n = await prewarm.run(queries=queries)
    print(f"Prewarmed {n} keys.")
    await cache.close()


if __name__ == "__main__":
    asyncio.run(main())
