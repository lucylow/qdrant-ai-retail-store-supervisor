"""Streaming behavioral features for real-time personalization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class RealTimeFeatures:
    """Live session/journey features (last N minutes)."""

    customer_id: str
    session_id: str
    timestamp: datetime
    # Session
    page_views: int
    products_viewed: List[str]
    categories_viewed: List[str]
    search_queries: List[str]
    add_to_cart_events: List[Dict[str, Any]]
    # Intent signals
    dwell_time_seconds: float
    scroll_depth_avg: float
    exit_intent: bool
    # Channel
    channel: str
    device: str
    region: str

    def to_vector_input(self) -> Dict[str, Any]:
        """Features for embedding or model input."""
        return {
            "customer_id": self.customer_id,
            "session_id": self.session_id,
            "products_viewed": self.products_viewed[-20:],
            "categories_viewed": list(dict.fromkeys(self.categories_viewed))[-10:],
            "search_queries": self.search_queries[-5:],
            "channel": self.channel,
            "dwell_time": self.dwell_time_seconds,
            "page_views": self.page_views,
        }


def compute_real_time_features(
    customer_id: str,
    session_id: str,
    events: List[Dict[str, Any]],
    context: Dict[str, Any],
) -> RealTimeFeatures:
    """Build real-time features from raw session events (production stub)."""
    products = []
    categories = []
    queries = []
    add_to_cart = []
    dwell = 0.0
    scroll_sum, scroll_n = 0.0, 0
    for e in events:
        if e.get("type") == "view":
            products.append(e.get("product_id", ""))
            categories.append(e.get("category", ""))
        elif e.get("type") == "search":
            queries.append(e.get("query", ""))
        elif e.get("type") == "add_to_cart":
            add_to_cart.append(e)
        dwell += float(e.get("dwell_sec", 0))
        if "scroll_depth" in e:
            scroll_sum += float(e["scroll_depth"])
            scroll_n += 1
    return RealTimeFeatures(
        customer_id=customer_id,
        session_id=session_id,
        timestamp=datetime.utcnow(),
        page_views=len(events),
        products_viewed=products,
        categories_viewed=categories,
        search_queries=queries,
        add_to_cart_events=add_to_cart,
        dwell_time_seconds=dwell,
        scroll_depth_avg=scroll_sum / scroll_n if scroll_n else 0.0,
        exit_intent=any(e.get("exit_intent") for e in events),
        channel=context.get("channel", "web"),
        device=context.get("device", "desktop"),
        region=context.get("location", "unknown"),
    )
