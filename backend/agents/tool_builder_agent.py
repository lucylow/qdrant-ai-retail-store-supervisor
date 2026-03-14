from typing import Any, Dict, List, Tuple


class ToolBuilderAgent:
    """
    Builds simple, composable Python tools from retail context.
    """

    # --- Inventory tools ---

    def build_inventory_risk_tool(self):
        def inventory_risk(inventory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            risks: List[Dict[str, Any]] = []
            for item in inventory:
                if item.get("stock", 0) < item.get("reorder_point", 0):
                    risks.append(item)
            return risks

        return inventory_risk

    # --- Bundling tools ---

    def build_bundle_tool(self):
        def bundle(products: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
            bundles: List[Tuple[str, str]] = []
            for p in products:
                for q in products:
                    if (
                        p.get("category") == q.get("category")
                        and p.get("id") != q.get("id")
                    ):
                        bundles.append((p.get("name", ""), q.get("name", "")))
            return bundles

        return bundle

