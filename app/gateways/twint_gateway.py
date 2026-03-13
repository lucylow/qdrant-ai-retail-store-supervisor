"""
TWINT payment gateway (Swiss mobile payment, ~52% market share).
"""
from __future__ import annotations

import io
from hashlib import sha256
from typing import Any, Dict

from app.models.swiss_payments import PaymentStatus, TWINTPaymentRequest

try:
    import qrcode
    HAS_QR = True
except ImportError:
    HAS_QR = False

try:
    import httpx
except ImportError:
    httpx = None


class TWINTGateway:
    """Production-style TWINT integration (sandbox: sandbox-api.twint.ch)."""

    BASE_URL = "https://api.twint.ch/v2"

    def __init__(self, api_key: str = "", merchant_id: str = ""):
        self.api_key = api_key or ""
        self.merchant_id = merchant_id or ""
        self.client = httpx.AsyncClient() if httpx else None

    async def create_payment(self, request: TWINTPaymentRequest) -> Dict[str, Any]:
        """Create TWINT payment with QR code (or placeholder when no API key)."""
        if not self.api_key or not self.client:
            # Stub response for demo/CI
            qr_string = f"twint://pay?order={request.order_id}&amount={request.amount_chf}&chf"
            return {
                "payment_id": f"twint_stub_{request.order_id}",
                "status": PaymentStatus.PENDING.value,
                "qr_string": qr_string,
                "payment_url": qr_string,
                "expires_in": 600,
                "qr_code_png": _make_qr_png(qr_string) if HAS_QR else None,
            }

        payload = {
            "merchant_id": self.merchant_id,
            "amount": float(request.amount_chf),
            "currency": "CHF",
            "order_id": request.order_id,
            "customer_reference": request.phone_hash,
            "return_url": f"https://your-retail.ch/twint/callback/{request.order_id}",
            "notification_url": f"https://your-retail.ch/twint/webhook/{request.order_id}",
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        response = await self.client.post(
            f"{self.BASE_URL}/payments",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        twint_data = response.json()

        qr_string = twint_data.get("qr_string", "")
        qr_bytes = _make_qr_png(qr_string) if HAS_QR and qr_string else None

        return {
            "payment_id": twint_data.get("payment_id", ""),
            "status": PaymentStatus.PENDING.value,
            "qr_code_png": qr_bytes,
            "qr_string": qr_string,
            "payment_url": twint_data.get("payment_url", qr_string),
            "expires_in": twint_data.get("expires_in", 600),
        }

    async def verify_payment(self, payment_id: str) -> PaymentStatus:
        """Poll TWINT status (webhook preferred in production)."""
        if not self.api_key or not self.client:
            return PaymentStatus.PENDING
        response = await self.client.get(
            f"{self.BASE_URL}/payments/{payment_id}",
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        data = response.json()
        return PaymentStatus(data.get("status", "pending"))


def _make_qr_png(qr_string: str) -> bytes:
    if not HAS_QR or not qr_string:
        return b""
    qr = qrcode.make(qr_string)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()
