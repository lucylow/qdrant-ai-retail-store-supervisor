"""Unified Customer 360 profile models for personalization agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class CustomerSegment:
    """Behavioral and value segments for a customer."""

    loyalty_tier: str  # BRONZE, SILVER, GOLD, PLATINUM
    rf_score: float  # Recency-Frequency-Monetary 0-5
    price_sensitivity: float  # 0=insensitive, 1=very sensitive
    category_affinity: Dict[str, float] = field(default_factory=dict)


@dataclass
class CustomerProfile:
    """Real-time Customer 360 unified profile."""

    customer_id: str
    demographics: Dict[str, Any]
    rf_score: float
    segments: CustomerSegment
    price_sensitivity: float
    last_updated: datetime
    confidence: float
    # Real-time context (session, channel, location) - updated by ProfileBuilder
    current_channel: Optional[str] = None
    current_region: Optional[str] = None
    current_time_of_day: Optional[str] = None
    recent_product_views: List[str] = field(default_factory=list)
    consent_marketing: bool = True
    consent_personalization: bool = True

    def update_context(self, context: Dict[str, Any]) -> None:
        """Update profile with real-time session/context (channel, location, time)."""
        if "channel" in context:
            self.current_channel = str(context["channel"])
        if "location" in context:
            self.current_region = str(context["location"])
        if "time_of_day" in context:
            self.current_time_of_day = str(context["time_of_day"])
        if "recent_views" in context:
            self.recent_product_views = list(context["recent_views"])[:20]

    def to_payload(self) -> Dict[str, Any]:
        """Serialize for Qdrant payload (indexed fields)."""
        return {
            "customer_id": self.customer_id,
            "loyalty_tier": self.segments.loyalty_tier,
            "rf_score": self.rf_score,
            "price_sensitivity": self.price_sensitivity,
            "region": self.current_region or "unknown",
            "last_active": self.last_updated.isoformat(),
            "channel_preference": self.current_channel or "web",
            "confidence": self.confidence,
        }
