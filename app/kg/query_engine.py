"""Cypher query generator and parameterized query execution."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from app.kg.neo4j_client import ProductionNeo4jClient, KGQueryResult


class QueryTemplate(str, Enum):
    """Named Cypher templates for retail KG."""

    SIMILAR_CUSTOMERS = "similar_customers"
    PRODUCT_RECOMMENDATIONS = "product_recommendations"
    INVENTORY_PATHS = "inventory_paths"
    COMPETITOR_PRODUCTS = "competitor_products"
    SUPPLIER_WAREHOUSE_PRODUCT = "supplier_warehouse_product"
    CAMPAIGN_BOOSTS = "campaign_boosts"
    CUSTOMER_SEGMENT = "customer_segment"
    DEMAND_IMPACT = "demand_impact"


_TEMPLATES: Dict[str, str] = {
    QueryTemplate.SIMILAR_CUSTOMERS: """
        MATCH (c1:Customer {id: $customer_id})-[:SIMILAR_TO*1..3]-(c2:Customer)
        WHERE c1.id <> c2.id
        RETURN DISTINCT c2.id AS customer_id, c2.rf_score AS rf_score,
               c2.loyalty_tier AS tier, c2.region AS region
        LIMIT $max_results
    """,
    QueryTemplate.PRODUCT_RECOMMENDATIONS: """
        MATCH path = (c:Customer {id: $customer_id})-[:PURCHASED|SIMILAR_TO*1..4]-(p:Product)
        WHERE NOT (c)-[:PURCHASED]->(p)
        OPTIONAL MATCH (p)-[:BELONGS_TO]->(cat:Category)
        WITH p, path, cat
        WHERE $category_filter IS NULL OR cat.name CONTAINS $category_filter OR p.category = $category_filter
        RETURN DISTINCT p.id AS product_id, p.name AS product_name, p.category AS category,
               length(path) AS path_length
        ORDER BY path_length ASC
        LIMIT $max_results
    """,
    QueryTemplate.INVENTORY_PATHS: """
        MATCH (p:Product {id: $product_id})-[r2:INVENTORY_IN]->(w:Warehouse)<-[r1:SUPPLIED_BY]-(s:Supplier)
        RETURN p.id AS product_id, w.id AS warehouse_id, w.location AS location,
               s.id AS supplier_id, s.name AS supplier_name,
               r2.stock_level AS stock_level, r1.lead_time_days AS lead_time_days
        LIMIT $max_results
    """,
    QueryTemplate.COMPETITOR_PRODUCTS: """
        MATCH (p:Product {id: $product_id})-[:COMPETITOR_OF|SIMILAR_TO]-(comp:Product)
        RETURN comp.id AS product_id, comp.name AS name, comp.price AS price, comp.brand AS brand
        LIMIT $max_results
    """,
    QueryTemplate.SUPPLIER_WAREHOUSE_PRODUCT: """
        MATCH (s:Supplier)-[r1:SUPPLIED_BY]->(w:Warehouse)-[r2:INVENTORY_IN]->(p:Product)
        WHERE ($product_id IS NULL) OR (p.id = $product_id)
        RETURN s.id AS supplier_id, s.name AS supplier_name, w.id AS warehouse_id,
               w.location AS location, p.id AS product_id, r2.stock_level AS stock_level
        LIMIT $max_results
    """,
    QueryTemplate.CAMPAIGN_BOOSTS: """
        MATCH (camp:Campaign)-[r:BOOSTS]->(p:Product)
        WHERE $product_id IS NULL OR p.id = $product_id
        RETURN camp.id AS campaign_id, camp.name AS campaign_name, p.id AS product_id,
               r.lift_pct AS lift_pct
        LIMIT $max_results
    """,
    QueryTemplate.CUSTOMER_SEGMENT: """
        MATCH (c:Customer {id: $customer_id})-[:IN]->(seg:Segment)
        RETURN seg.id AS segment_id, seg.name AS segment_name
        LIMIT $max_results
    """,
    QueryTemplate.DEMAND_IMPACT: """
        MATCH (e:Event)-[r:IMPACTS]->(p:Product)
        WHERE $product_id IS NULL OR p.id = $product_id
        RETURN e.name AS event_name, e.date AS date, p.id AS product_id, r.demand_delta AS demand_delta
        LIMIT $max_results
    """,
}


_SUPPLIER_WAREHOUSE = """
MATCH (s:Supplier)-[r1:SUPPLIED_BY]->(w:Warehouse)-[r2:INVENTORY_IN]->(p:Product)
WHERE ($product_id IS NULL) OR (p.id = $product_id)
RETURN s.id AS supplier_id, s.name AS supplier_name, w.id AS warehouse_id,
       w.location AS location, p.id AS product_id, r2.stock_level AS stock_level
LIMIT $max_results
"""
_TEMPLATES[QueryTemplate.SUPPLIER_WAREHOUSE_PRODUCT] = _SUPPLIER_WAREHOUSE


@dataclass
class CypherParams:
    """Typed parameters for Cypher queries."""

    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    category_filter: Optional[str] = None
    max_results: int = 20
    min_similarity: Optional[float] = None


class KGQueryEngine:
    """Generate and execute parameterized Cypher from templates."""

    def __init__(self, client: ProductionNeo4jClient) -> None:
        self.client = client

    def get_query(self, template: QueryTemplate) -> str:
        """Return raw Cypher for a template."""
        return _TEMPLATES.get(template.value, "").strip()

    def _params(self, template: QueryTemplate, **kwargs: Any) -> Dict[str, Any]:
        """Build parameter dict for template."""
        params: Dict[str, Any] = {
            "customer_id": kwargs.get("customer_id"),
            "product_id": kwargs.get("product_id"),
            "category_filter": kwargs.get("category_filter"),
            "max_results": kwargs.get("max_results", 20),
            "min_similarity": kwargs.get("min_similarity"),
        }
        return {k: v for k, v in params.items() if v is not None}

    async def run(
        self,
        template: QueryTemplate,
        **kwargs: Any,
    ) -> KGQueryResult:
        """Execute template with given parameters."""
        query = self.get_query(template)
        params = self._params(template, **kwargs)
        return await self.client.execute_cypher(query, params)
