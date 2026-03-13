"""XGBoost + LightGBM ensemble for elasticity and demand prediction."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    import xgboost as xgb

    _HAS_XGB = True
except ImportError:
    _HAS_XGB = False
    xgb = None  # type: ignore

try:
    import lightgbm as lgb

    _HAS_LGB = True
except ImportError:
    _HAS_LGB = False
    lgb = None  # type: ignore


class ElasticityEnsemble:
    """Ensemble of XGBoost + LightGBM for price elasticity prediction."""

    def __init__(
        self,
        n_features: int = 12,
        n_estimators: int = 100,
        model_dir: Optional[Path] = None,
    ):
        self.n_features = n_features
        self.n_estimators = n_estimators
        self.model_dir = model_dir or Path("/tmp")
        self._xgb_model: Any = None
        self._lgb_model: Any = None
        self._fallback_coef: Optional[np.ndarray] = None
        self._fit = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> "ElasticityEnsemble":
        """Train ensemble on (features, elasticity) pairs."""
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if X.shape[1] != self.n_features and X.shape[1] > 0:
            # Pad or slice to n_features
            if X.shape[1] < self.n_features:
                X = np.pad(
                    X,
                    ((0, 0), (0, self.n_features - X.shape[1])),
                    mode="constant",
                    constant_values=0,
                )[:, : self.n_features]
            else:
                X = X[:, : self.n_features]

        # Fallback: linear coeffs for demo when no xgb/lgb
        self._fallback_coef = np.zeros(self.n_features)
        self._fallback_coef[0] = -0.02  # competitor price effect
        self._fallback_coef[1] = 0.01   # inventory effect
        self._fallback_coef[2] = 0.05   # category elasticity base
        if len(y) > 0:
            self._fallback_coef = np.linalg.lstsq(
                np.hstack([X, np.ones((X.shape[0], 1))]), y, rcond=None
            )[0][: self.n_features]

        if _HAS_XGB:
            try:
                self._xgb_model = xgb.XGBRegressor(
                    n_estimators=self.n_estimators,
                    max_depth=4,
                    learning_rate=0.1,
                )
                self._xgb_model.fit(X, y)
            except Exception as e:
                logger.warning("XGBoost fit failed, using fallback: %s", e)

        if _HAS_LGB:
            try:
                self._lgb_model = lgb.LGBMRegressor(
                    n_estimators=self.n_estimators,
                    max_depth=4,
                    learning_rate=0.1,
                    verbose=-1,
                )
                self._lgb_model.fit(X, y)
            except Exception as e:
                logger.warning("LightGBM fit failed, using fallback: %s", e)

        self._fit = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict elasticity; shape (n_samples,) or (1, n_features)."""
        if X.ndim == 1:
            X = X.reshape(1, -1)
        if X.shape[1] != self.n_features:
            if X.shape[1] < self.n_features:
                X = np.pad(
                    X,
                    ((0, 0), (0, self.n_features - X.shape[1])),
                    mode="constant",
                    constant_values=0,
                )[:, : self.n_features]
            else:
                X = X[:, : self.n_features]

        preds: List[float] = []
        if self._xgb_model is not None:
            preds.append(self._xgb_model.predict(X).flatten())
        if self._lgb_model is not None:
            preds.append(self._lgb_model.predict(X).flatten())
        if self._fallback_coef is not None:
            preds.append((X @ self._fallback_coef).flatten())

        if not preds:
            return np.full(X.shape[0], -1.5)  # default elasticity
        return np.mean(preds, axis=0)


def load_elasticity_model(path: Optional[Path] = None) -> ElasticityEnsemble:
    """Load or create default elasticity model."""
    model = ElasticityEnsemble(n_features=12)
    if path and path.exists():
        try:
            if _HAS_XGB:
                model._xgb_model = xgb.XGBRegressor()
                model._xgb_model.load_model(str(path))
            model._fit = True
        except Exception as e:
            logger.warning("Could not load elasticity model from %s: %s", path, e)
    if not model._fit:
        # Demo: fit on synthetic data
        np.random.seed(42)
        X = np.random.randn(200, 12).astype(np.float32)
        y = -1.5 + 0.02 * X[:, 0] + 0.01 * X[:, 1] + np.random.randn(200) * 0.2
        model.fit(X, y)
    return model
