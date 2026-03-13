"""
Episodic memory: goal_solution_links collection in Qdrant.

Stores goal → solution → outcome with semantic embedding (goal_text | solution_summary)
for case-based planning and learning. Used by Shopper (past success examples) and
Inventory (episodic precedents).
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Sequence

from app.data.memory_collections import COLL_GOAL_SOLUTION_LINKS
from app.embeddings import embed_single
from app.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)


def _embed_text(text: str) -> list[float]:
    return embed_single(text).vectors[0].tolist()


def upsert_episode(
    goal_id: str,
    solution_id: str,
    user_id: str,
    goal_text: str,
    solution_summary: str,
    outcome: str,
    score: float,
    revenue: float | None = None,
    success: bool | None = None,
) -> str:
    """
    Insert an episodic link. Vector = embed(goal_text + " | " + solution_summary).
    Returns episode_id.
    """
    client = get_qdrant_client()
    combined = f"{goal_text} | {solution_summary}"
    vec = _embed_text(combined)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    episode_id = f"ep-{uuid.uuid4().hex[:12]}"
    payload = {
        "episodeId": episode_id,
        "goalId": goal_id,
        "solutionId": solution_id,
        "userId": user_id,
        "success": success if success is not None else (outcome in ("success", "purchased")),
        "revenue": revenue,
        "summary": combined[:1000],
        "outcome": outcome,
        "score": score,
        "created_at": now,
    }
    from qdrant_client.http import models as rest
    point_id = hash(episode_id) % (2**63)
    client.upsert(
        collection_name=COLL_GOAL_SOLUTION_LINKS,
        points=[rest.PointStruct(id=point_id, vector=vec, payload=payload)],
    )
    logger.info("Upserted goal_solution_link %s (goal=%s, outcome=%s)", episode_id, goal_id, outcome)
    return episode_id


def search_similar(
    goal_text: str,
    top_k: int = 5,
    *,
    outcome_filter: str | None = None,
    user_id: str | None = None,
    min_score: float | None = None,
) -> list[dict[str, Any]]:
    """
    Semantic search for episodes similar to goal_text.
    Optionally filter by outcome (e.g. "purchased", "success"), user_id, min_score.
    """
    client = get_qdrant_client()
    vec = _embed_text(goal_text)
    from qdrant_client.http import models as rest
    from qdrant_client.models import Filter, FieldCondition, MatchValue, Range
    must = []
    if outcome_filter:
        must.append(FieldCondition(key="outcome", match=MatchValue(value=outcome_filter)))
    if user_id:
        must.append(FieldCondition(key="userId", match=MatchValue(value=user_id)))
    if min_score is not None:
        must.append(FieldCondition(key="score", range=Range(gte=min_score)))
    flt = Filter(must=must) if must else None
    hits = client.search(
        collection_name=COLL_GOAL_SOLUTION_LINKS,
        query_vector=vec,
        limit=top_k,
        query_filter=flt,
        with_payload=True,
    )
    return [{"id": h.id, "score": h.score, "payload": h.payload or {}} for h in hits]


def format_episodic_summaries(hits: list[dict], max_lines: int = 3) -> str:
    """Format episodic hits as brief lines for prompt injection."""
    lines = []
    for h in hits[:max_lines]:
        p = h.get("payload") or {}
        summary = p.get("summary", "")
        outcome = p.get("outcome", "?")
        score = p.get("score", 0)
        lines.append(f"goal: {summary[:120]}... | outcome: {outcome} | score: {score:.2f}")
    return "\n".join(lines) if lines else "(no prior episodes)"


__all__: Sequence[str] = ["upsert_episode", "search_similar", "format_episodic_summaries"]
