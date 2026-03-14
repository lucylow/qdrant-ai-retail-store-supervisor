"""Fill rate and service level SLAs for inventory."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    from scipy.stats import norm

    _HAS_NORM = True
except ImportError:
    _HAS_NORM = False


@dataclass
class ServiceLevelMetrics:
    """Service level and fill rate."""
    target_sl: float
    achieved_sl: float
    fill_rate: float
    safety_stock: float


class ServiceLevelPolicy:
    """Compute safety stock for target service level (e.g. 95%)."""

    def __init__(self, target_service_level: float = 0.95):
        self.target_service_level = target_service_level

    def safety_stock(
        self,
        demand_std: float,
        lead_time_days: int = 7,
    ) -> float:
        """Safety stock for target service level (normal demand)."""
        if not _HAS_NORM:
            return demand_std * (lead_time_days ** 0.5) * 1.65
        z = norm.ppf(self.target_service_level)
        return float(z * demand_std * (lead_time_days ** 0.5))

    def reorder_point(
        self,
        demand_mean: float,
        demand_std: float,
        lead_time_days: int = 7,
    ) -> float:
        """Reorder point = lead-time demand + safety stock."""
        return demand_mean * lead_time_days + self.safety_stock(demand_std, lead_time_days)
