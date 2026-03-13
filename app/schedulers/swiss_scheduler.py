"""
Strict Swiss pickup windows (08:00-12:00, 14:00-18:00) and punctuality.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class SwissPunctualityScheduler:
    """Swiss retail pickup windows (strictly enforced)."""

    PREFERRED_WINDOWS: Dict[str, tuple] = {
        "morning": ("08:00", "12:00"),
        "afternoon": ("14:00", "18:00"),
        "evening": ("18:30", "20:00"),
    }

    BUSINESS_DAYS = (0, 1, 2, 3, 4)  # Mon–Fri

    @staticmethod
    def snap_to_pickup_window(
        requested_time: datetime, tenant: str = "coop"
    ) -> Optional[Dict[str, Any]]:
        """Snap 10:47 -> 08:00-12:00 window (Swiss precision)."""
        today = requested_time.date()
        best_window: Optional[Dict[str, Any]] = None
        best_distance = float("inf")

        for window_name, (start, end) in SwissPunctualityScheduler.PREFERRED_WINDOWS.items():
            window_start = datetime.combine(
                today, datetime.strptime(start, "%H:%M").time()
            )
            window_end = datetime.combine(
                today, datetime.strptime(end, "%H:%M").time()
            )
            if requested_time.weekday() in SwissPunctualityScheduler.BUSINESS_DAYS:
                dist = abs((requested_time - window_start).total_seconds())
                if dist < best_distance:
                    best_distance = dist
                    best_window = {
                        "window": window_name,
                        "start": window_start,
                        "end": window_end,
                        "duration_minutes": int(
                            (window_end - window_start).total_seconds() / 60
                        ),
                    }
        return best_window

    @staticmethod
    def validate_punctuality(dt: datetime, pickup_window: Dict[str, Any]) -> bool:
        """Swiss tolerance: ±15 min."""
        tolerance = timedelta(minutes=15)
        start = pickup_window.get("start")
        end = pickup_window.get("end")
        if start is None or end is None:
            return False
        return start - tolerance <= dt <= end + tolerance
