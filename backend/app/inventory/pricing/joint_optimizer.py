"""Revenue + holding cost joint optimization."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    from scipy.optimize import minimize_scalar

    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False


@dataclass
class JointRecommendation:
    """Price and order quantity from joint optimization."""
    price: float
    order_qty: float
    expected_revenue: float
    holding_cost: float
    net_profit: float


class JointPricingInventoryOptimizer:
    """Optimize price and order quantity jointly (revenue - holding cost)."""

    def __init__(
        self,
        holding_cost_pct: float = 0.20,
        unit_cost: float = 30.0,
    ):
        self.holding_cost_pct = holding_cost_pct
        self.unit_cost = unit_cost

    def expected_demand(self, price: float, ref_price: float = 35.0, elasticity: float = -1.5) -> float:
        return 100.0 * (price / ref_price) ** elasticity

    def optimize(
        self,
        ref_price: float = 35.0,
        elasticity: float = -1.5,
        max_price: float = 50.0,
        min_price: float = 20.0,
    ) -> JointRecommendation:
        """Maximize revenue - holding cost over price and implied demand."""
        def neg_profit(price: float) -> float:
            demand = self.expected_demand(price, ref_price, elasticity)
            revenue = price * demand
            holding = self.unit_cost * demand * self.holding_cost_pct * 0.25  # ~quarter turn
            return -(revenue - holding)

        if _HAS_SCIPY:
            try:
                res = minimize_scalar(
                    neg_profit,
                    bounds=(min_price, max_price),
                    method="bounded",
                )
                price_opt = float(res.x)
            except Exception:
                price_opt = ref_price * 0.98
        else:
            price_opt = ref_price * 0.98

        demand = self.expected_demand(price_opt, ref_price, elasticity)
        revenue = price_opt * demand
        holding = self.unit_cost * demand * self.holding_cost_pct * 0.25
        return JointRecommendation(
            price=price_opt,
            order_qty=max(1, demand),
            expected_revenue=revenue,
            holding_cost=holding,
            net_profit=revenue - holding,
        )
