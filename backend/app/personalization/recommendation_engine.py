"""RecommendationEngineAgent: multi-objective recs (relevance, diversity, novelty)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List

from app.cdp.customer_profile import CustomerProfile


@dataclass
class RecommendationScore:
    """Per-product multi-objective score."""

    product_id: str
    relevance_score: float
    diversity_score: float
    novelty_score: float
    final_score: float
    reasons: List[str]


class RecommendationEngine:
    """Multi-objective recommendation engine (relevance + diversity + novelty)."""

    def __init__(self) -> None:
        self._candidate_ids: List[str] = [f"prod_{i}" for i in range(1, 101)]

    async def generate(
        self,
        profile: CustomerProfile,
        preferences: Dict[str, Any],
        behavior: Dict[str, Any],
        ab_variant: str,
    ) -> List[Dict[str, Any]]:
        """Multi-objective recommendations (relevance + diversity + novelty)."""
        candidates = await self._generate_candidates(profile, preferences)
        scores = await asyncio.gather(
            *[
                self._score_product(profile, preferences, behavior, cand, ab_variant)
                for cand in candidates[:50]
            ]
        )
        ranked = sorted(scores, key=lambda x: x.final_score, reverse=True)[:12]
        return [
            {
                "product_id": s.product_id,
                "scores": {
                    "relevance": s.relevance_score,
                    "diversity": s.diversity_score,
                    "novelty": s.novelty_score,
                },
                "reasons": s.reasons,
                "personalization_explanation": self._generate_explanation(s, profile),
            }
            for s in ranked
        ]

    async def _generate_candidates(
        self,
        profile: CustomerProfile,
        preferences: Dict[str, Any],
    ) -> List[str]:
        """Candidate product IDs (top 100 from catalog/collab; stub returns fixed list)."""
        await asyncio.sleep(0)
        aff = preferences.get("category_affinity") or {}
        if aff:
            # Bias toward categories with affinity (stub: just shuffle by hash)
            seed = hash(profile.customer_id) % 100
            return [self._candidate_ids[(i + seed) % len(self._candidate_ids)] for i in range(100)]
        return self._candidate_ids[:100]

    async def _score_product(
        self,
        profile: CustomerProfile,
        prefs: Dict[str, Any],
        behavior: Dict[str, Any],
        product_id: str,
        ab_variant: str,
    ) -> RecommendationScore:
        """Score one product on relevance, diversity, novelty."""
        await asyncio.sleep(0)
        rev = (hash(product_id + profile.customer_id) % 100) / 100.0
        div = 0.5 + (hash(product_id) % 50) / 100.0
        nov = 0.3 + (hash(product_id + ab_variant) % 70) / 100.0
        w_r, w_d, w_n = 0.6, 0.2, 0.2
        final = w_r * rev + w_d * div + w_n * nov
        reasons = [
            f"Relevance to {profile.segments.loyalty_tier} tier",
            "Category match",
            "Diversity in carousel",
        ]
        return RecommendationScore(
            product_id=product_id,
            relevance_score=rev,
            diversity_score=div,
            novelty_score=nov,
            final_score=final,
            reasons=reasons,
        )

    def _generate_explanation(self, score: RecommendationScore, profile: CustomerProfile) -> str:
        """Human-readable personalization explanation."""
        return (
            f"Based on your {profile.segments.loyalty_tier} profile and recent activity; "
            f"relevance {score.relevance_score:.0%}, diversity {score.diversity_score:.0%}."
        )
