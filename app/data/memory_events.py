"""
Wire episode outcomes into goal_solution_links (episodic) and procedural_memory.

Call after each episode (e.g. from supervisor) to keep semantic episodic store
and procedural patterns in sync.
"""

from __future__ import annotations

import logging
from typing import Any, Sequence

from app.data.goal_solution_links import upsert_episode
from app.data.procedural_memory import upsert_from_episode

logger = logging.getLogger(__name__)


def record_episode_to_memory(
    goal_id: str,
    goal_text: str,
    bundle_skus: Sequence[str],
    outcome: str,
    score: float,
    user_id: str = "anonymous",
    solution_id: str | None = None,
    solution_summary: str | None = None,
    revenue: float | None = None,
    trigger: dict[str, Any] | None = None,
) -> str:
    """
    Write episode to goal_solution_links and update procedural_memory.
    outcome: "success" | "partial" | "failure" | "purchased" | "unknown"
    Returns episode_id from goal_solution_links.
    """
    import uuid
    sol_id = solution_id or str(uuid.uuid4())
    summary = solution_summary or f"bundle:{','.join(bundle_skus[:5])}"
    success = outcome in ("success", "purchased")

    episode_id = upsert_episode(
        goal_id=goal_id,
        solution_id=sol_id,
        user_id=user_id,
        goal_text=goal_text,
        solution_summary=summary,
        outcome=outcome,
        score=score,
        revenue=revenue,
        success=success,
    )

    upsert_from_episode({
        "summary": goal_text,
        "solution_skus": list(bundle_skus),
        "success": success,
        "score": score,
        "trigger": trigger or {},
    })
    return episode_id
