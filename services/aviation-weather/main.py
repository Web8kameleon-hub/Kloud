#!/usr/bin/env python3
"""
Aviation Weather API - Kloud Cloud
Port: 8030
Provides METAR, TAF, NOTAM data for aviation operations
"""

import os
import asyncio
import httpx
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aviation-weather")

app = FastAPI(
    title="Aviation Weather API",
    description="Real-time aviation weather data - METAR, TAF, NOTAM",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Aviation Weather API sources
AVWX_API_KEY = os.getenv("AVWX_API_KEY", "")
CHECKWX_API_KEY = os.getenv("CHECKWX_API_KEY", "")

# =====================
# MODELS
# =====================

class MetarResponse(BaseModel):
    icao: str
    raw: str
    station: str
    time: str
    temperature: Optional[float] = None
    dewpoint: Optional[float] = None
    wind_direction: Optional[int] = None
    wind_speed: Optional[int] = None
    wind_gust: Optional[int] = None
    visibility: Optional[float] = None
    altimeter: Optional[float] = None
    flight_category: Optional[str] = None
    clouds: List[Dict[str, Any]] = []
    weather: List[str] = []

class TafResponse(BaseModel):
    icao: str
    raw: str
    station: str
    time: str
    valid_from: str
    valid_to: str
    forecast: List[Dict[str, Any]] = []

class AirportInfo(BaseModel):
    icao: str
    iata: Optional[str] = None
    name: str
    city: str
    country: str
    latitude: float
    longitude: float
    elevation: int
    timezone: str

class FlightConditions(BaseModel):
    category: str  # VFR, MVFR, IFR, LIFR
    color: str
    description: str
    ceiling: Optional[int] = None
    visibility: Optional[float] = None

# =====================
# HELPER FUNCTIONS
# =====================

async def fetch_metar_avwx(icao: str) -> Optional[Dict]:
    """Fetch METAR from AVWX API"""
    if not AVWX_API_KEY:
        return None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://avwx.rest/api/metar/{icao}",
                headers={"Authorization": f"BEARER {AVWX_API_KEY}"},
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        logger.error(f"AVWX METAR error: {e}")
    return None

async def fetch_metar_checkwx(icao: str) -> Optional[Dict]:
    """Fetch METAR from CheckWX API"""
    if not CHECKWX_API_KEY:
        return None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.checkwx.com/metar/{icao}/decoded",
                headers={"X-API-Key": CHECKWX_API_KEY},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("results", 0) > 0:
                    return data["data"][0]
    except Exception as e:
        logger.error(f"CheckWX METAR error: {e}")
    return None

async def fetch_metar_noaa(icao: str) -> Optional[str]:
    """Fetch raw METAR from NOAA (free, no API key)"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao}.TXT",
                timeout=10
            )
            if resp.status_code == 200:
                lines = resp.text.strip().split('\n')
                if len(lines) >= 2:
                    return lines[1]  # METAR is on second line
    except Exception as e:
        logger.error(f"NOAA METAR error: {e}")
    return None

async def fetch_taf_noaa(icao: str) -> Optional[str]:
    """Fetch raw TAF from NOAA (free, no API key)"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://tgftp.nws.noaa.gov/data/forecasts/taf/stations/{icao}.TXT",
                timeout=10
            )
            if resp.status_code == 200:
                lines = resp.text.strip().split('\n')
                if len(lines) >= 2:
                    return ' '.join(lines[1:])  # TAF can span multiple lines
    except Exception as e:
        logger.error(f"NOAA TAF error: {e}")
    return None

def parse_flight_category(metar_raw: str) -> FlightConditions:
    """Parse flight category from METAR"""
    # Simplified parsing - in production use proper METAR parser
    categories = {
        "VFR": {"color": "#00C853", "description": "Visual Flight Rules - Good conditions"},
        "MVFR": {"color": "#2196F3", "description": "Marginal VFR - Reduced visibility"},
        "IFR": {"color": "#F44336", "description": "Instrument Flight Rules - Poor conditions"},
        "LIFR": {"color": "#9C27B0", "description": "Low IFR - Very poor conditions"}
    }
    
    # Default to VFR if we can't determine
    category = "VFR"
    
    # Check for visibility indicators
    if "1/4SM" in metar_raw or "1/2SM" in metar_raw:
        category = "LIFR"
    elif "1SM" in metar_raw or "2SM" in metar_raw:
        category = "IFR"
    elif "3SM" in metar_raw or "4SM" in metar_raw or "5SM" in metar_raw:
        category = "MVFR"
    
    # Check for ceiling (OVC/BKN below certain altitudes)
    if "OVC0" in metar_raw or "BKN00" in metar_raw:
        category = "LIFR"
    elif "OVC01" in metar_raw or "BKN01" in metar_raw:
        category = "IFR"
    
    cat_info = categories.get(category, categories["VFR"])
    return FlightConditions(
        category=category,
        color=cat_info["color"],
        description=cat_info["description"]
    )

# =====================
# API ENDPOINTS
# =====================

@app.get("/")
async def root():
    """API root"""
    return {
        "service": "Aviation Weather API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "metar": "/metar/{icao}",
            "taf": "/taf/{icao}",
            "conditions": "/conditions/{icao}",
            "multi": "/multi?icaos=KJFK,KLAX,EGLL",
            "health": "/health"
        }
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "aviation-weather-api",
        "port": 8080
    }


