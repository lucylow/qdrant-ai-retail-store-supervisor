from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ReasoningResult:
    answer: str
    confidence: float
    reasoning_steps: List[str]
    sources: List[str]


class RetailReasoningEngine:
    """
    LLM-backed reasoning engine for retail Q&A.

    Applies chain-of-thought decomposition:
    1. Classify intent (product search / comparison / stock check / general)
    2. Extract constraints from context
    3. Reason over constraints → candidate answer
    4. Self-critique & refine
    """

    INTENT_TYPES = ["product_search", "comparison", "stock_check", "promotion", "general"]

    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.model = model

    def answer(self, context: str, question: str) -> str:
        """Simple string answer (backward-compatible API)."""
        result = self.reason(context, question)
        return result.answer

    def reason(self, context: str, question: str) -> ReasoningResult:
        """Full reasoning pipeline returning structured result."""
        steps: List[str] = []

        # 1 — Intent classification (lightweight heuristic; swap with LLM call)
        intent = self._classify_intent(question)
        steps.append(f"intent={intent}")

        # 2 — Constraint extraction
        constraints = self._extract_constraints(question)
        steps.append(f"constraints={json.dumps(constraints)}")

        # 3 — Generate answer from context + constraints
        answer = self._generate(context, question, intent, constraints)
        steps.append("generated_answer")

        # 4 — Confidence estimate (simple heuristic)
        confidence = min(1.0, 0.5 + 0.1 * len(context.split()))
        if not context.strip():
            confidence = 0.1

        sources = self._extract_sources(context)

        return ReasoningResult(
            answer=answer,
            confidence=confidence,
            reasoning_steps=steps,
            sources=sources,
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _classify_intent(self, question: str) -> str:
        q = question.lower()
        if any(w in q for w in ("compare", "vs", "versus", "difference")):
            return "comparison"
        if any(w in q for w in ("stock", "available", "in stock", "inventory")):
            return "stock_check"
        if any(w in q for w in ("promo", "discount", "sale", "deal", "coupon")):
            return "promotion"
        if any(w in q for w in ("find", "search", "looking for", "need", "want", "buy")):
            return "product_search"
        return "general"

    @staticmethod
    def _extract_constraints(question: str) -> Dict[str, Any]:
        constraints: Dict[str, Any] = {}
        q = question.lower()
        # Budget
        for currency in ("chf", "€", "$", "eur", "usd"):
            if currency in q:
                import re
                match = re.search(r"(\d+)\s*" + re.escape(currency), q)
                if not match:
                    match = re.search(re.escape(currency) + r"\s*(\d+)", q)
                if match:
                    constraints["budget"] = int(match.group(1))
                    constraints["currency"] = currency.upper()
        # Region
        for region in ("zurich", "berlin", "eu", "switzerland", "germany"):
            if region in q:
                constraints["region"] = region.title()
        return constraints

    def _generate(
        self,
        context: str,
        question: str,
        intent: str,
        constraints: Dict[str, Any],
    ) -> str:
        """
        In production, call an LLM here. For the prototype, build a
        structured answer from context.
        """
        if not context.strip():
            return (
                "I don't have enough information to answer that question. "
                "Could you provide more details?"
            )

        budget_note = ""
        if "budget" in constraints:
            budget_note = f" (budget: {constraints['budget']} {constraints.get('currency', '')})"

        return (
            f"Based on {len(context.split())} words of retrieved context "
            f"for your {intent} query{budget_note}:\n\n{context[:1500]}"
        )

    @staticmethod
    def _extract_sources(context: str) -> List[str]:
        """Pull source identifiers from context if present."""
        sources: List[str] = []
        for line in context.split("\n"):
            if line.strip().startswith("source:") or line.strip().startswith("id:"):
                sources.append(line.strip())
        return sources[:10]
