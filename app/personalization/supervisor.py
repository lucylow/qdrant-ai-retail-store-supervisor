"""PersonalizationSupervisorAgent: 8-agent orchestration + GDPR compliance."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Dict, List

from app.cdp.customer_profile import CustomerProfile
from app.cdp.gdpr_compliance import GDPRCompliance
from app.personalization.ab_tester import ABTesterAgent
from app.personalization.behavior_analyzer import BehaviorAnalyzerAgent
from app.personalization.journey_orchestrator import JourneyOrchestratorAgent
from app.personalization.offer_personalizer import OfferPersonalizerAgent
from app.personalization.preference_learner import PreferenceLearnerAgent
from app.personalization.profile_builder import ProfileBuilderAgent
from app.personalization.recommendation_engine import RecommendationEngine
from app.qdrant.personalization.client import PersonalizationQdrantClient


@dataclass
class PersonalizationResult:
    """Full personalization pipeline result."""

    customer_id: str
    profile: CustomerProfile
    recommendations: List[Dict]
    offers: List[Dict]
    journey_next_step: str
    confidence: float
    ab_test_variant: str
    gdpr_compliant: bool


class PersonalizationSupervisor:
    """Orchestrate 8 personalization agents and enforce GDPR."""

    def __init__(self) -> None:
        self.agents = {
            "profile": ProfileBuilderAgent(),
            "behavior": BehaviorAnalyzerAgent(),
            "preferences": PreferenceLearnerAgent(),
            "recommendations": RecommendationEngine(),
            "offers": OfferPersonalizerAgent(),
            "journey": JourneyOrchestratorAgent(),
            "ab_test": ABTesterAgent(),
        }
        self.qdrant = PersonalizationQdrantClient()
        self.gdpr = GDPRCompliance()

    async def personalize(
        self,
        customer_id: str,
        context: Dict,
        channel: str = "web",
    ) -> PersonalizationResult:
        """Full 8-agent personalization pipeline."""
        if "channel" not in context:
            context["channel"] = channel

        async def run_agents():
            profile_task = self.agents["profile"].build_profile(customer_id, context)
            behavior_task = self.agents["behavior"].analyze_session(customer_id, context)
            ab_task = self.agents["ab_test"].assign_variant(customer_id, context)
            profile, behavior, ab_variant = await asyncio.gather(
                profile_task, behavior_task, ab_task
            )
            prefs = await self.agents["preferences"].infer_preferences(profile, behavior)
            recs = await self.agents["recommendations"].generate(
                profile, prefs, behavior, ab_variant
            )
            offers = await self.agents["offers"].personalize(recs, profile)
            journey_step = await self.agents["journey"].plan_next_step(profile, recs)
            return profile, recs, offers, journey_step, ab_variant

        profile, recs, offers, journey_step, ab_variant = await run_agents()

        compliant = await self._check_gdpr_compliance(customer_id, recs, offers)
        await self.qdrant.store_interaction(
            customer_id, {**context, "ab_variant": ab_variant}, recs, offers, profile.confidence
        )

        return PersonalizationResult(
            customer_id=customer_id,
            profile=profile,
            recommendations=recs,
            offers=offers,
            journey_next_step=journey_step,
            confidence=profile.confidence,
            ab_test_variant=ab_variant,
            gdpr_compliant=compliant,
        )

    async def _check_gdpr_compliance(
        self,
        customer_id: str,
        recommendations: List[Dict],
        offers: List[Dict],
    ) -> bool:
        """Ensure recommendations/offers respect consent and data minimization."""
        return await self.gdpr.check_recommendation_compliance(
            customer_id, recommendations, offers
        )