@app.get("/status")
@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "service": "Aviation Weather API",
        "version": "1.0.0",
        "port": 8080,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/metar/{icao}")
async def get_metar(icao: str):
    """
    Get METAR for airport
    - icao: ICAO airport code (e.g., KJFK, EGLL, EDDF)
    """
    icao = icao.upper().strip()
    if len(icao) != 4:
        raise HTTPException(status_code=400, detail="Invalid ICAO code - must be 4 characters")
    
    # Try multiple sources
    raw_metar = None
    
    # Try NOAA first (free)
    raw_metar = await fetch_metar_noaa(icao)
    
    if raw_metar:
        conditions = parse_flight_category(raw_metar)
        return {
            "icao": icao,
            "raw": raw_metar,
            "time": datetime.now(timezone.utc).isoformat(),
            "flight_category": conditions.category,
            "category_color": conditions.color,
            "category_description": conditions.description,
            "source": "NOAA"
        }
    
    # Try AVWX if available
    avwx_data = await fetch_metar_avwx(icao)
    if avwx_data:
        return {
            "icao": icao,
            "raw": avwx_data.get("raw", ""),
            "time": avwx_data.get("time", {}).get("dt", ""),
            "temperature": avwx_data.get("temperature", {}).get("value"),
            "dewpoint": avwx_data.get("dewpoint", {}).get("value"),
            "wind_direction": avwx_data.get("wind_direction", {}).get("value"),
            "wind_speed": avwx_data.get("wind_speed", {}).get("value"),
            "visibility": avwx_data.get("visibility", {}).get("value"),
            "flight_category": avwx_data.get("flight_rules", "VFR"),
            "source": "AVWX"
        }
    
    raise HTTPException(status_code=404, detail=f"METAR not found for {icao}")

@app.get("/taf/{icao}")
async def get_taf(icao: str):
    """
    Get TAF (Terminal Aerodrome Forecast) for airport
    - icao: ICAO airport code
    """
    icao = icao.upper().strip()
    if len(icao) != 4:
        raise HTTPException(status_code=400, detail="Invalid ICAO code - must be 4 characters")
    
    raw_taf = await fetch_taf_noaa(icao)
    
    if raw_taf:
        return {
            "icao": icao,
            "raw": raw_taf,
            "time": datetime.now(timezone.utc).isoformat(),
            "source": "NOAA"
        }
    
    raise HTTPException(status_code=404, detail=f"TAF not found for {icao}")

@app.get("/conditions/{icao}")
async def get_conditions(icao: str):
    """Get flight conditions for airport"""
    icao = icao.upper().strip()
    
    raw_metar = await fetch_metar_noaa(icao)
    if raw_metar:
        conditions = parse_flight_category(raw_metar)
        return {
            "icao": icao,
            "conditions": conditions.dict(),
            "metar": raw_metar,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    raise HTTPException(status_code=404, detail=f"Conditions not available for {icao}")

@app.get("/multi")
async def get_multi_airport(
    icaos: str = Query(..., description="Comma-separated ICAO codes")
):
    """Get METAR for multiple airports"""
    codes = [c.strip().upper() for c in icaos.split(",") if c.strip()]
    
    if len(codes) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 airports per request")
    
    results = []
    tasks = [fetch_metar_noaa(code) for code in codes]
    metars = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, code in enumerate(codes):
        metar = metars[i]
        if isinstance(metar, str) and metar:
            conditions = parse_flight_category(metar)
            results.append({
                "icao": code,
                "raw": metar,
                "flight_category": conditions.category,
                "category_color": conditions.color
            })
        else:
            results.append({
                "icao": code,
                "error": "Not available"
            })
    
    return {
        "count": len(results),
        "airports": results,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/airports/search")
async def search_airports(
    query: str = Query(..., min_length=2, description="Search by ICAO, IATA, or city name")
):
    """Search for airports"""
    # In production, this would query a database
    # For now, return common airports matching query
    common_airports = [
        {"icao": "KJFK", "iata": "JFK", "name": "John F Kennedy Intl", "city": "New York", "country": "USA"},
        {"icao": "KLAX", "iata": "LAX", "name": "Los Angeles Intl", "city": "Los Angeles", "country": "USA"},
        {"icao": "EGLL", "iata": "LHR", "name": "London Heathrow", "city": "London", "country": "UK"},
        {"icao": "EDDF", "iata": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany"},
        {"icao": "LFPG", "iata": "CDG", "name": "Charles de Gaulle", "city": "Paris", "country": "France"},
        {"icao": "EHAM", "iata": "AMS", "name": "Amsterdam Schiphol", "city": "Amsterdam", "country": "Netherlands"},
        {"icao": "LATI", "iata": "TIA", "name": "Tirana Intl", "city": "Tirana", "country": "Albania"},
        {"icao": "BKPR", "iata": "PRN", "name": "Pristina Intl", "city": "Pristina", "country": "Kosovo"},
    ]
    
    query_lower = query.lower()
    matches = [
        a for a in common_airports
        if query_lower in a["icao"].lower()
        or query_lower in a.get("iata", "").lower()
        or query_lower in a["city"].lower()
        or query_lower in a["name"].lower()
    ]
    
    return {"results": matches, "count": len(matches)}

# =====================
# STARTUP
# =====================

if __name__ == "__main__":
    port = int(os.getenv("AVIATION_PORT", 8080))
    logger.info(f"🛫 Starting Aviation Weather API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

