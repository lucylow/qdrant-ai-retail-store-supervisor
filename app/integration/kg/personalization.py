"""KG-powered customer similarity and recommendations for personalization agents."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.kg.agents.supervisor import KGSupervisorAgent


async def kg_similar_customers(customer_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Use KG SIMILAR_TO traversal for similar customers (segmentation, targeting)."""
    supervisor = KGSupervisorAgent()
    return await supervisor.similar_customers(customer_id, max_results=max_results)


async def kg_recommendations(
    customer_id: str,
    category_filter: Optional[str] = None,
    max_results: int = 20,
) -> List[Dict[str, Any]]:
    """Use KG path-based product recommendations (explainable recs)."""
    supervisor = KGSupervisorAgent()
    return await supervisor.recommend_products(
        customer_id, category_filter=category_filter, max_results=max_results
    )
