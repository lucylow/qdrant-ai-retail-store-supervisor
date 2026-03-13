# app/geospatial/alerts.py
"""Broadcast inventory/logistics alerts over WebSocket for real-time dashboards."""

from app.geospatial.ws_manager import ws_manager


async def broadcast_inventory_alert(store_id: str, sku: str, qty: int) -> None:
    message = {
        "type": "inventory_alert",
        "store_id": store_id,
        "sku": sku,
        "quantity": qty,
    }
    await ws_manager.broadcast("logistics", message)
