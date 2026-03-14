#!/usr/bin/env python3
"""Real-time price recommendations for a SKU (CLI)."""

from __future__ import annotations

import asyncio
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.dynamic_pricing.supervisor import DynamicPricingSupervisor


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sku", default="tshirt_blue_m")
    parser.add_argument("--store", default="store_001")
    parser.add_argument("--competitors", type=float, nargs="+", default=[35.0, 34.0, 36.0])
    parser.add_argument("--inventory", type=float, default=150.0)
    args = parser.parse_args()

    async def run() -> None:
        supervisor = DynamicPricingSupervisor()
        rec = await supervisor.compute_optimal_prices(
            sku=args.sku,
            store_id=args.store,
            competitor_prices=args.competitors,
            inventory_level=args.inventory,
        )
        print(f"SKU: {rec.sku}")
        print(f"Base price: ${rec.base_price:.2f}")
        print(f"Dynamic price: ${rec.dynamic_price:.2f}")
        print(f"Action: {rec.recommended_action}")
        print(f"Revenue lift: +{rec.expected_revenue_lift:.1f}%")

    asyncio.run(run())


if __name__ == "__main__":
    main()
