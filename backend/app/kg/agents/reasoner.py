"""KG Reasoner Agent: multi-hop relationship traversal and Cypher-backed insights."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.kg.neo4j_client import ProductionNeo4jClient, KGQueryResult
from app.kg.query_engine import KGQueryEngine, QueryTemplate


class KGReasonerAgent:
    """
    Multi-hop reasoning over the retail KG.
    Exposes similar customers, product recommendations, inventory paths, competitor analysis.
    """

    def __init__(self, neo4j_client: Optional[ProductionNeo4jClient] = None) -> None:
        from app.kg.neo4j_client import ProductionNeo4jClient as DefaultClient
        self.neo4j = neo4j_client or DefaultClient()
        self.query_engine = KGQueryEngine(self.neo4j)

    async def find_similar_customers(
        self,
        customer_id: str,
        min_similarity: Optional[float] = None,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Multi-hop customer similarity via SIMILAR_TO traversal."""
        result = await self.query_engine.run(
            QueryTemplate.SIMILAR_CUSTOMERS,
            customer_id=customer_id,
            max_results=max_results,
        )
        return result.records

    async def product_recommendation_paths(
        self,
        customer_id: str,
        category_filter: Optional[str] = None,
        max_results: int = 20,
    ) -> List[Dict[str, Any]]:
        """KG-powered recommendations via PURCHASED/SIMILAR_TO paths (exclude already purchased)."""
        result = await self.query_engine.run(
            QueryTemplate.PRODUCT_RECOMMENDATIONS,
            customer_id=customer_id,
            category_filter=category_filter,
            max_results=max_results,
        )
        return result.records

    async def inventory_paths(self, product_id: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Product → Warehouse → Supplier paths for inventory reasoning."""
        result = await self.query_engine.run(
            QueryTemplate.INVENTORY_PATHS,
            product_id=product_id,
            max_results=max_results,
        )
        return result.records

    async def competitor_products(self, product_id: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Competitor and similar products from KG."""
        result = await self.query_engine.run(
            QueryTemplate.COMPETITOR_PRODUCTS,
            product_id=product_id,
            max_results=max_results,
        )
        return result.records

    async def supplier_warehouse_product(
        self,
        product_id: Optional[str] = None,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """Supplier → Warehouse → Product paths (optional product filter)."""
        result = await self.query_engine.run(
            QueryTemplate.SUPPLIER_WAREHOUSE_PRODUCT,
            product_id=product_id,
            max_results=max_results,
        )
        return result.records

    async def campaign_boosts(self, product_id: Optional[str] = None, max_results: int = 20) -> List[Dict[str, Any]]:
        """Campaigns that boost products."""
        result = await self.query_engine.run(
            QueryTemplate.CAMPAIGN_BOOSTS,
            product_id=product_id,
            max_results=max_results,
        )
        return result.records

    async def customer_segment(self, customer_id: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Segments the customer belongs to."""
        result = await self.query_engine.run(
            QueryTemplate.CUSTOMER_SEGMENT,
            customer_id=customer_id,
            max_results=max_results,
        )
        return result.records

    async def demand_impact_events(self, product_id: Optional[str] = None, max_results: int = 20) -> List[Dict[str, Any]]:
        """Events that impact product demand."""
        result = await self.query_engine.run(
            QueryTemplate.DEMAND_IMPACT,
            product_id=product_id,
            max_results=max_results,
        )
        return result.records

    async def run_cypher(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> KGQueryResult:
        """Execute arbitrary Cypher (for explorer/dashboard)."""
        return await self.neo4j.execute_cypher(query, parameters)
