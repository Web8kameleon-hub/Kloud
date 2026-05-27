"""
Kloud Stripe billing routes with real subscription management integrations.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import stripe
import stripe.error  # type: ignore
import logging
from datetime import datetime, timezone
import json

from ..database.session import get_db
from ..auth.models import User, Subscription
from ..auth.dependencies import get_current_user
from ..settings import settings

# Configure Stripe
stripe.api_key = settings.stripe_secret_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


class StripeService:
    """Service class for Stripe operations"""

    @staticmethod
    async def create_customer(user: User) -> str:
        """Create Stripe customer for user"""
        try:
            customer = stripe.Customer.create(
                email=getattr(user, "email"),
                name=f"{user.first_name} {user.last_name}",
                metadata={"user_id": str(user.id), "environment": settings.environment},
            )
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise HTTPException(status_code=500, detail="Failed to create customer")

    @staticmethod
    async def create_checkout_session(
        user: User, plan: str, success_url: str, cancel_url: str
    ) -> Dict[str, Any]:
        """Create Stripe checkout session"""

        price_id = settings.get_stripe_price_id(plan)
        if not price_id:
            raise HTTPException(status_code=400, detail=f"Invalid plan: {plan}")

        try:
            # Ensure user has Stripe customer ID
            customer_id = getattr(user, "stripe_customer_id", None)
            if customer_id is None:
                customer_id = await StripeService.create_customer(user)
                # Update user with customer ID (would need database session)

            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=cancel_url,
                metadata={
                    "user_id": str(user.id),
                    "plan": plan,
                    "environment": settings.environment,
                },
                subscription_data={"metadata": {"user_id": str(user.id), "plan": plan}},
                allow_promotion_codes=True,
                billing_address_collection="required",
                automatic_tax={"enabled": True}
                if settings.environment == "production"
                else None,  # type: ignore
            )

            return {"checkout_url": session.url, "session_id": session.id}

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to create checkout session"
            )

    @staticmethod
    async def create_portal_session(customer_id: str, return_url: str) -> str:
        """Create Stripe customer portal session"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session.url
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create portal session: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to create portal session"
            )


@router.get("/plans")
async def get_plans():
    """Get available subscription plans with quotas"""
    plans = {}

    for plan_name, quotas in settings.plan_quotas.items():
        # Add pricing information (would typically come from Stripe)
        plan_info = quotas.copy()

        # Add pricing (these would be fetched from Stripe in production)
        pricing = {
            "free": {"price": 0, "currency": "USD", "interval": "month"},
            "standard": {"price": 29, "currency": "USD", "interval": "month"},
            "professional": {"price": 99, "currency": "USD", "interval": "month"},
            "enterprise": {"price": 499, "currency": "USD", "interval": "month"},
        }

        plan_info["pricing"] = pricing.get(plan_name, pricing["free"])
        plan_info["name"] = plan_name
        plan_info["popular"] = plan_name == "professional"  # Mark popular plan

        plans[plan_name] = plan_info

    return {"plans": plans}


