"""KG Forecaster Agent: graph-aware temporal demand predictions (GNN-style)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.kg.neo4j_client import ProductionNeo4jClient


class KGForecasterAgent:
    """
    Graph-based demand forecasting using KG structure.
    Uses neighborhood aggregation (product category, campaign, events) for temporal predictions.
    Production GNN can be plugged in; here we use a simple heuristic over KG context.
    """

    def __init__(self, neo4j_client: Optional[ProductionNeo4jClient] = None) -> None:
        from app.kg.neo4j_client import ProductionNeo4jClient as DefaultClient
        self.neo4j = neo4j_client or DefaultClient()

    async def get_demand_context(self, product_id: str) -> Dict[str, Any]:
        """Gather KG context for a product: campaigns, events, category, competitors."""
        context: Dict[str, Any] = {"product_id": product_id, "campaign_lift": 0.0, "event_delta": 0.0}
        # Campaign boost sum
        q_campaign = """
        MATCH (camp:Campaign)-[r:BOOSTS]->(p:Product {id: $product_id})
        RETURN sum(r.lift_pct) AS total_lift
        """
        r1 = await self.neo4j.execute_cypher(q_campaign, {"product_id": product_id})
        if r1.records and r1.records[0].get("total_lift") is not None:
            context["campaign_lift"] = float(r1.records[0].get("total_lift", 0) or 0)
        # Event impact sum
        q_event = """
        MATCH (e:Event)-[r:IMPACTS]->(p:Product {id: $product_id})
        RETURN sum(r.demand_delta) AS total_delta
        """
        r2 = await self.neo4j.execute_cypher(q_event, {"product_id": product_id})
        if r2.records and r2.records[0].get("total_delta") is not None:
            context["event_delta"] = float(r2.records[0].get("total_delta", 0) or 0)
        return context

    async def forecast_demand(
        self,
        product_id: str,
        base_demand: float,
        horizon_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Simple graph-informed demand forecast: base_demand * (1 + campaign_lift + event_delta).
        Replace with GNN model for production (+22% accuracy claim).
        """
        ctx = await self.get_demand_context(product_id)
        lift = ctx.get("campaign_lift", 0.0) / 100.0 if ctx.get("campaign_lift") else 0.0
        delta = ctx.get("event_delta", 0.0)
        predicted = base_demand * (1.0 + lift) + delta
        return {
            "product_id": product_id,
            "base_demand": base_demand,
            "predicted_demand": max(0.0, predicted),
            "campaign_lift_pct": ctx.get("campaign_lift", 0.0),
            "event_delta": ctx.get("event_delta", 0.0),
        }
