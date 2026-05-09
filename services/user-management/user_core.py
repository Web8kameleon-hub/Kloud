"""
KLOUD USER MANAGEMENT - Centralized User Registry
=====================================================

Një sistem i QARTË dhe i centralizuar për menaxhimin e përdoruesve.

Ky modul është BURIMI I VETËM I SË VËRTETËS për të gjitha të dhënat e përdoruesve.
Të gjitha shërbimet e tjera (Ocean, KLAJDI, MALI, etj.) përdorin këtë modul.

Author: Ledjan Ahmati (CEO, ABA GmbH)
"""

import hashlib
import json
import logging
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("user_core")


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS - Llojet e përdoruesve dhe planeve
# ═══════════════════════════════════════════════════════════════════════════════

class UserRole(str, Enum):
    """Rolet e përdoruesve"""
    GUEST = "guest"           # Pa llogari, vetëm shikues
    USER = "user"             # Përdorues i regjistruar
    PROFESSIONAL = "pro"      # Profesionist (mjek, kërkues)
    ADMIN = "admin"           # Administrator
    SUPERADMIN = "superadmin" # Super-admin (vetëm Ledjan)


class SubscriptionPlan(str, Enum):
    """Planet e abonimit"""
    FREE = "free"
    STARTER = "starter"           # €19/muaj
    STANDARD = "standard"         # €49/muaj
    PROFESSIONAL = "professional" # €99/muaj
    ENTERPRISE = "enterprise"     # Çmim i personalizuar


class AccountStatus(str, Enum):
    """Statusi i llogarisë"""
    PENDING = "pending"       # Pret verifikimin
    ACTIVE = "active"         # Aktiv
    SUSPENDED = "suspended"   # I pezulluar
    BANNED = "banned"         # I ndaluar
    DELETED = "deleted"       # I fshirë


class VerificationStatus(str, Enum):
    """Statusi i verifikimit"""
    UNVERIFIED = "unverified"
    EMAIL_VERIFIED = "email_verified"
    PHONE_VERIFIED = "phone_verified"
    FULLY_VERIFIED = "fully_verified"
    PROFESSIONAL_VERIFIED = "professional_verified"  # Për mjekë, etj.


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES - Strukturat e të dhënave
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class UserProfile:
    """Profili i përdoruesit"""
    user_id: str
    email: str
    username: str
    
    # Personal info
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    
    # Location
    country: Optional[str] = None
    city: Optional[str] = None
    timezone: str = "Europe/Berlin"
    language: str = "en"
    
    # Professional (for doctors, researchers)
    organization: Optional[str] = None
    job_title: Optional[str] = None
    specialization: Optional[str] = None
    license_number: Optional[str] = None  # Numri i liçencës mjekësore
    
    # Custom metadata (clerk_id, auth_provider, etc.)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name or f"{self.first_name or ''} {self.last_name or ''}".strip() or self.username,
            "avatar_url": self.avatar_url,
            "phone": self.phone,
            "country": self.country,
            "city": self.city,
            "timezone": self.timezone,
            "language": self.language,
            "organization": self.organization,
            "job_title": self.job_title,
            "specialization": self.specialization,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


