#!/usr/bin/env python3
"""
Marketplace Stub - Kloud Plugin & Model Marketplace
"""
import sys
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8004

app = FastAPI(
    title="Kloud Marketplace",
    description="Plugins, models, and integrations marketplace",
    version="1.0.0"
)

# Mock marketplace items - UPDATED: phi3:mini removed (doesn't speak Albanian)
MODELS = {
    "llama3.1:8b": {"downloads": 100000, "rating": 4.9, "price": 0, "author": "Meta"},
    "kloud-ocean:v2": {"downloads": 25000, "rating": 4.9, "price": 0, "author": "Kloud"},
    "gpt-oss:120b": {"downloads": 5000, "rating": 4.95, "price": 0, "author": "Community"}
}

PLUGINS = {
    "excel-export": {"downloads": 12000, "rating": 4.6, "price": 0, "category": "export"},
    "pdf-generator": {"downloads": 8000, "rating": 4.5, "price": 9.99, "category": "export"},
    "slack-integration": {"downloads": 5000, "rating": 4.7, "price": 0, "category": "integration"},
    "jira-connector": {"downloads": 3000, "rating": 4.4, "price": 14.99, "category": "integration"},
    "custom-personas": {"downloads": 7000, "rating": 4.8, "price": 0, "category": "ai"}
}

@app.get("/")
def root():
    return {
        "service": "Kloud Marketplace",
        "version": "1.0.0",
        "models": len(MODELS),
        "plugins": len(PLUGINS),
        "status": "operational"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "marketplace",
        "items_total": len(MODELS) + len(PLUGINS),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/models")
def list_models():
    """List all available models"""
    return {
        "models": MODELS,
        "total": len(MODELS)
    }

@app.get("/plugins")
def list_plugins():
    """List all available plugins"""
    return {
        "plugins": PLUGINS,
        "total": len(PLUGINS)
    }

@app.get("/featured")
def featured():
    """Get featured items"""
    return {
        "featured_models": ["kloud-ocean:v2", "llama3.1:8b"],
        "featured_plugins": ["excel-export", "custom-personas"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/search")
def search(q: str = "", category: str = "all"):
    """Search marketplace"""
    results = []
    
    if category in ["all", "models"]:
        for name, data in MODELS.items():
            if q.lower() in name.lower():
                results.append({"type": "model", "name": name, **data})
    
    if category in ["all", "plugins"]:
        for name, data in PLUGINS.items():
            if q.lower() in name.lower() or q.lower() in data.get("category", ""):
                results.append({"type": "plugin", "name": name, **data})
    
    return {
        "query": q,
        "category": category,
        "results": results,
        "total": len(results)
    }

@app.get("/stats")
def stats():
    """Get marketplace statistics"""
    return {
        "total_downloads": sum(m["downloads"] for m in MODELS.values()) + sum(p["downloads"] for p in PLUGINS.values()),
        "total_models": len(MODELS),
        "total_plugins": len(PLUGINS),
        "avg_rating": 4.7,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    print(f"🛒 Starting Marketplace on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

