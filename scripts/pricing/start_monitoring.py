#!/usr/bin/env python3
"""Start competitor monitoring: index demo prices into Qdrant."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.data.pricing.competitor_prices import ensure_competitor_prices_collection, upsert_competitor_price
from app.dynamic_pricing.market_monitor import MarketMonitorAgent


async def main() -> None:
    ensure_competitor_prices_collection()
    agent = MarketMonitorAgent()
    skus = ["tshirt_blue_m", "jeans_slim_black", "dress_party_red"]
    for sku in skus:
        prices = await agent.update_competitor_prices(sku, "store_001")
        print(f"{sku}: {prices}")
    print("Competitor monitoring data indexed to Qdrant (competitor_prices).")


if __name__ == "__main__":
    asyncio.run(main())
