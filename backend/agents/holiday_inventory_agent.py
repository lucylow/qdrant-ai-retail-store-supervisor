"""
Holiday-aware inventory: Christmas 4x cheese, Ski season 2x goggles, safety stock.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from app.services.holiday_inventory import SwissHolidayInventory
from app.services.holiday_pricing import SwissHolidayPricing


class HolidayAwareInventoryAgent:
    """Christmas = 4x cheese stock, Ski season = 2x goggles."""

    async def optimize_inventory(
        self,
        products: List[Dict[str, Any]],
        tenant: str,
        canton: str = "ZH",
    ) -> List[Dict[str, Any]]:
        """Enrich products with holiday demand multiplier and safety stock."""
        today = date.today()
        optimized = []

        for product in products:
            category = product.get("category", "general")
            price = float(product.get("price", 0.0))
            stock = int(product.get("stock", 0))

            demand_mult = SwissHolidayInventory.get_demand_multiplier(
                today, category, canton
            )
            holiday_price = SwissHolidayPricing.calculate_holiday_price(
                price, category, demand_mult
            )
            safety_stock = SwissHolidayInventory.calculate_safety_stock(
                stock, category, canton
            )
            stockout_risk = (stock / safety_stock) if safety_stock > 0 else 1.0
            active_periods = SwissHolidayInventory.get_active_periods(
                today, category
            )

            product["holiday_analysis"] = {
                "demand_multiplier": demand_mult,
                "safety_stock_required": safety_stock,
                "stockout_risk": round(stockout_risk, 2),
                "holiday_price": holiday_price,
                "active_periods": active_periods,
            }
            optimized.append(product)

        return sorted(
            optimized,
            key=lambda x: x.get("holiday_analysis", {}).get("stockout_risk", 1.0),
        )
