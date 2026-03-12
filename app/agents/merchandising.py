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
class MerchandisingPlan:
    primary_promo_text: str
    hero_image_url: str | None
    layout_hint: str


class MerchandisingAgent:
    """
    Multi-modal merchandising plan generator.

    This version focuses on deterministic text & layout hints suitable
    for driving multi-modal generation and UI layouts.
    """

    async def build_merchandising_plan(
        self,
        goal: ShopperGoal,
        bundle: InventoryPlan,
        pricing: PricingPlan,
    ) -> MerchandisingPlan:
        # AUTONOMOUS-AGENT-HACKATHON: merchandising summary for Streamlit demo.
        started = time.perf_counter()
        product_count = len(bundle.items)
        tagline = f"Styled bundle for {goal.region or 'your city'} in under {bundle.eta_days} days"
        if goal.budget_eur is not None:
            tagline += f" • under €{goal.budget_eur:.0f}"
        hero_image_url: str | None = None
        layout = "grid-3-wide" if product_count >= 3 else "single-hero"
        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "Merchandising plan created",
            extra={
                "event": "merchandising.build_plan",
                "goal_id": goal.goal_id,
                "product_count": product_count,
                "layout": layout,
                "latency_ms": latency_ms,
            },
        )
        return MerchandisingPlan(
            primary_promo_text=tagline,
            hero_image_url=hero_image_url,
            layout_hint=layout,
        )


__all__: Sequence[str] = ["MerchandisingAgent", "MerchandisingPlan"]

