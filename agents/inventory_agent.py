from typing import Any, Dict, List


class InventoryAgent:
    """
    Domain agent focused on stock health and inventory risk.
    """

    def detect_stock_risk(self, inventory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []

        for item in inventory:
            stock = item.get("stock", 0)
            reorder_point = item.get("reorder_point", 0)

            if stock < reorder_point:
                alerts.append(
                    {
                        "product": item.get("name", ""),
                        "stock": stock,
                        "reorder_point": reorder_point,
                    }
                )

        return alerts

