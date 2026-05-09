#!/usr/bin/env python3
"""
DataSource Stub - Generic stub for all 8 datasource containers
Usage: python datasource_stub.py <port> <region>
Example: python datasource_stub.py 9301 europe
"""
import sys
import uvicorn
from fastapi import FastAPI
from datetime import datetime

# Parse arguments
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9301
REGION = sys.argv[2] if len(sys.argv) > 2 else "unknown"

app = FastAPI(
    title=f"DataSource {REGION.title()}",
    description=f"Kloud DataSource for {REGION.upper()} region",
    version="1.0.0"
)

# Regional data sources configuration
REGIONAL_SOURCES = {
    "europe": ["eurostat", "ecb", "balkans", "eu_open_data"],
    "americas": ["us_census", "fred", "brazil", "canada"],
    "asia": ["china_nbs", "japan_stat", "kostat", "asean"],
    "india": ["india_data", "rbi", "pakistan", "south_asia"],
    "africa": ["afdb", "saudi", "uae", "nigeria", "south_africa"],
    "oceania": ["abs_australia", "stats_nz", "pacific_spc"],
    "central_asia": ["kazstat", "uzstat", "georgia", "armenia"],
    "antarctica": ["scar", "ats", "research_stations"]
}

@app.get("/")
def root():
    return {
        "service": f"datasource-{REGION}",
        "region": REGION,
        "port": PORT,
        "status": "operational"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "region": REGION,
        "port": PORT,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/sources")
def sources():
    return {
        "region": REGION,
        "sources": REGIONAL_SOURCES.get(REGION, []),
        "total": len(REGIONAL_SOURCES.get(REGION, []))
    }

@app.get("/data/{source_id}")
def get_data(source_id: str):
    return {
        "source": source_id,
        "region": REGION,
        "data": {"sample": True, "message": f"Data from {source_id} in {REGION}"},
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    print(f"🌍 Starting DataSource {REGION.upper()} on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

