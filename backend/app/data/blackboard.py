"""
Blackboard pattern: central task board for multi-agent coordination.

Shopper Agent writes goals; Inventory (and optionally Logistics, Pricing) poll
goals with payload filters (status=open, agent_role) and update status/candidate_skus.
Qdrant stores goal vectors + payload (goal_id, user_id, status, assigned_to, timestamps).
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Sequence

from qdrant_client.http import models as rest

from app.config import COLLECTIONS
from app.embeddings import embed_single
from app.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)

COLL_GOALS: str = COLLECTIONS.goals


def _embed_text(text: str) -> list[float]:
    return embed_single(text).vectors[0].tolist()


def write_goal(
    goal_text: str,
    user_id: str = "anonymous",
    goal_id: str | None = None,
    region: str | None = None,
    budget_eur: float | None = None,
    status: str = "open",
    agent_role: str = "inventory",
) -> str:
    """
    Write a goal to the blackboard (goals collection).
    Returns goal_id.
    """
    client = get_qdrant_client()
    gid = goal_id or f"goal-{uuid.uuid4().hex[:12]}"
    vec = _embed_text(goal_text)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload: dict[str, Any] = {
        "goal_id": gid,
        "user_id": user_id,
        "status": status,
        "goal_text": goal_text[:2000],
        "created_at": now,
        "updated_at": now,
        "agent_role": agent_role,
    }
    if region is not None:
        payload["region"] = region
    if budget_eur is not None:
        payload["budget_eur"] = budget_eur
    point_id = hash(gid) % (2**63)
    client.upsert(
        collection_name=COLL_GOALS,
        points=[rest.PointStruct(id=point_id, vector=vec, payload=payload)],
    )
    logger.info("Blackboard: wrote goal %s status=%s", gid, status)
    return gid


def poll_goals_for_agent(
    agent_role: str,
    status: str = "open",
    limit: int = 10,
    user_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Poll goals relevant to an agent (e.g. status=open, agent_role in ["inventory","pricing"]).
    Returns list of {id, payload} (no vector).
    """
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    client = get_qdrant_client()
    must = [
        FieldCondition(key="status", match=MatchValue(value=status)),
    ]
    if agent_role:
        # Goals that this agent can pick (assigned_to empty or this role)
        must.append(
            FieldCondition(
                key="agent_role",
                match=MatchValue(value=agent_role),
            )
        )
    if user_id is not None:
        must.append(FieldCondition(key="user_id", match=MatchValue(value=user_id)))
    flt = Filter(must=must)
    points, _ = client.scroll(
        collection_name=COLL_GOALS,
        scroll_filter=flt,
        limit=limit,
        with_payload=True,
        with_vectors=False,
    )
    return [{"id": p.id, "payload": p.payload or {}} for p in points]


def update_goal_status(
    goal_id: str,
    status: str,
    payload_update: dict[str, Any] | None = None,
) -> bool:
    """
    Update a goal's status and optionally other payload fields (e.g. candidate_skus, assigned_to).
    Finds point by goal_id (scroll with filter), then upserts with updated payload.
    Returns True if updated, False if goal not found.
    """
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    client = get_qdrant_client()
    flt = Filter(must=[FieldCondition(key="goal_id", match=MatchValue(value=goal_id))])
    points, _ = client.scroll(
        collection_name=COLL_GOALS,
        scroll_filter=flt,
        limit=1,
        with_payload=True,
        with_vectors=True,
    )
    if not points:
        logger.warning("Blackboard: goal %s not found for update", goal_id)
        return False
    point = points[0]
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload = dict(point.payload or {})
    payload["status"] = status
    payload["updated_at"] = now
    if payload_update:
        payload.update(payload_update)
    client.upsert(
        collection_name=COLL_GOALS,
        points=[
            rest.PointStruct(
                id=point.id,
                vector=point.vector or [],
                payload=payload,
            )
        ],
    )
    logger.info("Blackboard: updated goal %s status=%s", goal_id, status)
    return True


def search_similar_goals(goal_text: str, top_k: int = 5, status: str | None = None) -> list[dict[str, Any]]:
    """
    Similarity search over goals (e.g. to reuse a previously solved goal pattern).
    Optionally filter by status (e.g. "closed").
    """
    client = get_qdrant_client()
    vec = _embed_text(goal_text)
    flt = None
    if status is not None:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        flt = Filter(must=[FieldCondition(key="status", match=MatchValue(value=status))])
    hits = client.search(
        collection_name=COLL_GOALS,
        query_vector=vec,
        limit=top_k,
        query_filter=flt,
        with_payload=True,
    )
    return [{"id": h.id, "score": h.score, "payload": h.payload or {}} for h in hits]


__all__ = ["write_goal", "poll_goals_for_agent", "update_goal_status", "search_similar_goals"]
