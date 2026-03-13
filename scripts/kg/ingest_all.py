"""Full KG population: schema + customers + products + transactions + optional Qdrant sync."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

# Ensure project root on path when run as script
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from app.kg.neo4j_client import ProductionNeo4jClient
from app.kg.ontologies.retail import create_retail_schema
from scripts.kg.ingest_customers import ingest_customers, create_similar_customer_links
from scripts.kg.ingest_products import ingest_categories, ingest_products, ingest_competitor_links
from scripts.kg.ingest_transactions import ingest_transactions, ingest_events

logger = logging.getLogger(__name__)


async def ingest_warehouses_suppliers(client: ProductionNeo4jClient) -> None:
    """Create sample Warehouse and Supplier nodes and SUPPLIED_BY / INVENTORY_IN."""
    await client.execute_cypher(
        """
        MERGE (w:Warehouse {id: 'WH1'}) SET w.location = 'Berlin', w.capacity = 10000, w.region = 'EU'
        MERGE (s:Supplier {id: 'SUP1'}) SET s.name = 'Supplier One', s.reliability_score = 0.9, s.region = 'EU'
        WITH 1 AS _
        MATCH (w:Warehouse {id: 'WH1'}), (s:Supplier {id: 'SUP1'})
        MERGE (w)<-[r:SUPPLIED_BY]-(s) SET r.lead_time_days = 7
        """
    )
    await client.execute_cypher(
        """
        MATCH (p:Product), (w:Warehouse {id: 'WH1'})
        MERGE (p)-[r:INVENTORY_IN]->(w) SET r.stock_level = 100, r.reorder_point = 20
        """
    )


async def ingest_campaigns(client: ProductionNeo4jClient) -> None:
    """Create sample Campaign and BOOSTS edges."""
    await client.execute_cypher(
        """
        MERGE (c:Campaign {id: 'camp_1'}) SET c.name = 'Summer Sale', c.start_date = '2025-06-01', c.end_date = '2025-06-30', c.channel = 'web'
        WITH c
        MATCH (p:Product)
        MERGE (c)-[r:BOOSTS]->(p) SET r.lift_pct = 15.0, r.priority = 1
        """
    )


async def sync_kg_to_qdrant(client: ProductionNeo4jClient) -> None:
    """
    Optional: sync KG product/customer context to Qdrant for hybrid search.
    Lightweight: ensure product collection exists; full sync would upsert vectors from KG + text.
    """
    try:
        from app.qdrant_client import get_qdrant_client
        from app.data.collections import ensure_all_collections
        ensure_all_collections()
        q = get_qdrant_client()
        q.get_collections()
        logger.info("Qdrant collections ready for KG hybrid sync.")
    except Exception as e:  # noqa: BLE001
        logger.warning("Qdrant sync skipped: %s", e)


async def full_kg_ingestion() -> None:
    """Production KG population from all sources."""
    client = ProductionNeo4jClient()
    try:
        await create_retail_schema(client)

        segments = [{"id": "seg_1", "name": "High value EU", "criteria": "region=EU, rf>50"}]
        customers = [
            {"id": "cust_001", "loyalty_tier": "gold", "rf_score": 85, "region": "EU", "segment_id": "seg_1"},
            {"id": "cust_002", "loyalty_tier": "silver", "rf_score": 60, "region": "EU", "segment_id": "seg_1"},
        ]
        await ingest_customers(client, customers, segments)
        await create_similar_customer_links(client, [{"customer_id_1": "cust_001", "customer_id_2": "cust_002", "similarity": 0.75}])

        await ingest_categories(client, [{"name": "Electronics", "parent_category": "Root", "level": 1}])
        products = [
            {"id": "prod_1", "sku": "SKU1", "name": "Widget A", "category": "Electronics", "brand": "Acme", "price": 29.99, "cost": 15.0},
            {"id": "prod_2", "sku": "SKU2", "name": "Widget B", "category": "Electronics", "brand": "Acme", "price": 39.99, "cost": 20.0},
        ]
        await ingest_products(client, products, [{"product_id": "prod_1", "category_name": "Electronics"}, {"product_id": "prod_2", "category_name": "Electronics"}])
        await ingest_competitor_links(client, [{"product_id_1": "prod_1", "product_id_2": "prod_2", "similarity": 0.8}])

        await ingest_transactions(client, [
            {"customer_id": "cust_001", "product_id": "prod_1", "quantity": 2, "timestamp": "2025-01-15T10:00:00", "amount": 59.98},
            {"customer_id": "cust_002", "product_id": "prod_2", "quantity": 1, "timestamp": "2025-01-16T11:00:00", "amount": 39.99},
        ])

        await ingest_warehouses_suppliers(client)
        await ingest_campaigns(client)

        await sync_kg_to_qdrant(client)

        result = await client.execute_cypher("MATCH (n) RETURN count(n) AS total")
        rel_result = await client.execute_cypher("MATCH ()-[r]->() RETURN count(r) AS total")
        node_count = int(result.records[0].get("total", 0) or 0) if result.records else 0
        rel_count = int(rel_result.records[0].get("total", 0) or 0) if rel_result.records else 0
        logger.info("Retail Knowledge Graph: %s nodes, %s relationships", node_count, rel_count)
        print("Retail Knowledge Graph: {} nodes, {} relationships".format(node_count, rel_count))
    finally:
        client.close()


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    asyncio.run(full_kg_ingestion())
    print("KG ingestion complete.")


if __name__ == "__main__":
    main()
