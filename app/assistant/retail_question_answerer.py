from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Literal

from app.assistant.retail_copilot import RetailCopilot
from app.agents.retail_supervisor import RetailSupervisor
from app.agents.inventory_agent import InventoryAgent as InventoryPlanAgent
from app.agents.merch_agent import MerchAgent as MerchandisingPlanAgent
from app.marketing.promotion_generator import PromotionGenerator
from app.context_manager import build_context_for_query
from app.generator import rag_answer


RetailQuestionType = Literal[
    "inventory",
    "pricing",
    "promotion",
    "merchandising",
]


@dataclass
class RetailAnswer:
    """
    Structured response for retail questions so demos and UIs can
    render consistent outputs and inspect reasoning.
    """

    question: str
    answer_text: str
    question_type: RetailQuestionType
    agent_used: str
    confidence: float
    reasoning: str
    context_metadata: Dict[str, Any]


class RetailQuestionAnswerer:
    """
    High-level orchestrator for retail business questions.

    This class:
    - uses RetailSupervisor to route to the right domain
    - builds an Agentic RAG context via context_manager
    - optionally calls specialised agents for planning (inventory / merch)
    - falls back to RetailCopilot for fluent explanations
    """

    def __init__(
        self,
        copilot: Optional[RetailCopilot] = None,
        supervisor: Optional[RetailSupervisor] = None,
    ) -> None:
        self.copilot = copilot or RetailCopilot()
        self.supervisor = supervisor or RetailSupervisor()
        self._inventory_agent = InventoryPlanAgent()
        self._merch_agent = MerchandisingPlanAgent()
        self._promo_generator = PromotionGenerator()

    def _infer_question_type(self, question: str) -> RetailQuestionType:
        routed = self.supervisor.route_task(question)
        if routed == "InventoryAgent":
            return "inventory"
        if routed == "PricingAgent":
            return "pricing"
        if routed == "MarketingAgent":
            return "promotion"
        return "merchandising"

    def _confidence_from_scores(self, scores: List[float]) -> float:
        if not scores:
            return 0.2
        top = max(scores)
        if len(scores) == 1:
            return min(0.95, max(0.3, top))
        second = sorted(scores, reverse=True)[1]
        margin = max(0.0, top - second)
        return float(min(0.99, 0.4 + 0.4 * top + 0.2 * margin))

    def _build_agentic_context(
        self,
        question: str,
        collection: str = "products",
        multi_hop: bool = False,
    ) -> Dict[str, Any]:
        context_input: Dict[str, Any] = {
            "agent": {"name": "RetailQuestionAnswerer"},
            "task": {
                "intent": "retail_business_question",
                "multi_hop": multi_hop,
            },
            "collection": collection,
            "policy": {
                "trusted_sources": ["catalog", "transactions"],
            },
        }
        return build_context_for_query(context_input, question)

    def answer(self, question: str) -> RetailAnswer:
        qtype = self._infer_question_type(question)

        ctx = self._build_agentic_context(
            question,
            collection="products",
            multi_hop=qtype in {"inventory", "merchandising"},
        )
        selected = ctx.get("selected_docs", [])
        scores = [float(d.get("adj_score", 0.0)) for d in selected]
        confidence = self._confidence_from_scores(scores)

        reasoning_parts: List[str] = []
        reasoning_parts.append(
            f"Retrieved {len(selected)} context documents for question type '{qtype}'."
        )

        if qtype == "inventory":
            answer_text = self._answer_inventory(question, ctx, reasoning_parts)
            agent_name = "InventoryAgent + RetailCopilot"
        elif qtype == "promotion":
            answer_text = self._answer_promotion(question, ctx, reasoning_parts)
            agent_name = "MarketingAgent + RetailCopilot"
        elif qtype == "pricing":
            answer_text = self._answer_pricing(question, ctx, reasoning_parts)
            agent_name = "PricingAgent (rag_answer)"
        else:
            answer_text = self._answer_merchandising(question, ctx, reasoning_parts)
            agent_name = "MerchAgent + RetailCopilot"

        reasoning = "\n".join(reasoning_parts)
        return RetailAnswer(
            question=question,
            answer_text=answer_text,
            question_type=qtype,
            agent_used=agent_name,
            confidence=confidence,
            reasoning=reasoning,
            context_metadata=ctx.get("metadata", {}),
        )

    def _answer_inventory(
        self,
        question: str,
        ctx: Dict[str, Any],
        reasoning: List[str],
    ) -> str:
        context_input = {
            "user": {},
            "agent": {"name": "InventoryAgent"},
            "task": {"intent": "inventory_risk_analysis"},
            "product": {},
            "collection": "products",
            "policy": {},
        }
        rag = rag_answer(context_input, question, token_budget=1024)
        reasoning.append("InventoryAgent used rag_answer for detailed risk analysis.")
        reasoning.append(f"RAG provenance: {rag.get('provenance')}")
        return rag.get("answer", "")

    def _answer_promotion(
        self,
        question: str,
        ctx: Dict[str, Any],
        reasoning: List[str],
    ) -> str:
        docs = ctx.get("selected_docs", [])[:1]
        if not docs:
            return self.copilot.answer(question)
        payload = docs[0].get("payload") or {}
        product = {
            "name": payload.get("name") or payload.get("title") or "Featured Product",
        }
        campaign = self._promo_generator.generate_campaign(product, season="Seasonal")
        reasoning.append("PromotionGenerator used to create a structured campaign.")
        return (
            f"Suggested campaign: {campaign['headline']} with {campaign['discount']} "
            f"via channels {', '.join(campaign['channels'])}."
        )

    def _answer_pricing(
        self,
        question: str,
        ctx: Dict[str, Any],
        reasoning: List[str],
    ) -> str:
        context_input = {
            "user": {},
            "agent": {"name": "PricingAgent"},
            "task": {"intent": "pricing_intelligence"},
            "collection": "products",
        }
        rag = rag_answer(context_input, question, token_budget=1024)
        reasoning.append("PricingAgent-style rag_answer used for pricing guidance.")
        return rag.get("answer", "")

    def _answer_merchandising(
        self,
        question: str,
        ctx: Dict[str, Any],
        reasoning: List[str],
    ) -> str:
        answer = self.copilot.answer(question)
        reasoning.append("RetailCopilot used for merchandising / cross-sell narrative.")
        return answer


__all__ = ["RetailQuestionAnswerer", "RetailAnswer"]

