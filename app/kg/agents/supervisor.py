"""KG Supervisor Agent: coordinates KG reasoning across all 25+ store agents."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.kg.neo4j_client import ProductionNeo4jClient
from app.kg.agents.reasoner import KGReasonerAgent
from app.kg.agents.embedder import KGEmbedderAgent
from app.kg.agents.forecaster import KGForecasterAgent
from app.kg.agents.validator_agent import KGValidatorAgent


class KGSupervisorAgent:
    """
    Single entrypoint for KG capabilities across pricing, inventory, forecasting, personalization.
    Delegates to reasoner, embedder, forecaster, validator.
    """

    def __init__(self, neo4j_client: Optional[ProductionNeo4jClient] = None) -> None:
        self.neo4j = neo4j_client or ProductionNeo4jClient()
        self.reasoner = KGReasonerAgent(self.neo4j)
        self.embedder = KGEmbedderAgent()
        self.forecaster = KGForecasterAgent(self.neo4j)
        self.validator = KGValidatorAgent()

    async def similar_customers(self, customer_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        return await self.reasoner.find_similar_customers(customer_id, max_results=max_results)

    async def recommend_products(
        self,
        customer_id: str,
        category_filter: Optional[str] = None,
        max_results: int = 20,
    ) -> List[Dict[str, Any]]:
        return await self.reasoner.product_recommendation_paths(
            customer_id, category_filter=category_filter, max_results=max_results
        )

    async def inventory_paths(self, product_id: str, max_results: int = 20) -> List[Dict[str, Any]]:
        return await self.reasoner.inventory_paths(product_id, max_results=max_results)

    async def competitor_analysis(self, product_id: str, max_results: int = 20) -> List[Dict[str, Any]]:
        return await self.reasoner.competitor_products(product_id, max_results=max_results)

    async def demand_forecast(self, product_id: str, base_demand: float) -> Dict[str, Any]:
        return await self.forecaster.forecast_demand(product_id, base_demand)

    def validate_entity(self, node_type: str, properties: Dict[str, Any]) -> Any:
        return self.validator.validate_node(node_type, properties)

    def validate_rel(
        self,
        from_type: str,
        rel_type: str,
        to_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self.validator.validate_relationship(from_type, rel_type, to_type, properties)

    async def run_cypher(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Any:
        return await self.reasoner.run_cypher(query, parameters)
