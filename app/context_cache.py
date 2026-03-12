import time
import threading
from typing import Dict, Any

from app.config import CONTEXT

_lock = threading.Lock()
_cache: Dict[str, Dict[str, Any]] = {}


def set_cache(key: str, value: Dict[str, Any], ttl: int | None = None) -> None:
    ttl = ttl or CONTEXT.get("context_fingerprint_ttl", 3600)
    with _lock:
        _cache[key] = {"value": value, "expires": time.time() + ttl}


def get_cache(key: str) -> Dict[str, Any] | None:
    with _lock:
        item = _cache.get(key)
        if not item:
            return None
        if item["expires"] < time.time():
            del _cache[key]
            return None
        return item["value"]


def invalidate(key: str) -> None:
    with _lock:
        if key in _cache:
            del _cache[key]

