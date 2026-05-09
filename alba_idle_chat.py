"""ALBA Idle Chat API - Kloud Cloud."""
import os
from typing import Optional

import uvicorn
from fastapi import FastAPI

app = FastAPI(title="ALBA Idle Chat", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "alba-idle"}


@app.get("/")
def root():
    return {"message": "ALBA Idle Chat", "version": "1.0.0"}


@app.post("/chat")
def chat(message: Optional[dict] = None):
    return {"response": "ALBA idle mode active", "status": "ready"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8031))
    uvicorn.run(app, host="0.0.0.0", port=port)

