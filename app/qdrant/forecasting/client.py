"""Qdrant client for price forecasting: historical accuracy, competitor prices, strategies."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.qdrant_client import get_qdrant_client
from app.qdrant.forecasting.collections import (
    COLL_FORECAST_ACCURACY,
    COLL_PRICE_HISTORY,
    COLL_COMPETITOR_STRATEGIES,
)
from app.data.collections import COLL_COMPETITOR_PRICES

logger = logging.getLogger(__name__)

VECTOR_SIZE = 768


def _embed_dummy(size: int = VECTOR_SIZE) -> List[float]:
    """Deterministic placeholder vector for scalar queries."""
    return (np.zeros(size) + 0.1).tolist()


class PriceForecastClient:
    """Read/write price history, forecast accuracy, and competitor strategies from Qdrant."""

    def __init__(self, client: Optional[QdrantClient] = None):
        self._client = client or get_qdrant_client()

    async def get_agent_accuracy_weights(self, sku: str) -> Dict[str, float]:
        """Return per-agent historical MAPE weights for ensemble (lower MAPE = higher weight)."""
        try:
            res = self._client.scroll(
                collection_name=COLL_FORECAST_ACCURACY,
                scroll_filter=rest.Filter(
                    must=[rest.FieldCondition(key="sku", match=rest.MatchValue(value=sku))]
                ),
                limit=50,
            )
            points, _ = res
            if not points:
                return {}
            # Default weights by agent (demo)
            default_mape = {"market_trend": 0.12, "seasonal": 0.09, "events": 0.15, "competitor_response": 0.18, "elasticity": 0.14, "anomaly": 0.20}
            weights = {}
            for p in points:
                payload = p.payload or {}
                agent = payload.get("agent")
                mape = payload.get("mape", default_mape.get(agent, 0.15))
                if agent:
                    weights[agent] = max(1e-6, 1.0 - mape)
            total = sum(weights.values()) or 1.0
            return {k: v / total for k, v in weights.items()}
        except Exception as e:  # noqa: BLE001
            logger.debug("get_agent_accuracy_weights: %s", e)
            return {
                "market_trend": 0.18, "seasonal": 0.20, "events": 0.14,
                "competitor_response": 0.15, "elasticity": 0.16, "anomaly": 0.17,
            }

    async def get_competitor_prices(self, sku: str, days: int = 90) -> np.ndarray:
        """Retrieve competitor price history for SKU from price_history or competitor_prices."""
        try:
            res = self._client.scroll(
                collection_name=COLL_PRICE_HISTORY,
                scroll_filter=rest.Filter(
                    must=[rest.FieldCondition(key="sku", match=rest.MatchValue(value=sku))]
                ),
                limit=500,
            )
            points, _ = res
            if points:
                prices = [p.payload.get("price") for p in points if p.payload and p.payload.get("price") is not None]
                if prices:
                    return np.array(prices[-days:])
            # Fallback: competitor_prices collection
            res2 = self._client.scroll(
                collection_name=COLL_COMPETITOR_PRICES,
                limit=100,
            )
            points2, _ = res2
            prices = []
            for p in points2 or []:
                if p.payload and p.payload.get("sku") == sku:
                    prices.append(p.payload.get("price", 35.0))
            if prices:
                return np.array(prices[-days:] if len(prices) >= days else prices)
            return np.full(min(90, days), 35.0 + np.random.randn() * 2)
        except Exception as e:  # noqa: BLE001
            logger.debug("get_competitor_prices: %s", e)
            return np.full(min(90, days), 35.0)

    async def get_historical_responses(self, sku: str) -> List[Dict]:
        """Competitor strategies / response history for game-theory agent."""
        try:
            res = self._client.scroll(
                collection_name=COLL_COMPETITOR_STRATEGIES,
                scroll_filter=rest.Filter(
                    must=[rest.FieldCondition(key="sku", match=rest.MatchValue(value=sku))]
                ),
                limit=100,
            )
            points, _ = res
            return [p.payload or {} for p in points]
        except Exception as e:  # noqa: BLE001
            logger.debug("get_historical_responses: %s", e)
            return []

    def record_forecast_accuracy(self, sku: str, agent: str, mape: float) -> None:
        """Record agent MAPE for future weight tuning."""
        try:
            vec = _embed_dummy()
            self._client.upsert(
                collection_name=COLL_FORECAST_ACCURACY,
                points=[
                    rest.PointStruct(
                        id=f"{sku}_{agent}_{datetime.utcnow().timestamp()}",
                        vector=vec,
                        payload={"sku": sku, "agent": agent, "mape": mape, "timestamp": datetime.utcnow().timestamp()},
                    )
                ],
            )
        except Exception as e:  # noqa: BLE001
            logger.debug("record_forecast_accuracy: %s", e)
