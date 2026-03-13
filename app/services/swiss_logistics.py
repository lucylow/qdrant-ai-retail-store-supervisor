"""
CH-specific delivery zones and Alpine penalties for pickup/delivery.
"""
from __future__ import annotations

from typing import Dict, List


class SwissLogistics:
    """Swiss postal and pickup optimization."""

    POSTAL_ZONES: Dict[str, List[str]] = {
        "urban": ["ZH", "GE", "BS", "LU"],
        "alpine": ["GR", "VS", "UR", "OW"],
        "rural": ["AI", "AR", "GL", "NW", "SZ", "SH", "TG"],
    }

    ALPINE_PENALTIES: Dict[str, float] = {
        "GR": 0.25,  # St. Moritz ski gear
        "VS": 0.35,  # Zermatt
        "UR": 0.45,  # Andermatt
    }

    @staticmethod
    def calculate_delivery_penalty(canton: str, category: str) -> float:
        """Alpine ski gear = higher penalty, urban dairy = minimal."""
        if canton in SwissLogistics.ALPINE_PENALTIES:
            base_penalty = SwissLogistics.ALPINE_PENALTIES[canton]
            if category == "ski_gear":
                return base_penalty * 1.5  # Winter urgency
            return base_penalty
        return 0.0

    @staticmethod
    def preferred_pickup_times(canton: str) -> List[str]:
        """Swiss prefer 08:00-12:00 pickup windows."""
        return ["08:00-12:00", "14:00-18:00"]  # No evening pickup culture

    @staticmethod
    def delivery_penalty_for_tenant(tenant: str, canton: str = "ZH", category: str = "general") -> float:
        """Aggregate delivery penalty for a tenant (e.g. default canton)."""
        return SwissLogistics.calculate_delivery_penalty(canton, category)
