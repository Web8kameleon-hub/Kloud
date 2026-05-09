"""Marketplace API Service - Kloud Cloud."""
import os

import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Kloud Marketplace API", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "marketplace"}


@app.get("/")
def root():
    return {"message": "Marketplace API", "version": "1.0.0"}


@app.get("/items")
def list_items():
    return {"items": [], "total": 0}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port)

