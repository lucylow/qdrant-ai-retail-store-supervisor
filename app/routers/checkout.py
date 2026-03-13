"""
Swiss checkout API: TWINT, PostFinance, Apple Pay.
"""
from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
from typing import Any, Dict

from fastapi import APIRouter, Form, HTTPException

from app.models.swiss_payments import (
    SwissPaymentMethod,
    SwissPaymentRequest,
    TWINTPaymentRequest,
)
from app.services.checkout_service import SwissCheckoutService

router = APIRouter(prefix="/checkout", tags=["swiss-payments"])


@router.post("/twint")
async def create_twint_payment(
    amount_chf: float = Form(...),
    order_id: str = Form(...),
    phone: str = Form(...),
    tenant: str = Form("coop"),
) -> Dict[str, Any]:
    """TWINT QR code checkout (52% Swiss preference)."""
    phone_hash = sha256(phone.encode()).hexdigest()
    request = TWINTPaymentRequest(
        amount_chf=Decimal(str(amount_chf)),
        order_id=order_id,
        phone_hash=phone_hash,
        tenant=tenant,
        payment_method=SwissPaymentMethod.TWINT,
    )
    result = await SwissCheckoutService().process_checkout(request)
    return result


@router.post("/postfinance")
async def create_postfinance_payment(
    amount_chf: float = Form(...),
    order_id: str = Form(...),
    tenant: str = Form("coop"),
) -> Dict[str, Any]:
    """PostFinance E-Finance hosted payment page."""
    request = SwissPaymentRequest(
        amount_chf=Decimal(str(amount_chf)),
        order_id=order_id,
        tenant=tenant,
        payment_method=SwissPaymentMethod.POSTFINANCE_EFINANCE,
    )
    result = await SwissCheckoutService().process_checkout(request)
    return {"redirect_url": result.get("hosted_payment_url"), **result}


@router.post("/webhook/twint")
async def twint_webhook(payload: Dict[str, Any]) -> Dict[str, str]:
    """TWINT payment notification (production: update order status)."""
    _ = payload.get("payment_id"), payload.get("status")
    return {"status": "received"}
