"""
TWINT-first Swiss checkout orchestration.
"""
from __future__ import annotations

import os
from typing import Any, Dict

from app.models.swiss_payments import (
    SwissPaymentMethod,
    SwissPaymentRequest,
    TWINTPaymentRequest,
)
from app.gateways.twint_gateway import TWINTGateway
from app.gateways.postfinance_gateway import PostFinanceGateway
from app.gateways.wallet_gateway import SwissWalletGateway


def _twint_gateway() -> TWINTGateway:
    return TWINTGateway(
        api_key=os.getenv("TWINT_API_KEY", ""),
        merchant_id=os.getenv("TWINT_MERCHANT_ID", ""),
    )


def _postfinance_gateway() -> PostFinanceGateway:
    return PostFinanceGateway(
        pspid=os.getenv("POSTFINANCE_PSPID", ""),
        sha_in=os.getenv("POSTFINANCE_SHA_IN", ""),
        sha_out=os.getenv("POSTFINANCE_SHA_OUT", ""),
    )


def _wallet_gateway() -> SwissWalletGateway:
    return SwissWalletGateway(stripe_secret=os.getenv("STRIPE_SECRET", ""))


class SwissCheckoutService:
    """TWINT-first, then PostFinance, Apple Pay fallback."""

    async def process_checkout(self, request: SwissPaymentRequest) -> Dict[str, Any]:
        if request.payment_method == SwissPaymentMethod.TWINT:
            if isinstance(request, TWINTPaymentRequest):
                return await _twint_gateway().create_payment(request)
            raise ValueError("TWINT requires TWINTPaymentRequest with phone_hash")

        if request.payment_method == SwissPaymentMethod.POSTFINANCE_EFINANCE:
            return await _postfinance_gateway().create_hosted_payment(request)

        if request.payment_method == SwissPaymentMethod.APPLE_PAY:
            token = request.apple_pay_token or {}
            return await _wallet_gateway().process_apple_pay(request, token)

        raise ValueError(f"Unsupported payment method: {request.payment_method}")
