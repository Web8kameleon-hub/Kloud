from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import hashlib
import os

router = APIRouter()
API_KEYS = {}

AUTH_PUBLIC_MODE = os.getenv("AUTH_PUBLIC_MODE", "google_only").strip().lower()
INTERNAL_AUTH_KEY = os.getenv("INTERNAL_AUTH_KEY", "").strip()


class RegisterRequest(BaseModel):
    email: str
    password: str


class PhoneLoginRequest(BaseModel):
    phone: str


class GoogleLoginRequest(BaseModel):
    google_sub: str
    email: str


def _require_internal_auth(internal_key: str | None):
    if not INTERNAL_AUTH_KEY:
        raise HTTPException(
            status_code=503,
            detail="Internal auth key not configured",
        )
    if (internal_key or "").strip() != INTERNAL_AUTH_KEY:
        raise HTTPException(status_code=403, detail="Internal auth only")


def _ensure_public_auth_allowed(mode: str):
    if AUTH_PUBLIC_MODE == "google_only" and mode != "google":
        raise HTTPException(status_code=403, detail="Public auth limited to Google")


@router.post("/register")
def register_user(payload: RegisterRequest, internal_key: str | None = None):
    _require_internal_auth(internal_key)
    if payload.email in API_KEYS:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = hashlib.sha256(payload.password.encode()).hexdigest()
    api_key = f"NSX_{uuid4().hex}"
    API_KEYS[payload.email] = {"password": hashed, "api_key": api_key}
    return {"email": payload.email, "api_key": api_key}


@router.post("/login")
def login_user(payload: RegisterRequest):
    _ensure_public_auth_allowed("email")
    user = API_KEYS.get(payload.email)
    if (
        not user
        or user["password"] != hashlib.sha256(payload.password.encode()).hexdigest()
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"api_key": user["api_key"]}


@router.post("/login/phone")
def login_phone(payload: PhoneLoginRequest, internal_key: str | None = None):
    _require_internal_auth(internal_key)
    if not payload.phone:
        raise HTTPException(status_code=400, detail="Phone is required")
    return {"api_key": f"NSX_PHONE_{uuid4().hex}", "phone": payload.phone}


@router.post("/login/google")
def login_google(payload: GoogleLoginRequest):
    _ensure_public_auth_allowed("google")
    if not payload.google_sub or not payload.email:
        raise HTTPException(status_code=400, detail="google_sub and email are required")

    # We mint a local API key after Google identity is accepted.
    api_key = f"NSX_G_{uuid4().hex}"
    API_KEYS[payload.email] = {
        "password": "google-oauth",
        "api_key": api_key,
        "google_sub": payload.google_sub,
    }
    return {"api_key": api_key, "email": payload.email, "provider": "google"}