@dataclass
class UserAccount:
    """Llogaria e përdoruesit - Autentifikimi dhe statusi"""
    user_id: str
    email: str
    password_hash: str
    
    # Status
    role: UserRole = UserRole.USER
    status: AccountStatus = AccountStatus.PENDING
    verification: VerificationStatus = VerificationStatus.UNVERIFIED
    
    # Subscription
    plan: SubscriptionPlan = SubscriptionPlan.FREE
    plan_started_at: Optional[str] = None
    plan_expires_at: Optional[str] = None
    
    # Security
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    last_login: Optional[str] = None
    failed_login_attempts: int = 0
    locked_until: Optional[str] = None
    
    # Tokens
    api_key: Optional[str] = None
    refresh_token: Optional[str] = None
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def is_locked(self) -> bool:
        """Kontrollo nëse llogaria është e bllokuar"""
        if not self.locked_until:
            return False
        locked_time = datetime.fromisoformat(self.locked_until.replace('Z', '+00:00'))
        return datetime.now(timezone.utc) < locked_time
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        result = {
            "user_id": self.user_id,
            "email": self.email,
            "role": self.role.value,
            "status": self.status.value,
            "verification": self.verification.value,
            "plan": self.plan.value,
            "plan_started_at": self.plan_started_at,
            "plan_expires_at": self.plan_expires_at,
            "mfa_enabled": self.mfa_enabled,
            "last_login": self.last_login,
            "created_at": self.created_at
        }
        if include_sensitive:
            result["api_key"] = self.api_key
        return result


@dataclass  
class UserSession:
    """Sesioni aktiv i përdoruesit"""
    session_id: str
    user_id: str
    
    # Session info
    access_token: str
    refresh_token: str
    expires_at: str
    
    # Device/Location
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_type: Optional[str] = None  # web, mobile, api
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def is_expired(self) -> bool:
        expires = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
        return datetime.now(timezone.utc) > expires
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "expires_at": self.expires_at,
            "device_type": self.device_type,
            "ip_address": self.ip_address,
            "created_at": self.created_at,
            "last_activity": self.last_activity
        }


@dataclass
class UserUsage:
    """Përdorimi i resurseve nga përdoruesi"""
    user_id: str
    
    # Credits/Billing
    credits_balance: int = 0
    credits_used_today: int = 0
    credits_used_month: int = 0
    
    # API Usage
    api_calls_today: int = 0
    api_calls_month: int = 0
    
    # Storage
    storage_used_mb: float = 0.0
    storage_limit_mb: float = 100.0  # Based on plan
    
    # Ocean Sessions
    ocean_sessions_today: int = 0
    ocean_messages_today: int = 0
    
    # Timestamps
    last_api_call: Optional[str] = None
    reset_daily_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reset_monthly_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "credits_balance": self.credits_balance,
            "credits_used_today": self.credits_used_today,
            "credits_used_month": self.credits_used_month,
            "api_calls_today": self.api_calls_today,
            "api_calls_month": self.api_calls_month,
            "storage_used_mb": self.storage_used_mb,
            "storage_limit_mb": self.storage_limit_mb,
            "ocean_sessions_today": self.ocean_sessions_today,
            "ocean_messages_today": self.ocean_messages_today
        }


# ═══════════════════════════════════════════════════════════════════════════════
# USER REGISTRY - Regjistri qendror i përdoruesve
# ═══════════════════════════════════════════════════════════════════════════════

