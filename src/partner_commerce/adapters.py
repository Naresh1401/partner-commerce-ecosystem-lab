from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any

from partner_commerce.models import NormalizedOffer, PartnerOnboardingPlan


class PartnerAdapter(ABC):
    partner_id: str
    ecosystem: str

    @abstractmethod
    def normalize_offer(self, payload: dict[str, Any]) -> NormalizedOffer:
        raise NotImplementedError

    def onboarding_plan(self) -> PartnerOnboardingPlan:
        return PartnerOnboardingPlan(
            partner_id=self.partner_id,
            ecosystem=self.ecosystem,
            auth_pattern="oauth_client_credentials",
            checklist=[
                "Create sandbox app and credentials",
                "Document auth scopes and token lifecycle",
                "Map catalog, offer, inventory, checkout, and order status objects",
                "Configure webhook signing secret and replay window",
                "Run contract tests against partner sandbox",
                "Define retry, timeout, rate limit, and escalation behavior",
            ],
        )


class ShopifyLikeAdapter(PartnerAdapter):
    partner_id = "shopify_like"
    ecosystem = "commerce_platform"

    def normalize_offer(self, payload: dict[str, Any]) -> NormalizedOffer:
        variant = payload["variants"][0]
        return NormalizedOffer(
            sku=variant["sku"],
            title=payload["title"],
            price=Decimal(str(variant["price"])),
            availability="in_stock" if variant.get("inventory_quantity", 0) > 0 else "out_of_stock",
            partner_id=self.partner_id,
            source_ref=str(payload["id"]),
            attributes={"vendor": payload.get("vendor"), "product_type": payload.get("product_type")},
        )


class MarketplaceLikeAdapter(PartnerAdapter):
    partner_id = "marketplace_like"
    ecosystem = "large_partner_marketplace"

    def normalize_offer(self, payload: dict[str, Any]) -> NormalizedOffer:
        return NormalizedOffer(
            sku=payload["sellerSku"],
            title=payload["item"]["name"],
            price=Decimal(str(payload["offer"]["amount"])),
            currency=payload["offer"].get("currency", "USD"),
            availability="limited" if payload["offer"].get("quantity", 0) < 5 else "in_stock",
            partner_id=self.partner_id,
            source_ref=payload["listingId"],
            attributes={"seller_id": payload["sellerId"], "channel": "marketplace"},
        )


class UcpLikeAdapter(PartnerAdapter):
    partner_id = "ucp_like"
    ecosystem = "universal_commerce_protocol"

    def normalize_offer(self, payload: dict[str, Any]) -> NormalizedOffer:
        offer = payload["offers"][0]
        return NormalizedOffer(
            sku=payload["merchantSku"],
            title=payload["displayName"],
            price=Decimal(str(offer["price"]["amount"])),
            currency=offer["price"].get("currency", "USD"),
            availability=offer.get("availability", "in_stock"),
            partner_id=self.partner_id,
            source_ref=payload["commerceObjectId"],
            attributes={
                "journey_stage": payload.get("journeyStage", "discovery"),
                "agent_surface": payload.get("agentSurface", "unknown"),
            },
        )


class PartnerRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, PartnerAdapter] = {
            adapter.partner_id: adapter
            for adapter in [ShopifyLikeAdapter(), MarketplaceLikeAdapter(), UcpLikeAdapter()]
        }

    def adapter_for(self, partner_id: str) -> PartnerAdapter:
        return self._adapters[partner_id]

    def partner_ids(self) -> list[str]:
        return sorted(self._adapters)

