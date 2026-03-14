"""MarketTrendAgent: competitor trends + macroeconomic signals."""

from __future__ import annotations

import logging
from typing import Dict

import numpy as np

from app.forecasting.models.ensemble import AgentForecast
from app.forecasting.models.transformer import TransformerForecaster
from app.data.pricing.market_signals import MarketSignalsPipeline

logger = logging.getLogger(__name__)


class MacroEconomicSignals:
    """Macro signals for forecasting (inflation, consumer confidence)."""

    def __init__(self):
        self._pipeline = MarketSignalsPipeline()

    async def get_current_signals(self) -> Dict[str, float]:
        """Current macro features (demo: from pipeline)."""
        signals = self._pipeline.fetch_signals("global")
        return self._pipeline.to_features(signals)


class MarketTrendAgent:
    """Competitor trends + macroeconomic forecasting via transformer."""

    def __init__(self):
        self.trend_model = TransformerForecaster()
        self.macro_signals = MacroEconomicSignals()
        self._qdrant = None

    def _get_qdrant(self):
        if self._qdrant is None:
            from app.qdrant.forecasting.client import PriceForecastClient
            self._qdrant = PriceForecastClient()
        return self._qdrant

    def _build_trend_features(
        self,
        competitor_history: np.ndarray,
        macro_features: Dict[str, float],
    ) -> np.ndarray:
        return self.trend_model._build_features(competitor_history, macro_features)

    async def forecast(
        self,
        sku: str,
        store_id: str,
        horizon_days: int,
    ) -> AgentForecast:
        """Competitor trends + macroeconomic forecasting."""
        qdrant = self._get_qdrant()
        competitor_history = await qdrant.get_competitor_prices(sku, days=90)
        macro_features = await self.macro_signals.get_current_signals()
        features = self._build_trend_features(competitor_history, macro_features)
        trend_forecast = self.trend_model.predict(features, horizon_days)
        return AgentForecast(
            agent="market_trend",
            point_forecast=trend_forecast,
            confidence=0.87,
            feature_importance=self.trend_model.get_importance(),
        )
