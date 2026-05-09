#!/usr/bin/env python3
"""
BALANCER CACHE SERVICE (Port 3335)
Distributed cache layer for balancer data
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, TypedDict
import json
from cors_policy import apply_standard_cors


class CacheStats(TypedDict):
    hits: int
    misses: int
    sets: int
    deletes: int
    service_start: str


# Initialize FastAPI
app = FastAPI(
    title="Balancer Cache",
    description="Distributed cache layer for load distribution",
    version="1.0.0",
)

# Add CORS
apply_standard_cors(app)

# In-memory cache with TTL
CACHE: Dict[str, Dict[str, Any]] = {}
STATS: CacheStats = {
    "hits": 0,
    "misses": 0,
    "sets": 0,
    "deletes": 0,
    "service_start": datetime.now(timezone.utc).isoformat(),
}


@app.post("/cache/set")
async def cache_set(key: str, value: Any, ttl: Optional[int] = None):
    """Set cache value"""
    if not key:
        raise HTTPException(status_code=400, detail="key required")

    CACHE[key] = {
        "value": value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ttl": ttl,
        "accessed": 0,
    }
    STATS["sets"] += 1

    return {
        "success": True,
        "message": f"Cache key '{key}' set",
        "ttl": ttl,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/cache/get/{key}")
async def cache_get(key: str):
    """Get cache value"""
    if key not in CACHE:
        STATS["misses"] += 1
        raise HTTPException(status_code=404, detail=f"Cache key '{key}' not found")

    entry = CACHE[key]
    entry["accessed"] += 1
    STATS["hits"] += 1

    return {
        "success": True,
        "key": key,
        "value": entry["value"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cached_at": entry["timestamp"],
        "access_count": entry["accessed"],
    }


@app.delete("/cache/delete/{key}")
async def cache_delete(key: str):
    """Delete cache entry"""
    if key not in CACHE:
        raise HTTPException(status_code=404, detail=f"Cache key '{key}' not found")

    deleted_value = CACHE.pop(key)
    STATS["deletes"] += 1

    return {
        "success": True,
        "message": f"Cache key '{key}' deleted",
        "deleted_value": deleted_value.get("value"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/cache/keys")
async def cache_keys(pattern: Optional[str] = None):
    """List all cache keys"""
    if pattern:
        keys = [k for k in CACHE.keys() if pattern in k]
    else:
        keys = list(CACHE.keys())

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_keys": len(keys),
        "keys": keys,
        "pattern": pattern,
    }


@app.post("/cache/clear")
async def cache_clear():
    """Clear all cache"""
    size_before = len(CACHE)
    CACHE.clear()

    return {
        "success": True,
        "message": "Cache cleared",
        "entries_cleared": size_before,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/cache/stats")
async def cache_stats():
    """Cache statistics"""
    total_requests = STATS["hits"] + STATS["misses"]
    hit_rate = (STATS["hits"] / total_requests * 100) if total_requests > 0 else 0

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cache_size": len(CACHE),
        "total_hits": STATS["hits"],
        "total_misses": STATS["misses"],
        "total_sets": STATS["sets"],
        "total_deletes": STATS["deletes"],
        "hit_rate_percent": round(hit_rate, 2),
        "service_started": STATS["service_start"],
    }


@app.post("/cache/batch/set")
async def cache_batch_set(items: Dict[str, Any]):
    """Set multiple cache values"""
    count = 0
    for key, value in items.items():
        CACHE[key] = {
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "accessed": 0,
        }
        count += 1

    STATS["sets"] += count

    return {
        "success": True,
        "message": f"Batch set {count} cache entries",
        "count": count,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/cache/batch/get")
async def cache_batch_get(keys: list):
    """Get multiple cache values"""
    results = {}
    for key in keys:
        if key in CACHE:
            results[key] = CACHE[key]["value"]
            STATS["hits"] += 1
        else:
            STATS["misses"] += 1

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "requested_keys": len(keys),
        "found_keys": len(results),
        "results": results,
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "balancer-cache-3335",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cache_entries": len(CACHE),
        "cache_hits": STATS["hits"],
        "cache_misses": STATS["misses"],
    }


@app.get("/info")
async def info():
    """Service information"""
    return {
        "service": "Balancer Cache (Python)",
        "port": 3335,
        "type": "cache-layer",
        "version": "1.0.0",
        "started_at": STATS["service_start"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "POST /cache/set": "Set cache value",
            "GET /cache/get/:key": "Get cache value",
            "DELETE /cache/delete/:key": "Delete cache entry",
            "GET /cache/keys": "List cache keys",
            "POST /cache/clear": "Clear all cache",
            "GET /cache/stats": "Cache statistics",
            "POST /cache/batch/set": "Set multiple values",
            "POST /cache/batch/get": "Get multiple values",
            "GET /health": "Health check",
            "GET /info": "Service info",
        },
    }


if __name__ == "__main__":
    port = int(os.getenv("BALANCER_CACHE_PORT", "3335"))
    host = os.getenv("BALANCER_CACHE_HOST", "0.0.0.0")

    print(f"\n{'=' * 60}")
    print(f"  BALANCER CACHE SERVICE (Python)")
    print(f"  Listening on {host}:{port}")
    print(f"  Distributed cache layer")
    print(f"{'=' * 60}\n")

    uvicorn.run(app, host=host, port=port, log_level="info")
