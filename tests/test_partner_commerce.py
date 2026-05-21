from time import time

from fastapi.testclient import TestClient

from partner_commerce.adapters import MarketplaceLikeAdapter, ShopifyLikeAdapter, UcpLikeAdapter
from partner_commerce.main import WEBHOOK_SECRET, app
from partner_commerce.models import CheckoutMandate
from partner_commerce.security import sign_webhook

client = TestClient(app)


def test_ucp_like_payload_normalizes_to_internal_offer() -> None:
    offer = UcpLikeAdapter().normalize_offer(
        {
            "commerceObjectId": "ucp_obj_123",
            "merchantSku": "sku-coffee",
            "displayName": "Cincinnati Coffee",
            "journeyStage": "checkout",
            "agentSurface": "gemini",
            "offers": [{"price": {"amount": "12.99", "currency": "USD"}, "availability": "in_stock"}],
        }
    )

    assert offer.partner_id == "ucp_like"
    assert offer.attributes["journey_stage"] == "checkout"


def test_multiple_partner_ecosystems_are_supported() -> None:
    shopify = ShopifyLikeAdapter().normalize_offer(
        {
            "id": "p1",
            "title": "Mug",
            "vendor": "Naresh Lab",
            "product_type": "Drinkware",
            "variants": [{"sku": "mug-1", "price": "9.50", "inventory_quantity": 4}],
        }
    )
    marketplace = MarketplaceLikeAdapter().normalize_offer(
        {
            "listingId": "l1",
            "sellerId": "seller-1",
            "sellerSku": "market-1",
            "item": {"name": "Coffee"},
            "offer": {"amount": "12.99", "quantity": 10},
        }
    )

    assert shopify.sku == "mug-1"
    assert marketplace.attributes["channel"] == "marketplace"


def test_ap2_style_mandate_validation_rejects_untrusted_surface() -> None:
    mandate = CheckoutMandate(
        mandate_id="mandate_1",
        shopper_id="shopper_1",
        merchant_id="merchant_1",
        checkout_hash="abc1234567899999",
        max_total="50.00",
        expires_at_epoch=int(time()) + 1000,
        signed_by_trusted_surface=False,
    )

    response = client.post("/v1/mandates/validate?checkout_total=20.00", json=mandate.model_dump(mode="json"))
    assert response.status_code == 200
    assert response.json()["accepted"] is False


def test_webhook_signature_is_required() -> None:
    body = b'{"event":"offer.updated"}'
    signature = sign_webhook(WEBHOOK_SECRET, body)

    ok = client.post("/v1/webhooks/ucp_like", content=body, headers={"X-Partner-Signature": signature})
    bad = client.post("/v1/webhooks/ucp_like", content=body, headers={"X-Partner-Signature": "bad"})

    assert ok.status_code == 200
    assert bad.status_code == 401
