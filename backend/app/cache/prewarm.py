"""
Prewarm cache with popular queries for 85% hit rate target.
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


class PrewarmCache:
    """Load top queries from file or list and populate cache via compute_fn."""

    def __init__(
        self,
        cache: Any,
        compute_fn: Any,
        query_source: Optional[Path] = None,
        top_n: int = 1000,
    ) -> None:
        self.cache = cache
        self.compute_fn = compute_fn
        self.query_source = query_source
        self.top_n = top_n

    def _load_queries(self) -> List[str]:
        if self.query_source and self.query_source.exists():
            lines = self.query_source.read_text(encoding="utf-8").strip().splitlines()
            return [l.strip() for l in lines if l.strip()][: self.top_n]
        return []

    async def run(self, queries: Optional[List[str]] = None) -> int:
        """Prewarm cache for given queries or loaded list. Returns count warmed."""
        qs = queries or self._load_queries()
        if not qs:
            logger.warning("No queries to prewarm")
            return 0
        count = 0
        for q in qs[: self.top_n]:
            try:
                key = self.cache.fingerprint("orchestrate", query=q)
                await self.cache.get_or_set(key, lambda q=q: self._compute(q))
                count += 1
            except Exception as e:
                logger.debug("Prewarm failed for %s: %s", q[:50], e)
        logger.info("Prewarmed %s keys", count)
        return count

    async def _compute(self, query: str) -> Any:
        if asyncio.iscoroutinefunction(self.compute_fn):
            return await self.compute_fn(query)
        return self.compute_fn(query)
