from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Sequence

from app.promo.lift_modeling import LiftModeler, VariantLift
from app.promo.segmentation import Customer, Segmenter


@dataclass(slots=True)
class Opportunity:
    sku: str
    store: str
    customers: List[Customer]
    event: str


@dataclass(slots=True)
class PromoCampaign:
    variants: Dict[str, str]
    selected_variant: str
    lifts: Dict[str, VariantLift]


class AutonomousPromoPlanner:
    """
    Autonomous promotion planner with detection → generation → deploy.
    """

    def __init__(
        self,
        segmentation: Segmenter | None = None,
        lift_modeler: LiftModeler | None = None,
    ) -> None:
        self.segmentation = segmentation or Segmenter()
        self.lift_modeler = lift_modeler or LiftModeler()

    async def generate_text_promo(self, segments: List[object]) -> str:
        return f"Promo for {len(segments)} segments"

    async def generate_image_promo(self, top_skus: List[str]) -> str:
        return f"Image promo for {', '.join(top_skus)}"

    async def generate_video_promo(self, event: str) -> str:
        return f"Video promo for {event}"

    def forecasting_predict(self, sku: str, store: str) -> List[str]:
        return [sku]

    def simulate_ab_test(self, variants: Dict[str, str]) -> Dict[str, VariantLift]:
        return self.lift_modeler.simulate_ab_test(variants)

    def deploy_canary(
        self,
        variants: Dict[str, str],
        lift: Dict[str, VariantLift],
    ) -> PromoCampaign:
        selected = max(lift.values(), key=lambda v: v.expected_lift_pct).variant_id
        return PromoCampaign(variants=variants, selected_variant=selected, lifts=lift)

    async def plan_campaign(self, opportunity: Opportunity) -> PromoCampaign:
        # STAGE 1: DETECT
        segments = self.segmentation.cluster(opportunity.customers)
        forecasts = self.forecasting_predict(opportunity.sku, opportunity.store)

        # STAGE 2: GENERATE (multi-modal)
        variants_list = await asyncio.gather(
            self.generate_text_promo(segments),
            self.generate_image_promo(forecasts),
            self.generate_video_promo(opportunity.event),
        )
        variants: Dict[str, str] = {
            "text": variants_list[0],
            "image": variants_list[1],
            "video": variants_list[2],
        }

        # STAGE 3: SIMULATE A/B + DEPLOY
        lifts = self.simulate_ab_test(variants)
        return self.deploy_canary(variants, lift=lifts)


__all__: Sequence[str] = ["AutonomousPromoPlanner", "Opportunity", "PromoCampaign"]

