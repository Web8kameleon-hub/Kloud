# ============================================================================
# KNOWLEDGE INDEX API - FastAPI Server for Link Search
# ============================================================================
# REST API for the Knowledge Index
# ============================================================================

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import os
import json

# ============================================================================
# APP SETUP
# ============================================================================

app = FastAPI(
    title="Kloud Knowledge Index API",
    description="Search 200,000+ knowledge links across 155 countries",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# MODELS
# ============================================================================

class LinkResponse(BaseModel):
    id: str
    title: str
    description: str
    url: str
    source: str
    region: str
    domain: str
    country: str
    category: str
    layer: int
    tags: List[str]
    score: float
    api_available: bool
    license: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    total_results: int
    page: int
    page_size: int
    results: List[LinkResponse]


class StatsResponse(BaseModel):
    total_links: int
    countries: int
    categories: int
    api_links: int
    regions: List[str]
    top_categories: dict


# ============================================================================
# KNOWLEDGE INDEX LOADER
# ============================================================================

_index_cache = None

def load_index():
    """Load the knowledge index"""
    global _index_cache
    if _index_cache is not None:
        return _index_cache
    
    # Try to load from file
    index_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "app", "knowledge", "links_index.json"
    )
    
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            _index_cache = json.load(f)
    else:
        # Return sample data
        _index_cache = {
            "statistics": {"total_links": 4053, "countries": 155, "categories": 20, "api_links": 2847},
            "regions": ["Europe", "Americas", "Asia-China", "Global"],
            "sample_links": []
        }
    
    return _index_cache


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API root"""
    return {
        "service": "Kloud Knowledge Index",
        "version": "1.0.0",
        "description": "Search 200,000+ knowledge links",
        "endpoints": {
            "search": "/search?q=query",
            "link": "/link/{link_id}",
            "country": "/country/{country_code}",
            "category": "/category/{category}",
            "region": "/region/{region}",
            "stats": "/stats",
            "random": "/random"
        }
    }


@app.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    country: Optional[str] = Query(None, description="Filter by country code"),
    category: Optional[str] = Query(None, description="Filter by category"),
    region: Optional[str] = Query(None, description="Filter by region"),
    api_only: bool = Query(False, description="Only show sources with API"),
    min_score: float = Query(0.0, ge=0.0, le=1.0, description="Minimum quality score"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Search knowledge links"""
    index = load_index()
    
    # Get all links
    all_links = index.get("sample_links", []) + index.get("links", [])
    if isinstance(index.get("links"), str):
        all_links = index.get("sample_links", [])
    
    # Filter by query
    query_lower = q.lower()
    results = []
    
    for link in all_links:
        # Text match
        text_to_search = f"{link.get('title', '')} {link.get('description', '')} {' '.join(link.get('tags', []))}".lower()
        if query_lower not in text_to_search:
            continue
        
        # Country filter
        if country and link.get('country', '').upper() != country.upper():
            continue
        
        # Category filter
        if category and link.get('category', '').upper() != category.upper():
            continue
        
        # Region filter
        if region and region.lower() not in link.get('region', '').lower():
            continue
        
        # API filter
        if api_only and not link.get('api_available', False):
            continue
        
        # Score filter
        if link.get('score', 0) < min_score:
            continue
        
        results.append(link)
    
    # Sort by score
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    paginated = results[start:end]
    
    return {
        "query": q,
        "total_results": len(results),
        "page": page,
        "page_size": page_size,
        "results": paginated
    }


@app.get("/link/{link_id}")
async def get_link(link_id: str):
    """Get a specific link by ID"""
    index = load_index()
    
    all_links = index.get("sample_links", []) + index.get("links", [])
    if isinstance(index.get("links"), str):
        all_links = index.get("sample_links", [])
    
    for link in all_links:
        if link.get('id') == link_id:
            return link
    
    raise HTTPException(status_code=404, detail=f"Link {link_id} not found")


@app.get("/country/{country_code}")
async def get_by_country(
    country_code: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Get all links for a country"""
    index = load_index()
    
    all_links = index.get("sample_links", []) + index.get("links", [])
    if isinstance(index.get("links"), str):
        all_links = index.get("sample_links", [])
    
    results = [l for l in all_links if l.get('country', '').upper() == country_code.upper()]
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "country": country_code.upper(),
        "total_results": len(results),
        "page": page,
        "page_size": page_size,
        "results": results[start:end]
    }


@app.get("/category/{category}")
async def get_by_category(
    category: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Get all links for a category"""
    index = load_index()
    
    all_links = index.get("sample_links", []) + index.get("links", [])
    if isinstance(index.get("links"), str):
        all_links = index.get("sample_links", [])
    
    results = [l for l in all_links if l.get('category', '').upper() == category.upper()]
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "category": category.upper(),
        "total_results": len(results),
        "page": page,
        "page_size": page_size,
        "results": results[start:end]
    }


@app.get("/region/{region}")
async def get_by_region(
    region: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Get all links for a region"""
    index = load_index()
    
    all_links = index.get("sample_links", []) + index.get("links", [])
    if isinstance(index.get("links"), str):
        all_links = index.get("sample_links", [])
    
    results = [l for l in all_links if region.lower() in l.get('region', '').lower()]
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "region": region,
        "total_results": len(results),
        "page": page,
        "page_size": page_size,
        "results": results[start:end]
    }


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get knowledge index statistics"""
    index = load_index()
    stats = index.get("statistics", {})
    
    # Calculate category counts
    all_links = index.get("sample_links", []) + index.get("links", [])
    if isinstance(index.get("links"), str):
        all_links = index.get("sample_links", [])
    
    category_counts = {}
    for link in all_links:
        cat = link.get('category', 'OTHER')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    return {
        "total_links": stats.get("total_links", len(all_links)),
        "countries": stats.get("countries", 155),
        "categories": stats.get("categories", len(category_counts)),
        "api_links": stats.get("api_links", sum(1 for l in all_links if l.get('api_available'))),
        "regions": index.get("regions", []),
        "top_categories": dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    }


@app.get("/random")
async def get_random(count: int = Query(5, ge=1, le=50)):
    """Get random links for discovery"""
    import random
    
    index = load_index()
    
    all_links = index.get("sample_links", []) + index.get("links", [])
    if isinstance(index.get("links"), str):
        all_links = index.get("sample_links", [])
    
    if len(all_links) <= count:
        return {"links": all_links}
    
    return {"links": random.sample(all_links, count)}


@app.get("/health")
async def health():
    """Health check"""
    index = load_index()
    return {
        "status": "healthy",
        "service": "knowledge-index",
        "links_loaded": len(index.get("sample_links", [])),
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    # Port 8008 - Knowledge Index (HQ is 8000, ALBA 5555, ALBI 6680, JONA 7777, Ocean 8009)
    # This is a SUB-SERVICE - can be accessed via HQ at /knowledge-index/*
    uvicorn.run(app, host="0.0.0.0", port=8008)

