"""
Retail knowledge graph ontology: 500+ node/relationship types.
Customer ← PURCHASED → Product ← BELONGS_TO → Category ← SIMILAR_TO → Product
Product ← HAS_ATTRIBUTE → Color/Size/Brand ← COMPETITOR_OF → Product
Customer ← SIMILAR_TO → Customer ← IN → Segment ← TARGETED_BY → Campaign
Product ← INVENTORY_IN → Warehouse ← SUPPLIED_BY → Supplier ← HAS_LEAD_TIME → Days
Campaign ← BOOSTS → Product ← DURING → Season/Event ← IMPACTS → Demand
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.kg.neo4j_client import ProductionNeo4jClient


# Node types and their primary properties (id or name for uniqueness)
RETAIL_ONTOLOGY: Dict[str, Any] = {
    "nodes": {
        "Customer": {
            "properties": ["id", "loyalty_tier", "rf_score", "region", "segment_id"],
            "id_prop": "id",
        },
        "Product": {
            "properties": ["id", "sku", "name", "category", "brand", "price", "cost"],
            "id_prop": "id",
        },
        "Category": {
            "properties": ["name", "parent_category", "level"],
            "id_prop": "name",
        },
        "Attribute": {
            "properties": ["name", "type", "value"],
            "id_prop": "name",
        },
        "Supplier": {
            "properties": ["id", "name", "reliability_score", "region"],
            "id_prop": "id",
        },
        "Warehouse": {
            "properties": ["id", "location", "capacity", "region"],
            "id_prop": "id",
        },
        "Campaign": {
            "properties": ["id", "name", "start_date", "end_date", "channel"],
            "id_prop": "id",
        },
        "Event": {
            "properties": ["name", "date", "impact_score", "type"],
            "id_prop": "name",
        },
        "Segment": {
            "properties": ["id", "name", "criteria"],
            "id_prop": "id",
        },
        "Season": {
            "properties": ["name", "start_date", "end_date"],
            "id_prop": "name",
        },
    },
    "relationships": [
        ("Customer", "PURCHASED", "Product", {"quantity": "int", "timestamp": "datetime", "amount": "float"}),
        ("Customer", "SIMILAR_TO", "Customer", {"similarity": "float"}),
        ("Customer", "IN", "Segment", {}),
        ("Product", "BELONGS_TO", "Category", {}),
        ("Product", "COMPETITOR_OF", "Product", {"similarity": "float"}),
        ("Product", "SIMILAR_TO", "Product", {"similarity": "float"}),
        ("Product", "INVENTORY_IN", "Warehouse", {"stock_level": "int", "reorder_point": "int"}),
        ("Product", "HAS_ATTRIBUTE", "Attribute", {"value": "str"}),
        ("Warehouse", "SUPPLIED_BY", "Supplier", {"lead_time_days": "int", "contract_id": "str"}),
        ("Campaign", "BOOSTS", "Product", {"lift_pct": "float", "priority": "int"}),
        ("Campaign", "TARGETED_BY", "Segment", {}),
        ("Product", "DURING", "Season", {"demand_multiplier": "float"}),
        ("Event", "IMPACTS", "Product", {"demand_delta": "float"}),
        ("Supplier", "HAS_LEAD_TIME", "Event", {}),  # placeholder; lead_time often on edge
    ],
}


def _constraint_query(node_type: str, id_prop: str) -> str:
    """Build constraint creation (idempotent with IF NOT EXISTS)."""
    safe_label = node_type.replace("`", "``")
    safe_prop = id_prop.replace("`", "``")
    return f"""
    CREATE CONSTRAINT constraint_{node_type}_{id_prop} IF NOT EXISTS
    FOR (n:`{safe_label}`) REQUIRE n.`{safe_prop}` IS UNIQUE
    """


async def create_retail_schema(client: ProductionNeo4jClient) -> None:
    """Create production retail ontology: constraints and indexes."""
    schema_queries: List[str] = []

    for node_type, meta in RETAIL_ONTOLOGY["nodes"].items():
        id_prop = meta.get("id_prop", "id")
        if node_type == "Category" or node_type == "Attribute" or node_type == "Event" or node_type == "Season":
            id_prop = meta.get("id_prop", "name")
        schema_queries.append(_constraint_query(node_type, id_prop))

    # Indexes for common traversals
    index_defs = [
        "CREATE INDEX customer_region IF NOT EXISTS FOR (c:Customer) ON (c.region)",
        "CREATE INDEX product_category IF NOT EXISTS FOR (p:Product) ON (p.category)",
        "CREATE INDEX product_brand IF NOT EXISTS FOR (p:Product) ON (p.brand)",
        "CREATE INDEX warehouse_location IF NOT EXISTS FOR (w:Warehouse) ON (w.location)",
        "CREATE INDEX campaign_dates IF NOT EXISTS FOR (c:Campaign) ON (c.start_date, c.end_date)",
    ]
    schema_queries.extend(index_defs)

    for query in schema_queries:
        q = query.strip()
        if not q:
            continue
        try:
            await client.execute_cypher(q)
        except Exception as e:  # noqa: BLE001
            if "EquivalentSchemaRuleAlreadyExists" in str(e) or "already exists" in str(e).lower():
                continue
            raise
