"""
Swiss datetime parsing: "morgen 10h Zürich HB", 24h format, DE/FR phrases.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional


class SwissTimeFormat(Enum):
    MILITARY_24H = "HH:mm"
    SWISS_GERMAN = "H'h'"
    ISO8601 = "ISO"


class SwissDateParser:
    """Handles Swiss German/French time expressions and 24h format."""

    SWISS_TIME_PATTERNS: Dict[str, list] = {
        "de": [
            r"(\d{1,2})[h:]\s*(\d{0,2})?",
            r"(\d{1,2})\s*(?:Uhr)?",
            r"um\s+(\d{1,2})[h:]\s*(\d{0,2})?",
            r"morgen\s+(\d{1,2})[h:]\s*(\d{0,2})?",
            r"heute\s+(\d{1,2})[h:]\s*(\d{0,2})?",
        ],
        "fr": [
            r"à\s+(\d{1,2})[h:]\s*(\d{0,2})?",
            r"demain\s+(\d{1,2})[h:]\s*(\d{0,2})?",
            r"aujourd'hui\s+(\d{1,2})[h:]\s*(\d{0,2})?",
        ],
    }

    SWISS_PHRASES: Dict[str, Dict[str, str]] = {
        "de": {
            "morgen": "tomorrow",
            "heute": "today",
            "vormittag": "09:00-12:00",
            "nachmittag": "14:00-18:00",
        },
        "fr": {
            "demain": "tomorrow",
            "aujourd'hui": "today",
            "matin": "09:00-12:00",
            "après-midi": "14:00-18:00",
        },
    }

    @staticmethod
    def parse_swiss_datetime(
        text: str,
        language: str = "de",
        reference_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Parse e.g. 'morgen 10h Zürich HB' -> structured schedule."""
        if reference_date is None:
            reference_date = datetime.now()

        day_offset = 0
        if "morgen" in text.lower() or "demain" in text.lower():
            day_offset = 1

        time_match = None
        for pattern in SwissDateParser.SWISS_TIME_PATTERNS.get(language, []):
            time_match = re.search(pattern, text, re.IGNORECASE)
            if time_match:
                break

        parsed: Dict[str, Any] = {
            "original": text,
            "language": language,
            "reference_date": reference_date,
            "is_valid": False,
            "datetime": None,
            "time_window": None,
            "day_offset": day_offset,
        }

        if time_match:
            hour = int(time_match.group(1))
            minute = 0
            if time_match.lastindex and time_match.lastindex >= 2 and time_match.group(2):
                minute = int(time_match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                target = reference_date + timedelta(days=day_offset)
                parsed["datetime"] = target.replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )
                parsed["is_valid"] = True

        if "vormittag" in text.lower() or "matin" in text.lower():
            parsed["time_window"] = "09:00-12:00"
        elif "nachmittag" in text.lower() or "après-midi" in text.lower():
            parsed["time_window"] = "14:00-18:00"

        return parsed
