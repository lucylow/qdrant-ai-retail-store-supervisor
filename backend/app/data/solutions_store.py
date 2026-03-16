"""
Solutions collection: candidate plans per goal (blackboard + episodic link).

Inventory Agent writes candidate bundles to solutions; Shopper reads combined
solution (bundles + shipping ETA etc.) from the same goal_id.
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

COLL_SOLUTIONS: str = COLLECTIONS.solutions


def _embed_text(text: str) -> list[float]:
    return embed_single(text).vectors[0].tolist()


def upsert_solution(
    goal_id: str,
    bundle_summary: str,
    score_summary: str = "",
    bundles: list[dict[str, Any]] | None = None,
    status: str = "candidate",
    user_id: str = "anonymous",
    region: str | None = None,
) -> str:
    """
    Upsert a solution (candidate plan) for a goal. Vector = embed(bundle_summary).
    Returns solution_id.
    """
    client = get_qdrant_client()
    solution_id = f"sol-{uuid.uuid4().hex[:12]}"
    text = f"{bundle_summary} | {score_summary}" if score_summary else bundle_summary
    vec = _embed_text(text[:2000])
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload: dict[str, Any] = {
        "solution_id": solution_id,
        "goal_id": goal_id,
        "user_id": user_id,
        "status": status,
        "bundle_summary": bundle_summary[:1000],
        "score_summary": score_summary[:500],
        "created_at": now,
    }
    if bundles is not None:
        payload["bundles"] = bundles
    if region is not None:
        payload["region"] = region
    point_id = hash(solution_id) % (2**63)
    client.upsert(
        collection_name=COLL_SOLUTIONS,
        points=[rest.PointStruct(id=point_id, vector=vec, payload=payload)],
    )
    logger.info("Solutions: upserted %s for goal %s", solution_id, goal_id)
    return solution_id


def get_solutions_for_goal(
    goal_id: str,
    status: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Retrieve solutions for a goal (payload filter by goal_id, optional status).
    """
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    client = get_qdrant_client()
    must = [FieldCondition(key="goal_id", match=MatchValue(value=goal_id))]
    if status is not None:
        must.append(FieldCondition(key="status", match=MatchValue(value=status)))
    flt = Filter(must=must)
    points, _ = client.scroll(
        collection_name=COLL_SOLUTIONS,
        scroll_filter=flt,
        limit=limit,
        with_payload=True,
        with_vectors=False,
    )
    return [{"id": p.id, "payload": p.payload or {}} for p in points]
