"""
Kloud Marketplace API Service
================================
Lightweight FastAPI service for API marketplace functionality.
Runs on port 8004.

Features:
- API Key generation and validation
- Rate limiting
- Usage tracking
- Developer portal API
"""

from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import secrets
import hashlib
import json
import os
import time
from collections import defaultdict
from cors_policy import apply_standard_cors

app = FastAPI(
    title="Kloud Marketplace API",
    description="API Key management and developer portal for Kloud Cloud",
    version="1.0.0"
)

# CORS
apply_standard_cors(app)

# =============================================================================
# BILLING PLANS
# =============================================================================

BILLING_PLANS = {
    "free": {
        "id": "free",
        "name": "Free",
        "price_monthly": 0,
        "price_yearly": 0,
        "currency": "EUR",
        "rate_limit_per_minute": 10,
        "daily_limit": 50,
        "features": [
            "50 API calls/day",
            "Basic endpoints",
            "Community support",
            "Public documentation"
        ]
    },
    "pro": {
        "id": "pro",
        "name": "Pro",
        "price_monthly": 29,
        "price_yearly": 290,
        "currency": "EUR",
        "rate_limit_per_minute": 100,
        "daily_limit": 5000,
        "features": [
            "5,000 API calls/day",
            "All endpoints",
            "Priority support",
            "Webhooks",
            "Analytics dashboard"
        ]
    },
    "enterprise": {
        "id": "enterprise",
        "name": "Enterprise",
        "price_monthly": 199,
        "price_yearly": 1990,
        "currency": "EUR",
        "rate_limit_per_minute": 1000,
        "daily_limit": 50000,
        "features": [
            "50,000 API calls/day",
            "All endpoints + Beta",
            "Dedicated support",
            "Custom integrations",
            "SLA guarantee",
            "On-premise option"
        ]
    }
}

# =============================================================================
# IN-MEMORY STORAGE (use Redis in production)
# =============================================================================

api_keys_db: Dict[str, Dict] = {}
usage_tracker: Dict[str, Dict] = defaultdict(lambda: {"today": 0, "total": 0, "last_reset": datetime.now().date().isoformat()})
rate_limiter: Dict[str, List[float]] = defaultdict(list)

# =============================================================================
# MODELS
# =============================================================================

class GenerateKeyRequest(BaseModel):
    user_id: str
    plan: str = "free"
    name: Optional[str] = "Default Key"

class ValidateKeyRequest(BaseModel):
    api_key: str

class KeyInfo(BaseModel):
    key_id: str
    name: str
    plan: str
    created_at: str
    last_used: Optional[str]
    usage_today: int
    usage_total: int
    rate_limit: int
    daily_limit: int

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_api_key(plan: str) -> str:
    """Generate a secure API key with plan prefix"""
    prefix = f"cli_{plan}_"
    random_part = secrets.token_urlsafe(32)
    return prefix + random_part

def hash_key(api_key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def check_rate_limit(key_hash: str, limit_per_minute: int) -> bool:
    """Check if request is within rate limit"""
    now = time.time()
    minute_ago = now - 60
    
    # Clean old entries
    rate_limiter[key_hash] = [t for t in rate_limiter[key_hash] if t > minute_ago]
    
    if len(rate_limiter[key_hash]) >= limit_per_minute:
        return False
    
    rate_limiter[key_hash].append(now)
    return True

def reset_daily_usage_if_needed(key_hash: str):
    """Reset daily usage counter if it's a new day"""
    today = datetime.now().date().isoformat()
    if usage_tracker[key_hash]["last_reset"] != today:
        usage_tracker[key_hash]["today"] = 0
        usage_tracker[key_hash]["last_reset"] = today

# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    return {
        "service": "Kloud Marketplace API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "plans": "/api/marketplace/plans",
            "generate_key": "/api/marketplace/keys/generate",
            "validate_key": "/api/marketplace/keys/validate",
            "usage": "/api/marketplace/keys/{key_id}/usage",
            "sdk": "/api/marketplace/sdk"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "marketplace",
        "timestamp": datetime.now().isoformat(),
        "keys_issued": len(api_keys_db)
    }

# -----------------------------------------------------------------------------
# BILLING PLANS
# -----------------------------------------------------------------------------

