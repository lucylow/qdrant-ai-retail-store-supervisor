"""
SHA256 prompt/context cache keys for deterministic lookups.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


def fingerprint(*args: Any, **kwargs: Any) -> str:
    """Deterministic cache key from args and kwargs (SHA256, first 32 chars)."""
    data: dict = {f"arg{i}": _normalize(arg) for i, arg in enumerate(args)}
    data.update({str(k): _normalize(v) for k, v in sorted(kwargs.items())})
    return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()[:32]


def _normalize(value: Any) -> str:
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True, default=str)
    return str(value)
