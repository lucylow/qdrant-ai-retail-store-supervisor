"""
Holiday-aware demand forecasting and safety stock for Swiss retail.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List, Optional

from app.models.swiss_calendar import (
    SWISS_RETAIL_CALENDAR_2026,
    SwissHoliday,
    SwissHolidayType,
    DemandMultiplier,
)


class SwissHolidayInventory:
    """Dynamic demand forecasting based on Swiss retail calendar."""

    @staticmethod
    def get_demand_multiplier(
        today: date, category: str, canton: str = "ZH"
    ) -> float:
        """Calculate holiday demand surge for a specific category."""
        multiplier = 1.0

        for holiday in SWISS_RETAIL_CALENDAR_2026:
            if SwissHolidayInventory._is_active_period(today, holiday):
                if category in holiday.affected_categories and (
                    holiday.cantons is None or canton in holiday.cantons
                ):
                    mult_val = (
                        holiday.demand_multiplier.value
                        if hasattr(holiday.demand_multiplier, "value")
                        else float(holiday.demand_multiplier)
                    )
                    multiplier *= mult_val

        seasonal = SwissHolidayInventory._get_seasonal_multipliers(today)
        multiplier *= seasonal.get(category, 1.0)

        return round(multiplier, 2)

    @staticmethod
    def _is_active_period(today: date, holiday: SwissHoliday) -> bool:
        """Check if holiday period affects today."""
        if holiday.type != SwissHolidayType.SEASONAL_START:
            return today == holiday.date
        # Multi-week seasonal (e.g. Fondue Nov–Feb)
        end_date = holiday.date + timedelta(days=120)
        return holiday.date <= today <= end_date

    @staticmethod
    def _get_seasonal_multipliers(today: date) -> Dict[str, float]:
        """Fondue season = 1.5x cheese, Ski season = 2.0x goggles."""
        multipliers: Dict[str, float] = {}
        if today.month >= 11 or today.month <= 2:  # Fondue season
            multipliers.update({
                "cheese": 1.5,
                "fondue": 2.0,
                "white_wine": 1.3,
                "bread": 1.2,
                "dairy": 1.3,
            })
        if 12 <= today.month or today.month <= 3:  # Ski season
            multipliers.update({
                "ski_gear": 2.0,
                "goggles": 1.8,
                "gloves": 1.6,
                "base_layer": 1.4,
                "winter_clothing": 1.6,
                "hot_chocolate": 1.4,
            })
        return multipliers

    @staticmethod
    def calculate_safety_stock(
        base_stock: int, category: str, canton: str = "ZH"
    ) -> int:
        """Christmas dairy = 4x safety stock."""
        today = date.today()
        multiplier = SwissHolidayInventory.get_demand_multiplier(
            today, category, canton
        )
        return max(int(base_stock * multiplier), base_stock * 2)

    @staticmethod
    def get_active_periods(
        today: date, category: Optional[str] = None
    ) -> List[Dict]:
        """Return active holiday/seasonal periods for the date (optional category filter)."""
        active: List[Dict] = []
        for holiday in SWISS_RETAIL_CALENDAR_2026:
            if SwissHolidayInventory._is_active_period(today, holiday):
                if category is None or category in holiday.affected_categories:
                    active.append({
                        "name": holiday.name,
                        "type": holiday.type.value,
                        "demand_multiplier": (
                            holiday.demand_multiplier.value
                            if hasattr(holiday.demand_multiplier, "value")
                            else float(holiday.demand_multiplier)
                        ),
                    })
        seasonal = SwissHolidayInventory._get_seasonal_multipliers(today)
        if category and category in seasonal:
            active.append({
                "name": "seasonal",
                "type": "seasonal",
                "demand_multiplier": seasonal[category],
            })
        return active

    @staticmethod
    def get_all_multipliers(today: date) -> Dict[str, float]:
        """Current seasonal multipliers by category."""
        return SwissHolidayInventory._get_seasonal_multipliers(today)
