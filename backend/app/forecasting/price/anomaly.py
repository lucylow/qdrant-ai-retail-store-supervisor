"""AnomalyDetectorAgent: outlier detection + market shock probability."""

from __future__ import annotations

import logging
from typing import Any, Union

import numpy as np
import pandas as pd

from app.forecasting.models.ensemble import AgentForecast, EnsembleForecast

logger = logging.getLogger(__name__)


class AnomalyDetectorAgent:
    """Detect anomalies in ensemble forecast (volatility spikes, level shifts)."""

    def __init__(self, z_threshold: float = 3.0):
        self.z_threshold = z_threshold

    def detect_anomaly(
        self,
        ensemble_forecast: Union[EnsembleForecast, np.ndarray],
    ) -> float:
        """Return anomaly probability in [0, 1] (higher = more anomalous)."""
        if isinstance(ensemble_forecast, np.ndarray):
            series = pd.Series(ensemble_forecast.ravel())
        else:
            series = ensemble_forecast.point
        if len(series) < 2:
            return 0.0
        returns = series.pct_change().dropna()
        if returns.empty:
            return 0.0
        vol = returns.std()
        if vol == 0:
            return 0.0
        z = np.abs(returns).max() / vol
        # Map z to probability
        prob = 1.0 - np.exp(-z / self.z_threshold)
        return float(np.clip(prob, 0.0, 1.0))

    async def forecast(
        self,
        sku: str,
        store_id: str,
        horizon_days: int,
    ) -> AgentForecast:
        """Anomaly agent contributes a 'stability' forecast (mean-reverting)."""
        base = 35.0 + (hash(sku) % 25)
        # Mean-reverting path
        np.random.seed(hash(sku) % 2**32)
        path = base + np.cumsum(np.random.randn(horizon_days) * 0.3)
        path = np.maximum(path, base * 0.6)
        return AgentForecast(
            agent="anomaly",
            point_forecast=path,
            confidence=0.75,
            components={"base": base},
        )
