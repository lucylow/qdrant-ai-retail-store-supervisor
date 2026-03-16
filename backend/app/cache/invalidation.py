"""
LRU and time-based cache eviction for Redis keys.
"""
from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


class InvalidationPolicy(ABC):
    @abstractmethod
    def should_evict(self, key: str, meta: dict) -> bool:
        pass

    @abstractmethod
    def record_access(self, key: str, meta: dict) -> None:
        pass


class LRUEviction(InvalidationPolicy):
    """In-memory LRU tracking; evict keys not seen in max_size."""

    def __init__(self, max_size: int = 10_000) -> None:
        self.max_size = max_size
        self._order: OrderedDict[str, float] = OrderedDict()

    def should_evict(self, key: str, meta: dict) -> bool:
        if key not in self._order:
            return False
        if len(self._order) <= self.max_size:
            return False
        return self._order.move_to_end(key, last=False) or False

    def record_access(self, key: str, meta: dict) -> None:
        self._order[key] = time.monotonic()
        self._order.move_to_end(key)
        while len(self._order) > self.max_size:
            self._order.popitem(last=False)


class TTLEviction(InvalidationPolicy):
    """Time-based: evict if last access older than ttl_s."""

    def __init__(self, ttl_s: float = 1800) -> None:
        self.ttl_s = ttl_s

    def should_evict(self, key: str, meta: dict) -> bool:
        last = meta.get("last_access", 0)
        return (time.monotonic() - last) > self.ttl_s

    def record_access(self, key: str, meta: dict) -> None:
        meta["last_access"] = time.monotonic()
