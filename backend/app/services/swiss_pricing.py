"""
CHF precision and cultural pricing (psychological price endings).
"""
from __future__ import annotations

from typing import Dict, List


class SwissPricingCulture:
    """Swiss payment and pricing culture: round to .00, .50, .95."""

    CHF_PRECISION = 0.05  # Prices end in .00, .50, .95 (never .27)

    PREFERRED_PRICES: Dict[str, List[float]] = {
        "coop": [0.95, 1.95, 2.95, 4.95, 9.95],  # Psychological pricing
        "migros": [0.99, 1.99, 2.99, 4.99],  # Competitor matching
        "denner": [0.79, 0.99, 1.29],  # Ultra-low margins
    }

    @staticmethod
    def round_to_swiss_price(price: float, retailer: str) -> float:
        """
        Round to Swiss retail standard (e.g. 12.73 CHF -> 12.95 CHF).
        Uses retailer preferred endings when close; otherwise round to 0.05.
        """
        preferred = SwissPricingCulture.PREFERRED_PRICES.get(
            retailer, [0.95, 1.95, 2.95, 4.95, 9.95]
        )
        # Find closest preferred ending for the "decimal part" of CHF
        best = min(preferred, key=lambda x: abs(x - (price % 1)) if price >= 1 else abs(x - price))
        if price >= 1:
            base = int(price)
            return round(base + best, 2)
        # Round to 0.05 for small amounts
        return round(round(price / 0.05) * 0.05, 2)