@app.get("/api/marketplace/plans")
async def get_plans():
    """Get all available billing plans"""
    return {
        "plans": list(BILLING_PLANS.values()),
        "currency": "EUR",
        "billing_cycles": ["monthly", "yearly"],
        "yearly_discount": "2 months free"
    }

@app.get("/api/marketplace/plans/{plan_id}")
async def get_plan(plan_id: str):
    """Get specific plan details"""
    if plan_id not in BILLING_PLANS:
        raise HTTPException(status_code=404, detail="Plan not found")
    return BILLING_PLANS[plan_id]

# -----------------------------------------------------------------------------
# API KEY MANAGEMENT
# -----------------------------------------------------------------------------

@app.post("/api/marketplace/keys/generate")
async def generate_key(request: GenerateKeyRequest):
    """Generate a new API key"""
    if request.plan not in BILLING_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    # Generate key
    api_key = generate_api_key(request.plan)
    key_hash = hash_key(api_key)
    key_id = f"key_{secrets.token_hex(8)}"
    
    # Store key info
    plan_info = BILLING_PLANS[request.plan]
    api_keys_db[key_hash] = {
        "key_id": key_id,
        "user_id": request.user_id,
        "name": request.name,
        "plan": request.plan,
        "created_at": datetime.now().isoformat(),
        "last_used": None,
        "rate_limit": plan_info["rate_limit_per_minute"],
        "daily_limit": plan_info["daily_limit"],
        "active": True
    }
    
    return {
        "success": True,
        "api_key": api_key,  # Only shown once!
        "key_id": key_id,
        "plan": request.plan,
        "rate_limit": plan_info["rate_limit_per_minute"],
        "daily_limit": plan_info["daily_limit"],
        "warning": "Save this key securely. It will not be shown again."
    }

@app.post("/api/marketplace/keys/validate")
async def validate_key(request: ValidateKeyRequest):
    """Validate an API key and check rate limits"""
    key_hash = hash_key(request.api_key)
    
    if key_hash not in api_keys_db:
        return {
            "valid": False,
            "error": "Invalid API key"
        }
    
    key_info = api_keys_db[key_hash]
    
    if not key_info["active"]:
        return {
            "valid": False,
            "error": "API key has been revoked"
        }
    
    # Check rate limit
    if not check_rate_limit(key_hash, key_info["rate_limit"]):
        return {
            "valid": False,
            "error": "Rate limit exceeded",
            "retry_after": 60
        }
    
    # Check daily limit
    reset_daily_usage_if_needed(key_hash)
    if usage_tracker[key_hash]["today"] >= key_info["daily_limit"]:
        return {
            "valid": False,
            "error": "Daily limit exceeded",
            "reset_at": "midnight UTC"
        }
    
    # Update usage
    usage_tracker[key_hash]["today"] += 1
    usage_tracker[key_hash]["total"] += 1
    api_keys_db[key_hash]["last_used"] = datetime.now().isoformat()
    
    return {
        "valid": True,
        "key_id": key_info["key_id"],
        "plan": key_info["plan"],
        "usage_today": usage_tracker[key_hash]["today"],
        "daily_limit": key_info["daily_limit"],
        "remaining": key_info["daily_limit"] - usage_tracker[key_hash]["today"]
    }

@app.get("/api/marketplace/keys/{key_id}/usage")
async def get_key_usage(key_id: str):
    """Get usage statistics for an API key"""
    # Find key by key_id
    for key_hash, info in api_keys_db.items():
        if info["key_id"] == key_id:
            reset_daily_usage_if_needed(key_hash)
            return {
                "key_id": key_id,
                "plan": info["plan"],
                "usage": {
                    "today": usage_tracker[key_hash]["today"],
                    "total": usage_tracker[key_hash]["total"],
                    "daily_limit": info["daily_limit"],
                    "remaining_today": info["daily_limit"] - usage_tracker[key_hash]["today"]
                },
                "rate_limit": {
                    "requests_per_minute": info["rate_limit"],
                    "current_minute_usage": len(rate_limiter[key_hash])
                },
                "last_used": info["last_used"],
                "created_at": info["created_at"]
            }
    
    raise HTTPException(status_code=404, detail="Key not found")

