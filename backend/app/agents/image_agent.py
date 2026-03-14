import logging
from typing import Dict, Any

from app.agents.interfaces import safe_execute, timed
from app.generation.image_prompt import build_image_prompt
from app.generator import rag_answer

logger = logging.getLogger(__name__)


class ImageAgent:
    name = "ImageAgent"

    @safe_execute
    @timed
    def run(self, context: Dict[str, Any]):
        product = context.get("product_payload")
        if not product:
            return {"status": "skipped", "reason": "no product_payload"}

        brand_assets = context.get("brand_assets", [])
        style_hint = context.get("style_hint", "modern retail display")

        # Use RAG to enrich the image brief with grounded copy and constraints.
        question = context.get("image_brief") or context.get(
            "goal", {}
        ).get("goal_text", "")
        context_input: Dict[str, Any] = {
            "user": context.get("user", {}),
            "agent": {"name": "ImageAgent"},
            "task": {"intent": "generate product image brief"},
            "product": {
                "id": product.get("id") or product.get("sku"),
                "title": product.get("name") or product.get("title"),
            },
            "collection": context.get("collection", "products"),
            "policy": context.get("policy", {}),
        }
        rag = rag_answer(context_input, question, token_budget=512)

        prompt = build_image_prompt(
            product,
            brand_assets,
            style_hint=style_hint,
            rag_summary=rag.get("answer"),
        )
        return {
            "image_prompt": prompt,
            "rag_provenance": rag.get("provenance"),
            "note": "Use image generation service with this prompt",
        }

