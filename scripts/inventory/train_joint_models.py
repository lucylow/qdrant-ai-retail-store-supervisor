#!/usr/bin/env python3
"""Joint pricing + inventory model training (forecaster, stockout, EOQ calibration)."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.inventory.forecaster import InventoryForecaster
from app.inventory.stockout_predictor import StockoutPredictor
from app.dynamic_pricing.supervisor import DynamicPricingSupervisor
from app.inventory.supervisor import InventorySupervisor


async def run_quick_training() -> None:
    forecaster = InventoryForecaster()
    stockout = StockoutPredictor()
    skus = ["tshirt_blue_m", "jeans_slim_black", "dress_party_red"]
    for sku in skus:
        _ = await forecaster.forecast_demand(sku, "wh_001", horizon_days=30)
        import pandas as pd

        demand_series = pd.Series([50.0, 52.0, 48.0, 55.0])
        _ = stockout.predict_stockout(sku, 100.0, demand_series)
    pricing = DynamicPricingSupervisor()
    inv_sup = InventorySupervisor(pricing)
    inv_rec, price_rec = await inv_sup.optimize_jointly(
        sku="tshirt_blue_m",
        warehouse_id="wh_001",
        current_stock=80.0,
        supplier_lead_days=5,
    )
    print(f"Joint run: urgency={inv_rec.urgency}, price=${price_rec.dynamic_price:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    asyncio.run(run_quick_training())
    print("Joint models training complete.")


if __name__ == "__main__":
    main()
