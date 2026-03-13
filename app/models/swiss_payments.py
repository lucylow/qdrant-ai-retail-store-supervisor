"""
Swiss payment methods: TWINT, PostFinance E-Finance, Apple Pay, etc.
"""
from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class SwissPaymentMethod(Enum):
    TWINT = "twint"  # 52% Swiss market share
    POSTFINANCE_EFINANCE = "postfinance_efinance"  # 32%
    POSTFINANCE_TWINT = "postfinance_twint"  # PostFinance TWINT
    APPLE_PAY = "apple_pay"  # iPhone dominance
    GOOGLE_PAY = "google_pay"
    CREDIT_CARD = "credit_card"  # Visa/Mastercard (low usage)
    INVOICE = "invoice"  # B2B/Swiss corporates
    BANK_TRANSFER = "bank_transfer"  # PostFinance


class PaymentStatus(Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"


class SwissPaymentRequest(BaseModel):
    amount_chf: Decimal
    currency: str = "CHF"
    tenant: str  # "coop", "migros"
    payment_method: SwissPaymentMethod
    order_id: str
    customer_reference: Optional[str] = None  # TWINT phone number hash
    apple_pay_token: Optional[Dict[str, Any]] = None
    postfinance_pspid: Optional[str] = None

    def tenant_language(self) -> str:
        """Default language for tenant (for PostFinance hosted page)."""
        from app.models.swiss_culture import SWISS_RETAILERS

        culture = SWISS_RETAILERS.get(self.tenant)
        if culture and culture.primary_languages:
            return culture.primary_languages[0].value
        return "de"


class TWINTPaymentRequest(SwissPaymentRequest):
    phone_hash: str  # SHA256("41791234567")
    qr_code_url: Optional[str] = None


class PostFinancePaymentRequest(SwissPaymentRequest):
    efinance_id: str
    twint_id: Optional[str] = None
