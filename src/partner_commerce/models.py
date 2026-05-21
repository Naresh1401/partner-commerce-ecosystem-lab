from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field


class NormalizedOffer(BaseModel):
    sku: str
    title: str
    price: Decimal
    currency: str = "USD"
    availability: Literal["in_stock", "out_of_stock", "limited"]
    partner_id: str
    source_ref: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class PartnerOnboardingPlan(BaseModel):
    partner_id: str
    ecosystem: str
    auth_pattern: Literal["oauth_client_credentials", "api_key", "mtls"]
    checklist: list[str]


class CheckoutMandate(BaseModel):
    mandate_id: str
    shopper_id: str
    merchant_id: str
    checkout_hash: str = Field(min_length=16)
    max_total: Decimal
    currency: str = "USD"
    expires_at_epoch: int
    signed_by_trusted_surface: bool


class MandateValidationResult(BaseModel):
    accepted: bool
    reasons: list[str] = Field(default_factory=list)

