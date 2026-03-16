"""Warehouse constraints and allocation optimization."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AllocationPlan:
    """Per-SKU allocation across warehouses."""
    sku: str
    warehouse_allocations: Dict[str, float]
    total_allocated: float
    capacity_utilization: float


class CapacityPlanner:
    """Warehouse capacity constraints and allocation optimization."""

    def __init__(self, max_capacity_per_warehouse: float = 10000.0):
        self.max_capacity_per_warehouse = max_capacity_per_warehouse
        self._warehouse_used: Dict[str, float] = {}

    def set_warehouse_used(self, warehouse_id: str, used: float) -> None:
        self._warehouse_used[warehouse_id] = used

    def available_capacity(self, warehouse_id: str) -> float:
        return max(
            0.0,
            self.max_capacity_per_warehouse - self._warehouse_used.get(warehouse_id, 0.0),
        )

    def optimize_allocation(
        self,
        sku: str,
        warehouse_id: str,
        requested_qty: float,
        priority: float = 1.0,
    ) -> AllocationPlan:
        """Allocate quantity subject to warehouse capacity."""
        available = self.available_capacity(warehouse_id)
        allocated = min(requested_qty, available, requested_qty * priority)
        allocated = max(0.0, allocated)
        self._warehouse_used[warehouse_id] = (
            self._warehouse_used.get(warehouse_id, 0.0) + allocated
        )
        util = (
            self._warehouse_used[warehouse_id] / self.max_capacity_per_warehouse
            if self.max_capacity_per_warehouse > 0
            else 0.0
        )
        return AllocationPlan(
            sku=sku,
            warehouse_allocations={warehouse_id: allocated},
            total_allocated=allocated,
            capacity_utilization=util,
        )
