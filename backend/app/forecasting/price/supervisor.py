"""PriceForecastSupervisor: ensemble orchestration + uncertainty + trading signals."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

import numpy as np
import pandas as pd

from app.forecasting.models.ensemble import AgentForecast, EnsembleForecast, StackingEnsemble
from app.forecasting.price.market_trend import MarketTrendAgent
from app.forecasting.price.seasonal import SeasonalForecasterAgent
from app.forecasting.price.events import EventPredictorAgent
from app.forecasting.price.competitor_response import CompetitorResponseAgent
from app.forecasting.price.elasticity import ElasticityForecasterAgent
from app.forecasting.price.anomaly import AnomalyDetectorAgent
from app.qdrant.forecasting.client import PriceForecastClient

logger = logging.getLogger(__name__)


@dataclass
class PriceForecast:
    """Full multi-agent price forecast output."""
    sku: str
    forecast_horizon: pd.DatetimeIndex
    point_forecast: pd.Series
    confidence_intervals: pd.DataFrame
    ensemble_weights: Dict[str, float]
    accuracy_score: float
    anomaly_probability: float
    recommended_action: str


class PriceForecastSupervisor:
    """Orchestrates 7 specialized agents + stacking ensemble + Qdrant RAG weights."""

    def __init__(self):
        self.agents = {
            "market_trend": MarketTrendAgent(),
            "seasonal": SeasonalForecasterAgent(),
            "events": EventPredictorAgent(),
            "competitor_response": CompetitorResponseAgent(),
            "elasticity": ElasticityForecasterAgent(),
            "anomaly": AnomalyDetectorAgent(),
        }
        self.ensemble = StackingEnsemble()
        self.qdrant = PriceForecastClient()

    def _get_trading_signal(self, ensemble_forecast: EnsembleForecast) -> str:
        """Derive trading signal from short-horizon trend."""
        point = ensemble_forecast.point
        if len(point) < 2:
            return "STABLE"
        first_week = point.iloc[: min(7, len(point))].mean()
        last_week = point.iloc[-min(7, len(point)) :].mean()
        if last_week > first_week * 1.02:
            return "RAISE_EXPECTED"
        if last_week < first_week * 0.98:
            return "LOWER_EXPECTED"
        return "STABLE"

    async def forecast_price(
        self,
        sku: str,
        store_id: str,
        horizon_days: int = 30,
    ) -> PriceForecast:
        """Full multi-agent price forecasting pipeline."""
        # 1. Parallel agent forecasting
        async def run_agent(name: str, agent):
            try:
                return await agent.forecast(sku, store_id, horizon_days)
            except Exception as e:  # noqa: BLE001
                logger.warning("Agent %s failed: %s", name, e)
                return None

        tasks = [run_agent(name, agent) for name, agent in self.agents.items()]
        results = await asyncio.gather(*tasks)
        agent_forecasts = [r for r in results if r is not None]

        # 2. Qdrant RAG: historical forecast accuracy weighting
        historical_weights = await self.qdrant.get_agent_accuracy_weights(sku)

        # 3. Dynamic ensemble (stacking with meta-learner)
        ensemble_forecast = self.ensemble.combine(
            forecasts=agent_forecasts,
            weights=historical_weights,
            horizon=horizon_days,
        )

        # 4. Anomaly detection post-processing
        anomaly_agent = self.agents["anomaly"]
        anomaly_score = anomaly_agent.detect_anomaly(ensemble_forecast)

        horizon_dt = pd.date_range(
            start=pd.Timestamp.utcnow().normalize(),
            periods=horizon_days,
            freq="D",
        )
        return PriceForecast(
            sku=sku,
            forecast_horizon=horizon_dt,
            point_forecast=ensemble_forecast.point,
            confidence_intervals=ensemble_forecast.confidence,
            ensemble_weights=ensemble_forecast.weights_used,
            accuracy_score=ensemble_forecast.mape,
            anomaly_probability=anomaly_score,
            recommended_action=self._get_trading_signal(ensemble_forecast),
        )
