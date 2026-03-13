"""KG-powered supplier → warehouse → product paths for inventory agents."""

from __future__ import annotations

from typing import Any, Dict, List

from app.kg.agents.supervisor import KGSupervisorAgent


async def kg_inventory_paths(product_id: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """
    Use KG to get Product → Warehouse → Supplier paths (stock_level, lead_time_days).
    Integrates with inventory_agent and inventory_worker.
    """
    supervisor = KGSupervisorAgent()
    return await supervisor.inventory_paths(product_id, max_results=max_results)
