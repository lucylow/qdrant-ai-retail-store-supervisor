"""TTL cache with fingerprint key (Redis-ready interface)."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def fingerprint_key(*parts: str | int | float | bool) -> str:
    """Stable cache key from parts (e.g. query + tenant_id)."""
    content = json.dumps(list(parts), sort_keys=True, default=str)
    return hashlib.sha256(content.encode()).hexdigest()


class MemoryTTLCache:
    """In-memory TTL cache (production: swap backend to Redis)."""

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 10_000) -> None:
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._store: dict[str, tuple[Any, float]] = {}
        self._timestamps: dict[str, float] = {}

    def get(self, key: str) -> Any | None:
        """Return value if present and not expired."""
        if key not in self._store:
            return None
        val, expires = self._store[key]
        import time
        if time.monotonic() > expires:
            del self._store[key]
            del self._timestamps[key]
            return None
        return val

    def set(self, key: str, value: Any) -> None:
        """Set value with TTL."""
        import time
        expires = time.monotonic() + self._ttl
        if len(self._store) >= self._max_size and key not in self._store:
            oldest = min(self._timestamps, key=self._timestamps.get)
            del self._store[oldest]
            del self._timestamps[oldest]
        self._store[key] = (value, expires)
        self._timestamps[key] = time.monotonic()

    def get_or_set(self, key: str, factory: Callable[[], T]) -> T:
        """Get from cache or compute and set."""
        cached = self.get(key)
        if cached is not None:
            return cached  # type: ignore[return-value]
        val = factory()
        self.set(key, val)
        return val
