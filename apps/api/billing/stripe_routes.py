# -*- coding: utf-8 -*-
"""
Kloud Stripe Billing Routes (Standalone)
============================================
Routes për Stripe billing që funksionojnë pa varësi të jashtme.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe_lib: Any = None
STRIPE_CONFIGURED = False

try:
    import stripe as stripe_sdk  # type: ignore[import-untyped]

    api_key = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")
    _webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if api_key and api_key.startswith("sk_"):
        stripe_sdk.api_key = api_key
        stripe_lib = stripe_sdk
        STRIPE_CONFIGURED = True
        logger.info("✅ Stripe billing routes initialized")
    else:
        logger.warning("⚠️ Stripe API key not configured")
except ImportError:
    logger.warning("⚠️ Stripe SDK not installed")


def _stripe() -> Any:
    """Return initialized Stripe SDK or raise a clear service error."""
    if not STRIPE_CONFIGURED or stripe_lib is None:
        raise HTTPException(status_code=503, detail="Stripe not configured")
    return stripe_lib


router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


@router.get("/status")
async def billing_status():
    """Check Stripe billing status."""
    return {
        "stripe_configured": STRIPE_CONFIGURED,
        "webhook_url": "https://api.kloud.com/api/v1/billing/webhook",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/payment-intent")
async def create_payment_intent(
    amount: int = 2900,  # Default 29.00 EUR
    currency: str = "eur",
    description: str = "Kloud Subscription",
):
    """
    Create a Stripe Payment Intent.

    Args:
        amount: Amount in cents (2900 = 29.00 EUR)
        currency: Currency code (default: eur)
        description: Payment description
    """
    stripe = _stripe()

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            description=description,
            metadata={
                "product": "kloud",
                "environment": os.getenv("ENVIRONMENT", "production"),
            },
        )

        return {
            "status": "success",
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "amount": amount,
            "currency": currency,
        }
    except Exception as e:
        logger.error(f"Payment intent creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events.

    Configured webhook URL: https://api.kloud.com/api/v1/billing/webhook
    """
    stripe = _stripe()

    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        if webhook_secret and sig_header:
            # Verify signature
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        else:
            # Development mode - parse without verification
            data = json.loads(payload)
            event = stripe.Event.construct_from(data, stripe.api_key)

        # Handle events
        event_type = event.type
        event_data = event.data.object

        logger.info(f"📩 Stripe webhook received: {event_type}")

        if event_type == "payment_intent.succeeded":
            logger.info(f"✅ Payment succeeded: {event_data.id}")
            # TODO: Aktivizo subscription për user

        elif event_type == "payment_intent.payment_failed":
            logger.warning(f"❌ Payment failed: {event_data.id}")

        elif event_type == "customer.subscription.created":
            logger.info(f"📝 Subscription created: {event_data.id}")

        elif event_type == "customer.subscription.updated":
            logger.info(f"🔄 Subscription updated: {event_data.id}")

        elif event_type == "customer.subscription.deleted":
            logger.warning(f"🗑️ Subscription cancelled: {event_data.id}")

        elif event_type == "invoice.paid":
            logger.info(f"💰 Invoice paid: {event_data.id}")

        elif event_type == "invoice.payment_failed":
            logger.warning(f"⚠️ Invoice payment failed: {event_data.id}")

        return {"status": "success", "event_type": event_type}

    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-subscription")
async def create_subscription(customer_id: str, price_id: str):
    """
    Create a subscription for a customer.

    Available Price IDs:
    - price_1SqCxnJQa06Hh2HGsVfGS1an (Free - 0 EUR)
    - price_1SqCxzJQa06Hh2HGwhxR7Zld (Pro - 29 EUR/month)
    - price_1SqCyFJQa06Hh2HGhs2ZSBIp (Enterprise Base - 99 EUR/month)
    """
    stripe = _stripe()

    try:
        # Create subscription - Stripe API v2 compatible
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice"],
        )

        # Get payment intent from invoice if available
        client_secret = None
        if subscription.latest_invoice:
            invoice = stripe.Invoice.retrieve(subscription.latest_invoice.id)
            if hasattr(invoice, "payment_intent") and invoice.payment_intent:
                pi = stripe.PaymentIntent.retrieve(invoice.payment_intent)
                client_secret = pi.client_secret

        return {
            "status": "success",
            "subscription_id": subscription.id,
            "subscription_status": subscription.status,
            "client_secret": client_secret,
            "invoice_id": subscription.latest_invoice.id
            if subscription.latest_invoice
            else None,
        }
    except Exception as e:
        logger.error(f"Subscription creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-customer")
