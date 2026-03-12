from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Sequence

from app.agents.inventory import InventoryPlan
from app.agents.shopper import ShopperGoal


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CompetitorPrice:
    sku: str
    competitor: str
    price_eur: float


@dataclass(slots=True)
class CompetitorContext:
    competitors: List[CompetitorPrice]
    latency_ms: int


@dataclass(slots=True)
class PricingPlan:
    prices: Dict[str, float] = field(default_factory=dict)
    margin_pct: float = 0.0
    latency_ms: int = 0


class PricingAgent:
    """
    Simplified dynamic pricing agent.

    In production this would query real competitor feeds and a learned policy.
    """

    def fetch_competitor_context(self, query: str) -> CompetitorContext:
        started = time.perf_counter()
        # Deterministic dummy competitor context for hackathon demo.
        competitors = [
            CompetitorPrice(sku="SKU-BASE", competitor="comp_a", price_eur=70.0),
            CompetitorPrice(sku="SKU-BASE", competitor="comp_b", price_eur=75.0),
        ]
        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "Fetched competitor context",
            extra={
                "event": "pricing.fetch_competitor_context",
                "query": query,
                "competitors": len(competitors),
                "latency_ms": latency_ms,
            },
        )
        return CompetitorContext(competitors=competitors, latency_ms=latency_ms)

    def optimize_pricing(
        self,
        goal: ShopperGoal,
        competitor_ctx: CompetitorContext,
    ) -> PricingPlan:
        # AUTONOMOUS-AGENT-HACKATHON: transparent pricing heuristic.
        started = time.perf_counter()
        base_floor = min((c.price_eur for c in competitor_ctx.competitors), default=50.0)
        prices: Dict[str, float] = {}
        for comp in competitor_ctx.competitors:
            prices[comp.sku] = max(base_floor - 1.0, comp.price_eur * 0.98)
        avg_comp = (
            sum(c.price_eur for c in competitor_ctx.competitors) / len(competitor_ctx.competitors)
            if competitor_ctx.competitors
            else base_floor
        )
        ours = prices.get("SKU-BASE", avg_comp)
        margin_pct = (avg_comp - ours) / avg_comp if avg_comp else 0.0
        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "Optimized pricing",
            extra={
                "event": "pricing.optimize_pricing",
                "goal_id": goal.goal_id,
                "margin_pct": margin_pct,
                "latency_ms": latency_ms,
            },
        )
        return PricingPlan(prices=prices, margin_pct=margin_pct, latency_ms=latency_ms)


__all__: Sequence[str] = [
    "PricingAgent",
    "PricingPlan",
    "CompetitorPrice",
    "CompetitorContext",
]