@app.get("/api/marketplace/keys/user/{user_id}")
async def list_user_keys(user_id: str):
    """List all keys for a user"""
    user_keys = []
    for key_hash, info in api_keys_db.items():
        if info["user_id"] == user_id:
            reset_daily_usage_if_needed(key_hash)
            user_keys.append({
                "key_id": info["key_id"],
                "name": info["name"],
                "plan": info["plan"],
                "created_at": info["created_at"],
                "last_used": info["last_used"],
                "usage_today": usage_tracker[key_hash]["today"],
                "active": info["active"]
            })
    
    return {"user_id": user_id, "keys": user_keys, "total": len(user_keys)}

@app.delete("/api/marketplace/keys/{key_id}")
async def revoke_key(key_id: str):
    """Revoke an API key"""
    for key_hash, info in api_keys_db.items():
        if info["key_id"] == key_id:
            api_keys_db[key_hash]["active"] = False
            return {"success": True, "message": "API key revoked"}
    
    raise HTTPException(status_code=404, detail="Key not found")

# -----------------------------------------------------------------------------
# SDK & DOCUMENTATION
# -----------------------------------------------------------------------------

@app.get("/api/marketplace/sdk")
async def get_sdk_info():
    """Get SDK download links and documentation"""
    return {
        "sdks": {
            "typescript": {
                "name": "@kloud/sdk",
                "version": "1.0.0",
                "install": "npm install @kloud/sdk",
                "docs": "https://kloud.cloud/docs/sdk/typescript",
                "github": "https://github.com/kloud/sdk-typescript"
            },
            "python": {
                "name": "kloud",
                "version": "1.0.0",
                "install": "pip install kloud",
                "docs": "https://kloud.cloud/docs/sdk/python",
                "github": "https://github.com/kloud/sdk-python"
            }
        },
        "postman": {
            "collection": "https://kloud.cloud/postman/Kloud-Cloud-Marketplace.postman_collection.json",
            "environment": "https://kloud.cloud/postman/kloud-environment-hetzner.json"
        },
        "openapi": "https://api.kloud.com/openapi.json",
        "docs": {
            "getting_started": "https://kloud.cloud/docs/getting-started",
            "api_reference": "https://kloud.cloud/docs/api",
            "examples": "https://kloud.cloud/docs/examples"
        }
    }

@app.get("/api/marketplace/stats")
async def get_marketplace_stats():
    """Get marketplace statistics"""
    total_keys = len(api_keys_db)
    active_keys = sum(1 for k in api_keys_db.values() if k["active"])
    total_requests = sum(u["total"] for u in usage_tracker.values())
    
    plan_distribution = defaultdict(int)
    for info in api_keys_db.values():
        plan_distribution[info["plan"]] += 1
    
    return {
        "stats": {
            "total_api_keys": total_keys,
            "active_api_keys": active_keys,
            "total_api_requests": total_requests,
            "plans_distribution": dict(plan_distribution)
        },
        "api_status": {
            "main_api": "https://api.kloud.com",
            "reporting": "https://reporting.kloud.com",
            "excel": "https://excel.kloud.com",
            "marketplace": "https://marketplace.kloud.com"
        },
        "uptime": "99.9%",
        "timestamp": datetime.now().isoformat()
    }

# -----------------------------------------------------------------------------
# QUICK START EXAMPLES
# -----------------------------------------------------------------------------

@app.get("/api/marketplace/quickstart")
async def get_quickstart():
    """Get quick start code examples"""
    return {
        "curl": {
            "health_check": 'curl -X GET "https://api.kloud.com/health" -H "X-API-Key: YOUR_API_KEY"',
            "asi_status": 'curl -X GET "https://api.kloud.com/asi/status" -H "X-API-Key: YOUR_API_KEY"',
            "brain_ask": 'curl -X POST "https://api.kloud.com/brain/ask" -H "Content-Type: application/json" -H "X-API-Key: YOUR_API_KEY" -d \'{"question": "What is alpha wave activity?"}\''
        },
        "typescript": """
import Kloud from '@kloud/sdk';

const client = new Kloud({ apiKey: 'YOUR_API_KEY' });

// Check health
const health = await client.core.health();
console.log(health.status);

// Get ASI status
const asi = await client.asi.getStatus();
console.log(asi.components);
""",
        "python": """
from kloud import Kloud

client = Kloud(api_key='YOUR_API_KEY')

# Check health
health = client.core.health()
print(health['status'])

# Get ASI status
asi = client.asi.status()
print(asi['components'])
"""
    }

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)

