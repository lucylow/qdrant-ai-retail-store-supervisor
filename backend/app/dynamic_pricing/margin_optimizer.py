"""Cost-aware margin optimization with business constraints."""

from __future__ import annotations

import logging
from typing import List

import numpy as np

logger = logging.getLogger(__name__)

try:
    from scipy.optimize import minimize_scalar

    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False


class MarginOptimizer:
    """Optimize price within margin constraints and elasticity."""

    def __init__(self, min_margin_pct: float = 0.25):
        self.min_margin_pct = min_margin_pct
        self.cost_structure = _CostStructure()

    def _predict_demand(
        self, price: float, elasticity: float, inventory: float
    ) -> float:
        """Demand = base * (price / ref_price)^elasticity, capped by inventory."""
        ref_price = 35.0
        base_demand = 100.0
        demand = base_demand * (price / ref_price) ** elasticity
        return min(max(demand, 1.0), inventory)

    def _get_cost(self) -> float:
        return self.cost_structure.get_cost("average")

    def optimize(
        self,
        base_price: float,
        elasticity: float,
        inventory: float,
        competitor_prices: List[float],
    ) -> float:
        """Optimize price within margin constraints and elasticity."""
        cost = self._get_cost()

        def revenue(price: float) -> float:
            demand = self._predict_demand(price, elasticity, inventory)
            return price * demand

        def valid_margin(price: float) -> bool:
            if price <= 0:
                return False
            return (price - cost) / price >= self.min_margin_pct

        low = min(competitor_prices) * 0.85 if competitor_prices else base_price * 0.85
        high = max(competitor_prices) * 1.15 if competitor_prices else base_price * 1.15
        low = max(low, cost / (1 - self.min_margin_pct))
        bounds = (low, high)

        if _HAS_SCIPY:
            try:
                result = minimize_scalar(
                    lambda p: -revenue(p),
                    bounds=bounds,
                    method="bounded",
                )
                optimal = float(result.x)
                if valid_margin(optimal):
                    return round(optimal, 2)
            except Exception as e:
                logger.warning("Scipy optimize failed: %s", e)

        # Grid fallback
        best_price = base_price
        best_rev = revenue(base_price)
        for p in np.linspace(bounds[0], bounds[1], 50):
            if valid_margin(p):
                r = revenue(p)
                if r > best_rev:
                    best_rev = r
                    best_price = p
        return round(float(best_price), 2)


class _CostStructure:
    """Simple cost lookup (expand with real data)."""

    def __init__(self):
        self._costs = {"average": 22.0, "tshirt": 12.0, "jeans": 28.0, "dress": 35.0}

    def get_cost(self, key: str = "average") -> float:
        return self._costs.get(key, self._costs["average"])
