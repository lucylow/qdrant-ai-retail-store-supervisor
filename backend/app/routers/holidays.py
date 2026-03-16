"""
Swiss holiday APIs: demand forecast, active periods, seasonal multipliers.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict

from fastapi import APIRouter

from app.services.holiday_inventory import SwissHolidayInventory

router = APIRouter(prefix="/holidays", tags=["swiss-holidays"])


@router.get("/demand-forecast")
async def get_demand_forecast(
    category: str,
    canton: str = "ZH",
    days: int = 7,
) -> Dict[str, Any]:
    """Forecast demand for next N days (e.g. Christmas = 4x cheese)."""
    today = date.today()
    forecast: Dict[str, str] = {}
    for i in range(days):
        d = today + timedelta(days=i)
        mult = SwissHolidayInventory.get_demand_multiplier(d, category, canton)
        forecast[d.isoformat()] = str(mult)
    return forecast


@router.get("/active-periods")
async def get_active_periods() -> Dict[str, Any]:
    """Fondue season? Ski peak? Returns active multipliers."""
    today = date.today()
    return {
        "date": today.isoformat(),
        "active_holidays": SwissHolidayInventory.get_active_periods(today),
        "current_multipliers": SwissHolidayInventory.get_all_multipliers(today),
    }
