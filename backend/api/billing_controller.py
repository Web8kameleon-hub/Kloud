import os
from typing import Any

from fastapi import APIRouter, HTTPException, Request

stripe_sdk: Any = None
try:
    import stripe as _stripe_sdk  # type: ignore[import-untyped]

    stripe_sdk = _stripe_sdk
except ImportError:
    pass

router = APIRouter()

STRIPE_API_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

if stripe_sdk is not None and STRIPE_API_KEY:
    stripe_sdk.api_key = STRIPE_API_KEY


def _stripe() -> Any:
    if stripe_sdk is None or not STRIPE_API_KEY:
        raise HTTPException(status_code=503, detail="Stripe not configured")
    return stripe_sdk


@router.post("/create-checkout-session")
def create_checkout():
    stripe = _stripe()
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": os.getenv("STRIPE_PRICE_PRO"), "quantity": 1}],
            mode="subscription",
            success_url="https://kloud.com/success",
            cancel_url="https://kloud.com/cancel",
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    stripe = _stripe()
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if not STRIPE_WEBHOOK_SECRET or not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Stripe signature: {exc}")

    if event.get("type") == "checkout.session.completed":
        print(
            "Payment completed:",
            event.get("data", {}).get("object", {}).get("customer_email"),
        )
    return {"received": True}
