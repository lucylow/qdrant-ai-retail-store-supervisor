from __future__ import annotations

from typing import Any, Dict, List

from .retail_api_client import RetailAPIClient, Retailer


class InventoryAgent:
    """
    Domain agent focused on stock health and inventory risk.

    Extended with Coop leShop.ch bundle optimization using RetailAPIClient.
    """

    def __init__(self, api_client: RetailAPIClient | None = None) -> None:
        self.api_client = api_client

    def detect_stock_risk(self, inventory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []

        for item in inventory:
            stock = item.get("stock", 0)
            reorder_point = item.get("reorder_point", 0)

            if stock < reorder_point:
                alerts.append(
                    {
                        "product": item.get("name", ""),
                        "stock": stock,
                        "reorder_point": reorder_point,
                    }
                )

        return alerts

    async def optimize_coop_bundle(
        self,
        query: str,
        region: str = "ZH",
        max_budget: float = 50.0,
    ) -> Dict[str, Any]:
        """
        Coop leShop.ch specific: dairy perishables + Zurich pickup.

        Mock-first: relies on RetailAPIClient abstraction so we can swap
        real Coop API endpoints later.
        """
        if self.api_client is None:
            raise ValueError("InventoryAgent.optimize_coop_bundle requires a RetailAPIClient")

        coop_categories = {
            "milch": ["dairy", "milk"],
            "brot": ["bakery", "bread"],
            "käse": ["dairy", "cheese"],
            "fondue": ["dairy", "fondue_kit"],
        }
        _ = coop_categories  # kept for future query parsing

        products = await self.api_client.get_products(
            retailer=Retailer.COOP,
            filters={"category": "dairy", "region": region, "stock_status": "in_stock"},
        )

        available = [
            p
            for p in products
            if p.get("stock", 0) > 0
            and p.get("pickup_zones")
            and region in p.get("pickup_zones", [])
        ]

        coop_bundle = self._create_coop_bundle(available, max_budget)

        skus = [item.get("sku") for item in coop_bundle.get("items", []) if item.get("sku")]
        stock = await self.api_client.get_inventory(Retailer.COOP, skus, region) if skus else {}

        total_chf = sum(float(item.get("price", 0.0)) for item in coop_bundle.get("items", []))
        stock_confirmed = all(stock.get(sku, {}).get("qty", 0) > 0 for sku in skus) if stock else False
        eta = None
        if stock:
            first_key = next(iter(stock.keys()))
            eta = stock.get(first_key, {}).get("eta")

        return {
            "tenant": "coop",
            "bundle": coop_bundle,
            "stock_confirmed": stock_confirmed,
            "total_chf": total_chf,
            "pickup_location": f"{region}_HB",
            "eta": eta or "tomorrow",
        }

    def _create_coop_bundle(self, products: List[Dict[str, Any]], max_budget: float) -> Dict[str, Any]:
        """Coop-specific bundle logic: prioritize perishables within budget."""
        if not products:
            return {"items": [], "type": "perishable_grocery"}

        perishables = sorted(products, key=lambda p: p.get("expiry_risk", 0.0), reverse=True)
        items: List[Dict[str, Any]] = []
        total = 0.0
        for p in perishables:
            price = float(p.get("price", 0.0))
            if price <= 0:
                continue
            if total + price > max_budget:
                continue
            items.append(p)
            total += price
        if not items:
            items = perishables[:3]

        return {
            "items": items,
            "type": "perishable_grocery",
        }

