"""Price decision explainability and provenance for auditing."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class PriceProvenanceStep:
    """Single step in price decision chain."""
    agent: str
    input_summary: str
    output_summary: str
    timestamp: str


def build_price_provenance(
    sku: str,
    base_price: float,
    dynamic_price: float,
    elasticity: float,
    competitor_prices: List[float],
    recommended_action: str,
    steps: List[PriceProvenanceStep] | None = None,
) -> Dict[str, Any]:
    """Build explainability payload for a price recommendation."""
    return {
        "sku": sku,
        "base_price": base_price,
        "dynamic_price": dynamic_price,
        "elasticity": elasticity,
        "competitor_prices": competitor_prices,
        "recommended_action": recommended_action,
        "steps": [{"agent": s.agent, "input": s.input_summary, "output": s.output_summary} for s in (steps or [])],
        "generated_at": datetime.utcnow().isoformat(),
    }
