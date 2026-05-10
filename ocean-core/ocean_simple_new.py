#!/usr/bin/env python3
import os
import json
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://kloud-clx:11434")
MODEL = os.getenv("MODEL", "llama3.1:8b")

app = FastAPI(title="Ocean Simple")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ChatRequest(BaseModel):
    message: str | None = None
    query: str | None = None
    model: str | None = None


async def stream_chat(prompt: str, model: str):
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_HOST}/api/chat",
            json={"model": model, "messages": [{"role": "user", "content": prompt}], "stream": True, "options": {"num_predict": 50000}},
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                    except:
                        pass


@app.post("/api/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(400, "message required")
    return StreamingResponse(stream_chat(prompt, req.model or MODEL), media_type="text/plain")


@app.post("/api/v1/chat")
async def chat(req: ChatRequest):
    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(400, "message required")
    async with httpx.AsyncClient(timeout=300.0) as client:
        resp = await client.post(
            f"{OLLAMA_HOST}/api/chat",
            json={"model": req.model or MODEL, "messages": [{"role": "user", "content": prompt}], "stream": False},
        )
        data = resp.json()
        return {"response": data.get("message", {}).get("content", "")}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"service": "Ocean Simple"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8030)
