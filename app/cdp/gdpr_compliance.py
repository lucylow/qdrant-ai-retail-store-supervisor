"""GDPR compliance: consent management and data minimization for personalization."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ConsentRecord:
    """Single consent record for a customer."""

    customer_id: str
    purpose: str  # marketing, personalization, analytics
    granted: bool
    updated_at: datetime
    source: str  # web, mobile, email


class GDPRCompliance:
    """Consent management and data minimization checks."""

    def __init__(self) -> None:
        self._consent_cache: Dict[str, List[ConsentRecord]] = {}

    async def get_consent(self, customer_id: str) -> Dict[str, bool]:
        """Return current consent flags (marketing, personalization, analytics)."""
        # Production: query CDP/consent DB
        if customer_id in self._consent_cache:
            recs = self._consent_cache[customer_id]
            return {
                "marketing": any(r.granted for r in recs if r.purpose == "marketing"),
                "personalization": any(
                    r.granted for r in recs if r.purpose == "personalization"
                ),
                "analytics": any(r.granted for r in recs if r.purpose == "analytics"),
            }
        # Default: allow personalization for demo
        return {"marketing": True, "personalization": True, "analytics": True}

    async def check_recommendation_compliance(
        self,
        customer_id: str,
        recommendations: List[Dict[str, Any]],
        offers: List[Dict[str, Any]],
    ) -> bool:
        """
        Ensure recommendations/offers respect consent and data minimization.
        Returns True if compliant.
        """
        consent = await self.get_consent(customer_id)
        if not consent.get("personalization", True):
            logger.info("Customer %s has no personalization consent", customer_id)
            return len(recommendations) == 0 and len(offers) == 0
        # Data minimization: no PII in payloads
        for rec in recommendations:
            if rec.get("customer_id") and rec["customer_id"] != customer_id:
                return False
        return True

    def record_consent(
        self,
        customer_id: str,
        purpose: str,
        granted: bool,
        source: str = "web",
    ) -> None:
        """Store consent (in-memory for demo; production → DB)."""
        if customer_id not in self._consent_cache:
            self._consent_cache[customer_id] = []
        self._consent_cache[customer_id].append(
            ConsentRecord(
                customer_id=customer_id,
                purpose=purpose,
                granted=granted,
                updated_at=datetime.utcnow(),
                source=source,
            )
        )

    def anonymize_for_analytics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Strip PII for analytics storage (data minimization)."""
        out = dict(payload)
        for key in ("email", "phone", "name", "address", "customer_id"):
            if key in out:
                out[key] = "***" if key != "customer_id" else f"cust_{hash(out[key]) % 10**8}"
        return out
