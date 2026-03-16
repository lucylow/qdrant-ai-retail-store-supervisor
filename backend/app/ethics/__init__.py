"""
Ethics layer for the Multi-Agent Store Manager: fairness, transparency, privacy, anti-manipulation.

- Fair pricing & anti-discrimination: see app.agents.guardrails (ethical_pricing_guardrail).
- Transparent decision provenance: ethical_flags and scores on Qdrant payloads (shopping_agents).
- Privacy-first memory: hash user IDs, GDPR-compliant deletion (this package).
- Anti-manipulation: real stock only, deadline validation, real historical success (guardrails).
- Ethical monitoring: metrics and thresholds (monitoring module).
"""

from app.ethics.privacy import hash_user_id, gdpr_delete_user_data
from app.ethics.monitoring import (
    EthicalMonitoringMetrics,
    ETHICAL_DASHBOARD_THRESHOLDS,
    compute_ethical_metrics,
)

__all__ = [
    "hash_user_id",
    "gdpr_delete_user_data",
    "EthicalMonitoringMetrics",
    "ETHICAL_DASHBOARD_THRESHOLDS",
    "compute_ethical_metrics",
]
