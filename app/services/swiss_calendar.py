"""
Cultural events impact on pricing and inventory (fondue season, ski, holidays).
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Dict


class SwissCulturalCalendar:
    """Swiss holiday and seasonal logic for demand/price boosts."""

    HOLIDAYS: Dict[str, Dict] = {
        "national_day": {"date": "2026-08-01", "impact": "high_demand"},
        "fondue_season": {"start": "2025-11-01", "end": "2026-02-28", "boost": 1.5},
        "ski_season": {"start": "2025-12-01", "end": "2026-04-15", "boost": 1.8},
        "easter": {"date": "2026-04-05", "chocolate_boost": 2.0},
        "zh_carnival": {"canton": "ZH", "date": "2026-02-16", "impact": "bakery_surge"},
        "ge_escalade": {"canton": "GE", "date": "2025-12-11", "impact": "fondue_peak"},
    }

    @staticmethod
    def get_seasonal_boost(today: date, retailer: str) -> float:
        """Fondue season = 50% price boost, ski gear = 80% demand surge."""
        if SwissCulturalCalendar.is_fondue_season(today):
            return 1.5 if retailer in ["coop", "migros"] else 1.2
        return 1.0

    @staticmethod
    def is_fondue_season(today: date) -> bool:
        """Nov–Feb peak (month 11, 12, 1, 2)."""
        return today.month >= 11 or today.month <= 2
