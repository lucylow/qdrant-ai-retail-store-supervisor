"""Ingest products, categories, attributes, and COMPETITOR_OF/SIMILAR_TO/BELONGS_TO into KG."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, List

from app.kg.neo4j_client import ProductionNeo4jClient
from app.kg.validator import validate_node

logger = logging.getLogger(__name__)


async def ingest_categories(client: ProductionNeo4jClient, categories: List[Dict[str, Any]]) -> None:
    """Create Category nodes. categories: [{"name", "parent_category", "level"}, ...]"""
    for c in categories:
        v = validate_node("Category", c)
        if not v.valid:
            logger.warning("Skip category %s: %s", c.get("name"), v.errors)
            continue
        n = v.normalized or c
        await client.execute_cypher(
            """
            MERGE (cat:Category {name: $name})
            SET cat.parent_category = $parent_category, cat.level = $level
            """,
            {"name": n.get("name"), "parent_category": n.get("parent_category", ""), "level": n.get("level", 0)},
        )


async def ingest_products(
    client: ProductionNeo4jClient,
    products: List[Dict[str, Any]],
    category_links: List[Dict[str, str]],
) -> None:
    """
    Create Product nodes and BELONGS_TO to Category.
    products: [{"id", "sku", "name", "category", "brand", "price", "cost"}, ...]
    category_links: [{"product_id", "category_name"}, ...]
    """
    for p in products:
        v = validate_node("Product", p)
        if not v.valid:
            logger.warning("Skip product %s: %s", p.get("id"), v.errors)
            continue
        n = v.normalized or p
        await client.execute_cypher(
            """
            MERGE (p:Product {id: $id})
            SET p.sku = $sku, p.name = $name, p.category = $category, p.brand = $brand, p.price = $price, p.cost = $cost
            """,
            {
                "id": n.get("id"),
                "sku": n.get("sku", ""),
                "name": n.get("name", ""),
                "category": n.get("category", ""),
                "brand": n.get("brand", ""),
                "price": n.get("price"),
                "cost": n.get("cost"),
            },
        )

    for link in category_links:
        await client.execute_cypher(
            """
            MATCH (p:Product {id: $product_id}), (c:Category {name: $category_name})
            MERGE (p)-[:BELONGS_TO]->(c)
            """,
            {"product_id": link["product_id"], "category_name": link["category_name"]},
        )


async def ingest_competitor_links(
    client: ProductionNeo4jClient,
    pairs: List[Dict[str, Any]],
) -> None:
    """Create COMPETITOR_OF edges. pairs: [{"product_id_1", "product_id_2", "similarity"}, ...]"""
    for p in pairs:
        await client.execute_cypher(
            """
            MATCH (a:Product {id: $id1}), (b:Product {id: $id2})
            MERGE (a)-[r:COMPETITOR_OF]-(b)
            SET r.similarity = $similarity
            """,
            {"id1": p["product_id_1"], "id2": p["product_id_2"], "similarity": p.get("similarity", 0.7)},
        )


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    client = ProductionNeo4jClient()
    categories = [
        {"name": "Electronics", "parent_category": "Root", "level": 1},
        {"name": "Apparel", "parent_category": "Root", "level": 1},
    ]
    asyncio.run(ingest_categories(client, categories))
    products = [
        {"id": "prod_1", "sku": "SKU1", "name": "Widget A", "category": "Electronics", "brand": "Acme", "price": 29.99, "cost": 15.0},
        {"id": "prod_2", "sku": "SKU2", "name": "Widget B", "category": "Electronics", "brand": "Acme", "price": 39.99, "cost": 20.0},
    ]
    links = [{"product_id": "prod_1", "category_name": "Electronics"}, {"product_id": "prod_2", "category_name": "Electronics"}]
    asyncio.run(ingest_products(client, products, links))
    asyncio.run(ingest_competitor_links(client, [{"product_id_1": "prod_1", "product_id_2": "prod_2", "similarity": 0.8}]))
    client.close()
    logger.info("Product ingestion done.")


if __name__ == "__main__":
    main()
