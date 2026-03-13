"""Batch demographic and purchase history features for Customer 360."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class HistoricalFeatures:
    """Batch demographic + purchase history features."""

    customer_id: str
    # Demographics (anonymized/aggregated)
    region: str
    signup_date: datetime
    first_purchase_date: Optional[datetime] = None
    # Purchase
    total_orders: int
    total_revenue: float
    avg_order_value: float
    last_order_date: Optional[datetime] = None
    # RFM
    recency_days: float
    frequency: float
    monetary: float
    # Category/brand
    top_categories: List[str]
    top_brands: List[str]
    category_spend: Dict[str, float]
    # Loyalty
    loyalty_tier: str
    loyalty_points: int

    def to_payload(self) -> Dict[str, Any]:
        """For storage or model input."""
        return {
            "customer_id": self.customer_id,
            "region": self.region,
            "total_orders": self.total_orders,
            "total_revenue": self.total_revenue,
            "recency_days": self.recency_days,
            "frequency": self.frequency,
            "monetary": self.monetary,
            "loyalty_tier": self.loyalty_tier,
            "top_categories": self.top_categories[:10],
            "top_brands": self.top_brands[:10],
        }


def _parse_signup_date(value: Any) -> datetime:
    """Parse signup_date from datetime or ISO string."""
    if value is None:
        return datetime.utcnow()
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return datetime.utcnow()


def compute_historical_features(
    customer_id: str,
    demographics: Dict[str, Any],
    orders: List[Dict[str, Any]],
    loyalty: Dict[str, Any],
) -> HistoricalFeatures:
    """Compute historical features from CRM/orders (production stub)."""
    total_orders = len(orders)
    total_revenue = sum(float(o.get("revenue", 0)) for o in orders)
    avg_aov = total_revenue / total_orders if total_orders else 0.0
    last_date = None
    if orders:
        dates = [o.get("date") for o in orders if o.get("date")]
        if dates:
            last_date = max(
                d if isinstance(d, datetime) else datetime.fromisoformat(str(d))
                for d in dates
            )
    recency = (
        (datetime.utcnow() - last_date).total_seconds() / 86400.0
        if last_date
        else 999.0
    )
    categories = []
    for o in orders:
        categories.extend(o.get("categories", []))
    from collections import Counter

    top_cat = [c for c, _ in Counter(categories).most_common(10)]
    brands = []
    for o in orders:
        brands.append(o.get("brand", ""))
    top_brands = [b for b, _ in Counter(brands).most_common(10)]

    return HistoricalFeatures(
        customer_id=customer_id,
        region=demographics.get("region", "unknown"),
        signup_date=_parse_signup_date(demographics.get("signup_date")),
        first_purchase_date=(
            datetime.fromisoformat(str(orders[0]["date"])) if orders and orders[0].get("date") else None
        ),
        total_orders=total_orders,
        total_revenue=total_revenue,
        avg_order_value=avg_aov,
        last_order_date=last_date,
        recency_days=recency,
        frequency=float(total_orders),
        monetary=total_revenue,
        top_categories=top_cat,
        top_brands=top_brands,
        category_spend={},
        loyalty_tier=loyalty.get("tier", "BRONZE"),
        loyalty_points=int(loyalty.get("points", 0)),
    )