class UserRegistry:
    """
    REGJISTRI QENDROR I PËRDORUESVE
    
    Ky është BURIMI I VETËM I SË VËRTETËS për të gjitha të dhënat e përdoruesve.
    """
    
    def __init__(self) -> None:
        # Storage (in production: database)
        self._accounts: Dict[str, UserAccount] = {}
        self._profiles: Dict[str, UserProfile] = {}
        self._sessions: Dict[str, UserSession] = {}
        self._usage: Dict[str, UserUsage] = {}
        
        # Indexes for quick lookup
        self._email_index: Dict[str, str] = {}  # email -> user_id
        self._username_index: Dict[str, str] = {}  # username -> user_id
        self._api_key_index: Dict[str, str] = {}  # api_key -> user_id
        self._token_index: Dict[str, str] = {}  # access_token -> session_id
        self._clerk_index: Dict[str, str] = {}  # clerk_id -> user_id
        
        # Stats
        self._stats: Dict[str, Any] = {
            "total_users": 0,
            "active_users": 0,
            "active_sessions": 0,
            "registrations_today": 0,
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Create default admin
        self._create_default_admin()
    
    def _create_default_admin(self) -> None:
        """Krijo admin-in e parazgjedhur"""
        admin_id = "usr_admin_ledjan"
        admin_email = "ledjan@kloud.com"
        
        if admin_id not in self._accounts:
            # Account
            self._accounts[admin_id] = UserAccount(
                user_id=admin_id,
                email=admin_email,
                password_hash=self._hash_password("admin123"),  # Change in production!
                role=UserRole.SUPERADMIN,
                status=AccountStatus.ACTIVE,
                verification=VerificationStatus.FULLY_VERIFIED,
                plan=SubscriptionPlan.ENTERPRISE,
                api_key=f"clx_admin_{secrets.token_hex(16)}"
            )
            
            # Profile
            self._profiles[admin_id] = UserProfile(
                user_id=admin_id,
                email=admin_email,
                username="ledjan",
                first_name="Ledjan",
                last_name="Ahmati",
                organization="ABA GmbH",
                job_title="CEO & Founder",
                country="DE",
                city="Berlin"
            )
            
            # Usage
            self._usage[admin_id] = UserUsage(
                user_id=admin_id,
                credits_balance=999999,
                storage_limit_mb=10000.0
            )
            
            # Update indexes
            self._email_index[admin_email] = admin_id
            self._username_index["ledjan"] = admin_id
            admin_api_key = self._accounts[admin_id].api_key
            if admin_api_key is not None:
                self._api_key_index[admin_api_key] = admin_id
            
            self._stats["total_users"] = 1
            self._stats["active_users"] = 1
            
            logger.info(f"✅ Created default admin: {admin_email}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # REGISTRATION - Regjistrimi i përdoruesve
    # ═══════════════════════════════════════════════════════════════════════════
    
    def register_user(
        self,
        email: str,
        username: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        plan: SubscriptionPlan = SubscriptionPlan.FREE
    ) -> Dict[str, Any]:
        """
        Regjistro përdorues të ri.
        
        Returns: {"success": bool, "user_id": str, "error": str}
        """
        # Validate email
        if not self._validate_email(email):
            return {"success": False, "error": "Email i pavlefshëm"}
        
        # Check if email exists
        if email.lower() in self._email_index:
            return {"success": False, "error": "Ky email është regjistruar tashmë"}
        
        # Validate username
        if not self._validate_username(username):
            return {"success": False, "error": "Username duhet të jetë 3-30 karaktere, vetëm shkronja dhe numra"}
        
        # Check if username exists
        if username.lower() in self._username_index:
            return {"success": False, "error": "Ky username është marrë tashmë"}
        
        # Validate password
        password_validation = self._validate_password(password)
        if not password_validation["valid"]:
            return {"success": False, "error": password_validation["error"]}
        
        # Generate user ID
        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        
        # Create account
        self._accounts[user_id] = UserAccount(
            user_id=user_id,
            email=email.lower(),
            password_hash=self._hash_password(password),
            role=UserRole.USER,
            status=AccountStatus.PENDING,
            verification=VerificationStatus.UNVERIFIED,
            plan=plan,
            api_key=f"clx_{secrets.token_hex(16)}"
        )
        
        # Create profile
        self._profiles[user_id] = UserProfile(
            user_id=user_id,
            email=email.lower(),
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create usage record
        self._usage[user_id] = UserUsage(
            user_id=user_id,
            credits_balance=self._get_initial_credits(plan),
            storage_limit_mb=self._get_storage_limit(plan)
        )
        
        # Update indexes
        self._email_index[email.lower()] = user_id
        self._username_index[username.lower()] = user_id
        user_api_key = self._accounts[user_id].api_key
        if user_api_key is not None:
            self._api_key_index[user_api_key] = user_id
        
        # Update stats
        self._stats["total_users"] += 1
        self._stats["registrations_today"] += 1
        
        logger.info(f"✅ Registered new user: {email} (ID: {user_id})")
        
        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "username": username,
            "plan": plan.value,
            "message": "Regjistrimi u krye me sukses! Kontrollo email-in për verifikim."
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # AUTHENTICATION - Autentifikimi
    # ═══════════════════════════════════════════════════════════════════════════
    
    def login(
        self,
        email_or_username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Autentifiko përdoruesin dhe krijo sesion.
        
        Returns: {"success": bool, "session": dict, "error": str}
        """
        # Find user
        user_id = self._find_user_id(email_or_username)
        if not user_id:
            return {"success": False, "error": "Përdoruesi nuk u gjet"}
        
        account = self._accounts[user_id]
        
        # Check if locked
        if account.is_locked():
            return {"success": False, "error": "Llogaria është e bllokuar përkohësisht"}
        
        # Check password
        if not self._verify_password(password, account.password_hash):
            account.failed_login_attempts += 1
            
            # Lock after 5 failed attempts
            if account.failed_login_attempts >= 5:
                account.locked_until = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
                return {"success": False, "error": "Shumë tentativa të dështuara. Llogaria u bllokua për 15 minuta."}
            
            return {"success": False, "error": "Fjalëkalimi i gabuar"}
        
        # Check account status
        if account.status == AccountStatus.SUSPENDED:
            return {"success": False, "error": "Llogaria është pezulluar"}
        if account.status == AccountStatus.BANNED:
            return {"success": False, "error": "Llogaria është ndaluar"}
        
        # Reset failed attempts
        account.failed_login_attempts = 0
        account.locked_until = None
        account.last_login = datetime.now(timezone.utc).isoformat()
        
        # Create session
        session = self._create_session(user_id, ip_address, user_agent)
        
        # Get profile
        profile = self._profiles.get(user_id)
        
        logger.info(f"✅ User logged in: {email_or_username} (Session: {session.session_id})")
        
        return {
            "success": True,
            "session": session.to_dict(),
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "expires_at": session.expires_at,
            "user": {
                "user_id": user_id,
                "email": account.email,
                "username": profile.username if profile else None,
                "display_name": profile.display_name if profile else None,
                "role": account.role.value,
                "plan": account.plan.value
            }
        }
    
    def logout(self, session_id: str) -> Dict[str, Any]:
        """Mbyll sesionin"""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            
            # Remove from token index
            if session.access_token in self._token_index:
                del self._token_index[session.access_token]
            
            del self._sessions[session_id]
            self._stats["active_sessions"] -= 1
            
            return {"success": True, "message": "Sesioni u mbyll"}
        
        return {"success": False, "error": "Sesioni nuk u gjet"}
    
    def validate_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Valido token dhe kthe të dhënat e përdoruesit"""
        session_id = self._token_index.get(access_token)
        if not session_id:
            return None
        
        session = self._sessions.get(session_id)
        if not session or session.is_expired():
            return None
        
        # Update last activity
        session.last_activity = datetime.now(timezone.utc).isoformat()
        
        account = self._accounts.get(session.user_id)
        profile = self._profiles.get(session.user_id)
        
        if not account:
            return None
        
        return {
            "user_id": session.user_id,
            "email": account.email,
            "username": profile.username if profile else None,
            "role": account.role.value,
            "plan": account.plan.value,
            "session_id": session_id
        }
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Valido API key"""
        user_id = self._api_key_index.get(api_key)
        if not user_id:
            return None
        
        account = self._accounts.get(user_id)
        if not account or account.status != AccountStatus.ACTIVE:
            return None
        
        return {
            "user_id": user_id,
            "email": account.email,
            "role": account.role.value,
            "plan": account.plan.value
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PROFILE MANAGEMENT - Menaxhimi i profilit
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Merr profilin e përdoruesit"""
        profile = self._profiles.get(user_id)
        if not profile:
            return None
        return profile.to_dict()
    
    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Përditëso profilin"""
        if user_id not in self._profiles:
            return {"success": False, "error": "Profili nuk u gjet"}
        
        profile = self._profiles[user_id]
        
        # Update allowed fields
        allowed_fields = [
            "first_name", "last_name", "display_name", "avatar_url",
            "phone", "country", "city", "timezone", "language",
            "organization", "job_title", "specialization"
        ]
        
        for field_name in allowed_fields:
            if field_name in updates:
                setattr(profile, field_name, updates[field_name])
        
        profile.updated_at = datetime.now(timezone.utc).isoformat()
        
        return {"success": True, "profile": profile.to_dict()}
    
    def get_account(self, user_id: str, include_sensitive: bool = False) -> Optional[Dict[str, Any]]:
        """Merr të dhënat e llogarisë"""
        account = self._accounts.get(user_id)
        if not account:
            return None
        return account.to_dict(include_sensitive)
    
    def get_usage(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Merr të dhënat e përdorimit"""
        usage = self._usage.get(user_id)
        if not usage:
            return None
        return usage.to_dict()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # USER LOOKUP - Kërkimi i përdoruesve
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Gjej user nga email"""
        user_id = self._email_index.get(email.lower())
        if not user_id:
            return None
        return self._get_user_info(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Gjej user nga username"""
        user_id = self._username_index.get(username.lower())
        if not user_id:
            return None
        return self._get_user_info(user_id)
    
    def find_by_clerk_id(self, clerk_id: str) -> Optional[Dict[str, Any]]:
        """Gjej user nga Clerk ID"""
        user_id = self._clerk_index.get(clerk_id)
        if not user_id:
            return None
        return self._get_user_info(user_id)
    
    def update_user_metadata(self, user_id: str, metadata: Dict[str, Any]) -> bool:
        """Përditëso metadata të userit (clerk_id, auth_provider, etj)"""
        if user_id not in self._profiles:
            return False
        
        profile = self._profiles[user_id]
        
        # Store clerk_id in index
        if "clerk_id" in metadata:
            self._clerk_index[metadata["clerk_id"]] = user_id
        
        # Store in profile metadata
        profile.metadata.update(metadata)
        
        # Update avatar if provided
        if "avatar_url" in metadata:
            profile.avatar_url = metadata["avatar_url"]
        
        return True
    
    def _get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Helper: Get full user info"""
        account = self._accounts.get(user_id)
        profile = self._profiles.get(user_id)
        if not account:
            return None
        return {
            "user_id": user_id,
            "email": account.email,
            "username": profile.username if profile else None,
            "first_name": profile.first_name if profile else None,
            "last_name": profile.last_name if profile else None,
            "display_name": profile.display_name if profile else None,
            "avatar_url": profile.avatar_url if profile else None,
            "language": profile.language if profile else "en",
            "role": account.role.value,
            "plan": account.plan.value,
            "status": account.status.value,
            "clerk_id": self._get_clerk_id(user_id)
        }
    
    def _get_clerk_id(self, user_id: str) -> Optional[str]:
        """Get clerk_id for a user"""
        for clerk_id, uid in self._clerk_index.items():
            if uid == user_id:
                return clerk_id
        return None
    
    def delete_user(self, user_id: str) -> bool:
        """Fshi/deaktivo userin"""
        if user_id not in self._accounts:
            return False
        self._accounts[user_id].status = AccountStatus.DELETED
        return True
    
    def user_exists(self, email_or_username: str) -> bool:
        """Kontrollo nëse përdoruesi ekziston"""
        return self._find_user_id(email_or_username) is not None
    
    def list_users(
        self,
        status: Optional[AccountStatus] = None,
        plan: Optional[SubscriptionPlan] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Listo përdoruesit"""
        users = []
        
        for user_id, account in list(self._accounts.items())[offset:offset+limit]:
            if status and account.status != status:
                continue
            if plan and account.plan != plan:
                continue
            
            profile = self._profiles.get(user_id)
            users.append({
                "user_id": user_id,
                "email": account.email,
                "username": profile.username if profile else None,
                "display_name": profile.display_name if profile else None,
                "role": account.role.value,
                "status": account.status.value,
                "plan": account.plan.value,
                "created_at": account.created_at
            })
        
        return users
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ADMIN FUNCTIONS - Funksionet admin
    # ═══════════════════════════════════════════════════════════════════════════
    
    def activate_user(self, user_id: str) -> Dict[str, Any]:
        """Aktivo llogarinë"""
        if user_id not in self._accounts:
            return {"success": False, "error": "Përdoruesi nuk u gjet"}
        
        self._accounts[user_id].status = AccountStatus.ACTIVE
        self._stats["active_users"] += 1
        
        return {"success": True, "message": "Llogaria u aktivizua"}
    
    def suspend_user(self, user_id: str, reason: str) -> Dict[str, Any]:
        """Pezullo llogarinë"""
        if user_id not in self._accounts:
            return {"success": False, "error": "Përdoruesi nuk u gjet"}
        
        self._accounts[user_id].status = AccountStatus.SUSPENDED
        self._stats["active_users"] -= 1
        
        logger.warning(f"⚠️ User suspended: {user_id} - Reason: {reason}")
        
        return {"success": True, "message": "Llogaria u pezullua"}
    
    def change_plan(
        self,
        user_id: str,
        new_plan: SubscriptionPlan,
        duration_days: int = 30
    ) -> Dict[str, Any]:
        """Ndrysho planin e abonimit"""
        if user_id not in self._accounts:
            return {"success": False, "error": "Përdoruesi nuk u gjet"}
        
        account = self._accounts[user_id]
        old_plan = account.plan
        
        account.plan = new_plan
        account.plan_started_at = datetime.now(timezone.utc).isoformat()
        account.plan_expires_at = (datetime.now(timezone.utc) + timedelta(days=duration_days)).isoformat()
        
        # Update usage limits
        if user_id in self._usage:
            self._usage[user_id].storage_limit_mb = self._get_storage_limit(new_plan)
            self._usage[user_id].credits_balance += self._get_initial_credits(new_plan)
        
        logger.info(f"📦 Plan changed for {user_id}: {old_plan.value} → {new_plan.value}")
        
        return {
            "success": True,
            "old_plan": old_plan.value,
            "new_plan": new_plan.value,
            "expires_at": account.plan_expires_at
        }
    
    def add_credits(self, user_id: str, amount: int) -> Dict[str, Any]:
        """Shto kredite"""
        if user_id not in self._usage:
            return {"success": False, "error": "Përdoruesi nuk u gjet"}
        
        self._usage[user_id].credits_balance += amount
        
        return {
            "success": True,
            "credits_added": amount,
            "new_balance": self._usage[user_id].credits_balance
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HELPER METHODS - Metodat ndihmëse
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _find_user_id(self, email_or_username: str) -> Optional[str]:
        """Gjej user_id nga email ose username"""
        key = email_or_username.lower()
        return self._email_index.get(key) or self._username_index.get(key)
    
    def _hash_password(self, password: str) -> str:
        """Hash password me salt"""
        salt = secrets.token_hex(16)
        hash_input = f"{password}{salt}".encode()
        password_hash = hashlib.sha256(hash_input).hexdigest()
        return f"{salt}${password_hash}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verifiko password"""
        try:
            salt, stored_hash = password_hash.split("$")
            hash_input = f"{password}{salt}".encode()
            computed_hash = hashlib.sha256(hash_input).hexdigest()
            return computed_hash == stored_hash
        except Exception:
            return False
    
    def _validate_email(self, email: str) -> bool:
        """Valido formatin e email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_username(self, username: str) -> bool:
        """Valido username"""
        import re
        pattern = r'^[a-zA-Z0-9_]{3,30}$'
        return bool(re.match(pattern, username))
    
    def _validate_password(self, password: str) -> Dict[str, Any]:
        """Valido fjalëkalimin"""
        if len(password) < 8:
            return {"valid": False, "error": "Fjalëkalimi duhet të ketë të paktën 8 karaktere"}
        if not any(c.isupper() for c in password):
            return {"valid": False, "error": "Fjalëkalimi duhet të ketë të paktën një shkronjë të madhe"}
        if not any(c.islower() for c in password):
            return {"valid": False, "error": "Fjalëkalimi duhet të ketë të paktën një shkronjë të vogël"}
        if not any(c.isdigit() for c in password):
            return {"valid": False, "error": "Fjalëkalimi duhet të ketë të paktën një numër"}
        return {"valid": True}
    
    def _create_session(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """Krijo sesion të ri"""
        session_id = f"sess_{uuid.uuid4().hex[:16]}"
        access_token = f"at_{secrets.token_hex(32)}"
        refresh_token = f"rt_{secrets.token_hex(32)}"
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=self._detect_device_type(user_agent) if user_agent else "unknown"
        )
        
        self._sessions[session_id] = session
        self._token_index[access_token] = session_id
        self._stats["active_sessions"] += 1
        
        return session
    
    def _detect_device_type(self, user_agent: str) -> str:
        """Detekto llojin e pajisjes"""
        ua = user_agent.lower()
        if "mobile" in ua or "android" in ua or "iphone" in ua:
            return "mobile"
        if "tablet" in ua or "ipad" in ua:
            return "tablet"
        return "web"
    
    def _get_initial_credits(self, plan: SubscriptionPlan) -> int:
        """Kreditet fillestare sipas planit"""
        credits_map = {
            SubscriptionPlan.FREE: 100,
            SubscriptionPlan.STARTER: 1000,
            SubscriptionPlan.STANDARD: 5000,
            SubscriptionPlan.PROFESSIONAL: 20000,
            SubscriptionPlan.ENTERPRISE: 100000
        }
        return credits_map.get(plan, 100)
    
    def _get_storage_limit(self, plan: SubscriptionPlan) -> float:
        """Limiti i ruajtjes sipas planit (MB)"""
        storage_map = {
            SubscriptionPlan.FREE: 100.0,
            SubscriptionPlan.STARTER: 1000.0,
            SubscriptionPlan.STANDARD: 5000.0,
            SubscriptionPlan.PROFESSIONAL: 20000.0,
            SubscriptionPlan.ENTERPRISE: 100000.0
        }
        return storage_map.get(plan, 100.0)
    
    def get_stats(self) -> Dict[str, Any]:
        """Merr statistikat"""
        return {
            **self._stats,
            "accounts_count": len(self._accounts),
            "profiles_count": len(self._profiles),
            "sessions_count": len(self._sessions)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON - Instanca globale
# ═══════════════════════════════════════════════════════════════════════════════

_registry: Optional[UserRegistry] = None


def get_user_registry() -> UserRegistry:
    """Merr ose krijo regjistrin e përdoruesve"""
    global _registry
    if _registry is None:
        _registry = UserRegistry()
        logger.info("👤 User Registry initialized")
    return _registry


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO)
    
    registry = get_user_registry()
    
    # Test registration
    result = registry.register_user(
        email="test@example.com",
        username="testuser",
        password="Test123!",
        first_name="Test",
        last_name="User"
    )
    print("Registration:", json.dumps(result, indent=2))
    
    if result["success"]:
        # Activate user
        registry.activate_user(result["user_id"])
        
        # Test login
        login_result = registry.login("test@example.com", "Test123!")
        print("\nLogin:", json.dumps(login_result, indent=2))
        
        # Test token validation
        if login_result["success"]:
            user = registry.validate_token(login_result["access_token"])
            print("\nValidated user:", json.dumps(user, indent=2))
    
    # Print stats
    print("\nStats:", json.dumps(registry.get_stats(), indent=2))

