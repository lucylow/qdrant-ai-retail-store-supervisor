from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence


@dataclass(slots=True)
class VariantLift:
    variant_id: str
    expected_lift_pct: float


class LiftModeler:
    """
    Deterministic lift modeling for campaigns.
    """

    def simulate_ab_test(self, variants: Dict[str, str]) -> Dict[str, VariantLift]:
        lifts: Dict[str, VariantLift] = {}
        for idx, (variant_id, _) in enumerate(variants.items()):
            lifts[variant_id] = VariantLift(
                variant_id=variant_id,
                expected_lift_pct=0.05 + 0.02 * float(idx),
            )
        return lifts


__all__: Sequence[str] = ["LiftModeler", "VariantLift"]