@router.post("/checkout")
async def create_checkout(
    request: Request,
    plan: str,
    success_url: Optional[str] = None,
    cancel_url: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create Stripe checkout session for subscription"""

    # Validate plan
    if plan not in settings.plan_quotas:
        raise HTTPException(status_code=400, detail="Invalid subscription plan")

    if plan == "free":
        raise HTTPException(
            status_code=400, detail="Free plan doesn't require checkout"
        )

    # Use provided URLs or defaults
    success_url = success_url or settings.stripe_success_url
    cancel_url = cancel_url or settings.stripe_cancel_url

    # Check if user already has this plan
    if str(getattr(current_user, "subscription_plan", "")) == plan:
        raise HTTPException(status_code=400, detail="User already has this plan")

    try:
        # Create checkout session
        checkout_data = await StripeService.create_checkout_session(
            user=current_user, plan=plan, success_url=success_url, cancel_url=cancel_url
        )

        return {
            "checkout_url": checkout_data["checkout_url"],
            "session_id": checkout_data["session_id"],
        }

    except Exception as e:
        logger.error(f"Checkout creation failed for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@router.get("/portal")
async def create_portal_session(
    request: Request,
    return_url: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Create Stripe customer portal session"""

    if not getattr(current_user, "stripe_customer_id", None):
        raise HTTPException(
            status_code=400,
            detail="No Stripe customer found. Please subscribe to a plan first.",
        )

    return_url = return_url or "https://app.Kloud.com/billing"

    try:
        portal_url = await StripeService.create_portal_session(
            customer_id=getattr(current_user, "stripe_customer_id"),
            return_url=return_url,
        )

        return {"portal_url": portal_url}

    except Exception as e:
        logger.error(f"Portal creation failed for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create portal session")


@router.get("/subscription")
async def get_subscription_status(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get current user's subscription status and usage"""

    # Get subscription from database
    stmt = select(Subscription).where(Subscription.user_id == current_user.id)
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()

    # Get plan quotas
    plan_quotas = settings.plan_quotas.get(
        str(getattr(current_user, "subscription_plan", "")), {}
    )

    # Get current usage (would integrate with Redis/analytics)
    current_usage = {
        "uploads_this_month": 0,  # Would fetch from Redis
        "concurrent_jobs": 0,  # Would fetch from Redis
        "api_calls_this_hour": 0,  # Would fetch from Redis
        "storage_used_gb": 0.0,  # Would fetch from database
    }

    return {
        "plan": str(getattr(current_user, "subscription_plan", "")),
        "status": subscription.status if subscription else "inactive",
        "quotas": plan_quotas,
        "usage": current_usage,
        "subscription_id": subscription.stripe_subscription_id
        if subscription
        else None,
        "current_period_end": subscription.current_period_end if subscription else None,
        "cancel_at_period_end": subscription.cancel_at_period_end
        if subscription
        else False,
    }


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhooks"""

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing signature")

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        logger.error("Invalid payload in Stripe webhook")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature in Stripe webhook")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Process webhook event in background
    background_tasks.add_task(process_webhook_event, event, db)

    return {"status": "success"}


async def process_webhook_event(event: Dict[str, Any], db: AsyncSession):
    """Process Stripe webhook event"""

    event_type = event["type"]
    data = event["data"]["object"]

    logger.info(f"Processing Stripe webhook: {event_type}")

    try:
        if event_type == "checkout.session.completed":
            await handle_checkout_completed(data, db)

        elif event_type == "customer.subscription.created":
            await handle_subscription_created(data, db)

        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(data, db)

        elif event_type == "customer.subscription.deleted":
            await handle_subscription_cancelled(data, db)

        elif event_type == "invoice.payment_succeeded":
            await handle_payment_succeeded(data, db)

        elif event_type == "invoice.payment_failed":
            await handle_payment_failed(data, db)

        else:
            logger.info(f"Unhandled webhook event: {event_type}")

    except Exception as e:
        logger.error(f"Error processing webhook {event_type}: {e}")


async def handle_checkout_completed(session_data: Dict[str, Any], db: AsyncSession):
    """Handle successful checkout completion"""

    user_id = session_data.get("metadata", {}).get("user_id")
    if not user_id:
        logger.error("No user_id in checkout session metadata")
        return

    # Update user's Stripe customer ID if not set
    if session_data.get("customer"):
        stmt = (
            update(User)
            .where(User.id == int(user_id))
            .values(stripe_customer_id=session_data["customer"])
        )
        await db.execute(stmt)

    await db.commit()
    logger.info(f"Checkout completed for user {user_id}")


async def handle_subscription_created(
    subscription_data: Dict[str, Any], db: AsyncSession
):
    """Handle new subscription creation"""

    user_id = subscription_data.get("metadata", {}).get("user_id")
    if not user_id:
        logger.error("No user_id in subscription metadata")
        return

    # Get plan from price ID
    price_id = subscription_data["items"]["data"][0]["price"]["id"]
    plan = settings.get_plan_from_price_id(price_id)

    # Create or update subscription record
    subscription = Subscription(
        user_id=int(user_id),
        stripe_subscription_id=subscription_data["id"],
        stripe_customer_id=subscription_data["customer"],
        status=subscription_data["status"],
        current_period_start=datetime.fromtimestamp(
            subscription_data["current_period_start"], tz=timezone.utc
        ),
        current_period_end=datetime.fromtimestamp(
            subscription_data["current_period_end"], tz=timezone.utc
        ),
        plan=plan,
    )

    db.add(subscription)

    # Update user's plan
    stmt = update(User).where(User.id == int(user_id)).values(subscription_plan=plan)
    await db.execute(stmt)

    await db.commit()
    logger.info(f"Subscription created for user {user_id}: {plan}")


async def handle_subscription_updated(
    subscription_data: Dict[str, Any], db: AsyncSession
):
    """Handle subscription updates"""

    subscription_id = subscription_data["id"]

    # Update subscription record
    stmt = (
        update(Subscription)
        .where(Subscription.stripe_subscription_id == subscription_id)
        .values(
            status=subscription_data["status"],
            current_period_end=datetime.fromtimestamp(
                subscription_data["current_period_end"], tz=timezone.utc
            ),
            cancel_at_period_end=subscription_data.get("cancel_at_period_end", False),
        )
    )

    await db.execute(stmt)
    await db.commit()

    logger.info(f"Subscription updated: {subscription_id}")


async def handle_subscription_cancelled(
    subscription_data: Dict[str, Any], db: AsyncSession
):
    """Handle subscription cancellation"""

    user_id = subscription_data.get("metadata", {}).get("user_id")
    subscription_id = subscription_data["id"]

    if user_id:
        # Downgrade user to free plan
        stmt = (
            update(User).where(User.id == int(user_id)).values(subscription_plan="free")
        )
        await db.execute(stmt)

    # Update subscription status
    stmt = (
        update(Subscription)
        .where(Subscription.stripe_subscription_id == subscription_id)
        .values(status="cancelled", cancelled_at=datetime.now(timezone.utc))
    )

    await db.execute(stmt)
    await db.commit()

    logger.info(f"Subscription cancelled for user {user_id}")


async def handle_payment_succeeded(invoice_data: Dict[str, Any], db: AsyncSession):
    """Handle successful payment"""

    subscription_id = invoice_data.get("subscription")
    if subscription_id:
        # Update subscription as active
        stmt = (
            update(Subscription)
            .where(Subscription.stripe_subscription_id == subscription_id)
            .values(status="active")
        )
        await db.execute(stmt)
        await db.commit()

        logger.info(f"Payment succeeded for subscription {subscription_id}")


async def handle_payment_failed(invoice_data: Dict[str, Any], db: AsyncSession):
    """Handle failed payment"""

    subscription_id = invoice_data.get("subscription")
    if subscription_id:
        # Mark subscription as past due
        stmt = (
            update(Subscription)
            .where(Subscription.stripe_subscription_id == subscription_id)
            .values(status="past_due")
        )
        await db.execute(stmt)
        await db.commit()

        logger.info(f"Payment failed for subscription {subscription_id}")


@router.get("/usage")
async def get_usage_analytics(current_user: User = Depends(get_current_user)):
    """Get detailed usage analytics for current user"""

    raise HTTPException(
        status_code=503,
        detail={
            "error": "usage_analytics_backend_unconfigured",
            "message": "No fake ever: usage analytics are unavailable until Redis and analytics storage are configured.",
            "required_sources": ["redis", "analytics_db", "usage_ingest"],
            "plan": str(getattr(current_user, "subscription_plan", "")),
        },
    )
