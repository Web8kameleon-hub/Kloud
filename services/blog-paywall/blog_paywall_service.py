"""
Kloud Blog Paywall Service
Premium content access control with Stripe subscriptions
"""

import hashlib
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    import stripe  # type: ignore[import-not-found]
except ImportError:
    stripe = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"      # 9€/month
    PRO = "pro"          # 29€/month
    ENTERPRISE = "enterprise"  # 199€/month


@dataclass
class TierConfig:
    name: str
    price_cents: int
    currency: str
    features: list[str]
    stripe_price_id: str


TIER_CONFIG: dict[SubscriptionTier, TierConfig] = {
    SubscriptionTier.FREE: TierConfig(
        name="Free",
        price_cents=0,
        currency="eur",
        features=[
            "Public blog posts",
            "Basic documentation",
            "Community support"
        ],
        stripe_price_id=""
    ),
    SubscriptionTier.BASIC: TierConfig(
        name="Basic",
        price_cents=999,  # 9.99€
        currency="eur",
        features=[
            "All Free features",
            "Premium articles",
            "Technical deep dives",
            "Monthly newsletter"
        ],
        stripe_price_id=os.getenv("STRIPE_PRICE_BASIC", "price_1Sy86EJQa06Hh2HG4C3FYHhB")
    ),
    SubscriptionTier.PRO: TierConfig(
        name="Pro",
        price_cents=2999,  # 29.99€
        currency="eur",
        features=[
            "All Basic features",
            "Whitepapers access",
            "Private Discord community",
            "Early access to features",
            "Q&A sessions"
        ],
        stripe_price_id=os.getenv("STRIPE_PRICE_PRO", "price_1Sy88IJQa06Hh2HGw2nKvsVP")
    ),
    SubscriptionTier.ENTERPRISE: TierConfig(
        name="Enterprise",
        price_cents=19900,  # 199€
        currency="eur",
        features=[
            "All Pro features",
            "1:1 consultation calls",
            "Architecture reviews",
            "Priority support",
            "Custom integrations"
        ],
        stripe_price_id=os.getenv("STRIPE_PRICE_ENTERPRISE", "price_1SynwsJQa06Hh2HGPWzx00N0")
    )
}

# ============================================
# MODELS
# ============================================

class SubscriptionRequest(BaseModel):
    email: str
    tier: SubscriptionTier


class ContentAccessRequest(BaseModel):
    article_id: str
    user_token: str


class WebhookEvent(BaseModel):
    type: str
    data: dict[str, Any]


# ============================================
# PAYWALL SERVICE
# ============================================

class BlogPaywallService:
    """Manages blog subscriptions and content access"""
    
    def __init__(self):
        self.stripe_api_key = os.getenv("STRIPE_SECRET_KEY", "")
        self.stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        
        if self.stripe_api_key and stripe:
            stripe.api_key = self.stripe_api_key
            logger.info("✅ Stripe initialized for Blog Paywall")
        
        # In-memory cache (use Redis in production)
        self._subscriptions: dict[str, dict[str, Any]] = {}
        self._article_tiers: dict[str, SubscriptionTier] = {}
    
    def get_tier_config(self, tier: SubscriptionTier) -> TierConfig:
        """Get configuration for a subscription tier"""
        return TIER_CONFIG[tier]
    
    def create_checkout_session(
        self, 
        email: str, 
        tier: SubscriptionTier,
        success_url: str = "https://kloud.com/subscription/success",
        cancel_url: str = "https://kloud.com/subscription/cancel"
    ) -> dict[str, Any]:
        """Create Stripe Checkout session for subscription"""
        if not stripe:
            return {"status": "error", "message": "Stripe not available"}
        
        tier_config = self.get_tier_config(tier)
        
        if tier == SubscriptionTier.FREE:
            return {"status": "error", "message": "Free tier doesn't require payment"}
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="subscription",
                customer_email=email,
                line_items=[{
                    "price": tier_config.stripe_price_id,
                    "quantity": 1
                }],
                success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=cancel_url,
                metadata={
                    "tier": tier.value,
                    "source": "blog_paywall"
                }
            )
            
            logger.info(f"✅ Checkout session created: {session.id} for {email}")
            
            return {
                "status": "success",
                "session_id": session.id,
                "checkout_url": session.url,
                "tier": tier.value,
                "price": tier_config.price_cents / 100
            }
            
        except stripe.error.StripeError as e:  # type: ignore[union-attr]
            logger.error(f"Stripe error: {e}")
            return {"status": "error", "message": str(e)}
    
    def verify_subscription(self, user_email: str) -> dict[str, Any]:
        """Verify user's subscription status"""
        if not stripe:
            return {"status": "error", "tier": SubscriptionTier.FREE.value}
        
        try:
            # Find customer by email
            customers = stripe.Customer.list(email=user_email, limit=1)
            
            if not customers.data:
                return {
                    "status": "active",
                    "tier": SubscriptionTier.FREE.value,
                    "message": "No subscription found"
                }
            
            customer = customers.data[0]
            
            # Get active subscriptions
            subscriptions = stripe.Subscription.list(
                customer=customer.id,
                status="active",
                limit=1
            )
            
            if not subscriptions.data:
                return {
                    "status": "active",
                    "tier": SubscriptionTier.FREE.value,
                    "message": "No active subscription"
                }
            
            sub = subscriptions.data[0]
            tier_value = sub.metadata.get("tier", "basic")
            
            return {
                "status": "active",
                "tier": tier_value,
                "subscription_id": sub.id,
                "current_period_end": datetime.fromtimestamp(
                    sub.current_period_end
                ).isoformat(),
                "cancel_at_period_end": sub.cancel_at_period_end
            }
            
        except Exception as e:
            logger.error(f"Subscription verification error: {e}")
            return {"status": "error", "tier": SubscriptionTier.FREE.value}
    
    def check_content_access(
        self, 
        article_id: str, 
        user_email: str
    ) -> dict[str, Any]:
        """Check if user has access to specific content"""
        
        # Get article's required tier
        required_tier = self._article_tiers.get(article_id, SubscriptionTier.FREE)
        
        # Get user's subscription
        sub_status = self.verify_subscription(user_email)
        user_tier = SubscriptionTier(sub_status.get("tier", "free"))
        
        # Tier hierarchy
        tier_levels = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.BASIC: 1,
            SubscriptionTier.PRO: 2,
            SubscriptionTier.ENTERPRISE: 3
        }
        
        has_access = tier_levels[user_tier] >= tier_levels[required_tier]
        
        return {
            "article_id": article_id,
            "has_access": has_access,
            "required_tier": required_tier.value,
            "user_tier": user_tier.value,
            "upgrade_url": f"https://kloud.com/subscribe/{required_tier.value}"
            if not has_access else None
        }
    
    def set_article_tier(self, article_id: str, tier: SubscriptionTier) -> None:
        """Set the required tier for an article"""
        self._article_tiers[article_id] = tier
        logger.info(f"📝 Article {article_id} set to tier: {tier.value}")
    
    def handle_webhook(self, payload: bytes, sig_header: str) -> dict[str, Any]:
        """Handle Stripe webhook events"""
        if not stripe:
            return {"status": "error", "message": "Stripe not available"}
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.stripe_webhook_secret
            )
        except stripe.error.SignatureVerificationError:  # type: ignore[union-attr]
            return {"status": "error", "message": "Invalid signature"}
        
        event_type = event["type"]
        data = event["data"]["object"]
        
        if event_type == "checkout.session.completed":
            customer_email = data.get("customer_email")
            tier = data.get("metadata", {}).get("tier", "basic")
            logger.info(f"✅ New subscription: {customer_email} -> {tier}")
            
            # Cache subscription
            self._subscriptions[customer_email] = {
                "tier": tier,
                "activated_at": datetime.utcnow().isoformat()
            }
            
        elif event_type == "customer.subscription.deleted":
            customer_id = data.get("customer")
            logger.info(f"❌ Subscription cancelled: {customer_id}")
            
        elif event_type == "invoice.payment_failed":
            customer_email = data.get("customer_email")
            logger.warning(f"⚠️ Payment failed: {customer_email}")
        
        return {"status": "success", "event_type": event_type}
    
    def generate_access_token(self, email: str) -> str:
        """Generate a simple access token for content"""
        secret = os.getenv("PAYWALL_SECRET", "kloud-paywall-secret")
        timestamp = datetime.utcnow().isoformat()
        raw = f"{email}:{timestamp}:{secret}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]


# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="Kloud Blog Paywall",
    description="Premium content access with Stripe subscriptions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kloud.com", "https://www.kloud.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

paywall = BlogPaywallService()


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "blog-paywall",
        "timestamp": datetime.utcnow().isoformat(),
        "stripe_configured": bool(paywall.stripe_api_key)
    }


@app.get("/api/tiers")
async def get_tiers():
    """Get all subscription tiers"""
    return {
        "tiers": {
            tier.value: {
                "name": config.name,
                "price": config.price_cents / 100,
                "currency": config.currency,
                "features": config.features
            }
            for tier, config in TIER_CONFIG.items()
        }
    }


@app.post("/api/subscribe")
async def create_subscription(request: SubscriptionRequest):
    """Create a subscription checkout session"""
    result = paywall.create_checkout_session(
        email=request.email,
        tier=request.tier
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@app.get("/api/subscription/{email}")
async def check_subscription(email: str):
    """Check subscription status for a user"""
    return paywall.verify_subscription(email)


@app.post("/api/access/check")
async def check_access(request: ContentAccessRequest):
    """Check if user has access to content"""
    # In production, decode token to get email
    # For now, treat token as email
    return paywall.check_content_access(
        article_id=request.article_id,
        user_email=request.user_token
    )


@app.post("/api/articles/{article_id}/tier")
async def set_article_tier(article_id: str, tier: SubscriptionTier):
    """Set the required tier for an article (admin only)"""
    paywall.set_article_tier(article_id, tier)
    return {"status": "success", "article_id": article_id, "tier": tier.value}


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    
    result = paywall.handle_webhook(payload, sig_header)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


# ============================================
# ARTICLE TIER EXAMPLES
# ============================================

# Pre-configure some article tiers
PREMIUM_ARTICLES = {
    # Basic tier articles
    "eeg-signal-processing-deep-dive": SubscriptionTier.BASIC,
    "neural-mesh-architecture": SubscriptionTier.BASIC,
    "healthcare-ai-compliance": SubscriptionTier.BASIC,
    
    # Pro tier articles
    "alda-labor-array-whitepaper": SubscriptionTier.PRO,
    "liam-binary-algebra-guide": SubscriptionTier.PRO,
    "distributed-inference-patterns": SubscriptionTier.PRO,
    
    # Enterprise tier articles
    "kloud-architecture-blueprint": SubscriptionTier.ENTERPRISE,
    "custom-integration-guide": SubscriptionTier.ENTERPRISE,
}

# Initialize article tiers
for article_id, tier in PREMIUM_ARTICLES.items():
    paywall.set_article_tier(article_id, tier)


if __name__ == "__main__":
    import uvicorn
    print("🔒 Kloud Blog Paywall Service")
    print("=" * 50)
    print("Tiers:")
    for tier, config in TIER_CONFIG.items():
        print(f"  {tier.value}: {config.price_cents/100}€/month - {config.name}")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8020)

