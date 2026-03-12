from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import List, Mapping, Sequence

from qdrant_client.http import models as rest

from app.agents.shopper import ShopperGoal
from app.config import COLL_PRODUCTS
from app.qdrant_client import get_qdrant_client


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Product:
    sku: str
    name: str
    price_eur: float
    attributes: Mapping[str, str]


@dataclass(slots=True)
class InventorySearchContext:
    candidates: List[Product]
    latency_ms: int


@dataclass(slots=True)
class InventoryPlanItem:
    sku: str
    quantity: int
    unit_price_eur: float


@dataclass(slots=True)
class InventoryPlan:
    items: List[InventoryPlanItem] = field(default_factory=list)
    eta_days: int = 3
    total_price_eur: float = 0.0
    latency_ms: int = 0


class InventoryAgent:
    """
    Inventory search + simple bundle optimization over Qdrant products.
    """

    def initial_search(self, query: str) -> InventorySearchContext:
        started = time.perf_counter()
        client = get_qdrant_client()
        search_query = rest.SearchRequest(
            vector=[0.0] * 3,
            limit=32,
            with_payload=True,
        )
        result = client.search(collection_name=COLL_PRODUCTS, **search_query.dict())
        candidates: List[Product] = []
        for point in result:
            payload = point.payload or {}
            sku = str(payload.get("sku", ""))
            if not sku:
                continue
            name = str(payload.get("name", sku))
            price = float(payload.get("price_eur", 0.0))
            attributes = {
                k: str(v)
                for k, v in payload.items()
                if k not in {"sku", "name", "price_eur"}
            }
            candidates.append(
                Product(
                    sku=sku,
                    name=name,
                    price_eur=price,
                    attributes=attributes,
                )
            )
        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "Inventory initial search",
            extra={
                "event": "inventory.initial_search",
                "query": query,
                "candidates": len(candidates),
                "latency_ms": latency_ms,
            },
        )
        return InventorySearchContext(candidates=candidates, latency_ms=latency_ms)

    def optimize_bundle(
        self,
        goal: ShopperGoal,
        ctx: InventorySearchContext,
    ) -> InventoryPlan:
        # AUTONOMOUS-AGENT-HACKATHON: simple deterministic bundle selection.
        started = time.perf_counter()
        remaining = goal.budget_eur or 9999.0
        items: List[InventoryPlanItem] = []
        for product in sorted(ctx.candidates, key=lambda p: p.price_eur):
            if product.price_eur <= 0 or product.price_eur > remaining:
                continue
            items.append(
                InventoryPlanItem(
                    sku=product.sku,
                    quantity=1,
                    unit_price_eur=product.price_eur,
                )
            )
            remaining -= product.price_eur
            if remaining <= 0:
                break
        total_price = sum(i.unit_price_eur * i.quantity for i in items)
        eta_days = goal.urgency_days or 3
        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "Inventory bundle optimization",
            extra={
                "event": "inventory.optimize_bundle",
                "goal_id": goal.goal_id,
                "items": len(items),
                "total_price_eur": total_price,
                "eta_days": eta_days,
                "latency_ms": latency_ms,
            },
        )
        return InventoryPlan(
            items=items,
            eta_days=eta_days,
            total_price_eur=total_price,
            latency_ms=latency_ms,
        )


__all__: Sequence[str] = [
    "InventoryAgent",
    "InventoryPlan",
    "InventoryPlanItem",
    "InventorySearchContext",
    "Product",
]

