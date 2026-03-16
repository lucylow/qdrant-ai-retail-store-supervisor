"""Real-time KG updates: listen to events and apply incremental Cypher writes."""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, Callable, Dict, List, Optional

from app.kg.neo4j_client import ProductionNeo4jClient

logger = logging.getLogger(__name__)


class KGContinuousSync:
    """
    Poll or push-based sync: apply batches of node/relationship updates to Neo4j.
    Production: plug in Kafka/Redis stream for event-driven updates.
    """

    def __init__(self, client: ProductionNeo4jClient, batch_size: int = 100) -> None:
        self.client = client
        self.batch_size = batch_size
        self._buffer: List[Dict[str, Any]] = []

    def push(self, event: Dict[str, Any]) -> None:
        """Queue an event for sync. event: {type: 'customer'|'product'|'transaction'|'inventory', ...}"""
        self._buffer.append(event)
        if len(self._buffer) >= self.batch_size:
            asyncio.get_event_loop().create_task(self.flush())

    async def flush(self) -> int:
        """Apply buffered events to Neo4j; return count applied."""
        if not self._buffer:
            return 0
        batch, self._buffer = self._buffer[: self.batch_size], self._buffer[self.batch_size :]
        applied = 0
        for ev in batch:
            try:
                await self._apply_one(ev)
                applied += 1
            except Exception as e:  # noqa: BLE001
                logger.warning("KG sync failed for event %s: %s", ev.get("type"), e)
        return applied

    async def _apply_one(self, event: Dict[str, Any]) -> None:
        t = event.get("type")
        if t == "customer":
            await self.client.execute_cypher(
                "MERGE (c:Customer {id: $id}) SET c += $props",
                {"id": event.get("id"), "props": {k: v for k, v in event.items() if k not in ("type", "id")}},
            )
        elif t == "product":
            await self.client.execute_cypher(
                "MERGE (p:Product {id: $id}) SET p += $props",
                {"id": event.get("id"), "props": {k: v for k, v in event.items() if k not in ("type", "id")}},
            )
        elif t == "transaction":
            await self.client.execute_cypher(
                """
                MATCH (c:Customer {id: $customer_id}), (p:Product {id: $product_id})
                MERGE (c)-[r:PURCHASED]->(p)
                SET r.quantity = $quantity, r.timestamp = $timestamp, r.amount = $amount
                """,
                {
                    "customer_id": event.get("customer_id"),
                    "product_id": event.get("product_id"),
                    "quantity": event.get("quantity", 1),
                    "timestamp": event.get("timestamp", ""),
                    "amount": event.get("amount"),
                },
            )
        elif t == "inventory":
            await self.client.execute_cypher(
                """
                MATCH (p:Product {id: $product_id}), (w:Warehouse {id: $warehouse_id})
                MERGE (p)-[r:INVENTORY_IN]->(w)
                SET r.stock_level = $stock_level
                """,
                {
                    "product_id": event.get("product_id"),
                    "warehouse_id": event.get("warehouse_id"),
                    "stock_level": event.get("stock_level"),
                },
            )
        else:
            logger.debug("Unknown event type: %s", t)


async def run_polling_sync(
    client: ProductionNeo4jClient,
    fetch_events: Callable[[], List[Dict[str, Any]]],
    interval_seconds: float = 60.0,
) -> None:
    """Poll fetch_events every interval and sync to KG."""
    sync = KGContinuousSync(client)
    while True:
        events = fetch_events()
        for e in events:
            sync.push(e)
        await sync.flush()
        await asyncio.sleep(interval_seconds)


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    client = ProductionNeo4jClient()

    async def demo() -> None:
        sync = KGContinuousSync(client, batch_size=5)
        sync.push({"type": "customer", "id": "cust_sync_1", "region": "EU"})
        sync.push({"type": "product", "id": "prod_sync_1", "price": 19.99})
        n = await sync.flush()
        logger.info("Synced %s events", n)

    asyncio.run(demo())
    client.close()


if __name__ == "__main__":
    main()
