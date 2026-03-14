from __future__ import annotations

from typing import Any, Dict

from .inventory_agent import InventoryAgent
from .merchandising_agent import MerchandisingAgent
from .retail_api_client import RetailAPIClient, Retailer


class SwissSupervisorAgent:
    """
    Orchestrator for Swiss retailer-specific inventory + merchandising agents.
    """

    def __init__(self, api_client: RetailAPIClient) -> None:
        self.api_client = api_client
        self.inventory = InventoryAgent(api_client)
        self.merchandising = MerchandisingAgent(api_client)

    async def handle_swiss_query(self, tenant_slug: str, query: str, region: str) -> Dict[str, Any]:
        """
        Unified Swiss retail query → multi-agent coordination.

        Mock-first orchestration: for Coop and Migros we call specialized
        bundle methods; can be extended to other retailers later.
        """
        retailer_map = {
            "coop": Retailer.COOP,
            "migros": Retailer.MIGROS,
            "denner": Retailer.DENNER,
            "manor": Retailer.MANOR,
        }

        retailer = retailer_map.get(tenant_slug)
        if retailer is None:
            raise ValueError(f"Unsupported retailer: {tenant_slug}")

        if retailer is Retailer.COOP:
            inventory_result = await self.inventory.optimize_coop_bundle(query=query, region=region)
            merchandising_result: Dict[str, Any] = {}
        elif retailer is Retailer.MIGROS:
            inventory_result = {}
            merchandising_result = await self.merchandising.create_migros_seasonal_bundle(
                query=query,
                season="winter",
            )
        else:
            inventory_result = {}
            merchandising_result = {}

        combined = self._merge_solutions(inventory_result, merchandising_result)

        return {
            "tenant": tenant_slug,
            "retailer": retailer.value,
            "query": query,
            "region": region,
            "inventory_solution": inventory_result,
            "merchandising_solution": merchandising_result,
            "combined_recommendation": combined,
        }

    def _merge_solutions(self, inventory_result: Dict[str, Any], merchandising_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lightweight merge of inventory + merchandising bundles.
        """
        inv_bundle = (inventory_result or {}).get("bundle", {})
        merch_bundle = (merchandising_result or {}).get("bundle", [])

        items = list(inv_bundle.get("items", []))
        if merch_bundle:
            items.extend(merch_bundle)

        total_chf = 0.0
        for item in items:
            try:
                total_chf += float(item.get("price") or item.get("dynamic_price_chf") or 0.0)
            except Exception:  # noqa: BLE001
                continue

        return {
            "items": items,
            "estimated_total_chf": round(total_chf, 2),
        }


__all__ = ["SwissSupervisorAgent"]

