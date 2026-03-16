"""JourneyOrchestratorAgent: multi-channel journey planning."""

from __future__ import annotations

from typing import Any, Dict, List

from app.cdp.customer_profile import CustomerProfile


class JourneyOrchestratorAgent:
    """Plan and orchestrate next step in omni-channel journey."""

    def __init__(self) -> None:
        self._state: Dict[str, str] = {}

    async def plan_next_step(
        self,
        profile: CustomerProfile,
        recommendations: List[Dict[str, Any]],
    ) -> str:
        """Multi-channel journey: return next step (e.g. email_campaign, push, web_banner)."""
        cid = profile.customer_id
        current = self._state.get(cid, "discovery")
        channel_scores = self._score_channels(profile, current)
        best_channel = max(channel_scores, key=channel_scores.get)
        next_step = self._select_step(current, recommendations, best_channel)
        self._state[cid] = next_step
        return next_step

    def _score_channels(self, profile: CustomerProfile, current_state: str) -> Dict[str, float]:
        """Score channels for this profile and state."""
        ch = profile.current_channel or "web"
        scores = {"web": 0.8, "mobile": 0.7, "email": 0.6, "in_store": 0.5, "push": 0.5}
        scores[ch] = scores.get(ch, 0.5) + 0.2
        return scores

    def _select_step(
        self,
        current_state: str,
        recommendations: List[Dict[str, Any]],
        best_channel: str,
    ) -> str:
        """Select next journey step (action + channel)."""
        if not recommendations:
            return f"{best_channel}_browse"
        return f"{best_channel}_recommendations"
