#!/usr/bin/env python3
"""90-day walk-forward backtest for dynamic vs static pricing."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
from app.dynamic_pricing.supervisor import DynamicPricingSupervisor
from app.dynamic_pricing.margin_optimizer import MarginOptimizer

# Simulated days for backtest (quick: 10, full: 90)
DAYS_QUICK = 10
DAYS_FULL = 90


async def run_backtest(days: int) -> dict:
    supervisor = DynamicPricingSupervisor()
    skus = ["tshirt_blue_m", "jeans_slim_black", "dress_party_red"]
    revenue_dynamic = 0.0
    revenue_static = 0.0
    np.random.seed(42)

    for d in range(days):
        for sku in skus:
            comp = list(np.random.uniform(28, 42, 3))
            inv = float(np.random.uniform(80, 200))
            rec = await supervisor.compute_optimal_prices(
                sku=sku, store_id="store_001", competitor_prices=comp, inventory_level=inv
            )
            # Simulated demand: elasticity applied
            base_demand = 100
            static_price = np.mean(comp) * 0.98
            demand_static = base_demand * (static_price / 35.0) ** -1.5
            demand_dynamic = base_demand * (rec.dynamic_price / 35.0) ** rec.elasticity
            revenue_static += static_price * min(demand_static, inv)
            revenue_dynamic += rec.dynamic_price * min(demand_dynamic, inv)

    lift = (revenue_dynamic / revenue_static - 1) * 100 if revenue_static else 0
    return {
        "days": days,
        "revenue_static": round(revenue_static, 2),
        "revenue_dynamic": round(revenue_dynamic, 2),
        "lift_pct": round(lift, 1),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    days = DAYS_QUICK if args.quick else min(args.days, DAYS_FULL)

    result = asyncio.run(run_backtest(days))
    print(f"Backtest ({result['days']} days):")
    print(f"  Static:  ${result['revenue_static']:,.2f}")
    print(f"  Dynamic: ${result['revenue_dynamic']:,.2f} (+{result['lift_pct']:.1f}%)")


if __name__ == "__main__":
    main()
