"""
Short-term (working) memory: per-session buffer in Redis.

Used by Shopper for dialog state and by Inventory for immediate goal-solving context.
Retention: 1 hour TTL. Eviction: sliding window, keep last 10 turns (~4k tokens).
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, List, Sequence

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SESSION_TTL_S = int(os.getenv("SESSION_TTL_S", "3600"))  # 1 hour
MAX_TURNS = int(os.getenv("SHORT_TERM_MAX_TURNS", "10"))


def _get_redis():
    import redis
    return redis.from_url(REDIS_URL, decode_responses=True)


def session_key(user_id: str, session_id: str) -> str:
    return f"session:{user_id}:{session_id}"


def push_turn(session_key_str: str, turn: dict[str, Any]) -> None:
    """
    Append a turn to the session buffer. Keep only last MAX_TURNS; set TTL.
    turn = {"role": "user" | "agent", "text": "...", "ts": "ISO8601 or float"}
    """
    try:
        r = _get_redis()
        raw = r.get(session_key_str) or "[]"
        buf = json.loads(raw)
        buf.append(turn)
        buf = buf[-MAX_TURNS:]
        r.set(session_key_str, json.dumps(buf), ex=SESSION_TTL_S)
    except Exception as e:  # noqa: BLE001
        logger.warning("Short-term memory push_turn failed: %s", e)


def read_session(session_key_str: str) -> List[dict[str, Any]]:
    """Return the list of turns for this session (last N)."""
    try:
        r = _get_redis()
        raw = r.get(session_key_str) or "[]"
        return json.loads(raw)
    except Exception as e:  # noqa: BLE001
        logger.warning("Short-term memory read_session failed: %s", e)
        return []


def clear_session(session_key_str: str) -> None:
    """Delete the session buffer."""
    try:
        r = _get_redis()
        r.delete(session_key_str)
    except Exception as e:  # noqa: BLE001
        logger.warning("Short-term memory clear_session failed: %s", e)


def format_short_term_context(turns: Sequence[dict], last_n: int = 3) -> str:
    """Format last N turns as bullet lines for prompt injection."""
    if not turns:
        return "(no prior turns)"
    lines = []
    for t in turns[-last_n:]:
        role = t.get("role", "?")
        text = (t.get("text") or "").strip()
        if text:
            lines.append(f"- [{role}] {text[:200]}")
    return "\n".join(lines) if lines else "(no prior turns)"
