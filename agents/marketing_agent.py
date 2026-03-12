from typing import Any, Dict


class MarketingAgent:
    """
    Agent for simple campaign generation around a given product.
    """

    def create_campaign(self, product: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "headline": f"Discover the new {product.get('name', 'product')}",
            "promotion": "20% off",
            "channels": ["email", "social", "homepage"],
        }

