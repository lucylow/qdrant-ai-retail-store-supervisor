from __future__ import annotations

from typing import Any, Dict


class RetailSupervisor:
    """
    Very lightweight retail-specific routing helper.

    This does not replace the existing generic Supervisor in app.agents.supervisor,
    but can be used by higher-level assistants to choose which vertical agent to
    invoke based on a natural-language task description.
    """

    def route_task(self, task: str | Dict[str, Any]) -> str:
        """
        Route a task description to a high-level agent name.
        """
        if isinstance(task, dict):
            text = str(task.get("text") or task.get("goal") or "")
        else:
            text = task

        lowered = text.lower()

        if "price" in lowered or "pricing" in lowered:
            return "PricingAgent"

        if "promotion" in lowered or "campaign" in lowered or "marketing" in lowered:
            return "MarketingAgent"

        if "inventory" in lowered or "stock" in lowered:
            return "InventoryAgent"

        if "personalized" in lowered or "customer" in lowered:
            return "CustomerAgent"

        return "MerchandisingAgent"


__all__ = ["RetailSupervisor"]

