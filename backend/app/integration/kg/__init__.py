"""KG integration across pricing, inventory, personalization, forecasting agents."""

from app.integration.kg.pricing import kg_competitor_analysis
from app.integration.kg.inventory import kg_inventory_paths
from app.integration.kg.personalization import kg_similar_customers, kg_recommendations
from app.integration.kg.forecasting import kg_demand_forecast

__all__ = [
    "kg_competitor_analysis",
    "kg_inventory_paths",
    "kg_similar_customers",
    "kg_recommendations",
    "kg_demand_forecast",
]
