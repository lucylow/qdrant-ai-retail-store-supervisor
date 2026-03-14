"""ElasticityForecasterAgent: dynamic demand elasticity evolution."""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np

from app.forecasting.models.ensemble import AgentForecast
from app.dynamic_pricing.demand_elasticity import DemandElasticityModel

logger = logging.getLogger(__name__)


class ElasticityForecasterAgent:
    """Forecast price path from evolving demand elasticity curves."""

    def __init__(self):
        self.demand_model = DemandElasticityModel()
        self._qdrant = None

    def _get_qdrant(self):
        if self._qdrant is None:
            from app.qdrant.forecasting.client import PriceForecastClient
            self._qdrant = PriceForecastClient()
        return self._qdrant

    async def forecast(
        self,
        sku: str,
        store_id: str,
        horizon_days: int,
    ) -> AgentForecast:
        """Price forecast from dynamic elasticity (revenue-optimal path)."""
        base_price = 35.0 + (hash(sku) % 25)
        competitor_history = await self._get_qdrant().get_competitor_prices(sku, days=30)
        comp_avg = float(np.mean(competitor_history)) if competitor_history.size else base_price
        # Elasticity over time (e.g. more elastic post-promo)
        elasticity_path = -1.5 - 0.02 * np.arange(horizon_days)
        # Simple optimal price from elasticity: P* proportional to comp and elasticity
        point_forecast = base_price * (1 + 0.01 * np.arange(horizon_days))
        for i in range(horizon_days):
            e = elasticity_path[i]
            if e < -1:
                point_forecast[i] = base_price * (1 + 0.005 * i) * (comp_avg / base_price) ** 0.3
        point_forecast = np.maximum(point_forecast, base_price * 0.5)
        return AgentForecast(
            agent="elasticity",
            point_forecast=point_forecast,
            confidence=0.85,
            components={"base": base_price, "elasticity_mean": float(np.mean(elasticity_path))},
        )
