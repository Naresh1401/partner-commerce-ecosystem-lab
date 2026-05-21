from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request

from partner_commerce.adapters import PartnerRegistry
from partner_commerce.mandates import validate_checkout_mandate
from partner_commerce.models import CheckoutMandate, MandateValidationResult, NormalizedOffer
from partner_commerce.security import verify_webhook

app = FastAPI(title="Partner Commerce Ecosystem Lab", version="0.1.0")
registry = PartnerRegistry()
WEBHOOK_SECRET = "demo-secret"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/partners")
def partners() -> dict[str, list[str]]:
    return {"partners": registry.partner_ids()}


@app.get("/v1/partners/{partner_id}/onboarding")
def onboarding(partner_id: str) -> dict[str, Any]:
    return registry.adapter_for(partner_id).onboarding_plan().model_dump()


@app.post("/v1/partners/{partner_id}/normalize", response_model=NormalizedOffer)
def normalize(partner_id: str, payload: dict[str, Any]) -> NormalizedOffer:
    try:
        return registry.adapter_for(partner_id).normalize_offer(payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown partner") from exc


@app.post("/v1/mandates/validate", response_model=MandateValidationResult)
def validate_mandate(mandate: CheckoutMandate, checkout_total: float) -> MandateValidationResult:
    return validate_checkout_mandate(mandate, checkout_total)


@app.post("/v1/webhooks/{partner_id}")
async def webhook(partner_id: str, request: Request, x_partner_signature: str = Header(...)) -> dict[str, str]:
    body = await request.body()
    if not verify_webhook(WEBHOOK_SECRET, body, x_partner_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    return {"status": "accepted", "partner_id": partner_id}

