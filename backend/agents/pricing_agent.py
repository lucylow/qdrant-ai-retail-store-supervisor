from __future__ import annotations

from typing import Any, Dict, List


class PricingAgent:
    """
    Domain agent for dynamic pricing, margin analysis, and price-based alerts.
    """

    DEFAULT_MARGIN_THRESHOLD = 0.15  # 15%

    def analyze_margins(
        self, products: List[Dict[str, Any]], threshold: float | None = None
    ) -> List[Dict[str, Any]]:
        """Flag products whose margin falls below threshold."""
        threshold = threshold or self.DEFAULT_MARGIN_THRESHOLD
        alerts: List[Dict[str, Any]] = []
        for p in products:
            cost = p.get("cost", 0)
            price = p.get("price", 0)
            if price <= 0:
                continue
            margin = (price - cost) / price
            if margin < threshold:
                alerts.append(
                    {
                        "product": p.get("name", ""),
                        "price": price,
                        "cost": cost,
                        "margin": round(margin, 3),
                        "threshold": threshold,
                    }
                )
        return alerts

    def suggest_bundle_price(
        self, items: List[Dict[str, Any]], discount_pct: float = 0.10
    ) -> Dict[str, Any]:
        """Compute a bundle price with a configurable discount."""
        total = sum(i.get("price", 0) for i in items)
        discounted = round(total * (1 - discount_pct), 2)
        return {
            "items": [i.get("name", "") for i in items],
            "original_total": total,
            "bundle_price": discounted,
            "savings": round(total - discounted, 2),
            "discount_pct": discount_pct,
        }

    def competitive_position(
        self, product: Dict[str, Any], competitors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simple competitive price positioning."""
        our_price = product.get("price", 0)
        comp_prices = [c.get("price", 0) for c in competitors if c.get("price", 0) > 0]
        if not comp_prices:
            return {"position": "unknown", "price": our_price}
        avg_comp = sum(comp_prices) / len(comp_prices)
        position = "below" if our_price < avg_comp else "above" if our_price > avg_comp else "at"
        return {
            "position": position,
            "our_price": our_price,
            "avg_competitor": round(avg_comp, 2),
            "delta_pct": round((our_price - avg_comp) / avg_comp * 100, 1) if avg_comp else 0,
        }
