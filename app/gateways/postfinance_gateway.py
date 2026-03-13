"""
PostFinance E-Finance / TWINT (Swiss bank #1) hosted payment.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any, Dict

from app.models.swiss_payments import SwissPaymentRequest, PaymentStatus


class PostFinanceGateway:
    """PostFinance hosted payment page (SHA-256 signature)."""

    def __init__(
        self,
        pspid: str = "",
        sha_in: str = "",
        sha_out: str = "",
    ):
        self.PSPID = pspid or "your_postfinance_pspid"
        self.SHA_IN_SIGNATURE = sha_in or "your_sha_in_key"
        self.SHA_OUT_SIGNATURE = sha_out or "your_sha_out_key"

    async def create_hosted_payment(
        self, request: SwissPaymentRequest
    ) -> Dict[str, Any]:
        """Redirect to PostFinance hosted payment page."""
        amount_cents = f"{int(float(request.amount_chf) * 100):d}"
        lang = request.tenant_language()

        params = {
            "PSPID": self.PSPID,
            "ORDERID": request.order_id,
            "AMOUNT": amount_cents,
            "CURRENCY": "CHF",
            "LANGUAGE": lang,
            "ACCEPTURL": "https://your-retail.ch/postfinance/success",
            "DECLINEURL": "https://your-retail.ch/postfinance/decline",
            "EXCEPTIONURL": "https://your-retail.ch/postfinance/exception",
            "CANCELURL": "https://your-retail.ch/postfinance/cancel",
        }
        sig_string = (
            "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            + self.SHA_IN_SIGNATURE
        )
        params["SHASIGN"] = sha256(sig_string.encode()).hexdigest().upper()

        return {
            "hosted_payment_url": (
                f"https://e-payment.postfinance.ch/ncol/{self.PSPID}/orderstandard_utf-8.aspx"
            ),
            "form_params": params,
            "status": PaymentStatus.PENDING.value,
        }
