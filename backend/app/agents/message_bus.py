"""
Simple message bus with durable SQLite backend (fallback to in-memory).
Used to publish agent actions, events, and to provide an audit trail.
"""

import sqlite3
import json
import os
import threading
import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)
DB_PATH = os.getenv("AGENT_BUS_DB", "/tmp/agent_bus.sqlite")

_lock = threading.Lock()
_conn = None


def _get_conn():
    global _conn
    if _conn is None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL,
                agent TEXT,
                event_type TEXT,
                payload TEXT
            )
        """
        )
        _conn.commit()
    return _conn


def publish(agent: str, event_type: str, payload: Dict[str, Any]):
    conn = _get_conn()
    with _lock:
        conn.execute(
            "INSERT INTO events (ts, agent, event_type, payload) VALUES (?, ?, ?, ?)",
            (time.time(), agent, event_type, json.dumps(payload)),
        )
        conn.commit()
    logger.debug("Published event %s by %s", event_type, agent)


def list_events(limit: int = 100) -> List[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.execute(
        "SELECT id, ts, agent, event_type, payload FROM events ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    out: List[Dict[str, Any]] = []
    for row in cur:
        out.append(
            {
                "id": row[0],
                "ts": row[1],
                "agent": row[2],
                "event_type": row[3],
                "payload": json.loads(row[4]),
            }
        )
    return out


def query_by_agent(agent: str, limit: int = 100) -> List[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.execute(
        "SELECT id, ts, event_type, payload FROM events WHERE agent=? ORDER BY id DESC LIMIT ?",
        (agent, limit),
    )
    return [
        {
            "id": r[0],
            "ts": r[1],
            "event_type": r[2],
            "payload": json.loads(r[3]),
        }
        for r in cur
    ]

