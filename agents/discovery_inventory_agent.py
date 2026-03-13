"""
Inventory Agent: RetailRocket co-occurrence patterns → bundle recommendations.

Uses Discovery API (co_purchased / co_carted) to propose bundles with high
fulfillment probability. "Items co-carted 92% of time → higher fulfillment."
"""

from __future__ import annotations

from typing import Any

try:
    from app.services.retailrocket_discovery import RetailRocketDiscovery
except ImportError:
    RetailRocketDiscovery = None  # type: ignore


class DiscoveryInventoryAgent:
    """Recommend bundles from RetailRocket co-purchase / co-cart patterns."""

    def __init__(self, discovery_service: RetailRocketDiscovery | None = None):
        self.discovery = discovery_service or (
            RetailRocketDiscovery() if RetailRocketDiscovery else None
        )

    async def recommend_bundles(
        self,
        shopper_goal: dict[str, Any],
        session_history: list[int],
        limit: int = 5,
    ) -> dict[str, Any]:
        """Multi-context Discovery → optimal bundle candidates."""
        if not self.discovery:
            return {
                "recommended_bundle": [],
                "bundle_conv_lift": "0%",
                "retailrocket_patterns": 0,
                "cross_sell_opportunities": 0,
            }
        last_items = session_history[-3:] if len(session_history) >= 3 else session_history
        if not last_items:
            return {
                "recommended_bundle": [],
                "bundle_conv_lift": "0%",
                "retailrocket_patterns": 0,
                "cross_sell_opportunities": 0,
            }
        primary_recs = self.discovery.discover_recommendations(
            last_items, context="co_purchased", limit=20
        )
        cross_sell_recs = self.discovery.discover_recommendations(
            last_items[-1:], context="co_carted", limit=10
        )
        bundle_candidates = self._score_bundles(primary_recs, cross_sell_recs)
        top = bundle_candidates[0] if bundle_candidates else {"itemid": 0, "conv_lift": 0.0}
        return {
            "recommended_bundle": [b.get("itemid") for b in bundle_candidates[:3]],
            "bundle_conv_lift": f"{top.get('conv_lift', 0):.1%}",
            "retailrocket_patterns": len(primary_recs),
            "cross_sell_opportunities": len(cross_sell_recs),
        }

    def _score_bundles(
        self,
        primary_recs: list[dict[str, Any]],
        cross_sell_recs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """RRF-style + conversion weighting."""
        scored: dict[int, float] = {}
        for rec in primary_recs:
            iid = rec.get("itemid")
            if iid is None:
                continue
            rate = rec.get("conversion_rate") or 0
            s = (rec.get("score") or 0) * 2.0 * (1.0 + rate)
            scored[iid] = scored.get(iid, 0) + s
        for rec in cross_sell_recs:
            iid = rec.get("itemid")
            if iid is None:
                continue
            scored[iid] = scored.get(iid, 0) + (rec.get("score") or 0) * 1.0
        out = [
            {"itemid": iid, "conv_lift": rate}
            for iid, rate in sorted(scored.items(), key=lambda x: -x[1])[:10]
        ]
        return out
