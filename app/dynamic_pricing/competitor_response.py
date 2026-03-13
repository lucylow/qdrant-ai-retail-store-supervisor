"""Game-theory competitor response and Nash equilibrium prediction."""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class CompetitorResponseAgent:
    """Predict competitor response using simplified game-theory (Nash-style)."""

    def __init__(self, n_competitors: int = 3):
        self.n_competitors = n_competitors

    def predict_nash_prices(
        self,
        our_price: float,
        competitor_prices: List[float],
        demand_elasticity: float,
    ) -> List[float]:
        """Predict competitor prices at Nash equilibrium (best-response)."""
        if not competitor_prices:
            return [our_price] * self.n_competitors
        avg = float(np.mean(competitor_prices))
        # Simplified: competitors move toward market average and our signal
        weight_ours = 0.3
        weight_avg = 0.7
        target = weight_ours * our_price + weight_avg * avg
        return [target + np.random.randn() * 0.5 for _ in competitor_prices]

    def best_response(
        self,
        our_price: float,
        competitor_prices: List[float],
        elasticity: float,
    ) -> Tuple[float, Dict[str, float]]:
        """Our best response given competitor prices; return (price, metrics)."""
        nash = self.predict_nash_prices(our_price, competitor_prices, elasticity)
        suggested = float(np.median(nash)) * 0.98  # slightly undercut
        return suggested, {"nash_avg": float(np.mean(nash)), "our_suggested": suggested}
