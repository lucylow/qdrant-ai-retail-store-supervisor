"""
Executor module: implements functions that APPLY actions suggested by agents.
Examples: write solution to database, schedule an order, send a notification (simulated).
All executors must be idempotent and return standardized results.
"""

from typing import Dict, Any
import logging

from app.agents.memory import get_memory

logger = logging.getLogger(__name__)


def upsert_solution(solution: Dict[str, Any]) -> Dict[str, Any]:
    """
    Persist a solution into memory under 'solutions' collection.
    Must be idempotent (use unique 'solution_id').
    """
    mem = get_memory()
    sid = solution.get("bundle_id") or solution.get("plan_id") or solution.get("id")
    if not sid:
        raise ValueError("solution missing id")
    try:
        from app.embeddings import embed_texts

        vec = embed_texts([solution.get("summary", "")])[0].tolist()
    except Exception:  # pragma: no cover - best-effort embedding
        vec = [0.0] * 384
    mem.upsert("solutions", sid, vec, solution)
    logger.info("Persisted solution %s", sid)
    return {"persisted_id": sid}


def apply_merch_change(change: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate a merch change (e.g., move product to front display).
    Real systems would call an API or issue a task.
    """
    logger.info("Applying merch change: %s", change)
    job_id = change.get("job_id") or f"merch::{change.get('product_id')}::{change.get('location')}"
    try:
        from app.embeddings import embed_texts

        vec = embed_texts([str(job_id)])[0].tolist()
    except Exception:  # pragma: no cover - best-effort embedding
        vec = [0.0] * 384
    mem = get_memory()
    mem.upsert("applied_changes", job_id, vec, change)
    return {"applied": True, "job_id": job_id}

