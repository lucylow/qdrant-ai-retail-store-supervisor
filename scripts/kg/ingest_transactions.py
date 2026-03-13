"""Ingest PURCHASED relationships (and optional Event/Season) into KG."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, List

from app.kg.neo4j_client import ProductionNeo4jClient

logger = logging.getLogger(__name__)


async def ingest_transactions(
    client: ProductionNeo4jClient,
    transactions: List[Dict[str, Any]],
) -> None:
    """
    Create PURCHASED edges between Customer and Product.
    transactions: [{"customer_id", "product_id", "quantity", "timestamp", "amount"}, ...]
    """
    for t in transactions:
        await client.execute_cypher(
            """
            MATCH (c:Customer {id: $customer_id}), (p:Product {id: $product_id})
            MERGE (c)-[r:PURCHASED]->(p)
            SET r.quantity = $quantity, r.timestamp = $timestamp, r.amount = $amount
            """,
            {
                "customer_id": t["customer_id"],
                "product_id": t["product_id"],
                "quantity": t.get("quantity", 1),
                "timestamp": t.get("timestamp", ""),
                "amount": t.get("amount"),
            },
        )


async def ingest_events(client: ProductionNeo4jClient, events: List[Dict[str, Any]]) -> None:
    """Create Event nodes and IMPACTS to Product. events: [{"name", "date", "impact_score", "type", "product_id", "demand_delta"}, ...]"""
    for e in events:
        await client.execute_cypher(
            """
            MERGE (ev:Event {name: $name})
            SET ev.date = $date, ev.impact_score = $impact_score, ev.type = $type
            WITH ev
            OPTIONAL MATCH (p:Product {id: $product_id})
            WHERE $product_id IS NOT NULL
            FOREACH (_ IN CASE WHEN p IS NOT NULL THEN [1] ELSE [] END |
                MERGE (ev)-[r:IMPACTS]->(p) SET r.demand_delta = $demand_delta
            )
            """,
            {
                "name": e.get("name"),
                "date": e.get("date", ""),
                "impact_score": e.get("impact_score"),
                "type": e.get("type", ""),
                "product_id": e.get("product_id"),
                "demand_delta": e.get("demand_delta", 0.0),
            },
        )


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    client = ProductionNeo4jClient()
    transactions = [
        {"customer_id": "cust_001", "product_id": "prod_1", "quantity": 2, "timestamp": "2025-01-15T10:00:00", "amount": 59.98},
        {"customer_id": "cust_002", "product_id": "prod_2", "quantity": 1, "timestamp": "2025-01-16T11:00:00", "amount": 39.99},
    ]
    asyncio.run(ingest_transactions(client, transactions))
    client.close()
    logger.info("Transaction ingestion done.")


if __name__ == "__main__":
    main()
