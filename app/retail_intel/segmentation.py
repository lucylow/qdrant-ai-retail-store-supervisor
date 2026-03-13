from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Final, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class SegmentLabel(str, Enum):
    VIP = "VIP"
    LOYAL = "Loyal"
    AT_RISK = "At-Risk"
    PRICE_SENSITIVE = "Price-Sensitive"
    NEW = "New"
    INACTIVE = "Inactive"


SEGMENTS: Final[List[str]] = [s.value for s in SegmentLabel]


@dataclass
class CustomerRFM:
    recency_days: float
    frequency: float
    monetary: float


@dataclass
class CustomerBehavioral:
    avg_basket_size: float
    category_diversity: float
    days_since_first_purchase: float


@dataclass
class CustomerSegmentResult:
    customer_id: str
    segment: SegmentLabel
    recency_days: float
    frequency: float
    monetary: float
    avg_basket_size: float
    category_diversity: float


class CustomerSegmenter:
    """RFM + behavioral clustering into 6 business segments.

    # RETAIL-INTEL-HACKATHON: Used in dashboard Tab 1 - Customer Segments.
    """

    SEGMENTS: Final[List[str]] = SEGMENTS

    def __init__(self, n_clusters: int = 6, random_state: int = 42) -> None:
        self.n_clusters: int = n_clusters
        self.random_state: int = random_state
        self._scaler: StandardScaler | None = None
        self._kmeans: KMeans | None = None
        self._cluster_to_label: Dict[int, SegmentLabel] = {}

    def fit_transform(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """Fit the segmenter and return per-customer segment assignments.

        Expected columns:
        - customer_id
        - order_id
        - order_date (datetime-like)
        - order_value (float)
        - category (str)
        """
        if orders_df.empty:
            return pd.DataFrame(
                columns=[
                    "customer_id",
                    "segment",
                    "recency_days",
                    "frequency",
                    "monetary",
                    "avg_basket_size",
                    "category_diversity",
                ]
            )

        orders = orders_df.copy()
        if not np.issubdtype(orders["order_date"].dtype, np.datetime64):
            orders["order_date"] = pd.to_datetime(orders["order_date"])

        rfm = self._compute_rfm(orders)
        behavioral = self._compute_behavioral(orders)

        features = rfm.merge(behavioral, on="customer_id", how="inner")

        feature_cols = [
            "recency_days",
            "frequency",
            "monetary",
            "avg_basket_size",
            "category_diversity",
        ]

        X = features[feature_cols].astype(float).values

        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)

        self._kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init="auto",
        )
        cluster_labels = self._kmeans.fit_predict(X_scaled)

        self._cluster_to_label = self._derive_cluster_labels(
            self._kmeans.cluster_centers_, feature_cols
        )

        features["segment"] = [
            self._cluster_to_label[int(c)].value for c in cluster_labels
        ]

        return features[
            [
                "customer_id",
                "segment",
                "recency_days",
                "frequency",
                "monetary",
                "avg_basket_size",
                "category_diversity",
            ]
        ]

    def predict_new(self, customer_id: str, recent_orders: pd.DataFrame) -> str:
        """Predict real-time segment for a single customer's new activity."""
        if (
            self._kmeans is None
            or self._scaler is None
            or not self._cluster_to_label
        ):
            raise RuntimeError("CustomerSegmenter must be fitted before prediction.")

        if recent_orders.empty:
            return SegmentLabel.INACTIVE.value

        orders = recent_orders.copy()
        if not np.issubdtype(orders["order_date"].dtype, np.datetime64):
            orders["order_date"] = pd.to_datetime(orders["order_date"])

        rfm_row = self._compute_rfm(orders, single_customer_id=customer_id)
        beh_row = self._compute_behavioral(orders, single_customer_id=customer_id)

        features = rfm_row.merge(beh_row, on="customer_id", how="inner")
        feature_cols = [
            "recency_days",
            "frequency",
            "monetary",
            "avg_basket_size",
            "category_diversity",
        ]

        X = features[feature_cols].astype(float).values
        X_scaled = self._scaler.transform(X)
        cluster = int(self._kmeans.predict(X_scaled)[0])
        return self._cluster_to_label[cluster].value

    def _compute_rfm(
        self, orders: pd.DataFrame, single_customer_id: str | None = None
    ) -> pd.DataFrame:
        df = orders
        if single_customer_id is not None:
            df = df[df["customer_id"] == single_customer_id]

        snapshot_date = df["order_date"].max() + pd.Timedelta(days=1)

        grouped = (
            df.groupby("customer_id")
            .agg(
                last_order_date=("order_date", "max"),
                frequency=("order_id", "nunique"),
                monetary=("order_value", "sum"),
            )
            .reset_index()
        )

        grouped["recency_days"] = (
            snapshot_date - grouped["last_order_date"]
        ).dt.days.astype(float)

        return grouped[
            ["customer_id", "recency_days", "frequency", "monetary"]
        ].astype(
            {
                "recency_days": float,
                "frequency": float,
                "monetary": float,
            }
        )

    def _compute_behavioral(
        self, orders: pd.DataFrame, single_customer_id: str | None = None
    ) -> pd.DataFrame:
        df = orders
        if single_customer_id is not None:
            df = df[df["customer_id"] == single_customer_id]

        # Assume each row is a line-item; basket size is items per order.
        basket = (
            df.groupby(["customer_id", "order_id"])
            .size()
            .reset_index(name="items")
        )
        basket_agg = (
            basket.groupby("customer_id")["items"]
            .agg(avg_basket_size="mean")
            .reset_index()
        )

        category_agg = (
            df.groupby("customer_id")["category"]
            .nunique()
            .reset_index(name="category_diversity")
        )

        first_last = (
            df.groupby("customer_id")["order_date"]
            .agg(first_purchase="min", last_purchase="max")
            .reset_index()
        )
        first_last["days_since_first_purchase"] = (
            first_last["last_purchase"] - first_last["first_purchase"]
        ).dt.days.astype(float)

        behavioral = basket_agg.merge(category_agg, on="customer_id", how="inner").merge(
            first_last[["customer_id", "days_since_first_purchase"]],
            on="customer_id",
            how="inner",
        )

        return behavioral.astype(
            {
                "avg_basket_size": float,
                "category_diversity": float,
                "days_since_first_purchase": float,
            }
        )[["customer_id", "avg_basket_size", "category_diversity"]]

    def _derive_cluster_labels(
        self, centers: np.ndarray, feature_cols: List[str]
    ) -> Dict[int, SegmentLabel]:
        """Map cluster centers to human-readable business labels."""
        # Heuristic: high monetary & frequency & low recency => VIP/Loyal
        col_index = {name: idx for idx, name in enumerate(feature_cols)}

        scores: List[Tuple[int, float, float, float]] = []
        for idx, center in enumerate(centers):
            recency = float(center[col_index["recency_days"]])
            frequency = float(center[col_index["frequency"]])
            monetary = float(center[col_index["monetary"]])
            scores.append((idx, recency, frequency, monetary))

        # Lower recency is better (more recent)
        scores_sorted = sorted(
            scores, key=lambda t: (-t[2], -t[3], t[1])
        )  # by freq desc, monetary desc, recency asc

        cluster_to_label: Dict[int, SegmentLabel] = {}
        if not scores_sorted:
            return cluster_to_label

        # Top cluster: VIP
        cluster_to_label[scores_sorted[0][0]] = SegmentLabel.VIP
        # Second: Loyal
        if len(scores_sorted) > 1:
            cluster_to_label[scores_sorted[1][0]] = SegmentLabel.LOYAL
        # Worst recency & low monetary: Inactive
        worst = max(scores_sorted, key=lambda t: (t[1], -t[3]))
        cluster_to_label[worst[0]] = SegmentLabel.INACTIVE

        remaining_clusters = [c for c, _, _, _ in scores_sorted if c not in cluster_to_label]
        for idx, cluster_id in enumerate(remaining_clusters):
            if idx == 0:
                cluster_to_label[cluster_id] = SegmentLabel.AT_RISK
            elif idx == 1:
                cluster_to_label[cluster_id] = SegmentLabel.PRICE_SENSITIVE
            else:
                cluster_to_label[cluster_id] = SegmentLabel.NEW

        return cluster_to_label


__all__ = [
    "CustomerSegmenter",
    "CustomerSegmentResult",
    "SegmentLabel",
]

