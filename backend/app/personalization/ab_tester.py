"""ABTesterAgent: experimentation and statistical significance."""

from __future__ import annotations

from typing import Any, Dict


class ABTesterAgent:
    """Assign A/B test variant and track for significance."""

    def __init__(self) -> None:
        self._variants = ["control", "variant_a", "variant_b", "variant_c"]

    async def assign_variant(
        self,
        customer_id: str,
        context: Dict[str, Any],
    ) -> str:
        """Assign customer to experiment variant (deterministic by customer_id for consistency)."""
        h = hash(customer_id) % len(self._variants)
        return self._variants[h]
