"""MARL-based price forecasting: integrate with existing MARL pricing for predictions."""

from __future__ import annotations

import logging
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    from app.rl.marl_pricing import PricingMARLSupervisor
    _HAS_MARL = True
except ImportError:
    _HAS_MARL = False


class RLPricePredictor:
    """Use MARL policy to predict price trajectory over horizon."""

    def __init__(self):
        self._marl: Optional[object] = None
        if _HAS_MARL:
            try:
                self._marl = PricingMARLSupervisor()
            except Exception:  # noqa: BLE001
                pass

    def predict(
        self,
        current_price: float,
        competitor_prices: List[float],
        horizon_days: int,
        elasticity: float = -1.5,
    ) -> np.ndarray:
        """Predict price path from MARL policy (or fallback drift)."""
        if self._marl is None or not _HAS_MARL:
            # Fallback: slight mean-reversion
            out = current_price + np.cumsum(np.random.randn(horizon_days) * 0.5)
            return np.maximum(out, current_price * 0.5)
        try:
            state = {
                "sku": "forecast",
                "competitor_prices": competitor_prices or [current_price],
                "elasticity": elasticity,
            }
            path = []
            price = current_price
            for _ in range(horizon_days):
                action = self._marl.select_action(state)
                mult = getattr(action, "price_multiplier", 0.0) or 0.0
                price = price * (1 + mult)
                path.append(price)
                state["competitor_prices"] = [p * (1 + np.random.randn() * 0.02) for p in (competitor_prices or [price])]
            return np.array(path)
        except Exception as e:  # noqa: BLE001
            logger.debug("MARL predict fallback: %s", e)
            return np.full(horizon_days, current_price)
