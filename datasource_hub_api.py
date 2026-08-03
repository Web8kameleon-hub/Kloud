"""
DATASOURCE HUB API - Scalable Free Open Data Registry (40402)
=============================================================

Unified access to all 4000+ real free/open data sources aggregated
from data_sources/*.py. No-fake: every source is a real declared entry.

Author: Ledjan Ahmati / WEB8euroweb GmbH
System: Kloud Cloud - Sovereign Runtime
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from data_sources import (
    get_all_sources,
    get_sources_by_country,
    get_api_sources,
    search_sources,
)
from data_sources import category_algebra as ca

PORT = int(os.getenv("PORT", "40402"))

app = FastAPI(
    title="Kloud Datasource Hub",
    description="Unified registry of 4000+ free/open data sources",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


def _serialize(ds: Any) -> Dict[str, Any]:
    cat = getattr(ds, "category", None)
    return {
        "url": getattr(ds, "url", ""),
        "name": getattr(ds, "name", ""),
        "category": getattr(cat, "value", str(cat)) if cat is not None else "GENERAL",
        "country": getattr(ds, "country", "XX"),
        "description": getattr(ds, "description", ""),
        "api_available": getattr(ds, "api_available", False),
        "license": getattr(ds, "license", "Public"),
    }


@lru_cache(maxsize=1)
def _all() -> List[Any]:
    return list(get_all_sources())


@lru_cache(maxsize=1)
def _stats_cache() -> Dict[str, Any]:
    sources = _all()
    countries: Dict[str, int] = {}
    categories: Dict[str, int] = {}
    api_count = 0
    for s in sources:
        c = getattr(s, "country", "XX")
        countries[c] = countries.get(c, 0) + 1
        cat = getattr(s, "category", None)
        cv = getattr(cat, "value", str(cat)) if cat is not None else "GENERAL"
        categories[cv] = categories.get(cv, 0) + 1
        if getattr(s, "api_available", False):
            api_count += 1
    return {
        "total_sources": len(sources),
        "total_countries": len(countries),
        "base_categories": len(categories),
        "taxonomy": ca.coverage(sources),
        "api_sources": api_count,
        "top_countries": dict(sorted(countries.items(), key=lambda kv: -kv[1])[:20]),
        "base_category_counts": dict(sorted(categories.items(), key=lambda kv: -kv[1])),
    }


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "datasource-hub",
        "total_sources": len(_all()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/stats")
async def stats() -> Dict[str, Any]:
    return _stats_cache()


@app.get("/api/v1/sources")
async def sources(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    api_only: bool = False,
) -> Dict[str, Any]:
    data = get_api_sources() if api_only else _all()
    page = data[offset : offset + limit]
    return {
        "total": len(data),
        "offset": offset,
        "limit": limit,
        "returned": len(page),
        "sources": [_serialize(s) for s in page],
    }


@app.get("/api/v1/sources/country/{code}")
async def by_country(code: str) -> Dict[str, Any]:
    data = get_sources_by_country(code.upper())
    return {
        "country": code.upper(),
        "total": len(data),
        "sources": [_serialize(s) for s in data],
    }


@app.get("/api/v1/sources/search")
async def search(q: str = Query(..., min_length=2), limit: int = Query(100, ge=1, le=1000)) -> Dict[str, Any]:
    results = search_sources(q)[:limit]
    return {
        "query": q,
        "total": len(results),
        "sources": [_serialize(s) for s in results],
    }


@app.get("/api/v1/categories")
async def categories(
    populated_only: bool = False,
    limit: int = Query(1001, ge=1, le=1001),
    offset: int = Query(0, ge=0),
) -> Dict[str, Any]:
    """The full 7x11x13 = 1001 composed category taxonomy (algebraic)."""
    dist = ca.distribution(_all())
    cats = ca.all_categories()
    rows = [{**c.to_dict(), "count": dist.get(c.code, 0)} for c in cats]
    if populated_only:
        rows = [r for r in rows if r["count"] > 0]
    page = rows[offset : offset + limit]
    return {
        "taxonomy_size": ca.TAXONOMY_SIZE,
        "axes": {"domains": ca.DOMAINS, "facets": ca.FACETS, "scopes": ca.SCOPES},
        "total": len(rows),
        "offset": offset,
        "limit": limit,
        "categories": page,
    }


@app.get("/api/v1/categories/coverage")
async def categories_coverage() -> Dict[str, Any]:
    return ca.coverage(_all())


if __name__ == "__main__":
    print(f"🌍 Datasource Hub API starting on {PORT} | sources={len(_all())}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
