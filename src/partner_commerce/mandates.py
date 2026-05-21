from time import time

from partner_commerce.models import CheckoutMandate, MandateValidationResult


def validate_checkout_mandate(mandate: CheckoutMandate, checkout_total: float) -> MandateValidationResult:
    reasons: list[str] = []
    if not mandate.signed_by_trusted_surface:
        reasons.append("mandate must be signed by trusted surface")
    if mandate.expires_at_epoch <= int(time()):
        reasons.append("mandate expired")
    if checkout_total > float(mandate.max_total):
        reasons.append("checkout total exceeds mandate max_total")
    return MandateValidationResult(accepted=not reasons, reasons=reasons)

