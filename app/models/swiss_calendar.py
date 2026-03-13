"""
Complete Swiss retail calendar: national/cantonal holidays and seasonal periods.
"""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class SwissHolidayType(Enum):
    NATIONAL = "national"  # Aug 1st
    CANTONAL = "cantonal"  # Varies by canton
    RETAIL_PEAK = "retail_peak"  # Christmas, Easter
    SEASONAL_START = "seasonal"  # Fondue, Ski


class DemandMultiplier(Enum):
    LOW = 1.0
    MODERATE = 1.5
    HIGH = 2.5
    EXTREME = 4.0


class SwissHoliday(BaseModel):
    name: str
    date: date
    type: SwissHolidayType
    demand_multiplier: DemandMultiplier
    affected_categories: List[str]
    cantons: Optional[List[str]] = None  # None = all Switzerland

    # Retail-specific impacts
    dynamic_pricing_allowed: bool = True
    auto_replenish_trigger: float = 2.0  # Reorder when stock < demand * 2


# Complete 2026 Swiss retail calendar (sample; extend per year)
SWISS_RETAIL_CALENDAR_2026: List[SwissHoliday] = [
    SwissHoliday(
        name="National Day",
        date=date(2026, 8, 1),
        type=SwissHolidayType.NATIONAL,
        demand_multiplier=DemandMultiplier.HIGH,
        affected_categories=["bbq", "fireworks", "drinks"],
    ),
    SwissHoliday(
        name="Christmas Peak",
        date=date(2026, 12, 24),
        type=SwissHolidayType.RETAIL_PEAK,
        demand_multiplier=DemandMultiplier.EXTREME,
        affected_categories=["gifts", "chocolate", "fondue", "wine"],
    ),
    SwissHoliday(
        name="Easter",
        date=date(2026, 4, 5),
        type=SwissHolidayType.RETAIL_PEAK,
        demand_multiplier=DemandMultiplier.HIGH,
        affected_categories=["chocolate", "bakery", "ham"],
    ),
    SwissHoliday(
        name="Fondue Season Start",
        date=date(2025, 11, 1),
        type=SwissHolidayType.SEASONAL_START,
        demand_multiplier=DemandMultiplier.MODERATE,
        affected_categories=["fondue", "cheese", "white_wine", "bread"],
    ),
    SwissHoliday(
        name="Ski Season Peak",
        date=date(2026, 2, 15),
        type=SwissHolidayType.SEASONAL_START,
        demand_multiplier=DemandMultiplier.HIGH,
        affected_categories=["ski_gear", "winter_clothing", "hot_chocolate"],
    ),
    SwissHoliday(
        name="ZH Sechseläuten",
        date=date(2026, 4, 18),
        type=SwissHolidayType.CANTONAL,
        demand_multiplier=DemandMultiplier.MODERATE,
        affected_categories=["bbq", "beer"],
        cantons=["ZH"],
    ),
]
