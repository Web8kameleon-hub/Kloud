from fastapi import APIRouter, HTTPException, Request
import stripe, os

router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.post("/create-checkout-session")
def create_checkout():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": os.getenv("STRIPE_PRICE_PRO"), "quantity": 1}],
            mode="subscription",
            success_url="https://Kloud.cloud/success",
            cancel_url="https://Kloud.cloud/cancel",
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = stripe.Webhook.construct_event(payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET"))
    if event["type"] == "checkout.session.completed":
        print("âœ… Payment completed:", event["data"]["object"]["customer_email"])
    return {"received": True}


