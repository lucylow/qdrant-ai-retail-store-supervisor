"""Newsvendor (single-period) model for inventory under uncertainty."""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class NewsboyModel:
    """Single-period optimal order quantity: balance overage vs underage cost."""

    def __init__(
        self,
        unit_cost: float = 30.0,
        selling_price: float = 45.0,
        salvage_value: float = 15.0,
    ):
        self.unit_cost = unit_cost
        self.selling_price = selling_price
        self.salvage_value = salvage_value

    def critical_ratio(self) -> float:
        """Cu / (Cu + Co); optimal order up to this fractile of demand."""
        cu = self.selling_price - self.unit_cost
        co = self.unit_cost - self.salvage_value
        if cu + co <= 0:
            return 0.5
        return cu / (cu + co)

    def optimal_order(
        self,
        demand_mean: float,
        demand_std: Optional[float] = None,
    ) -> float:
        """Order quantity for normal demand (or mean if no std)."""
        cr = self.critical_ratio()
        if demand_std is None or demand_std <= 0:
            return max(1, demand_mean * (0.8 + cr * 0.4))
        try:
            from scipy.stats import norm

            z = norm.ppf(cr)
            return float(max(1, demand_mean + z * demand_std))
        except ImportError:
            return max(1, demand_mean * (0.8 + cr * 0.4))
