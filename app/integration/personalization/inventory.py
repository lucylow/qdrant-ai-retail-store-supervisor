"""Preference-aware allocation: align inventory with customer preferences."""

from __future__ import annotations

from typing import Any, Dict, List

from app.cdp.customer_profile import CustomerProfile


async def preference_aware_allocation(
    profile: CustomerProfile,
    product_ids: List[str],
    warehouse_capacity: Dict[str, int],
) -> Dict[str, Any]:
    """
    Suggest allocation weights per product given customer preference (category_affinity);
    for use with inventory/capacity planning.
    """
    aff = profile.segments.category_affinity or {}
    weights = {}
    for pid in product_ids:
        w = aff.get(pid, 0.1) + aff.get(f"product_{pid}", 0.05) + 0.1
        weights[pid] = min(1.0, w)
    total = sum(weights.values()) or 1.0
    normalized = {k: v / total for k, v in weights.items()}
    return {
        "customer_id": profile.customer_id,
        "allocation_weights": normalized,
        "warehouse_capacity": warehouse_capacity,
    }
