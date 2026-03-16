"""Real warehouse capacity constraints for allocation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Optional

from app.inventory.capacity_planner import CapacityPlanner

logger = logging.getLogger(__name__)


@dataclass
class WarehouseConstraints:
    """Per-warehouse capacity and current usage."""
    warehouse_id: str
    max_units: float
    used_units: float
    reserved_units: float = 0.0

    @property
    def available(self) -> float:
        return max(0.0, self.max_units - self.used_units - self.reserved_units)


def apply_capacity_constraints(
    planner: CapacityPlanner,
    warehouse_id: str,
    requested_qty: float,
    sku: str = "",
) -> float:
    """Return allocated quantity respecting warehouse capacity."""
    plan = planner.optimize_allocation(sku, warehouse_id, requested_qty, priority=1.0)
    return plan.total_allocated
