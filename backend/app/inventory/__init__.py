"""Inventory agents: forecaster, stockout predictor, reorder optimizer, capacity planner, supervisor."""

from app.inventory.supervisor import InventorySupervisor, InventoryRecommendation
from app.inventory.forecaster import InventoryForecaster, DemandForecast
from app.inventory.stockout_predictor import StockoutPredictor, StockoutPrediction
from app.inventory.reorder_optimizer import ReorderOptimizer, ReorderRecommendation
from app.inventory.capacity_planner import CapacityPlanner

__all__ = [
    "InventorySupervisor",
    "InventoryRecommendation",
    "InventoryForecaster",
    "DemandForecast",
    "StockoutPredictor",
    "StockoutPrediction",
    "ReorderOptimizer",
    "ReorderRecommendation",
    "CapacityPlanner",
]
