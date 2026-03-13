"""
Apple Pay / Google Pay tokenization (Swiss iPhone dominance).
"""
from __future__ import annotations

from typing import Any, Dict

from app.models.swiss_payments import SwissPaymentRequest, PaymentStatus


class SwissWalletGateway:
    """Apple Pay via Stripe (or stub when no Stripe key)."""

    def __init__(self, stripe_secret: str = ""):
        self.stripe_secret = stripe_secret
        self._stripe = None
        if stripe_secret and stripe_secret.startswith("sk_"):
            try:
                import stripe
                stripe.api_key = stripe_secret
                self._stripe = stripe
            except ImportError:
                pass

    async def process_apple_pay(
        self,
        request: SwissPaymentRequest,
        apple_pay_token: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apple Pay tokenization (Swiss card compliance)."""
        if not self._stripe:
            return {
                "client_secret": None,
                "status": PaymentStatus.PENDING.value,
                "message": "Stripe not configured; use TWINT or PostFinance",
            }

        intent = self._stripe.PaymentIntent.create(
            amount=int(float(request.amount_chf) * 100),
            currency="chf",
            payment_method_types=["card"],
            metadata={
                "tenant": request.tenant,
                "order_id": request.order_id,
                "swiss_retailer": "true",
            },
        )
        return {
            "client_secret": intent.get("client_secret"),
            "status": (
                PaymentStatus.AUTHORIZED.value
                if intent.get("status") == "succeeded"
                else PaymentStatus.PENDING.value
            ),
        }
