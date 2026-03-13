#!/usr/bin/env python3
"""Create Qdrant inventory collections and payload indexes."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.qdrant.inventory.collections import setup_inventory_collections

if __name__ == "__main__":
    setup_inventory_collections()
    print("Inventory collections OK: inventory_levels, reorder_history, stockout_events")
