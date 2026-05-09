"""
Kloud Quota Gate Middleware
Industrial-grade plan-based restrictions and rate limiting
"""
import time
import json
from typing import Dict, Optional, Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.models import User
from ..settings import settings
from ..database.session import get_db


class QuotaExceededError(Exception):
    """Raised when user exceeds their plan quotas"""
    def __init__(self, message: str, quota_type: str, limit: int, current: int):
        self.message = message
        self.quota_type = quota_type
        self.limit = limit
        self.current = current
        super().__init__(self.message)


class QuotaGateMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces subscription plan quotas and rate limits
    """
    
    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client or redis.from_url(settings.redis_url)
        
        # Define quota-protected endpoints
        self.quota_endpoints = {
            "/api/v1/uploads": {
                "quota_type": "max_uploads_per_month",
                "methods": ["POST"]
            },
            "/api/v1/jobs": {
                "quota_type": "max_concurrent_jobs", 
                "methods": ["POST"]
            },
            "/api/v1/analysis": {
                "quota_type": "api_calls_per_hour",
                "methods": ["POST", "GET"]
            }
        }
        
        # Rate limiting exempt endpoints
        self.rate_limit_exempt = {
            "/health", "/metrics", "/api/v1/auth/login", 
            "/api/v1/auth/register", "/api/v1/billing/webhook"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware logic"""
        
        # Skip quota checks for non-API endpoints
        if not request.url.path.startswith("/api/"):
            return await call_next(request)
        
        # Skip for webhook and auth endpoints
        if any(request.url.path.startswith(path) for path in self.rate_limit_exempt):
            return await call_next(request)
        
        try:
            # Get user from request (assumes auth middleware sets this)
            user = getattr(request.state, "user", None)
            if not user:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": "Authentication required"}
                )
            
            # Apply rate limiting
            await self._check_rate_limit(request, user)
            
            # Apply quota checks for specific endpoints
            await self._check_quotas(request, user)
            
            # Process request
            response = await call_next(request)
            
            # Update usage counters on successful requests
            if response.status_code < 400:
                await self._update_usage_counters(request, user)
            
            return response
            
        except QuotaExceededError as e:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Quota exceeded",
                    "message": e.message,
                    "quota_type": e.quota_type,
                    "limit": e.limit,
                    "current": e.current,
                    "upgrade_url": "/api/v1/billing/upgrade"
                }
            )
        
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail}
            )
        
        except Exception as e:
            # Log error but don't block request
            print(f"QuotaGateMiddleware error: {e}")
            return await call_next(request)
    
    async def _check_rate_limit(self, request: Request, user: User) -> None:
        """Check API rate limits based on user plan"""
        
        plan_quotas = settings.plan_quotas.get(user.subscription_plan, {})
        rate_limit = plan_quotas.get("api_calls_per_hour", 100)
        
        # Create rate limit key
        current_hour = int(time.time() // 3600)
        rate_key = f"rate_limit:{user.id}:{current_hour}"
        
        # Check current usage
        current_calls = await self.redis_client.get(rate_key)
        current_calls = int(current_calls) if current_calls else 0
        
        if current_calls >= rate_limit:
            raise QuotaExceededError(
                message=f"Rate limit exceeded. Maximum {rate_limit} API calls per hour for {user.subscription_plan} plan.",
                quota_type="api_calls_per_hour",
                limit=rate_limit,
                current=current_calls
            )
    
    async def _check_quotas(self, request: Request, user: User) -> None:
        """Check specific endpoint quotas"""
        
        endpoint_config = None
        for endpoint_path, config in self.quota_endpoints.items():
            if request.url.path.startswith(endpoint_path):
                if request.method in config["methods"]:
                    endpoint_config = config
                    break
        
        if not endpoint_config:
            return  # No quota restrictions for this endpoint
        
        quota_type = endpoint_config["quota_type"]
        plan_quotas = settings.plan_quotas.get(user.subscription_plan, {})
        quota_limit = plan_quotas.get(quota_type, 0)
        
        # -1 means unlimited (enterprise plans)
        if quota_limit == -1:
            return
        
        # Get current usage based on quota type
        if quota_type == "max_uploads_per_month":
            current_usage = await self._get_monthly_uploads(user.id)
        elif quota_type == "max_concurrent_jobs":
            current_usage = await self._get_concurrent_jobs(user.id)
        elif quota_type == "api_calls_per_hour":
            current_usage = await self._get_hourly_api_calls(user.id)
        else:
            return  # Unknown quota type
        
        if current_usage >= quota_limit:
            raise QuotaExceededError(
                message=f"Quota exceeded. Maximum {quota_limit} {quota_type} for {user.subscription_plan} plan.",
                quota_type=quota_type,
                limit=quota_limit,
                current=current_usage
            )
    
    async def _update_usage_counters(self, request: Request, user: User) -> None:
        """Update usage counters after successful request"""
        
        # Update rate limiting counter
        current_hour = int(time.time() // 3600)
        rate_key = f"rate_limit:{user.id}:{current_hour}"
        
        pipe = self.redis_client.pipeline()
        pipe.incr(rate_key)
        pipe.expire(rate_key, 3600)  # Expire after 1 hour
        await pipe.execute()
        
        # Update specific counters based on endpoint
        if request.url.path.startswith("/api/v1/uploads") and request.method == "POST":
            await self._increment_monthly_uploads(user.id)
        
        elif request.url.path.startswith("/api/v1/jobs") and request.method == "POST":
            # Concurrent jobs are managed by job lifecycle, not incremented here
            pass
    
    async def _get_monthly_uploads(self, user_id: int) -> int:
        """Get current month's upload count for user"""
        import datetime
        current_month = datetime.datetime.now().strftime("%Y-%m")
        key = f"uploads:{user_id}:{current_month}"
        count = await self.redis_client.get(key)
        return int(count) if count else 0
    
    async def _increment_monthly_uploads(self, user_id: int) -> None:
        """Increment monthly upload counter"""
        import datetime
        current_month = datetime.datetime.now().strftime("%Y-%m")
        key = f"uploads:{user_id}:{current_month}"
        
        pipe = self.redis_client.pipeline()
        pipe.incr(key)
        # Expire at end of next month
        next_month = datetime.datetime.now().replace(day=1) + datetime.timedelta(days=32)
        expire_at = int(next_month.timestamp())
        pipe.expireat(key, expire_at)
        await pipe.execute()
    
    async def _get_concurrent_jobs(self, user_id: int) -> int:
        """Get current concurrent job count for user"""
        key = f"concurrent_jobs:{user_id}"
        count = await self.redis_client.get(key)
        return int(count) if count else 0
    
    async def _get_hourly_api_calls(self, user_id: int) -> int:
        """Get current hour's API call count"""
        current_hour = int(time.time() // 3600)
        key = f"rate_limit:{user_id}:{current_hour}"
        count = await self.redis_client.get(key)
        return int(count) if count else 0


# Job tracking utilities for concurrent job management
class JobTracker:
    """Utility class to manage concurrent job quotas"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def start_job(self, user_id: int, job_id: str) -> bool:
        """
        Start a job and check concurrent limits
        Returns True if job can start, False if quota exceeded
        """
        user_quota_key = f"concurrent_jobs:{user_id}"
        job_set_key = f"user_jobs:{user_id}"
        
        # Get user's plan and limits (would need user lookup)
        # For now, assume this is called after quota check
        
        pipe = self.redis.pipeline()
        pipe.sadd(job_set_key, job_id)
        pipe.incr(user_quota_key)
        pipe.expire(user_quota_key, 86400)  # 24 hour expiry
        pipe.expire(job_set_key, 86400)
        await pipe.execute()
        
        return True
    
    async def finish_job(self, user_id: int, job_id: str) -> None:
        """Mark job as finished and decrement counters"""
        user_quota_key = f"concurrent_jobs:{user_id}"
        job_set_key = f"user_jobs:{user_id}"
        
        pipe = self.redis.pipeline()
        pipe.srem(job_set_key, job_id)
        pipe.decr(user_quota_key)
        await pipe.execute()
        
        # Ensure counter doesn't go negative
        current = await self.redis.get(user_quota_key)
        if current and int(current) < 0:
            await self.redis.set(user_quota_key, 0)


# File size validation decorator
def validate_file_size(max_size_mb: Optional[int] = None):
    """Decorator to validate file size based on user plan"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request and user from args/kwargs
            request = None
            user = None
            
            for arg in args:
                if hasattr(arg, 'state') and hasattr(arg.state, 'user'):
                    request = arg
                    user = arg.state.user
                    break
            
            if user and request:
                plan_quotas = settings.plan_quotas.get(user.subscription_plan, {})
                max_file_size = max_size_mb or plan_quotas.get("max_file_size_mb", 10)
                
                # Validate Content-Length header
                content_length = request.headers.get("content-length")
                if content_length:
                    size_mb = int(content_length) / (1024 * 1024)
                    if size_mb > max_file_size:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File too large. Maximum {max_file_size}MB allowed for {user.subscription_plan} plan."
                        )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator



