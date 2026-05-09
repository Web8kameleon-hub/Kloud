"""
Kloud Authentication Dependencies

JWT authentication, API keys, subscription plans, and Redis session management.
Author: Ledjan Ahmati
License: Closed Source
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any, Callable

from datetime import datetime, timedelta
import json
import uuid
import hashlib

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from jose import JWTError, jwt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import redis.asyncio as redis

from .models import User, APIKey
from ..database.session import get_db
from ..settings import settings


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class AuthenticationError(Exception):
    """Raised when authentication or token verification fails."""


# ---------------------------------------------------------------------------
# Security scheme
# ---------------------------------------------------------------------------

security = HTTPBearer()


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def _get_jwt_secret() -> str:
    # expecting settings.secret_key (kloud/Kloud style)
    return settings.secret_key


def _get_jwt_algorithm() -> str:
    # fallback HS256 if not defined
    return getattr(settings, "jwt_algorithm", "HS256")


def create_access_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a signed JWT access token.
    """
    if expires_delta is None:
        minutes = getattr(settings, "access_token_expire_minutes", 30)
        expires_delta = timedelta(minutes=minutes)

    now = datetime.utcnow()
    expire = now + expires_delta

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
    }

    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        _get_jwt_secret(),
        algorithm=_get_jwt_algorithm(),
    )
    return encoded_jwt


def create_refresh_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT refresh token.
    """
    if expires_delta is None:
        days = getattr(settings, "refresh_token_expire_days", 7)
        expires_delta = timedelta(days=days)

    now = datetime.utcnow()
    expire = now + expires_delta

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "refresh",
    }

    encoded_jwt = jwt.encode(
        to_encode,
        _get_jwt_secret(),
        algorithm=_get_jwt_algorithm(),
    )
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and return payload.
    Raises AuthenticationError on failure.
    """
    try:
        payload = jwt.decode(
            token,
            _get_jwt_secret(),
            algorithms=[_get_jwt_algorithm()],
        )
    except JWTError as exc:
        raise AuthenticationError("Invalid token") from exc

    # Basic structural checks
    if "sub" not in payload:
        raise AuthenticationError("Token missing subject")
    if "exp" not in payload:
        raise AuthenticationError("Token missing expiry")

    return payload


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Load user by primary key from database.
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# ---------------------------------------------------------------------------
# Redis client & Session Manager
# ---------------------------------------------------------------------------

def get_redis_client() -> redis.Redis:
    """
    Create Redis client using settings.redis_url
    """
    redis_url = getattr(settings, "redis_url", "redis://localhost:6379/0")
    return redis.from_url(redis_url, encoding="utf-8", decode_responses=True)


class SessionManager:
    """
    Manage user sessions in Redis.

    Keys: session:{session_id}
    Value: JSON with user_id, created_at, plus extra session data.
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def create_session(
        self,
        user_id: int,
        session_data: Dict[str, Any],
        ttl: int = 3600,
    ) -> str:
        """Create user session and return session_id."""
        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"

        payload = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            **session_data,
        }

        await self.redis.setex(session_key, ttl, json.dumps(payload))
        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID."""
        session_key = f"session:{session_id}"
        data = await self.redis.get(session_key)
        if not data:
            return None
        return json.loads(data)

    async def invalidate_session(self, session_id: str) -> None:
        """Delete session from Redis."""
        session_key = f"session:{session_id}"
        await self.redis.delete(session_key)

    async def extend_session(self, session_id: str, ttl: int = 3600) -> bool:
        """Extend session TTL."""
        session_key = f"session:{session_id}"
        return await self.redis.expire(session_key, ttl)


# Optional global instance (can also be injected with Depends)
redis_client = get_redis_client()
session_manager = SessionManager(redis_client)


# ---------------------------------------------------------------------------
# Password utilities
# ---------------------------------------------------------------------------

