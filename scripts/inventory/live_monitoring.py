#!/usr/bin/env python3
"""Real-time inventory alerts (stockout risk, reorder suggestions)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.inventory.supervisor import InventorySupervisor
from app.dynamic_pricing.supervisor import DynamicPricingSupervisor


async def check_sku(sku: str, current_stock: float, lead_days: int) -> None:
    pricing = DynamicPricingSupervisor()
    inv = InventorySupervisor(pricing)
    inv_rec, price_rec = await inv.optimize_jointly(
        sku=sku,
        warehouse_id="wh_001",
        current_stock=current_stock,
        supplier_lead_days=lead_days,
    )
    alert = "ALERT" if inv_rec.urgency in ("CRITICAL", "HIGH") else "OK"
    print(f"[{alert}] {sku} stock={current_stock:.0f} urgency={inv_rec.urgency} "
          f"order_qty={inv_rec.optimal_order_qty:.0f} price=${price_rec.dynamic_price:.2f}")


async def run_all() -> None:
    await check_sku("tshirt_blue_m", 25.0, 5)
    await check_sku("jeans_slim_black", 120.0, 7)
    print("Live monitoring check done.")


def main() -> None:
    asyncio.run(run_all())


if __name__ == "__main__":
    main()
