"""External market data pipeline for pricing (placeholder for live feeds)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class MarketSignal:
    """Single market signal (e.g. commodity index, demand proxy)."""
    name: str
    value: float
    timestamp: str


class MarketSignalsPipeline:
    """Aggregate external market signals for pricing (demo: synthetic)."""

    def __init__(self):
        self._cache: Dict[str, List[MarketSignal]] = {}

    def fetch_signals(self, sku: str) -> List[MarketSignal]:
        """Fetch relevant market signals for a SKU."""
        # Placeholder: return synthetic signals
        return [
            MarketSignal("demand_index", 1.02, datetime.utcnow().isoformat()),
            MarketSignal("competitor_activity", 0.95, datetime.utcnow().isoformat()),
        ]

    def to_features(self, signals: List[MarketSignal]) -> Dict[str, float]:
        """Convert signals to feature dict for models."""
        return {s.name: s.value for s in signals}
