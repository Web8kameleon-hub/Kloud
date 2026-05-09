"""
API Manager starter stub
- FastAPI app that queries API Producers (or accepts push events)
- In-memory MANAGER_DB to store catalog entries
- Endpoints:
  - POST /sync_from_producer -> pull published APIs from a Producer URL (simple HTTP call)
  - GET /catalog -> list managed APIs
  - POST /apply_policy -> attach a simple policy to an API (rate-limit, quota)
  - GET /health

Run: uvicorn manager:app --reload --port 8002
"""
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import requests
import time

app = FastAPI(title="API Manager (stub)")

MANAGER_DB: Dict[str, Dict] = {}
POLICIES: Dict[str, Dict] = {}
AUDIT: List[Dict] = []
CATALOG_FILE = "data/manager_catalog.json"
SYNC_TOKEN = "dev-sync-token"  # replace with secure value in prod or env var

import os, json

def load_catalog():
    global MANAGER_DB
    try:
        if os.path.exists(CATALOG_FILE):
            with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
                MANAGER_DB = json.load(f)
        else:
            MANAGER_DB = {}
    except Exception:
        MANAGER_DB = {}

def save_catalog():
    os.makedirs(os.path.dirname(CATALOG_FILE), exist_ok=True)
    with open(CATALOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(MANAGER_DB, f, indent=2)

load_catalog()

class SyncRequest(BaseModel):
    producer_url: str

class PolicyRequest(BaseModel):
    api_id: str
    policy: Dict[str, Any]


ALLOWED_PRODUCER_HOSTS = frozenset(["api.kloud.com", "producer.kloud.com", "localhost", "127.0.0.1"])

def validate_producer_url(url: str) -> bool:
    """Validate producer URL to prevent SSRF attacks"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        if parsed.hostname not in ALLOWED_PRODUCER_HOSTS:
            return False
        return True
    except Exception:
        return False

@app.post("/sync_from_producer")
def sync_from_producer(req: SyncRequest, x_sync_token: Optional[str] = Header(None)):
    """Fetch published APIs from a Producer and store them in the Manager catalog."""
    if x_sync_token != SYNC_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid sync token")
    # SECURITY: Validate URL to prevent SSRF
    if not validate_producer_url(req.producer_url):
        raise HTTPException(status_code=400, detail="Invalid or untrusted producer URL")
    try:
        resp = requests.get(req.producer_url.rstrip("/") + "/apis?public_only=true", timeout=5)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    payload = resp.json()
    for item in payload.get("items", []):
        MANAGER_DB[item.get("id")] = item
        MANAGER_DB[item.get("id")]["managed_at"] = time.time()
    save_catalog()
    return {"synced": len(payload.get("items", []))}


@app.get("/catalog")
def catalog():
    return {"count": len(MANAGER_DB), "items": list(MANAGER_DB.values())}


@app.post("/apply_policy")
def apply_policy(req: PolicyRequest):
    if req.api_id not in MANAGER_DB:
        raise HTTPException(status_code=404, detail="API not found")
    POLICIES[req.api_id] = req.policy
    return {"status": "policy_applied", "api_id": req.api_id}


@app.get("/health")
def health():
    return {"status": "ok", "managed_count": len(MANAGER_DB)}


@app.get("/policies")
def list_policies():
    return POLICIES


