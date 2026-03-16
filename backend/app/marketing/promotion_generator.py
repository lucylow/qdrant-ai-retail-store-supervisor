from typing import Any, Dict


class PromotionGenerator:
    """
    Simple promotion generator for hackathon demos.

    This can later be upgraded to use LLMs and richer segmentation, but for now
    it provides a deterministic structure that other agents can rely on.
    """

    def generate_campaign(self, product: Dict[str, Any], season: str) -> Dict[str, Any]:
        """
        Generate a basic promotion campaign description for a single product.
        """
        product_name = product.get("name") or product.get("title") or "Featured Product"
        season_label = season or "Seasonal"
        return {
            "campaign_name": f"{season_label} Promotion",
            "headline": f"Don't miss our {season_label.lower()} deals!",
            "product": product_name,
            "discount": "20%",
            "channels": ["email", "social", "homepage"],
        }


__all__ = ["PromotionGenerator"]

