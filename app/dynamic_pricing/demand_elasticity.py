"""Real-time demand elasticity modeling (XGBoost + historical patterns)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import numpy as np

from app.dynamic_pricing.pricing_models import load_elasticity_model

logger = logging.getLogger(__name__)

# Category-level base elasticity (typical ranges)
_CATEGORY_ELASTICITY: dict[str, float] = {
    "apparel": -1.8,
    "electronics": -1.2,
    "groceries": -0.6,
    "default": -1.5,
}


class DemandElasticityModel:
    """Compute price elasticity using XGBoost ensemble + historical patterns."""

    def __init__(self, model_path: Path | None = None):
        self.xgb_model = load_elasticity_model(model_path)
        self.historical_data: dict[str, list[float]] = {}

    def _get_category_elasticity(self, sku: str) -> float:
        """Infer category from SKU prefix or key."""
        sku_lower = sku.lower()
        for cat, el in _CATEGORY_ELASTICITY.items():
            if cat != "default" and cat in sku_lower:
                return el
        return _CATEGORY_ELASTICITY["default"]

    def _get_market_position(self, sku: str) -> float:
        """Placeholder: 0 = low, 1 = high market position."""
        return 0.5

    def _build_elasticity_features(
        self,
        *,
        sku: str,
        competitor_prices: float,
        inventory_level: float,
        market_position: float,
    ) -> np.ndarray:
        """Feature vector for elasticity prediction (length 12)."""
        feature_vector = np.zeros(12, dtype=np.float32)
        feature_vector[0] = competitor_prices
        feature_vector[1] = inventory_level
        feature_vector[2] = self._get_category_elasticity(sku)
        feature_vector[3] = market_position
        feature_vector[4] = np.log1p(inventory_level)
        feature_vector[5] = competitor_prices / (competitor_prices + 1e-6)
        feature_vector[6] = min(inventory_level / 500.0, 1.0)
        feature_vector[7] = 1.0 if "tshirt" in sku.lower() else 0.0
        feature_vector[8] = 1.0 if "jeans" in sku.lower() else 0.0
        feature_vector[9] = 1.0 if "dress" in sku.lower() else 0.0
        feature_vector[10] = (competitor_prices - 30.0) / 20.0  # normalized price
        feature_vector[11] = np.clip(inventory_level / 200.0, 0, 1)
        return feature_vector

    def compute_elasticity(
        self,
        sku: str,
        competitor_prices: List[float],
        inventory_level: float,
    ) -> float:
        """Compute price elasticity for SKU given competitor prices and inventory."""
        avg_comp = float(np.mean(competitor_prices)) if competitor_prices else 35.0
        features = self._build_elasticity_features(
            sku=sku,
            competitor_prices=avg_comp,
            inventory_level=inventory_level,
            market_position=self._get_market_position(sku),
        )
        elasticity = self.xgb_model.predict(features.reshape(1, -1))
        return float(elasticity[0])
