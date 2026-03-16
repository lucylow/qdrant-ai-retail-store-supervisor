"""Cypher + RAG fusion: use Cypher query results as context for LLM/generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.kg.neo4j_client import ProductionNeo4jClient
from app.kg.agents.reasoner import KGReasonerAgent


@dataclass
class CypherRAGContext:
    """Structured context from Cypher for RAG."""

    query: str
    cypher_used: Optional[str] = None
    records: List[Dict[str, Any]] = None
    summary: Optional[Dict[str, int]] = None

    def __post_init__(self) -> None:
        if self.records is None:
            self.records = []

    def to_text(self, max_records: int = 20) -> str:
        """Flatten to string for LLM context."""
        lines = [f"Query: {self.query}"]
        if self.cypher_used:
            lines.append(f"Cypher: {self.cypher_used}")
        for i, r in enumerate(self.records[:max_records]):
            lines.append(f"  {i+1}. {r}")
        if self.summary:
            lines.append(f"Summary: {self.summary}")
        return "\n".join(lines)


class CypherRAGFusion:
    """
    Run Cypher (via reasoner or raw), then format results as RAG context for downstream agents.
    """

    def __init__(self, neo4j_client: Optional[ProductionNeo4jClient] = None) -> None:
        from app.kg.neo4j_client import ProductionNeo4jClient as DefaultNeo4j
        self.neo4j = neo4j_client or DefaultNeo4j()
        self.reasoner = KGReasonerAgent(self.neo4j)

    async def get_context_for_customer(
        self,
        query: str,
        customer_id: str,
        include_recommendations: bool = True,
        include_similar_customers: bool = False,
    ) -> CypherRAGContext:
        """Build RAG context from KG for a customer-centric query."""
        records: List[Dict[str, Any]] = []
        cypher_used: Optional[str] = None
        summary: Dict[str, int] = {}

        if include_recommendations:
            recs = await self.reasoner.product_recommendation_paths(customer_id, max_results=15)
            records.extend(recs)
        if include_similar_customers:
            sim = await self.reasoner.find_similar_customers(customer_id, max_results=5)
            records.extend([{"similar_customer": r} for r in sim])

        return CypherRAGContext(
            query=query,
            cypher_used=cypher_used,
            records=records,
            summary=summary or {"record_count": len(records)},
        )

    async def get_context_for_product(
        self,
        query: str,
        product_id: str,
        include_competitors: bool = True,
        include_inventory: bool = True,
    ) -> CypherRAGContext:
        """Build RAG context from KG for a product-centric query."""
        records: List[Dict[str, Any]] = []
        if include_competitors:
            comp = await self.reasoner.competitor_products(product_id, max_results=10)
            records.extend(comp)
        if include_inventory:
            inv = await self.reasoner.inventory_paths(product_id, max_results=10)
            records.extend(inv)
        return CypherRAGContext(
            query=query,
            records=records,
            summary={"record_count": len(records)},
        )

    async def run_cypher_and_context(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> CypherRAGContext:
        """Execute raw Cypher and return as RAG context."""
        result = await self.neo4j.execute_cypher(cypher, parameters)
        return CypherRAGContext(
            query="",
            cypher_used=cypher,
            records=result.records,
            summary=result.summary,
        )
