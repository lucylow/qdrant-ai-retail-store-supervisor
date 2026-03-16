"""Ingest customers and segments into the retail KG."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, List

from app.kg.neo4j_client import ProductionNeo4jClient
from app.kg.validator import validate_node

logger = logging.getLogger(__name__)


async def ingest_customers(
    client: ProductionNeo4jClient,
    customers: List[Dict[str, Any]],
    segments: List[Dict[str, Any]],
) -> None:
    """
    Create Customer and Segment nodes and IN relationships.
    customers: [{"id", "loyalty_tier", "rf_score", "region", "segment_id"}, ...]
    segments: [{"id", "name", "criteria"}, ...]
    """
    # Segments first
    for seg in segments:
        v = validate_node("Segment", seg)
        if not v.valid:
            logger.warning("Skip segment %s: %s", seg.get("id"), v.errors)
            continue
        n = v.normalized or seg
        await client.execute_cypher(
            """
            MERGE (s:Segment {id: $id})
            SET s.name = $name, s.criteria = $criteria
            """,
            {"id": n.get("id"), "name": n.get("name", ""), "criteria": n.get("criteria", "")},
        )

    for c in customers:
        v = validate_node("Customer", c)
        if not v.valid:
            logger.warning("Skip customer %s: %s", c.get("id"), v.errors)
            continue
        n = v.normalized or c
        seg_id = n.get("segment_id")
        await client.execute_cypher(
            """
            MERGE (c:Customer {id: $id})
            SET c.loyalty_tier = $loyalty_tier, c.rf_score = $rf_score, c.region = $region
            WITH c
            OPTIONAL MATCH (s:Segment {id: $segment_id})
            WHERE $segment_id IS NOT NULL
            FOREACH (_ IN CASE WHEN s IS NOT NULL THEN [1] ELSE [] END |
                MERGE (c)-[:IN]->(s)
            )
            """,
            {
                "id": n.get("id"),
                "loyalty_tier": n.get("loyalty_tier", ""),
                "rf_score": n.get("rf_score"),
                "region": n.get("region", ""),
                "segment_id": seg_id,
            },
        )


async def create_similar_customer_links(
    client: ProductionNeo4jClient,
    pairs: List[Dict[str, Any]],
) -> None:
    """Create SIMILAR_TO edges. pairs: [{"customer_id_1", "customer_id_2", "similarity"}, ...]"""
    for p in pairs:
        await client.execute_cypher(
            """
            MATCH (a:Customer {id: $id1}), (b:Customer {id: $id2})
            MERGE (a)-[r:SIMILAR_TO]-(b)
            SET r.similarity = $similarity
            """,
            {"id1": p["customer_id_1"], "id2": p["customer_id_2"], "similarity": p.get("similarity", 0.8)},
        )


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    client = ProductionNeo4jClient()
    # Example minimal data
    customers = [
        {"id": "cust_001", "loyalty_tier": "gold", "rf_score": 85, "region": "EU", "segment_id": "seg_1"},
        {"id": "cust_002", "loyalty_tier": "silver", "rf_score": 60, "region": "EU", "segment_id": "seg_1"},
    ]
    segments = [{"id": "seg_1", "name": "High value EU", "criteria": "region=EU, rf>50"}]
    asyncio.run(ingest_customers(client, customers, segments))
    asyncio.run(create_similar_customer_links(client, [{"customer_id_1": "cust_001", "customer_id_2": "cust_002", "similarity": 0.75}]))
    client.close()
    logger.info("Customer ingestion done.")


if __name__ == "__main__":
    main()
