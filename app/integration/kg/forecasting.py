"""KG-powered demand forecasting (GNN-style context) for forecasting agents."""

from __future__ import annotations

from typing import Any, Dict

from app.kg.agents.supervisor import KGSupervisorAgent


async def kg_demand_forecast(product_id: str, base_demand: float) -> Dict[str, Any]:
    """
    Use KG campaign/event context for demand prediction.
    Integrates with dynamic_pricing/demand_elasticity and forecasting pipelines.
    """
    supervisor = KGSupervisorAgent()
    return await supervisor.demand_forecast(product_id, base_demand)
