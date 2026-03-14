"""ML stockout probability and urgency scoring."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

try:
    from sklearn.ensemble import RandomForestClassifier

    _HAS_RF = True
except ImportError:
    _HAS_RF = False


@dataclass
class StockoutPrediction:
    """Stockout risk and urgency."""
    probability: float
    days_to_stockout: float
    urgency_score: float
    confidence: float


class StockoutPredictor:
    """Predict stockout probability within 7 days."""

    def __init__(self):
        self.model = None
        if _HAS_RF:
            try:
                self.model = RandomForestClassifier(n_estimators=100)
                # Fit on synthetic data for demo
                X = np.random.rand(200, 6).astype(np.float32)
                y = (X[:, 0] * X[:, 1] < 0.3).astype(int)
                self.model.fit(X, y)
            except Exception as e:
                logger.warning("Stockout RF fit failed: %s", e)
                self.model = None

    def _compute_inventory_velocity(self, sku: str) -> float:
        """Placeholder: units per day."""
        return 15.0 + (hash(sku) % 10)

    def _get_supplier_score(self, sku: str) -> float:
        """Placeholder: 0-1 reliability."""
        return 0.85 + (hash(sku) % 15) / 100.0

    def _extract_stockout_features(
        self,
        sku: str,
        current_stock: float,
        demand_forecast: pd.Series,
        inventory_velocity: float,
        supplier_reliability: float,
    ) -> np.ndarray:
        """Feature vector for stockout model."""
        mean_demand = demand_forecast.mean() if len(demand_forecast) else 1.0
        days_cover = current_stock / mean_demand if mean_demand > 0 else 999.0
        features = np.array([
            current_stock / 200.0,
            mean_demand / 100.0,
            min(days_cover / 14.0, 1.0),
            inventory_velocity / 30.0,
            supplier_reliability,
            1.0 if days_cover < 7 else 0.0,
        ], dtype=np.float32).reshape(1, -1)
        return features

    def predict_stockout(
        self,
        sku: str,
        current_stock: float,
        demand_forecast: pd.Series,
    ) -> StockoutPrediction:
        """ML prediction of stockout probability within 7 days."""
        mean_demand = demand_forecast.mean() if len(demand_forecast) else 1.0
        days_to_stockout = (
            current_stock / mean_demand if mean_demand > 0 else float("inf")
        )
        features = self._extract_stockout_features(
            sku=sku,
            current_stock=current_stock,
            demand_forecast=demand_forecast,
            inventory_velocity=self._compute_inventory_velocity(sku),
            supplier_reliability=self._get_supplier_score(sku),
        )
        if self.model is not None:
            try:
                prob_7d = float(self.model.predict_proba(features)[0, 1])
            except Exception:
                prob_7d = 0.5
        else:
            # Rule-based fallback
            prob_7d = 0.9 if days_to_stockout < 3 else (0.5 if days_to_stockout < 7 else 0.1)
        urgency = min(
            1.0,
            prob_7d * (7.0 / max(days_to_stockout, 0.5)),
        )
        return StockoutPrediction(
            probability=prob_7d,
            days_to_stockout=days_to_stockout if np.isfinite(days_to_stockout) else 999.0,
            urgency_score=urgency,
            confidence=0.92,
        )
