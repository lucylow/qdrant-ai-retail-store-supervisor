from __future__ import annotations

from typing import Any, Dict, List

from .retail_api_client import RetailAPIClient, Retailer


class MerchandisingAgent:
    """
    Domain agent for product assortment, display strategy, and cross-sell logic.

    Extended with Migros seasonal bundle creation using RetailAPIClient.
    """

    def __init__(self, api_client: RetailAPIClient | None = None) -> None:
        self.api_client = api_client

    def recommend_cross_sells(
        self, cart: List[Dict[str, Any]], catalog: List[Dict[str, Any]], max_recs: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Simple category-based cross-sell: suggest items from categories
        not already in the cart.
        """
        cart_categories = {item.get("category", "") for item in cart}
        candidates = [
            p for p in catalog if p.get("category", "") not in cart_categories
        ]
        candidates.sort(key=lambda p: p.get("score", 0), reverse=True)
        return candidates[:max_recs]

    def assortment_gaps(
        self, catalog: List[Dict[str, Any]], target_categories: List[str]
    ) -> List[str]:
        """Identify target categories missing from the catalog."""
        present = {p.get("category", "") for p in catalog}
        return [c for c in target_categories if c not in present]

    def display_priority(
        self, products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rank products for display priority based on a composite score
        of margin, stock, and recency.
        """
        scored: List[tuple[float, Dict[str, Any]]] = []
        for p in products:
            margin = p.get("margin", 0.2)
            stock = min(p.get("stock", 0) / max(p.get("reorder_point", 1), 1), 2.0)
            recency = p.get("recency_score", 0.5)
            score = margin * 0.4 + stock * 0.3 + recency * 0.3
            scored.append((score, p))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {**p, "display_score": round(s, 3)} for s, p in scored
        ]

    async def create_migros_seasonal_bundle(self, query: str, season: str = "winter") -> Dict[str, Any]:
        """
        Migros: fondue season + ski gear bundles.

        Mock-first seasonal merchandising using RetailAPIClient.
        """
        if self.api_client is None:
            raise ValueError("MerchandisingAgent.create_migros_seasonal_bundle requires a RetailAPIClient")

        seasonal_categories = {
            "winter": "fondue",
            "ski": "ski",
            "summer": "bbq",
        }
        category = seasonal_categories.get(season, "grocery")
        _ = query  # reserved for future query-based refinements

        products = await self.api_client.get_products(
            retailer=Retailer.MIGROS,
            filters={"category": category},
        )

        skus = [p.get("sku") for p in products if p.get("sku")]
        prices = await self.api_client.get_pricing(Retailer.MIGROS, skus) if skus else {}

        for p in products:
            sku = p.get("sku")
            if sku and sku in prices:
                p["dynamic_price_chf"] = prices[sku]

        bundle_items = products[:4]

        return {
            "tenant": "migros",
            "season": season,
            "bundle": bundle_items,
            "dynamic_prices": prices,
            "expected_margin_uplift": 0.184,
        }

