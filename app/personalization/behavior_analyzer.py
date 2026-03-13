"""BehaviorAnalyzerAgent: session and journey pattern recognition."""

from __future__ import annotations

from typing import Any, Dict

from app.cdp.real_time_features import RealTimeFeatures, compute_real_time_features


class BehaviorAnalyzerAgent:
    """Analyze session and journey patterns for personalization."""

    async def analyze_session(
        self,
        customer_id: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze current session and journey; return behavior summary for
        preference learning and recommendations.
        """
        session_id = context.get("session_id", f"sess_{customer_id}")
        events = context.get("events", [])
        features = compute_real_time_features(customer_id, session_id, events, context)
        intent = self._infer_intent(features)
        journey_stage = self._journey_stage(features, context)
        return {
            "customer_id": customer_id,
            "session_id": session_id,
            "intent": intent,
            "journey_stage": journey_stage,
            "products_viewed": features.products_viewed,
            "categories_viewed": features.categories_viewed,
            "search_queries": features.search_queries,
            "dwell_time": features.dwell_time_seconds,
            "channel": features.channel,
            "real_time_features": features.to_vector_input(),
        }

    def _infer_intent(self, features: RealTimeFeatures) -> str:
        """Infer primary intent: browse, search, buy, reorder."""
        if features.add_to_cart_events:
            return "buy"
        if features.search_queries:
            return "search"
        if features.dwell_time_seconds > 120:
            return "browse_deep"
        return "browse"

    def _journey_stage(self, features: RealTimeFeatures, context: Dict[str, Any]) -> str:
        """Journey stage: awareness, consideration, conversion, loyalty."""
        if features.page_views <= 2:
            return "awareness"
        if features.add_to_cart_events:
            return "conversion"
        if features.page_views >= 5:
            return "consideration"
        return "awareness"
