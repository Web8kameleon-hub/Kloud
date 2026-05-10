"""
Kloud Cloud - API Key Management & Rate Limiting
Enterprise-grade API authentication and throttling
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from dataclasses import dataclass, field
from enum import Enum
import json
import os
from fastapi import Request, HTTPException, Depends, APIRouter
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


# ============== PLANS ==============


class PlanTier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class RateLimits:
    requests_per_minute: int
    requests_per_day: int
    burst_limit: int
    storage_mb: int


@dataclass
class Plan:
    name: str
    tier: PlanTier
    price_eur: float
    limits: RateLimits
    features: list


PLANS: Dict[PlanTier, Plan] = {
    PlanTier.FREE: Plan(
        name="Free",
        tier=PlanTier.FREE,
        price_eur=0,
        limits=RateLimits(
            requests_per_minute=10, requests_per_day=50, burst_limit=5, storage_mb=100
        ),
        features=["basic_api_access", "demo_endpoints", "community_support"],
    ),
    PlanTier.PRO: Plan(
        name="Pro",
        tier=PlanTier.PRO,
        price_eur=29,
        limits=RateLimits(
            requests_per_minute=100,
            requests_per_day=5000,
            burst_limit=50,
            storage_mb=10240,  # 10GB
        ),
        features=[
            "full_api_access",
            "eeg_processing",
            "audio_synthesis",
            "brain_sync",
            "priority_support",
            "webhooks",
        ],
    ),
    PlanTier.ENTERPRISE: Plan(
        name="Enterprise",
        tier=PlanTier.ENTERPRISE,
        price_eur=199,
        limits=RateLimits(
            requests_per_minute=1000,
            requests_per_day=50000,
            burst_limit=500,
            storage_mb=1048576,  # 1TB
        ),
        features=[
            "unlimited_api_access",
            "distributed_nodes",
            "realtime_analytics",
            "custom_integrations",
            "dedicated_support",
            "sla_99_9",
            "on_premise",
            "white_label",
        ],
    ),
}


# ============== API KEY ==============


@dataclass
class APIKey:
    key_id: str
    key_hash: str  # SHA-256 hash of the actual key
    prefix: str  # First 8 chars for identification
    user_id: str
    plan: PlanTier
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool = True
    name: str = "Default"
    scopes: list = field(default_factory=lambda: ["read", "write"])
    metadata: dict = field(default_factory=dict)

    # Usage tracking
    requests_today: int = 0
    requests_this_minute: int = 0
    last_request_at: Optional[datetime] = None
    last_minute_reset: Optional[datetime] = None


class APIKeyManager:
    """Manages API key creation, validation, and rate limiting"""

    def __init__(self, storage_path: str = "./data/api_keys.json"):
        self.storage_path = storage_path
        self.keys: Dict[str, APIKey] = {}
        self._load_keys()

    def _load_keys(self):
        """Load keys from storage"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    for key_data in data.get("keys", []):
                        key = self._dict_to_key(key_data)
                        self.keys[key.prefix] = key
            except Exception as e:
                print(f"Error loading keys: {e}")

    def _save_keys(self):
        """Save keys to storage"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        data = {
            "keys": [self._key_to_dict(k) for k in self.keys.values()],
            "updated_at": datetime.now().isoformat(),
        }
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def _key_to_dict(self, key: APIKey) -> dict:
        return {
            "key_id": key.key_id,
            "key_hash": key.key_hash,
            "prefix": key.prefix,
            "user_id": key.user_id,
            "plan": key.plan.value,
            "created_at": key.created_at.isoformat(),
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "is_active": key.is_active,
            "name": key.name,
            "scopes": key.scopes,
            "metadata": key.metadata,
            "requests_today": key.requests_today,
            "requests_this_minute": key.requests_this_minute,
            "last_request_at": key.last_request_at.isoformat()
            if key.last_request_at
            else None,
            "last_minute_reset": key.last_minute_reset.isoformat()
            if key.last_minute_reset
            else None,
        }

    def _dict_to_key(self, data: dict) -> APIKey:
        return APIKey(
            key_id=data["key_id"],
            key_hash=data["key_hash"],
            prefix=data["prefix"],
            user_id=data["user_id"],
            plan=PlanTier(data["plan"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"])
            if data.get("expires_at")
            else None,
            is_active=data.get("is_active", True),
            name=data.get("name", "Default"),
            scopes=data.get("scopes", ["read", "write"]),
            metadata=data.get("metadata", {}),
            requests_today=data.get("requests_today", 0),
            requests_this_minute=data.get("requests_this_minute", 0),
            last_request_at=datetime.fromisoformat(data["last_request_at"])
            if data.get("last_request_at")
            else None,
            last_minute_reset=datetime.fromisoformat(data["last_minute_reset"])
            if data.get("last_minute_reset")
            else None,
        )

    def generate_key(
        self,
        user_id: str,
        plan: PlanTier = PlanTier.FREE,
        name: str = "Default",
        expires_days: Optional[int] = None,
        scopes: Optional[list[str]] = None,  # was: list = None
    ) -> tuple[str, APIKey]:
        """
        Generate a new API key
        Returns: (raw_key, APIKey object)
        """
        if scopes is None:
            scopes = []

        # Generate secure random key
        # Format: pk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx (32 chars after prefix)
        prefix_type = "pk" if plan == PlanTier.FREE else "sk"
        env_type = "demo" if plan == PlanTier.FREE else "live"
        random_part = secrets.token_hex(16)  # 32 hex chars

        raw_key = f"{prefix_type}_{env_type}_{random_part}"
        prefix = raw_key[:12]  # For identification

        # Hash the key for storage
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_id = secrets.token_hex(8)

        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            prefix=prefix,
            user_id=user_id,
            plan=plan,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=expires_days)
            if expires_days
            else None,
            name=name,
            scopes=scopes,
            last_minute_reset=datetime.now(),
        )

        self.keys[prefix] = api_key
        self._save_keys()

        return raw_key, api_key

    def validate_key(self, raw_key: str) -> tuple[bool, Optional[APIKey], str]:
        """
        Validate an API key
        Returns: (is_valid, APIKey or None, error_message)
        """
        if not raw_key or len(raw_key) < 12:
            return False, None, "Invalid key format"

        prefix = raw_key[:12]

        if prefix not in self.keys:
            return False, None, "Key not found"

        api_key = self.keys[prefix]

        # Verify hash
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        if key_hash != api_key.key_hash:
            return False, None, "Invalid key"

        # Check if active
        if not api_key.is_active:
            return False, api_key, "Key is disabled"

        # Check expiration
        if api_key.expires_at and datetime.now() > api_key.expires_at:
            return False, api_key, "Key has expired"

        return True, api_key, "Valid"

    def check_rate_limit(self, api_key: APIKey) -> tuple[bool, dict]:
        """
        Check rate limits for a key
        Returns: (is_allowed, limit_info)
        """
        now = datetime.now()
        plan = PLANS[api_key.plan]
        limits = plan.limits

        # Reset daily counter if new day
        if api_key.last_request_at:
            if api_key.last_request_at.date() < now.date():
                api_key.requests_today = 0

        # Reset minute counter if new minute
        if api_key.last_minute_reset:
            if (now - api_key.last_minute_reset).total_seconds() >= 60:
                api_key.requests_this_minute = 0
                api_key.last_minute_reset = now
        else:
            api_key.last_minute_reset = now

        # Check limits
        info = {
            "plan": plan.name,
            "requests_today": api_key.requests_today,
            "limit_daily": limits.requests_per_day,
            "requests_minute": api_key.requests_this_minute,
            "limit_minute": limits.requests_per_minute,
            "remaining_daily": limits.requests_per_day - api_key.requests_today,
            "remaining_minute": limits.requests_per_minute
            - api_key.requests_this_minute,
        }

        # Daily limit
        if api_key.requests_today >= limits.requests_per_day:
            info["error"] = "Daily limit exceeded"
            info["retry_after"] = "next day"
            return False, info

        # Per-minute limit
        if api_key.requests_this_minute >= limits.requests_per_minute:
            seconds_until_reset = 60 - (now - api_key.last_minute_reset).total_seconds()
            info["error"] = "Rate limit exceeded"
            info["retry_after"] = f"{int(seconds_until_reset)} seconds"
            return False, info

        return True, info

    def record_request(self, api_key: APIKey):
        """Record a successful request"""
        api_key.requests_today += 1
        api_key.requests_this_minute += 1
        api_key.last_request_at = datetime.now()
        self._save_keys()

    def revoke_key(self, prefix: str) -> bool:
        """Revoke an API key"""
        if prefix in self.keys:
            self.keys[prefix].is_active = False
            self._save_keys()
            return True
        return False

    def get_user_keys(self, user_id: str) -> list[APIKey]:
        """Get all keys for a user"""
        return [k for k in self.keys.values() if k.user_id == user_id]

    def get_usage_stats(self, api_key: APIKey) -> dict:
        """Get usage statistics for a key"""
        plan = PLANS[api_key.plan]
        return {
            "key_id": api_key.key_id,
            "prefix": api_key.prefix,
            "plan": plan.name,
            "created_at": api_key.created_at.isoformat(),
            "expires_at": api_key.expires_at.isoformat()
            if api_key.expires_at
            else None,
            "is_active": api_key.is_active,
            "usage": {
                "requests_today": api_key.requests_today,
                "limit_daily": plan.limits.requests_per_day,
                "percentage_used": round(
                    api_key.requests_today / plan.limits.requests_per_day * 100, 2
                ),
            },
            "limits": {
                "requests_per_minute": plan.limits.requests_per_minute,
                "requests_per_day": plan.limits.requests_per_day,
                "storage_mb": plan.limits.storage_mb,
            },
        }


# ============== FASTAPI MIDDLEWARE ==============

# Global key manager
key_manager = APIKeyManager()

# Security scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(api_key: str = Depends(api_key_header)) -> APIKey:
    """Dependency to validate API key and check rate limits"""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "missing_api_key",
                "message": "API key required. Include X-API-Key header.",
                "docs": "https://kameleon.life/docs/authentication",
            },
        )

    is_valid, key_obj, error = key_manager.validate_key(api_key)

    if not is_valid or key_obj is None:
        raise HTTPException(
            status_code=401 if error in ["Key not found", "Invalid key"] else 403,
            detail={
                "error": "invalid_api_key",
                "message": error,
                "docs": "https://kameleon.life/docs/authentication",
            },
        )

    # Check rate limits
    is_allowed, limit_info = key_manager.check_rate_limit(key_obj)

    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "message": limit_info.get("error"),
                "retry_after": limit_info.get("retry_after"),
                "limits": limit_info,
                "upgrade_url": "https://kameleon.life/pricing",
            },
            headers={
                "X-RateLimit-Limit": str(limit_info["limit_minute"]),
                "X-RateLimit-Remaining": str(limit_info["remaining_minute"]),
                "X-RateLimit-Reset": limit_info.get("retry_after", "60"),
            },
        )

    # Record the request
    key_manager.record_request(key_obj)

    return key_obj


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting"""

    EXEMPT_PATHS = {"/", "/health", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        # Get API key from header
        api_key = request.headers.get("X-API-Key")

        if api_key:
            is_valid, key_obj, error = key_manager.validate_key(api_key)

            if is_valid and key_obj:
                is_allowed, limit_info = key_manager.check_rate_limit(key_obj)

                response = await call_next(request)

                # Add rate limit headers
                response.headers["X-RateLimit-Limit"] = str(limit_info["limit_minute"])
                response.headers["X-RateLimit-Remaining"] = str(
                    max(0, limit_info["remaining_minute"])
                )
                response.headers["X-RateLimit-Reset"] = "60"
                response.headers["X-Plan"] = limit_info["plan"]

                return response

        return await call_next(request)


# ============== API ENDPOINTS ==============

router = APIRouter(prefix="/api/keys", tags=["API Keys"])


@router.post("/generate")
async def generate_api_key(user_id: str, plan: str = "free", name: str = "Default"):
    """Generate a new API key"""
    try:
        tier = PlanTier(plan.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {plan}")

    raw_key, api_key = key_manager.generate_key(user_id=user_id, plan=tier, name=name)

    return {
        "success": True,
        "api_key": raw_key,
        "key_id": api_key.key_id,
        "prefix": api_key.prefix,
        "plan": tier.value,
        "message": "Store this key securely. It will not be shown again.",
        "limits": PLANS[tier].limits.__dict__,
    }


@router.get("/validate")
async def validate_api_key_endpoint(key: APIKey = Depends(get_api_key)):
    """Validate an API key and return info"""
    return {
        "valid": True,
        "key_id": key.key_id,
        "plan": key.plan.value,
        "scopes": key.scopes,
        "usage": key_manager.get_usage_stats(key),
    }


@router.get("/usage")
async def get_key_usage(key: APIKey = Depends(get_api_key)):
    """Get usage statistics for the API key"""
    return key_manager.get_usage_stats(key)


@router.post("/revoke/{key_prefix}")
async def revoke_api_key(key_prefix: str, key: APIKey = Depends(get_api_key)):
    """Revoke an API key"""
    # Only allow revoking own keys or if enterprise
    target_key = key_manager.keys.get(key_prefix)
    if not target_key:
        raise HTTPException(status_code=404, detail="Key not found")

    if target_key.user_id != key.user_id and key.plan != PlanTier.ENTERPRISE:
        raise HTTPException(status_code=403, detail="Cannot revoke other user's keys")

    success = key_manager.revoke_key(key_prefix)
    return {
        "success": success,
        "message": "Key revoked" if success else "Failed to revoke",
    }


@router.get("/plans")
async def list_plans():
    """List available plans"""
    return {
        "plans": [
            {
                "name": plan.name,
                "tier": plan.tier.value,
                "price_eur": plan.price_eur,
                "limits": plan.limits.__dict__,
                "features": plan.features,
            }
            for plan in PLANS.values()
        ]
    }


# ============== DEMO/TEST ==============

if __name__ == "__main__":
    print("=== Kloud API Key Manager Demo ===\n")

    # Create manager
    manager = APIKeyManager(storage_path="./test_keys.json")

    # Generate keys for each tier
    for tier in PlanTier:
        raw_key, api_key = manager.generate_key(
            user_id=f"user_{tier.value}",
            plan=tier,
            name=f"{tier.value.title()} Test Key",
        )
        print(f"[{tier.value.upper()}] Generated key: {raw_key[:20]}...")
        print(f"  Limits: {PLANS[tier].limits.requests_per_day}/day")

    print("\n=== Validation Test ===")

    # Test validation
    raw_key, api_key = manager.generate_key("test_user", PlanTier.PRO)
    print(f"Generated PRO key: {raw_key}")

    is_valid, key_obj, error = manager.validate_key(raw_key)
    print(f"Validation: {is_valid}, Error: {error}")

    if key_obj is None:
        print("Key not found, aborting test.")
    else:
        # Test rate limiting
        print("\n=== Rate Limit Test ===")
        for i in range(5):
            is_allowed, info = manager.check_rate_limit(key_obj)
            if is_allowed:
                manager.record_request(key_obj)
                print(
                    f"Request {i + 1}: Allowed (remaining: {info['remaining_minute']}/min)"
                )
            else:
                print(f"Request {i + 1}: Blocked - {info['error']}")

        print("\n=== Usage Stats ===")
        print(json.dumps(manager.get_usage_stats(key_obj), indent=2))
