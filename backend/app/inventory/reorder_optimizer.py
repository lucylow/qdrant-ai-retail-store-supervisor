"""EOQ and supplier lead-time optimization."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ReorderRecommendation:
    """Single reorder recommendation."""
    optimal_qty: float
    supplier: str
    lead_time_days: int
    total_cost: float
    arrival_date: datetime


class ReorderOptimizer:
    """Economic Order Quantity and multi-supplier selection."""

    def __init__(self):
        self.supplier_data = self._load_supplier_database()

    def _load_supplier_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """Per-SKU supplier options (demo data)."""
        base = [
            {"id": "sup_a", "unit_price": 28.0, "lead_time_days": 5, "reliability": 0.95},
            {"id": "sup_b", "unit_price": 26.0, "lead_time_days": 10, "reliability": 0.88},
            {"id": "sup_c", "unit_price": 30.0, "lead_time_days": 3, "reliability": 0.98},
        ]
        return {"default": base, "tshirt": base, "jeans": base, "dress": base}

    def compute_eoq(
        self,
        annual_demand: float,
        ordering_cost: float = 25.0,
        holding_cost_pct: float = 0.20,
        avg_unit_cost: float = 30.0,
    ) -> float:
        """Economic Order Quantity."""
        if annual_demand <= 0:
            return 100.0
        holding_cost = avg_unit_cost * holding_cost_pct
        if holding_cost <= 0:
            return max(annual_demand / 12, 50.0)
        eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
        return float(max(round(eoq), 1))

    def select_supplier(
        self, sku: str, required_qty: float
    ) -> Dict[str, Any]:
        """Best supplier by price + lead time + reliability."""
        suppliers = self.supplier_data.get(
            "tshirt" if "tshirt" in sku.lower() else "jeans" if "jeans" in sku.lower() else "default",
            self.supplier_data["default"],
        )
        def score(s: Dict[str, Any]) -> float:
            return (
                s["unit_price"] * required_qty
                + s["lead_time_days"] * 5.0
                + (1 - s["reliability"]) * 100.0
            )
        best = min(suppliers, key=score)
        return best

    def recommend(
        self,
        sku: str,
        annual_demand: float,
        ordering_cost: float = 25.0,
        holding_cost_pct: float = 0.20,
    ) -> ReorderRecommendation:
        """EOQ + supplier selection and arrival date."""
        unit_cost = 30.0
        eoq = self.compute_eoq(
            annual_demand,
            ordering_cost=ordering_cost,
            holding_cost_pct=holding_cost_pct,
            avg_unit_cost=unit_cost,
        )
        supplier = self.select_supplier(sku, eoq)
        lead = supplier["lead_time_days"]
        total_cost = supplier["unit_price"] * eoq
        arrival = datetime.utcnow() + timedelta(days=lead)
        return ReorderRecommendation(
            optimal_qty=eoq,
            supplier=supplier["id"],
            lead_time_days=lead,
            total_cost=total_cost,
            arrival_date=arrival,
        )
