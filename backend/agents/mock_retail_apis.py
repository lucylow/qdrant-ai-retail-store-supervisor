from __future__ import annotations

from typing import Any, Dict, List


async def mock_coop_leshop_products(category: str, region: str) -> List[Dict[str, Any]]:
    """Mock Coop leShop.ch dairy catalog."""
    _ = category
    _ = region
    return [
        {
            "sku": "milk_bio_2L",
            "name": "Bio-Milch 2L laktosefrei",
            "price": 3.95,
            "stock": 45,
            "pickup_zones": ["ZH", "GE"],
            "expiry_risk": 0.3,
        },
        {
            "sku": "muesli_oat_500g",
            "name": "Hafer Müsli 500g",
            "price": 4.20,
            "stock": 23,
            "pickup_zones": ["ZH"],
            "expiry_risk": 0.2,
        },
        {
            "sku": "yogurt_natural",
            "name": "Naturjoghurt 500g",
            "price": 2.80,
            "stock": 67,
            "pickup_zones": ["ZH", "GE"],
            "expiry_risk": 0.12,
        },
    ]


async def mock_coop_inventory(skus: List[str], region: str) -> Dict[str, Dict[str, Any]]:
    """Mock Coop inventory by SKU."""
    _ = region
    return {
        sku: {"qty": 10, "eta": "tomorrow"} for sku in skus
    }


async def mock_migros_fondue() -> List[Dict[str, Any]]:
    """Mock Migros Online fondue season catalog."""
    return [
        {
            "sku": "fondue_kaese_2kg",
            "name": "Käsefondue 2kg",
            "price": 28.50,
            "stock": 12,
        },
        {
            "sku": "fondue_topf_4p",
            "name": "Fondue Topf 4 Personen",
            "price": 15.90,
            "stock": 8,
        },
    ]


