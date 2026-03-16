from __future__ import annotations

from typing import Any, Mapping

from app.agents.base import Agent
from app.retriever import hybrid_retrieve_products


class InventoryAgent(Agent):
    name = "inventory_agent"

    def run(self, query: str, context: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        retrieval = hybrid_retrieve_products(query, top_k=10)
        return {
            "query": query,
            "products": [
                {
                    "id": d.id,
                    "name": d.payload.get("name"),
                    "price": d.payload.get("price"),
                    "score": d.score,
                }
                for d in retrieval.docs
            ],
            "context_fingerprint": retrieval.context.fingerprint,
        }


__all__ = ["InventoryAgent"]

from typing import Any, Dict
import logging

from app.agents.base import Context, AgentResult
from app.agents.interfaces import safe_execute, timed
from app.agents.planner import create_candidate_plans
from app.agents.executor import upsert_solution
from app.generator import rag_answer

logger = logging.getLogger(__name__)


class InventoryAgent:
    name = "InventoryAgent"

    @safe_execute
    @timed
    def run(self, context: Context) -> Dict[str, Any]:
        goal = context.get("goal")
        if not goal:
            return {"status": "skipped", "reason": "no goal in context"}

        # Build context_input for RAG-enhanced planning.
        context_input: Dict[str, Any] = {
            "user": context.get("user", {}),
            "agent": {"name": "InventoryAgent"},
            "task": {"intent": "find products for goal"},
            "product": context.get("product", {}),
            "collection": context.get("collection", "products"),
            "policy": context.get("policy", {}),
        }

        rag = rag_answer(
            context_input,
            goal.get("goal_text", ""),
            token_budget=1024,
        )

        plans = create_candidate_plans(goal, context, max_plans=3)

        feasible = []
        for p in plans:
            p["validated"] = True
            # attach a short RAG explanation for transparency
            if isinstance(rag.get("answer"), str):
                p["rag_explanation"] = rag["answer"][:400]
            feasible.append(p)

        persisted = []
        for p in feasible:
            sol = {
                "bundle_id": p.get("plan_id") or p.get("plan_id", "bundle_unknown"),
                "summary": p.get("summary"),
                "items": p.get("items"),
            }
            res = upsert_solution(sol)
            persisted.append(res)
        return {"plans": feasible, "persisted": persisted, "rag": rag}


