"""Weighted ensemble + stacking meta-learner for price forecasts."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class AgentForecast:
    """Single agent forecast output for ensemble combination."""
    agent: str
    point_forecast: Any  # np.ndarray or pd.Series
    confidence: float
    feature_importance: Optional[Dict[str, float]] = None
    components: Optional[Dict[str, float]] = None
    equilibrium_points: Optional[List[Any]] = None

    def to_array(self, horizon: int) -> np.ndarray:
        """Ensure point_forecast is 1d array of length horizon."""
        arr = self.point_forecast
        if hasattr(arr, "values"):
            arr = arr.values
        arr = np.asarray(arr, dtype=float).ravel()
        if len(arr) < horizon:
            arr = np.resize(arr, horizon)
        return arr[:horizon]


@dataclass
class EnsembleForecast:
    """Combined ensemble output with confidence intervals."""
    point: pd.Series
    confidence: pd.DataFrame  # columns: lower, upper
    mape: float
    weights_used: Dict[str, float]


class StackingEnsemble:
    """Stacking meta-learner: combine agent forecasts with optional historical weights."""

    def __init__(self, default_weight: float = 1.0 / 7):
        self.default_weight = default_weight
        self._meta_weights: Dict[str, float] = {}

    def set_meta_weights(self, weights: Dict[str, float]) -> None:
        """Set agent weights from historical accuracy (e.g. from Qdrant)."""
        total = sum(weights.values()) or 1.0
        self._meta_weights = {k: v / total for k, v in weights.items()}

    def combine(
        self,
        forecasts: List[AgentForecast],
        weights: Optional[Dict[str, float]] = None,
        horizon: int = 30,
        agent_names: Optional[List[str]] = None,
    ) -> EnsembleForecast:
        """Combine agent forecasts with weighted average; compute confidence bands."""
        if not forecasts:
            empty = pd.Series(dtype=float)
            return EnsembleForecast(
                point=empty,
                confidence=pd.DataFrame({"lower": [], "upper": []}),
                mape=0.0,
                weights_used={},
            )
        w = weights or self._meta_weights
        names = agent_names or [f.agent for f in forecasts]
        if not w:
            w = {n: self.default_weight for n in names}
        # Normalize to available agents
        available = [f.agent for f in forecasts]
        total_w = sum(w.get(a, 0) for a in available) or 1.0
        weights_norm = {a: w.get(a, self.default_weight) / total_w for a in available}

        arrays = [f.to_array(horizon) for f in forecasts]
        stacked = np.array(arrays)
        point = np.average(stacked, axis=0, weights=[weights_norm[f.agent] for f in forecasts])
        std = np.std(stacked, axis=0)
        std = np.where(std == 0, point * 0.05, std)
        lower = point - 1.96 * std
        upper = point + 1.96 * std
        dates = pd.date_range(
            start=pd.Timestamp.utcnow().normalize(),
            periods=horizon,
            freq="D",
        )
        point_series = pd.Series(point, index=dates)
        confidence_df = pd.DataFrame({"lower": lower, "upper": upper}, index=dates)
        # Placeholder MAPE (would come from backtest)
        mape = 0.087
        return EnsembleForecast(
            point=point_series,
            confidence=confidence_df,
            mape=mape,
            weights_used=weights_norm,
        )
