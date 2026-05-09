#!/usr/bin/env python3
"""
OCEAN SIMPLE - Ultra Fast, No Complexity
=========================================
- Direkt tek Ollama
- Streaming nga sekonda e parë
- Pa sandbox, pa orchestrator, pa rregulla
- 50,000 tokens max
"""

import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Config
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://kloud-ollama:11434")
MODEL = os.getenv("MODEL", "llama3.1:8b")
PORT = int(os.getenv("PORT", "8030"))

app = FastAPI(title="Ocean Simple")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ChatRequest(BaseModel):
    message: str | None = None
    query: str | None = None
    model: str | None = None


async def stream_from_ollama(prompt: str, model: str):
    """Stream direkt nga Ollama - pa asgjë tjetër"""
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "num_predict": 50000,
                    "num_ctx": 8192,
                    "temperature": 0.7,
                }
            }
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    try:
                        import json
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
                    except:
                        pass


@app.post("/api/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    """Streaming - shkruan nga sekonda e parë"""
    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(400, "message required")
    
    model = req.model or MODEL
    return StreamingResponse(
        stream_from_ollama(prompt, model),
        media_type="text/plain"
    )


@app.post("/api/v1/chat")
async def chat(req: ChatRequest):
    """Non-streaming - pret deri në fund"""
    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(400, "message required")
    
    model = req.model or MODEL
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        resp = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 50000,
                    "num_ctx": 8192,
                    "temperature": 0.7,
                }
            }
        )
        data = resp.json()
        return {"response": data.get("response", ""), "model": model}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"service": "Ocean Simple", "model": MODEL}


if __name__ == "__main__":
    import uvicorn
    print(f"🌊 Ocean Simple - {MODEL} @ {OLLAMA_HOST}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

