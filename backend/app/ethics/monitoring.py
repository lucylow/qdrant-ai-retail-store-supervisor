"""
Ethical monitoring dashboard: metrics, thresholds, and recommended actions.

Metrics and thresholds per the ethics spec:
- Price variance/region ±5% → Alert merchant
- Memory reuse rate >95% same user → Privacy review
- Low-confidence escalations >20% goals → Model retraining
- Human override rate >10% → Guardrail audit
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Thresholds for the ethical monitoring dashboard
ETHICAL_DASHBOARD_THRESHOLDS = {
    "price_variance_region_pct": 0.05,   # ±5%; alert merchant if exceeded
    "memory_reuse_same_user_pct": 0.95,   # >95% → privacy review
    "low_confidence_escalations_pct": 0.20,  # >20% goals → model retraining
    "human_override_rate_pct": 0.10,      # >10% → guardrail audit
}


@dataclass
class EthicalMonitoringMetrics:
    """Snapshot of ethical metrics for dashboard or alerts."""
    price_variance_region_pct: float = 0.0
    memory_reuse_same_user_pct: float = 0.0
    low_confidence_escalations_pct: float = 0.0
    human_override_rate_pct: float = 0.0
    alerts: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "price_variance_region_pct": self.price_variance_region_pct,
            "memory_reuse_same_user_pct": self.memory_reuse_same_user_pct,
            "low_confidence_escalations_pct": self.low_confidence_escalations_pct,
            "human_override_rate_pct": self.human_override_rate_pct,
            "alerts": self.alerts,
        }


def compute_ethical_metrics(
    *,
    price_variance_by_region: Optional[Dict[str, float]] = None,
    total_goals: int = 0,
    goals_with_low_confidence_escalation: int = 0,
    total_solutions_shown: int = 0,
    solutions_with_human_override: int = 0,
    memory_reuse_same_user_count: int = 0,
    memory_reuse_total_count: int = 0,
) -> EthicalMonitoringMetrics:
    """
    Compute ethical dashboard metrics and attach alerts when thresholds are exceeded.

    Caller should supply aggregates (e.g. from guardrail logs, episode payloads).
    """
    alerts: List[Dict[str, Any]] = []

    # Price variance: max absolute variance across regions (e.g. CH/DE/AT)
    price_variance_region_pct = 0.0
    if price_variance_by_region:
        for region, variance_pct in price_variance_by_region.items():
            abs_pct = abs(variance_pct)
            if abs_pct > price_variance_region_pct:
                price_variance_region_pct = abs_pct
        if price_variance_region_pct > ETHICAL_DASHBOARD_THRESHOLDS["price_variance_region_pct"]:
            alerts.append({
                "metric": "price_variance_region",
                "threshold_pct": ETHICAL_DASHBOARD_THRESHOLDS["price_variance_region_pct"] * 100,
                "value_pct": price_variance_region_pct * 100,
                "action": "Alert merchant",
            })

    # Low-confidence escalations
    low_confidence_escalations_pct = 0.0
    if total_goals > 0 and goals_with_low_confidence_escalation is not None:
        low_confidence_escalations_pct = goals_with_low_confidence_escalation / total_goals
        if low_confidence_escalations_pct > ETHICAL_DASHBOARD_THRESHOLDS["low_confidence_escalations_pct"]:
            alerts.append({
                "metric": "low_confidence_escalations",
                "threshold_pct": ETHICAL_DASHBOARD_THRESHOLDS["low_confidence_escalations_pct"] * 100,
                "value_pct": low_confidence_escalations_pct * 100,
                "action": "Model retraining",
            })

    # Human override rate
    human_override_rate_pct = 0.0
    if total_solutions_shown > 0 and solutions_with_human_override is not None:
        human_override_rate_pct = solutions_with_human_override / total_solutions_shown
        if human_override_rate_pct > ETHICAL_DASHBOARD_THRESHOLDS["human_override_rate_pct"]:
            alerts.append({
                "metric": "human_override_rate",
                "threshold_pct": ETHICAL_DASHBOARD_THRESHOLDS["human_override_rate_pct"] * 100,
                "value_pct": human_override_rate_pct * 100,
                "action": "Guardrail audit",
            })

    # Memory reuse (same user) → privacy review if >95%
    memory_reuse_same_user_pct = 0.0
    if memory_reuse_total_count > 0 and memory_reuse_same_user_count is not None:
        memory_reuse_same_user_pct = memory_reuse_same_user_count / memory_reuse_total_count
        if memory_reuse_same_user_pct > ETHICAL_DASHBOARD_THRESHOLDS["memory_reuse_same_user_pct"]:
            alerts.append({
                "metric": "memory_reuse_rate",
                "threshold_pct": ETHICAL_DASHBOARD_THRESHOLDS["memory_reuse_same_user_pct"] * 100,
                "value_pct": memory_reuse_same_user_pct * 100,
                "action": "Privacy review",
            })

    return EthicalMonitoringMetrics(
        price_variance_region_pct=price_variance_region_pct,
        memory_reuse_same_user_pct=memory_reuse_same_user_pct,
        low_confidence_escalations_pct=low_confidence_escalations_pct,
        human_override_rate_pct=human_override_rate_pct,
        alerts=alerts,
    )
