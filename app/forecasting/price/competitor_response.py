"""CompetitorResponseAgent: game theory + Nash equilibrium price forecasting."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import numpy as np

from app.forecasting.models.ensemble import AgentForecast
from app.dynamic_pricing.competitor_response import CompetitorResponseAgent as NashSolver

logger = logging.getLogger(__name__)


class NashEquilibriumSolver:
    """Nash equilibrium solver for competitor response (wraps existing game-theory)."""

    def __init__(self):
        self._solver = NashSolver(n_competitors=3)

    def solve_nash(
        self,
        our_price_history: List[float],
        competitor_strategies: List[Dict],
        market_elasticity: float,
    ) -> Dict[str, Any]:
        """Predict equilibrium our_price and competitor_prices."""
        our_price = our_price_history[-1] if our_price_history else 35.0
        comp_prices = []
        for s in competitor_strategies[-3:]:
            p = s.get("price") or s.get("response_price") or our_price
            comp_prices.append(float(p))
        if not comp_prices:
            comp_prices = [our_price * 1.02, our_price * 0.98, our_price]
        nash = self._solver.predict_nash_prices(our_price, comp_prices, market_elasticity)
        suggested, metrics = self._solver.best_response(our_price, comp_prices, market_elasticity)
        return {
            "our_price": suggested,
            "competitor_prices": nash,
            "metrics": metrics,
        }


class CompetitorResponseAgent:
    """Game-theory competitor response forecasting over horizon."""

    def __init__(self):
        self.game_theory_model = NashEquilibriumSolver()
        self._qdrant = None

    def _get_qdrant(self):
        if self._qdrant is None:
            from app.qdrant.forecasting.client import PriceForecastClient
            self._qdrant = PriceForecastClient()
        return self._qdrant

    async def _get_current_price(self, sku: str, store_id: str) -> float:
        """Placeholder: would read from catalog or pricing service."""
        return 35.0 + (hash(sku) % 25)

    async def _get_competitor_prices(self, sku: str) -> List[float]:
        q = self._get_qdrant()
        hist = await q.get_competitor_prices(sku, days=7)
        if hist.size:
            return hist.tolist()[-5:]
        return [35.0, 36.0, 34.0]

    async def _get_elasticity(self, sku: str) -> float:
        return -1.5 + (hash(sku) % 10) / 100.0

    async def forecast(
        self,
        sku: str,
        store_id: str,
        horizon_days: int,
    ) -> AgentForecast:
        """Nash equilibrium forecast for each day."""
        competitor_strategies = await self._get_qdrant().get_historical_responses(sku)
        our_price = await self._get_current_price(sku, store_id)
        competitor_prices = await self._get_competitor_prices(sku)
        elasticity = await self._get_elasticity(sku)
        nash_forecasts = []
        equilibrium_points = []
        for _ in range(horizon_days):
            eq = self.game_theory_model.solve_nash(
                our_price_history=[our_price],
                competitor_strategies=competitor_strategies,
                market_elasticity=elasticity,
            )
            nash_forecasts.append(eq["our_price"])
            equilibrium_points.append(eq["competitor_prices"])
            our_price = eq["our_price"]
        return AgentForecast(
            agent="competitor_response",
            point_forecast=np.array(nash_forecasts),
            confidence=0.78,
            equilibrium_points=equilibrium_points,
        )
