#!/usr/bin/env python3
"""
Ocean Nanogrid v3 - Clean & Fast
================================
~200 lines vs 1100 lines. Same functionality.
"""
import json
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from prompts import build_prompt
from pydantic import BaseModel

# Config
OLLAMA = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("MODEL", "llama3.1:8b")
PORT = int(os.getenv("PORT", "8030"))
RATE_LIMIT = 1000  # per hour

# State
_client: httpx.AsyncClient = None
rate_limits: dict = defaultdict(list)
memory: dict = defaultdict(list)  # session_id -> messages

# FastAPI
app = FastAPI(title="Ocean Nanogrid", version="3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Req(BaseModel):
    message: str = None
    query: str = None


class Res(BaseModel):
    response: str
    time: float


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=300.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            http2=True
        )
    return _client


def check_rate(user_id: str, is_admin: bool) -> tuple[bool, int]:
    """Rate limit check. Admins bypass."""
    if is_admin:
        return True, 9999
    
    now = datetime.now()
    hour_ago = now - timedelta(hours=1)
    rate_limits[user_id] = [t for t in rate_limits[user_id] if t > hour_ago]
    
    if len(rate_limits[user_id]) >= RATE_LIMIT:
        return False, 0
    
    rate_limits[user_id].append(now)
    return True, RATE_LIMIT - len(rate_limits[user_id])


def is_admin(msg: str, user_id: str) -> bool:
    """Detect admin by keywords."""
    check = (msg + user_id).lower()
    return any(x in check for x in ["ledjan", "ahmati", "admin"])


def add_memory(session: str, role: str, content: str):
    """Store message in conversation memory."""
    memory[session].append({"role": role, "content": content})
    if len(memory[session]) > 20:
        memory[session] = memory[session][-20:]


# ═══════════════════════════════════════════════════════════════════
# LIFECYCLE
# ═══════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    """Preload model for zero cold start."""
    client = await get_client()
    try:
        await client.get(f"{OLLAMA}/api/version")
        print("🟢 Nanogrid v3 ready")
        
        print(f"🔥 Preloading {MODEL}...")
        await client.post(
            f"{OLLAMA}/api/generate",
            json={"model": MODEL, "prompt": "", "keep_alive": "24h"},
            timeout=60.0
        )
        print(f"🚀 {MODEL} warm - zero cold start!")
    except Exception as e:
        print(f"🟡 Ready, Ollama will connect on first request: {e}")


@app.on_event("shutdown")
async def shutdown():
    global _client
    if _client:
        await _client.aclose()


# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {"service": "Ocean Nanogrid", "version": "3.0", "model": MODEL}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/v1/chat", response_model=Res)
async def chat(req: Req, request: Request):
    """Non-streaming chat."""
    t0 = time.time()
    q = req.message or req.query
    if not q:
        raise HTTPException(400, "message required")
    
    user_id = request.headers.get("X-User-ID") or request.client.host or "anon"
    session = request.headers.get("X-Session-ID") or user_id
    admin = is_admin(q, user_id)
    
    # Rate limit
    allowed, remaining = check_rate(user_id, admin)
    if not allowed:
        raise HTTPException(429, "Rate limit exceeded - upgrade at kloud.com/pricing")
    
    add_memory(session, "user", q)
    
    # Build prompt with history
    history = memory.get(session, [])
    prompt = build_prompt(is_admin=admin, conversation_history=history)
    
    client = await get_client()
    try:
        r = await client.post(f"{OLLAMA}/api/chat", json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": q}
            ],
            "stream": False,
            "options": {"num_ctx": 8192, "temperature": 0.7}
        })
        resp = r.json().get("message", {}).get("content", "")
        add_memory(session, "assistant", resp)
    except Exception as e:
        raise HTTPException(500, str(e))
    
    return Res(response=resp, time=round(time.time() - t0, 2))


@app.post("/api/v1/chat/stream")
async def chat_stream(req: Req, request: Request):
    """Streaming chat - first token in ~1s."""
    q = req.message or req.query
    if not q:
        raise HTTPException(400, "message required")
    
    user_id = request.headers.get("X-User-ID") or request.client.host or "anon"
    session = request.headers.get("X-Session-ID") or user_id
    admin = is_admin(q, user_id)
    
    allowed, _ = check_rate(user_id, admin)
    if not allowed:
        raise HTTPException(429, "Rate limit exceeded")
    
    add_memory(session, "user", q)
    history = memory.get(session, [])
    prompt = build_prompt(is_admin=admin, conversation_history=history)
    
    async def generate():
        client = httpx.AsyncClient(timeout=httpx.Timeout(None, connect=30.0), http2=True)
        try:
            async with client.stream("POST", f"{OLLAMA}/api/chat", json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": q}
                ],
                "stream": True,
                "options": {"num_ctx": 8192, "temperature": 0.7}
            }) as response:
                full = ""
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            content = data.get("message", {}).get("content", "")
                            if content:
                                full += content
                                yield content
                            if data.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
                add_memory(session, "assistant", full)
        finally:
            await client.aclose()
    
    return StreamingResponse(generate(), media_type="text/plain")


# ═══════════════════════════════════════════════════════════════════
# UTILITY ENDPOINTS (minimal)
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/status")
async def status():
    return {
        "model": MODEL,
        "ollama": OLLAMA,
        "active_sessions": len(memory),
        "rate_tracked_users": len(rate_limits)
    }


@app.delete("/api/v1/memory/{session_id}")
async def clear_memory(session_id: str):
    """Clear conversation memory for a session."""
    if session_id in memory:
        del memory[session_id]
        return {"cleared": True}
    return {"cleared": False, "reason": "session not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

