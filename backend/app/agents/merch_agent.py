from __future__ import annotations

from typing import Any, Mapping

from app.agents.base import Agent


class MerchAgent(Agent):
    name = "merch_agent"

    def run(self, query: str, context: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        inv = (context or {}).get("inventory") or {}
        products = inv.get("products") or []
        layout = [
            {
                "slot": idx,
                "product_id": p.get("id"),
                "headline": f"Boost visibility for {p.get('name')}",
            }
            for idx, p in enumerate(products[:5])
        ]
        # CURSOR: integrate multimodal layout/image generation later.
        return {"query": query, "layout": layout}


__all__ = ["MerchAgent"]

import logging
from typing import Any, Dict

from app.agents.interfaces import safe_execute, timed
from app.agents.executor import apply_merch_change
from app.generator import rag_answer

logger = logging.getLogger(__name__)


class MerchAgent:
    name = "MerchAgent"

    @safe_execute
    @timed
    def run(self, context: Dict[str, Any]):
        request = context.get("merch_request") or context.get("goal", {}).get(
            "merch_request"
        )
        if not request:
            return {"status": "skipped", "reason": "no merch request"}

        product_id = request.get("product_id")
        if not product_id:
            return {"status": "failed", "error": "no product_id"}

        # Use RAG to get a short justification for the merchandising change.
        goal_text = request.get("reason") or context.get("goal", {}).get(
            "goal_text", ""
        )
        context_input: Dict[str, Any] = {
            "user": context.get("user", {}),
            "agent": {"name": "MerchAgent"},
            "task": {"intent": "merchandising change justification"},
            "product": {"id": product_id, "title": request.get("product_title")},
            "collection": context.get("collection", "products"),
            "policy": context.get("policy", {}),
        }
        rag = rag_answer(context_input, goal_text, token_budget=512)

        change = {
            "product_id": product_id,
            "location": request.get("location", "front_display"),
            "reason": request.get("reason", "promotion"),
        }
        res = apply_merch_change(change)
        return {
            "change": change,
            "result": res,
            "rag_explanation": rag.get("answer"),
            "rag_provenance": rag.get("provenance"),
        }

