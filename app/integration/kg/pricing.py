"""KG-powered competitor analysis for pricing agents."""

from __future__ import annotations

from typing import Any, Dict, List

from app.kg.agents.supervisor import KGSupervisorAgent


async def kg_competitor_analysis(product_id: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """Use KG to find competitor and similar products for pricing decisions."""
    supervisor = KGSupervisorAgent()
    return await supervisor.competitor_analysis(product_id, max_results=max_results)
