"""
Dynamic pricing during Swiss peak periods (fondue, Christmas, ski).
"""
from __future__ import annotations

from datetime import date
from typing import Dict, Optional


class SwissHolidayPricing:
    """Holiday surge pricing with caps per category."""

    SURGE_PRICING_RULES: Dict[str, Dict] = {
        "fondue_season": {"max_increase": 0.15, "categories": ["cheese", "fondue", "dairy"]},
        "christmas_peak": {"max_increase": 0.25, "categories": ["gifts", "chocolate"]},
        "ski_peak": {"max_increase": 0.20, "categories": ["ski_gear", "winter_clothing"]},
    }

    @staticmethod
    def _get_surge_category(today: date, category: str) -> Optional[str]:
        """Determine which surge rule applies for (date, category)."""
        if today.month >= 11 or today.month <= 2:
            if category in SwissHolidayPricing.SURGE_PRICING_RULES["fondue_season"]["categories"]:
                return "fondue_season"
        if today.month == 12 and today.day >= 20:
            if category in SwissHolidayPricing.SURGE_PRICING_RULES["christmas_peak"]["categories"]:
                return "christmas_peak"
        if 12 <= today.month or today.month <= 3:
            if category in SwissHolidayPricing.SURGE_PRICING_RULES["ski_peak"]["categories"]:
                return "ski_peak"
        return None

    @staticmethod
    def calculate_holiday_price(
        base_price: float, category: str, multiplier: float
    ) -> float:
        """Fondue cheese: CHF 28 -> CHF 32.20 (+15% holiday)."""
        today = date.today()
        surge_category = SwissHolidayPricing._get_surge_category(today, category)

        if surge_category:
            rule = SwissHolidayPricing.SURGE_PRICING_RULES[surge_category]
            max_increase = rule["max_increase"]
            surge = min(max(0, multiplier - 1.0), max_increase)
            return round(base_price * (1 + surge), 2)
        return round(base_price * multiplier, 2)
