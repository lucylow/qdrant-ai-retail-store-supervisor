"""PreferenceLearnerAgent: category/brand/style affinity modeling and evolution."""

from __future__ import annotations

from typing import Any, Dict

from app.cdp.customer_profile import CustomerProfile


class PreferenceLearnerAgent:
    """Infer and evolve customer preferences from profile + behavior."""

    async def infer_preferences(
        self,
        profile: CustomerProfile,
        behavior: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Infer category/brand/style affinities from profile and session behavior.
        Returns dict with category_affinity, brand_affinity, style_affinity, recency_weights.
        """
        category_affinity = dict(profile.segments.category_affinity or {})
        for cat in behavior.get("categories_viewed", [])[:10]:
            if cat:
                category_affinity[cat] = category_affinity.get(cat, 0) + 0.15
        for pid in behavior.get("products_viewed", [])[:20]:
            if pid:
                category_affinity[f"product_{pid}"] = category_affinity.get(f"product_{pid}", 0) + 0.05
        # Normalize to 0-1
        if category_affinity:
            m = max(category_affinity.values())
            if m > 0:
                category_affinity = {k: v / m for k, v in category_affinity.items()}
        return {
            "category_affinity": category_affinity,
            "brand_affinity": {},
            "style_affinity": {},
            "recency_weights": {"recent_views": 1.0, "historical": 0.7},
            "intent": behavior.get("intent", "browse"),
            "journey_stage": behavior.get("journey_stage", "awareness"),
        }
