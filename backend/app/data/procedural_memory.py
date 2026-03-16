"""
Procedural memory: discovered high-value routing/bundle patterns and triggers.

Stored in Qdrant procedural_memory collection. Updated from episode outcomes:
- If similar pattern exists (score > 0.80), update successRate (weighted incremental).
- If no close pattern and episode success with score > threshold, create new pattern.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Sequence

from app.data.memory_collections import COLL_PROCEDURAL_MEMORY
from app.embeddings import embed_single
from app.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD_UPDATE = 0.80
MIN_SCORE_NEW_PATTERN = 0.85
N_MIN_FOR_PRUNING = 3
SUCCESS_RATE_THRESHOLD = 0.5


def _embed_text(text: str) -> list[float]:
    return embed_single(text).vectors[0].tolist()


def search(
    goal_vector: list[float],
    top_k: int = 3,
    min_success_rate: float | None = None,
) -> list[dict[str, Any]]:
    """
    Vector search procedural_memory for patterns similar to the goal.
    Optionally filter by successRate >= min_success_rate.
    """
    client = get_qdrant_client()
    from qdrant_client.http import models as rest
    from qdrant_client.models import Filter, FieldCondition, Range
    flt = None
    if min_success_rate is not None:
        flt = Filter(must=[FieldCondition(key="successRate", range=Range(gte=min_success_rate))])
    hits = client.search(
        collection_name=COLL_PROCEDURAL_MEMORY,
        query_vector=goal_vector,
        limit=top_k,
        query_filter=flt,
        with_payload=True,
    )
    return [{"id": h.id, "score": h.score, "payload": h.payload or {}} for h in hits]


def upsert_from_episode(
    episode_payload: dict[str, Any],
) -> None:
    """
    After an episode outcome: update existing procedural pattern if similarity > 0.80,
    else create a new pattern if episode success and score > MIN_SCORE_NEW_PATTERN.

    episode_payload should contain:
      - summary (or trigger_summary)
      - solution_skus (list of SKUs in bundle)
      - success (bool)
      - score (float)
      - trigger (optional dict: category, location, deadline_days, etc.)
    """
    client = get_qdrant_client()
    summary = episode_payload.get("summary") or episode_payload.get("trigger_summary", "")
    solution_skus = episode_payload.get("solution_skus") or []
    success = bool(episode_payload.get("success", False))
    score = float(episode_payload.get("score", 0.0))
    trigger = episode_payload.get("trigger") or {}

    trigger_summary = f"{summary} | bundles:{','.join(solution_skus[:10])}"
    vec = _embed_text(trigger_summary)

    hits = client.search(
        collection_name=COLL_PROCEDURAL_MEMORY,
        query_vector=vec,
        limit=5,
        with_payload=True,
    )

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    if hits and hits[0].score and hits[0].score >= SIMILARITY_THRESHOLD_UPDATE:
        # Update existing pattern: weighted incremental success rate
        p = dict(hits[0].payload or {})
        n = p.get("n", 1)
        old_sr = p.get("successRate", 0.0)
        new_sr = (old_sr * n + (1.0 if success else 0.0)) / (n + 1)
        p["successRate"] = new_sr
        p["n"] = n + 1
        p["updated_at"] = now
        # Optionally append to optimalBundles if this bundle repeats
        bundles = list(p.get("optimalBundles") or [])
        sku_key = ",".join(sorted(solution_skus[:5]))
        if sku_key and sku_key not in bundles:
            bundles.append(sku_key)
            p["optimalBundles"] = bundles[-10:]
        from qdrant_client.http import models as rest
        client.upsert(
            collection_name=COLL_PROCEDURAL_MEMORY,
            points=[rest.PointStruct(id=hits[0].id, vector=vec, payload=p)],
        )
        logger.info("Updated procedural pattern id=%s successRate=%.2f", hits[0].id, new_sr)
    elif success and score >= MIN_SCORE_NEW_PATTERN:
        # Create new pattern
        pattern_id = f"pat-{int(time.time() * 1000)}"
        payload = {
            "patternId": pattern_id,
            "trigger": trigger,
            "successRate": 1.0,
            "n": 1,
            "recommendedAgents": ["inventory"],
            "optimalBundles": [",".join(sorted(solution_skus[:5]))] if solution_skus else [],
            "notes": "",
            "created_at": now,
        }
        from qdrant_client.http import models as rest
        point_id = hash(pattern_id) % (2**63)
        client.upsert(
            collection_name=COLL_PROCEDURAL_MEMORY,
            points=[rest.PointStruct(id=point_id, vector=vec, payload=payload)],
        )
        logger.info("Created procedural pattern %s", pattern_id)


def format_procedural_pattern(hits: list[dict]) -> str:
    """Format top procedural pattern for prompt injection."""
    if not hits:
        return "(no matching procedural pattern)"
    p = (hits[0].get("payload") or {}) if hits else {}
    parts = [
        f"patternId: {p.get('patternId', '?')}",
        f"successRate: {p.get('successRate', 0):.2f}",
        f"optimalBundles: {p.get('optimalBundles', [])}",
        f"notes: {p.get('notes', '')}",
    ]
    return "\n".join(parts)


__all__: Sequence[str] = ["search", "upsert_from_episode", "format_procedural_pattern"]
