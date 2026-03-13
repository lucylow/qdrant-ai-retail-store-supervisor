"""Unit tests for app.utils.caching."""

from __future__ import annotations

from app.utils.caching import MemoryTTLCache, fingerprint_key


def test_fingerprint_key_stable() -> None:
    k1 = fingerprint_key("query", "tenant1")
    k2 = fingerprint_key("query", "tenant1")
    assert k1 == k2


def test_fingerprint_key_different() -> None:
    k1 = fingerprint_key("query1")
    k2 = fingerprint_key("query2")
    assert k1 != k2


def test_memory_cache_get_set() -> None:
    cache = MemoryTTLCache(ttl_seconds=60, max_size=100)
    cache.set("k1", "v1")
    assert cache.get("k1") == "v1"


def test_memory_cache_get_miss() -> None:
    cache = MemoryTTLCache(ttl_seconds=60)
    assert cache.get("missing") is None


def test_memory_cache_get_or_set() -> None:
    cache = MemoryTTLCache(ttl_seconds=60)
    calls = 0

    def factory() -> int:
        nonlocal calls
        calls += 1
        return 42

    assert cache.get_or_set("k", factory) == 42
    assert cache.get_or_set("k", factory) == 42
    assert calls == 1