class PasswordManager:
    """
    Password hashing and verification utilities (bcrypt via passlib).
    """

    def __init__(self):
        from passlib.context import CryptContext

        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """Hash password."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def generate_password_reset_token(self, user_id: int) -> str:
        """
        Generate password reset token with 1h expiry.
        """
        expire = datetime.utcnow() + timedelta(hours=1)

        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "type": "password_reset",
        }

        return jwt.encode(
            to_encode,
            _get_jwt_secret(),
            algorithm=_get_jwt_algorithm(),
        )

    def verify_password_reset_token(self, token: str) -> Optional[int]:
        """
        Verify password reset token and return user_id or None.
        """
        try:
            payload = verify_token(token)
            if payload.get("type") != "password_reset":
                return None
            user_id = payload.get("sub")
            return int(user_id) if user_id else None
        except AuthenticationError:
            return None


password_manager = PasswordManager()


# ---------------------------------------------------------------------------
# Dependencies: current user via JWT or API key
# ---------------------------------------------------------------------------

async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current user from JWT access token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials (token)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(credentials.credentials)
        user_id: Optional[str] = payload.get("sub")
        token_type = payload.get("type", "access")

        if user_id is None or token_type != "access":
            raise AuthenticationError("Invalid token type or subject")
    except AuthenticationError:
        raise credentials_exception

    user = await get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_from_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current user from API key (hashed in DB).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
        headers={"WWW-Authenticate": "Bearer"},
    )

    api_key_raw = credentials.credentials
    key_hash = hashlib.sha256(api_key_raw.encode()).hexdigest()

    stmt = select(APIKey).where(
        APIKey.key_hash == key_hash,
        APIKey.is_active.is_(True),
    )
    result = await db.execute(stmt)
    api_key_obj: Optional[APIKey] = result.scalar_one_or_none()

    if not api_key_obj:
        raise credentials_exception

    # Expiry check (model should expose is_expired property or expires_at)
    if getattr(api_key_obj, "is_expired", False):
        raise credentials_exception

    user = await get_user_by_id(db, getattr(api_key_obj, "user_id"))
    if not user:
        raise credentials_exception

    # Update usage
    setattr(api_key_obj, "last_used_at", datetime.utcnow())
    current_usage_count = getattr(api_key_obj, "usage_count", 0) or 0
    setattr(api_key_obj, "usage_count", current_usage_count + 1)
    await db.commit()

    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current user from JWT token OR API key.

    Tries JWT first, then API key, otherwise raises 401.
    """
    # Try JWT
    try:
        return await get_current_user_from_token(credentials, db)
    except HTTPException:
        pass

    # Try API key
    try:
        return await get_current_user_from_api_key(credentials, db)
    except HTTPException:
        pass

    # Both failed
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure user is active and verified.
    """
    if not getattr(current_user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    if not getattr(current_user, "is_verified", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not verified. Please check your email.",
        )

    return current_user


# ---------------------------------------------------------------------------
# Subscription plan & feature access
# ---------------------------------------------------------------------------

def require_subscription_plan(required_plans: List[str]) -> Callable[[User], User]:
    """
    Dependency factory: require specific subscription plans.
    """

    def plan_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_plan = getattr(current_user, "subscription_plan", "free")
        if user_plan not in required_plans:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "This feature requires "
                    f"{' or '.join(required_plans)} subscription plan. "
                    f"Current plan: {user_plan}"
                ),
            )
        return current_user

    return plan_checker


# Common plan dependencies
require_paid_plan = require_subscription_plan(["standard", "professional", "enterprise"])
require_professional_plan = require_subscription_plan(["professional", "enterprise"])
require_enterprise_plan = require_subscription_plan(["enterprise"])


async def check_feature_access(user: User, feature: str) -> bool:
    """
    Check if user has access to a specific feature based on their plan.

    Expects settings.plan_quotas to be a dict like:
    {
        "free": {"feature_a": False, "feature_b": True},
        "standard": {...},
        ...
    }
    """
    plan = getattr(user, "subscription_plan", "free")
    plan_quotas = getattr(settings, "plan_quotas", {})
    user_plan_quotas: Dict[str, Any] = plan_quotas.get(plan, {})
    return bool(user_plan_quotas.get(feature, False))


def require_feature(feature: str):
    """
    Dependency factory: require specific feature access for the current plan.
    """

    async def feature_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        has_access = await check_feature_access(current_user, feature)
        if not has_access:
            plan = getattr(current_user, "subscription_plan", "free")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"This feature '{feature}' is not available in your current "
                    f"plan: {plan}"
                ),
            )
        return current_user

    return feature_checker


__all__ = [
    "AuthenticationError",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "get_user_by_id",
    "SessionManager",
    "session_manager",
    "PasswordManager",
    "password_manager",
    "get_current_user_from_token",
    "get_current_user_from_api_key",
    "get_current_user",
    "get_current_active_user",
    "require_subscription_plan",
    "require_paid_plan",
    "require_professional_plan",
    "require_enterprise_plan",
    "check_feature_access",
    "require_feature",
]



