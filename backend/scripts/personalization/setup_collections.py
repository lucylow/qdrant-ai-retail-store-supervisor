#!/usr/bin/env python3
"""Create Qdrant personalization collections and 15+ payload indexes."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.qdrant.personalization.collections import setup_personalization_collections

if __name__ == "__main__":
    setup_personalization_collections()
    print(
        "Personalization collections OK: customer_profiles, "
        "recommendation_history, customer_journeys"
    )
