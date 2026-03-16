"""EventPredictorAgent: holiday + promo impact on price volatility."""

from __future__ import annotations

import logging
from datetime import datetime
import numpy as np
import pandas as pd

from app.forecasting.models.ensemble import AgentForecast

logger = logging.getLogger(__name__)

# Simplified holiday and promo calendar (month, day) -> uplift
HOLIDAY_UPLIFT = {
    (12, 25): 1.12,
    (12, 24): 1.08,
    (1, 1): 1.05,
    (11, 24): 1.10,
    (7, 4): 1.03,
    (2, 14): 1.04,
}
# Black Friday week
PROMO_WEEKS = [(11, 4), (11, 5)]  # week of Black Friday


class EventPredictorAgent:
    """Holiday + promo events → price volatility and level shifts."""

    def __init__(self):
        self._base_price = 35.0

    def _event_multiplier(self, d: pd.Timestamp) -> float:
        """Multiplier for a given date from events."""
        m, day = d.month, d.day
        if (m, day) in HOLIDAY_UPLIFT:
            return HOLIDAY_UPLIFT[(m, day)]
        for (wm, wd) in PROMO_WEEKS:
            if m == wm and 20 <= day <= 30:
                return 1.07
        return 1.0

    async def forecast(
        self,
        sku: str,
        store_id: str,
        horizon_days: int,
    ) -> AgentForecast:
        """Event-adjusted price forecast (holidays + promos)."""
        base = self._base_price + (hash(sku) % 20)
        dates = pd.date_range(
            start=pd.Timestamp.utcnow().normalize(),
            periods=horizon_days,
            freq="D",
        )
        mults = np.array([self._event_multiplier(d) for d in dates])
        # Slight trend + event bumps
        trend = 1 + np.linspace(0, 0.02, horizon_days)
        point_forecast = base * mults * trend
        return AgentForecast(
            agent="events",
            point_forecast=point_forecast,
            confidence=0.82,
            components={"base": float(base), "event_peak": float(np.max(mults))},
        )
