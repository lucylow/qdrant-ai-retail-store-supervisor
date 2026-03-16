"""
Swiss time intelligence API: parse "morgen 10h", pickup windows, punctuality.
"""
from __future__ import annotations

from datetime import datetime, timedelta, time
from typing import Any, Dict, List

from fastapi import APIRouter, Form

from app.parsers.swiss_datetime import SwissDateParser
from app.schedulers.swiss_scheduler import SwissPunctualityScheduler

router = APIRouter(prefix="/time", tags=["swiss-datetime"])


@router.post("/parse")
async def parse_swiss_datetime(
    query: str = Form(...),
    language: str = Form("de"),
    tenant: str = Form("coop"),
) -> Dict[str, Any]:
    """'morgen 10h Zürich HB' -> structured pickup schedule."""
    parsed = SwissDateParser.parse_swiss_datetime(query, language)
    dt = parsed.get("datetime")
    pickup_window = None
    if dt:
        pickup_window = SwissPunctualityScheduler.snap_to_pickup_window(dt, tenant)

    # Serialize pickup_window for JSON (datetime -> isoformat)
    pw_serialized = None
    if pickup_window:
        pw_serialized = {
            "window": pickup_window.get("window"),
            "start": pickup_window["start"].isoformat() if pickup_window.get("start") else None,
            "end": pickup_window["end"].isoformat() if pickup_window.get("end") else None,
            "duration_minutes": pickup_window.get("duration_minutes"),
        }

    return {
        "original_query": query,
        "parsed_datetime": dt.isoformat() if dt else None,
        "pickup_window": pw_serialized,
        "is_business_day": dt.weekday() < 5 if dt else None,
        "punctuality_feasible": pickup_window is not None,
    }


@router.get("/next-pickup-windows")
async def get_next_pickup_windows(
    tenant: str = "coop",
    days: int = 7,
) -> Dict[str, List[Dict[str, Any]]]:
    """Swiss-standard pickup windows for next N days (business days)."""
    windows: List[Dict[str, Any]] = []
    today = datetime.now().date()

    for i in range(days):
        target = today + timedelta(days=i)
        if target.weekday() < 5:
            windows.append({
                "date": target.isoformat(),
                "window": "08:00-12:00",
                "type": "morning",
            })
            windows.append({
                "date": target.isoformat(),
                "window": "14:00-18:00",
                "type": "afternoon",
            })

    return {"next_pickup_windows": windows[:10]}
