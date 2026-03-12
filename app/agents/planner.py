"""
Planner: generate candidate actions/plans given a goal and context.
Provides deterministic heuristics and LLM-assisted refinements (LLM call is optional).
"""

from typing import Dict, Any, List
import logging

from app.agents.memory import get_memory
from app.llm_client import generate

logger = logging.getLogger(__name__)


def create_candidate_plans(
    goal: Dict[str, Any], context: Dict[str, Any], max_plans: int = 3
) -> List[Dict[str, Any]]:
    """
    Deterministic candidate generator.
    - uses goal constraints (budget, region)
    - proposes bundles or merchandising actions
    """
    plans: List[Dict[str, Any]] = []
    mem = get_memory()
    query_text = (
        goal.get("goal_text")
        or goal.get("description")
        or goal.get("need", "")
    )

    try:
        from app.embeddings import embed_texts

        qvec = embed_texts([query_text])[0].tolist()
    except Exception:  # pragma: no cover - best-effort embedding
        qvec = None

    prod_hits = mem.search("products", qvec, top_k=10) if qvec else []

    for hit in prod_hits[:max_plans]:
        plans.append(
            {
                "plan_id": f"plan_{hit['id']}",
                "items": [hit["id"]],
                "summary": f"Recommend {hit['payload'].get('title', hit['id'])}",
                "confidence": float(hit.get("score", 0.5)),
            }
        )

    try:
        prompt = (
            f"Refine these plans for goal: {goal.get('goal_text')}\nPlans: {plans}"
        )
        llm_out = generate(prompt, max_tokens=128)
        for p in plans:
            p["llm_note"] = llm_out[:200]
    except Exception as e:  # pragma: no cover - best-effort LLM refine
        logger.debug("LLM refine skipped: %s", e)
    return plans