async def create_customer(email: str, name: Optional[str] = None):
    """Create a new Stripe customer."""
    stripe = _stripe()

    try:
        customer = stripe.Customer.create(
            email=email, name=name, metadata={"source": "kloud_api"}
        )

        return {"status": "success", "customer_id": customer.id, "email": email}
    except Exception as e:
        logger.error(f"Customer creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products")
async def list_products():
    """List all Kloud products."""
    stripe = _stripe()

    try:
        products = stripe.Product.list(limit=10)
        prices = stripe.Price.list(limit=20)

        result = []
        for product in products.data:
            product_prices = [p for p in prices.data if p.product == product.id]
            result.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "prices": [
                        {
                            "id": p.id,
                            "amount": p.unit_amount,
                            "currency": p.currency,
                            "interval": p.recurring.interval if p.recurring else None,
                            "nickname": p.nickname,
                        }
                        for p in product_prices
                    ],
                }
            )

        return {"products": result}
    except Exception as e:
        logger.error(f"Failed to list products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/checkout")
async def create_checkout_session(request: Request):
    """
    Create a Stripe Checkout Session.

    Body:
        price_id: Price ID from Stripe
        customer_email: Customer email (optional)
        success_url: Redirect URL on success
        cancel_url: Redirect URL on cancel
    """
    stripe = _stripe()

    try:
        body = await request.json()
        price_id = body.get("price_id")
        customer_email = body.get("customer_email")
        success_url = body.get("success_url", "https://kloud.com/success")
        cancel_url = body.get("cancel_url", "https://kloud.com/cancel")

        if not price_id:
            raise HTTPException(status_code=400, detail="price_id required")

        session_params = {
            "mode": "subscription",
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": success_url + "?session_id={CHECKOUT_SESSION_ID}",
            "cancel_url": cancel_url,
            "payment_method_types": ["card"],
        }

        if customer_email:
            session_params["customer_email"] = customer_email

        session = stripe.checkout.Session.create(**session_params)

        return {
            "status": "success",
            "session_id": session.id,
            "url": session.url,
            "expires_at": session.expires_at,
        }
    except Exception as e:
        logger.error(f"Checkout session creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/checkout/{session_id}")
async def get_checkout_session(session_id: str):
    """Get checkout session status."""
    stripe = _stripe()

    try:
        session = stripe.checkout.Session.retrieve(session_id)

        return {
            "id": session.id,
            "status": session.status,
            "payment_status": session.payment_status,
            "customer": session.customer,
            "subscription": session.subscription,
        }
    except Exception as e:
        logger.error(f"Failed to retrieve checkout session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Report usage for metered billing
@router.post("/report-usage")
async def report_usage(
    subscription_item_id: str, quantity: int, timestamp: Optional[int] = None
):
    """
    Report usage for metered billing.

    Args:
        subscription_item_id: The subscription item ID (si_xxx)
        quantity: Usage quantity
        timestamp: Unix timestamp (optional, defaults to now)
    """
    stripe = _stripe()

    try:
        usage = stripe.SubscriptionItem.create_usage_record(
            subscription_item_id,
            quantity=quantity,
            timestamp=timestamp or int(datetime.now(timezone.utc).timestamp()),
            action="increment",
        )

        return {"status": "success", "usage_record_id": usage.id, "quantity": quantity}
    except Exception as e:
        logger.error(f"Usage report failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
