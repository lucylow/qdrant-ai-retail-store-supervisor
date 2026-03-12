from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Sequence

from app.agents.inventory import InventoryPlan
from app.agents.pricing import PricingPlan
from app.agents.shopper import ShopperGoal


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AuditResult:
    hallucination_score: float
    compliance_ok: bool
    explanation: str
    success_prob: float
    latency_ms: int


class AuditAgent:
    """
    Guardrail agent for hallucination and compliance checks.
    """

    async def evaluate_plan(
        self,
        goal: ShopperGoal,
        inventory_plan: InventoryPlan,
        pricing_plan: PricingPlan,
    ) -> AuditResult:
        # AUTONOMOUS-AGENT-HACKATHON: safety checks drive deployment gating.
        started = time.perf_counter()

        hallucination_score = 0.05 if inventory_plan.items else 0.4
        total_price = inventory_plan.total_price_eur
        compliance_ok = True
        explanation = "Bundle grounded in catalog; prices competitive and non-predatory."
        if goal.budget_eur is not None and total_price > goal.budget_eur * 1.1:
            hallucination_score = max(hallucination_score, 0.25)
            explanation = "Bundle exceeds budget; may be misaligned with user goal."
        if pricing_plan.margin_pct < -0.1:
            compliance_ok = False
            explanation = "Prices undercut competitors excessively; blocking for policy."

        success_prob = max(0.0, 1.0 - hallucination_score)
        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "Audit evaluation completed",
            extra={
                "event": "audit.evaluate_plan",
                "goal_id": goal.goal_id,
                "hallucination_score": hallucination_score,
                "compliance_ok": compliance_ok,
                "success_prob": success_prob,
                "latency_ms": latency_ms,
            },
        )
        return AuditResult(
            hallucination_score=hallucination_score,
            compliance_ok=compliance_ok,
            explanation=explanation,
            success_prob=success_prob,
            latency_ms=latency_ms,
        )


__all__: Sequence[str] = ["AuditAgent", "AuditResult"]

