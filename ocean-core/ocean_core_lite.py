#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCEAN CORE LITE v2.0 - Fast + Streaming
========================================
- Translation Node - 72 gjuhë
- Service Router - 31 module
- Ollama - llama3.1:8b
- STREAMING - fillon nga sekonda 2
- 50,000 tokens max

Port: 8030
"""

import json
import logging
import os
import time
from typing import Optional, AsyncGenerator

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# ═══════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://kloud-ollama:11434")
MODEL = os.getenv("MODEL", "llama3.1:8b")
PORT = int(os.getenv("PORT", "8030"))
TRANSLATION_NODE = os.getenv("TRANSLATION_NODE", "http://localhost:8036")

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s - %(message)s")
logger = logging.getLogger("OceanLite")

# ═══════════════════════════════════════════════════════════════════
# KNOWLEDGE LAYER - Minimal (inline, no import)
# ═══════════════════════════════════════════════════════════════════
SERVICES = {
    "curiosity-ocean": "/modules/curiosity-ocean",
    "eeg-analysis": "/modules/eeg-analysis",
    "neural-biofeedback": "/modules/neural-biofeedback",
    "document-tools": "/modules/document-tools",
    "fitness-dashboard": "/modules/fitness-dashboard",
    "weather-dashboard": "/modules/weather-dashboard",
    "aviation-weather": "/modules/aviation-weather",
    "crypto-dashboard": "/modules/crypto-dashboard",
    "ocean-analytics": "/modules/ocean-analytics",
    "iot-network": "/modules/my-data-dashboard",
}

INTENTS = {
    "eeg": "eeg-analysis", "brain": "eeg-analysis", "neural": "neural-biofeedback",
    "document": "document-tools", "excel": "document-tools", "pdf": "document-tools",
    "fitness": "fitness-dashboard", "workout": "fitness-dashboard",
    "weather": "weather-dashboard", "metar": "aviation-weather", "aviation": "aviation-weather",
    "crypto": "crypto-dashboard", "bitcoin": "crypto-dashboard",
    "analytics": "ocean-analytics", "iot": "iot-network", "sensor": "iot-network",
}


def route_intent(text: str) -> Optional[str]:
    text_lower = text.lower()
    for kw, svc in INTENTS.items():
        if kw in text_lower:
            return svc
    return None


# ═══════════════════════════════════════════════════════════════════
# SYSTEM PROMPT - Minimal
# ═══════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """You are Curiosity Ocean 🌊 - AI assistant of Kloud Cloud (https://kloud.com).
Created by Ledjan Ahmati, ABA GmbH Germany.

RULES:
1. Respond in user's language
2. Be concise and helpful
3. Use emojis sparingly
4. START WRITING IMMEDIATELY - do not pause to think
5. For long responses, write continuously without stopping
6. Never conclude early - develop the full explanation

If asked about platform services, mention: EEG Analysis,
Neural Biofeedback, Document Tools, Fitness Dashboard,
Weather, Crypto, Analytics, IoT Network."""

# ═══════════════════════════════════════════════════════════════════
# FASTAPI
# ═══════════════════════════════════════════════════════════════════
app = FastAPI(title="Ocean Core Lite", version="2.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)


class ChatRequest(BaseModel):
    message: str = None
    query: str = None
    model: str = None


class ChatResponse(BaseModel):
    response: str
    model: str
    processing_time: float
    language_detected: str = "en"
    routed_service: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# LANGUAGE DETECTION - Fast (1s timeout)
# ═══════════════════════════════════════════════════════════════════

async def detect_language(text: str) -> tuple:
    try:
        async with httpx.AsyncClient(timeout=1.0) as client:
            resp = await client.post(f"{TRANSLATION_NODE}/api/v1/detect", json={"text": text})
            if resp.status_code == 200:
                data = resp.json()
                return data.get("detected_language", "en"), data.get("language_name", "English")
    except Exception:
        pass
    # Simple fallback detection
    albanian_words = ["si", "je", "çfarë", "ku", "pse", "kur", "shpjego", "trego"]
    if any(w in text.lower() for w in albanian_words):
        return "sq", "Albanian"
    return "en", "English"


# ═══════════════════════════════════════════════════════════════════
# STREAMING - fillon nga sekonda 2
# ═══════════════════════════════════════════════════════════════════

async def stream_ollama(prompt: str, lang_code: str) -> AsyncGenerator[str, None]:
    """Stream tokens nga Ollama - first token brenda 2 sekondave"""
    
    lang_hint = "\nRespond in Albanian (shqip)." if lang_code == "sq" else ""
    system = SYSTEM_PROMPT + lang_hint
    
    try:
        timeout = httpx.Timeout(300.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": True,
                    "keep_alive": -1,
                    "options": {
                        "temperature": 0.7,
                        "num_ctx": 8192,
                        "num_predict": 50000,
                        "repeat_penalty": 1.1,
                        "num_keep": 0,
                        "mirostat": 0,
                        "repeat_last_n": 64,
                        "stop": []
                    }
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                content = data["message"]["content"]
                                if content:
                                    yield content
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield f"Error: {str(e)}"


# ═══════════════════════════════════════════════════════════════════
# MAIN CHAT - Direct Ollama call (non-streaming)
# ═══════════════════════════════════════════════════════════════════

async def process_chat(req: ChatRequest) -> ChatResponse:
    start = time.time()
    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(400, "message required")

    # 1. Detect language (fast)
    lang_code, lang_name = await detect_language(prompt)

    # 2. Route service (instant)
    routed = route_intent(prompt)

    # 3. Build prompt
    lang_hint = f"\nRespond in {lang_name}." if lang_code != "en" else ""
    service_hint = f"\nUser is asking about {routed}. URL: {SERVICES.get(routed, '')}" if routed else ""

    system = SYSTEM_PROMPT + lang_hint + service_hint

    # 4. Call Ollama (main latency)
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": req.model or MODEL,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_ctx": 8192,
                        "num_predict": 50000,
                        "repeat_penalty": 1.1,
                        "num_keep": 0,
                        "mirostat": 0,
                        "repeat_last_n": 64,
                        "stop": []
                    }
                }
            )
            if resp.status_code != 200:
                raise HTTPException(resp.status_code, "Ollama error")

            response_text = resp.json().get("message", {}).get("content", "")
    except httpx.TimeoutException as exc:
        raise HTTPException(504, "Timeout") from exc
    except Exception as e:
        raise HTTPException(500, str(e)) from e

    elapsed = time.time() - start
    logger.info("[%s] %.1fs", lang_code, elapsed)

    return ChatResponse(
        response=response_text,
        model=req.model or MODEL,
        processing_time=round(elapsed, 2),
        language_detected=lang_code,
        routed_service=routed
    )


# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {"service": "Ocean Core Lite", "version": "1.0.0", "model": MODEL}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/v1/status")
async def status():
    return {"status": "operational", "model": MODEL, "services": len(SERVICES), "max_tokens": 50000}


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    return await process_chat(req)


@app.post("/api/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    """STREAMING - fillon nga sekonda 2"""
    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(400, "message required")
    
    lang_code, _ = await detect_language(prompt)
    logger.info(f"🌊 Stream [{lang_code}]: {prompt[:50]}...")
    
    return StreamingResponse(
        stream_ollama(prompt, lang_code),
        media_type="text/plain"
    )


@app.post("/api/v1/query", response_model=ChatResponse)
async def query(req: ChatRequest):
    return await process_chat(req)


@app.get("/api/v1/services")
async def list_services():
    return {"services": SERVICES}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🌊 Ocean Core Lite v2.0 on port {PORT}")
    logger.info(f"🤖 Model: {MODEL}")
    logger.info(f"📡 Ollama: {OLLAMA_HOST}")
    logger.info("✨ Streaming: enabled, 50K tokens")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

