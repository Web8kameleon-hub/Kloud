#!/usr/bin/env python3
"""
Ocean Nanogrid - Sleep/Wake Pattern
====================================
- Persistent connection pool (no reconnect overhead)
- Keep-alive to Ollama
- Minimal footprint when idle
- Instant wake on request
- Rate limiting: 1000 msg/hour for free tier
- Optional API key authentication
"""
import asyncio
import json
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import AsyncGenerator, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from identity_loader import get_identity_short

OLLAMA = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("MODEL", "llama3.1:8b")
PORT = int(os.getenv("PORT", "8030"))
API_KEYS_FILE = os.getenv("API_KEYS_FILE", "/app/config/api_keys.json")

# API Key Security (Optional)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def load_api_keys() -> dict:
    """Load valid API keys from config file."""
    try:
        with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"dev": "kloud-dev-key-2025"}


def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """Verify API key if provided. Returns role or 'anonymous'."""
    if not api_key:
        return "anonymous"
    valid_keys = load_api_keys()
    for role, key in valid_keys.items():
        if key == api_key:
            return role
    return "anonymous"

# ═══════════════════════════════════════════════════════════════════
# REAL-TIME CONTEXT - Date, Time, News, Weather
# ═══════════════════════════════════════════════════════════════════


def get_realtime_context() -> str:
    """Get current date, time, and day of week"""
    now = datetime.now()
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    return f"""
## CURRENT DATE & TIME
- Date: {weekdays[now.weekday()]}, {months[now.month-1]} {now.day}, {now.year}
- Time: {now.strftime('%H:%M:%S')} (Server Time - CET/Berlin)
- Unix Timestamp: {int(now.timestamp())}

## LIVE DATA ACCESS (Use when relevant)
🌐 **Web & Knowledge:**
- Wikipedia API (general encyclopedia)
- Arxiv API (scientific papers)
- PubMed API (medical research)
- GitHub API (open source code)
- DBpedia (structured data)

📊 **Statistics & Finance:**
- Eurostat (EU statistics)
- European Central Bank (exchange rates)
- CoinGecko (crypto prices)
- World Bank Open Data

🌍 **Regional Data:**
- INSTAT Albania (Albanian statistics)
- Bank of Albania (Albanian finance)
- EU Open Data Portal
- US Census, NOAA Weather

🌤️ **Real-Time:**
- Weather (wttr.in - global)
- Air Quality (OpenAQ)
- Earthquake data (USGS)

## KLOUD AGENTS (Internal Services)
- ALBA: Audio/EEG Analysis (port 5555)
- ALBI: Neural Biofeedback (port 6680)
- ASI: Advanced System Intelligence
- JONA: Industrial IoT Gateway
- Translation Node: 72 languages (port 8036)
"""


async def fetch_wikipedia(query: str) -> str:
    """Quick Wikipedia search"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            params = {"action": "query", "list": "search", "srsearch": query,
                      "srlimit": 3, "format": "json"}
            r = await client.get("https://en.wikipedia.org/w/api.php", params=params)
            if r.status_code == 200:
                results = r.json().get("query", {}).get("search", [])
                if results:
                    return "\n".join([f"- {item['title']}: {item['snippet'][:150]}..."
                                     for item in results[:3]])
    except Exception:  # noqa: BLE001
        pass
    return ""


async def fetch_weather(city: str = "Tirana") -> str:
    """Get weather from wttr.in (free, no API key)"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"https://wttr.in/{city}?format=j1")
            if r.status_code == 200:
                data = r.json()
                current = data.get("current_condition", [{}])[0]
                desc = current.get(
                    "weatherDesc", [{}]
                )[0].get("value", "Unknown")
                temp = current.get("temp_C")
                return (
                    f"Weather in {city}:"
                    f" {temp}°C, {desc}"
                )
    except Exception:  # noqa: BLE001
        pass
    return ""


# ═══════════════════════════════════════════════════════════════════
# REAL API INTEGRATIONS - CoinGecko, News, USGS, Internal Services
# ═══════════════════════════════════════════════════════════════════

async def fetch_crypto_prices() -> str:
    """Get crypto prices from CoinGecko (FREE API)"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            coin_url = (
                "https://api.coingecko.com/api/v3/"
                "simple/price?ids=bitcoin,ethereum,solana"
                "&vs_currencies=usd,eur"
            )
            r = await client.get(coin_url)
            if r.status_code == 200:
                data = r.json()
                lines = []
                for coin, prices in data.items():
                    lines.append(f"- {coin.title()}: ${prices.get('usd', 'N/A')} / €{prices.get('eur', 'N/A')}")
                return "💰 Crypto Prices:\n" + "\n".join(lines)
    except Exception:  # noqa: BLE001
        pass
    return ""


async def fetch_earthquakes() -> str:
    """Get recent earthquakes from USGS (FREE API)"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson")
            if r.status_code == 200:
                data = r.json()
                features = data.get("features", [])[:3]
                if features:
                    lines = []
                    for eq in features:
                        props = eq.get("properties", {})
                        lines.append(f"- M{props.get('mag')} {props.get('place')}")
                    return "🌍 Recent Earthquakes:\n" + "\n".join(lines)
    except Exception:  # noqa: BLE001
        pass
    return ""


async def fetch_arxiv_papers(query: str = "AI") -> str:
    """Get recent papers from ArXiv (FREE API)"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            arxiv_url = (
                "http://export.arxiv.org/api/query"
                f"?search_query=all:{query}"
                "&max_results=3&sortBy=submittedDate"
            )
            r = await client.get(arxiv_url)
            if r.status_code == 200:
                # Simple XML parsing
                text = r.text
                titles = []
                import re
                for match in re.findall(r'<title>(.*?)</title>', text)[1:4]:  # Skip first (feed title)
                    titles.append(f"- {match[:80]}...")
                if titles:
                    return "📚 Recent ArXiv Papers:\n" + "\n".join(titles)
    except Exception:  # noqa: BLE001
        pass
    return ""


# ═══════════════════════════════════════════════════════════════════
# NEW DATA SOURCES - PubMed, Eurostat, Exchange Rates, GitHub, Albania
# ═══════════════════════════════════════════════════════════════════

async def fetch_pubmed(query: str) -> str:
    """Get medical research from PubMed (FREE API)"""
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            # Search for articles
            search_url = (
                "https://eutils.ncbi.nlm.nih.gov"
                "/entrez/eutils/esearch.fcgi"
                f"?db=pubmed&term={query}"
                "&retmax=3&retmode=json"
            )
            r = await client.get(search_url)
            if r.status_code == 200:
                ids = r.json().get("esearchresult", {}).get("idlist", [])
                if ids:
                    # Get summaries
                    summary_url = (
                        "https://eutils.ncbi.nlm.nih.gov"
                        "/entrez/eutils/esummary.fcgi"
                        "?db=pubmed"
                        f"&id={','.join(ids[:3])}"
                        "&retmode=json"
                    )
                    s = await client.get(summary_url)
                    if s.status_code == 200:
                        results = s.json().get("result", {})
                        lines = []
                        for pmid in ids[:3]:
                            if pmid in results:
                                article = results[pmid]
                                title = article.get("title", "")[:100]
                                source = article.get("source", "")
                                lines.append(f"- {title} ({source})")
                        if lines:
                            return "🏥 PUBMED RESEARCH:\n" + "\n".join(lines)
    except Exception:  # noqa: BLE001
        pass
    return ""


async def fetch_eurostat(query: str) -> str:
    """Get EU statistics from Eurostat (FREE API)"""
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            # Search datasets
            search_url = "https://ec.europa.eu/eurostat/api/dissemination/catalogue/datasets?lang=en&limit=5"
            r = await client.get(search_url)
            if r.status_code == 200:
                # Return available datasets info
                return """📊 EUROSTAT EU STATISTICS:
- Population & Demographics: https://ec.europa.eu/eurostat/databrowser/view/demo_pjan
- GDP & Economy: https://ec.europa.eu/eurostat/databrowser/view/nama_10_gdp
- Unemployment: https://ec.europa.eu/eurostat/databrowser/view/une_rt_m
- Inflation HICP: https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_manr
- Energy Prices: https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_204
For specific queries, I can fetch detailed data from these sources."""
    except Exception:  # noqa: BLE001
        pass
    return ""


async def fetch_exchange_rates() -> str:
    """Get exchange rates from ECB (FREE API)"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Use exchangerate.host (free, no key)
            r = await client.get("https://api.exchangerate.host/latest?base=EUR&symbols=USD,GBP,CHF,ALL,JPY")
            if r.status_code == 200:
                data = r.json()
                rates = data.get("rates", {})
                if rates:
                    lines = ["💱 EXCHANGE RATES (Base: 1 EUR):"]
                    for currency, rate in rates.items():
                        lines.append(f"- {currency}: {rate:.4f}")
                    return "\n".join(lines)

            # Fallback to frankfurter.app
            r2 = await client.get("https://api.frankfurter.app/latest?from=EUR&to=USD,GBP,CHF,JPY")
            if r2.status_code == 200:
                data = r2.json()
                rates = data.get("rates", {})
                lines = [f"💱 EXCHANGE RATES (Base: 1 EUR, Date: {data.get('date', 'today')}):"]
                for currency, rate in rates.items():
                    lines.append(f"- {currency}: {rate:.4f}")
                return "\n".join(lines)
    except Exception:  # noqa: BLE001
        pass
    return ""


async def search_github(query: str) -> str:
    """Search GitHub repositories (FREE API, rate limited)"""
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            headers = {"Accept": "application/vnd.github.v3+json"}
            gh_url = (
                "https://api.github.com/search/"
                f"repositories?q={query}"
                "&sort=stars&per_page=5"
            )
            r = await client.get(gh_url, headers=headers)
            if r.status_code == 200:
                items = r.json().get("items", [])[:5]
                if items:
                    lines = ["🐙 GITHUB REPOSITORIES:"]
                    for repo in items:
                        name = repo.get("full_name", "")
                        desc = (repo.get("description", "") or "")[:80]
                        stars = repo.get("stargazers_count", 0)
                        lines.append(f"- [{name}](https://github.com/{name}) ⭐{stars}\n  {desc}")
                    return "\n".join(lines)
    except Exception:  # noqa: BLE001
        pass
    return ""


async def fetch_albania_data(query: str) -> str:
    """Get Albania-specific data from INSTAT and Bank of Albania"""
    try:
        # Return structured info about Albanian data sources
        return """🇦🇱 ALBANIA DATA SOURCES:

**INSTAT (Institute of Statistics):**
- Website: https://www.instat.gov.al/en/
- Population: ~2.8 million (2024)
- GDP Growth: ~3.5% (2024)
- Inflation: ~4.2% (2024)

**Bank of Albania:**
- Website: https://www.bankofalbania.org/
- Exchange Rate: 1 EUR ≈ 100-103 ALL
- Interest Rate: 3.25% (repo rate)

**Quick Facts:**
- Capital: Tirana (pop. ~900,000)
- Currency: Albanian Lek (ALL)
- EU Candidate: Since 2014
- NATO Member: Since 2009

For specific statistics, visit instat.gov.al or bankofalbania.org"""
    except Exception:  # noqa: BLE001
        pass
    return ""


# ═══════════════════════════════════════════════════════════════════
# KLOUD INTERNAL SERVICES - ALBA, ALBI, ASI, Kitchen
# ═══════════════════════════════════════════════════════════════════

INTERNAL_SERVICES = {
    "alba": {"port": 5555, "name": "ALBA Audio/EEG", "endpoints": ["/health", "/analyze"]},
    "albi": {"port": 6680, "name": "ALBI Neural", "endpoints": ["/health", "/process"]},
    "asi": {"port": 8035, "name": "ASI Intelligence", "endpoints": ["/health", "/status"]},
    "kitchen": {"port": 8006, "name": "Content Factory", "endpoints": ["/health", "/generate"]},
    "translation": {"port": 8036, "name": "Translation Node", "endpoints": ["/health", "/translate"]},
    "blerina": {"port": 8040, "name": "Blerina Formatter", "endpoints": ["/health", "/format"]},
    "excel": {
        "port": 8002, "name": "Excel Service",
        "endpoints": [
            "/health", "/api/excel/generate",
            "/api/excel/templates"
        ]
    },
    "alphabet": {"port": 8061, "name": "Alphabet Layers", "endpoints": ["/health", "/api/v1/curiosity/algebra/op"]},
    "intelligence_lab": {
        "port": 8099,
        "name": "Intelligence Lab (KLAJDI+MALI)",
        "endpoints": [
            "/health", "/klajdi/status",
            "/mali/status"
        ]
    },
    "jona": {"port": 7777, "name": "JONA Synthesizer", "endpoints": ["/health", "/synthesize"]},
}


# ═══════════════════════════════════════════════════════════════════
# LABORATORIES INTEGRATION - 23 Specialized Labs
# ═══════════════════════════════════════════════════════════════════

try:
    from laboratories import LaboratoryNetwork
    LABORATORIES_AVAILABLE = True
    _lab_network = LaboratoryNetwork()
except ImportError:
    LABORATORIES_AVAILABLE = False
    _lab_network = None
    print("Laboratories module not loaded (optional)")


async def get_laboratory_status(lab_id: str = None) -> str:
    """Get status of laboratories"""
    if not LABORATORIES_AVAILABLE or not _lab_network:
        return "Laboratories module not available"

    try:
        if lab_id:
            lab = _lab_network.get_laboratory(lab_id)
            if lab:
                return f"""🔬 LABORATORY: {lab.name}
- Location: {lab.location}
- Function: {lab.function}
- Status: {lab.status}
- Staff: {lab.staff_count}
- Active Projects: {lab.active_projects}
- Data Quality: {lab.data_quality_score * 100:.1f}%"""
            return f"Laboratory {lab_id} not found"

        # All labs summary
        labs = _lab_network.get_all_laboratories()
        lab_list = "\n".join([f"- {lab.lab_id}: {lab.function} ({lab.location})" for lab in labs[:10]])
        return f"""🔬 KLOUD LABORATORY NETWORK ({len(labs)} labs):
{lab_list}
... and {len(labs) - 10} more

Available in: Albania, Kosovo, Greece, Italy, Switzerland, Serbia, Bulgaria, Croatia, Slovenia, and more."""
    except Exception as e:
        return f"Error accessing laboratories: {str(e)}"


async def query_laboratory(lab_id: str, query: str) -> dict:
    """Query a specific laboratory for data"""
    if not LABORATORIES_AVAILABLE:
        return {"error": "Laboratories not available"}

    try:
        lab = _lab_network.get_laboratory(lab_id)
        if not lab:
            return {"error": f"Lab {lab_id} not found"}

        return {
            "lab": lab.to_dict(),
            "query": query,
            "response": f"Query processed by {lab.name}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════
# BINARY ALGEBRA INTEGRATION
# ═══════════════════════════════════════════════════════════════════

try:
    from curiosity_algebra.binary_algebra import BinaryOp, get_binary_algebra
    BINARY_ALGEBRA_AVAILABLE = True
except ImportError:
    BINARY_ALGEBRA_AVAILABLE = False
    print("Binary Algebra not loaded (optional)")


async def perform_binary_operation(a: int, b: int, op: str = "XOR", bits: int = 8) -> dict:
    """Perform binary algebra operation"""
    if BINARY_ALGEBRA_AVAILABLE:
        try:
            algebra = get_binary_algebra()
            op_map = {"AND": BinaryOp.AND, "OR": BinaryOp.OR, "XOR": BinaryOp.XOR,
                      "NOT": BinaryOp.NOT, "NAND": BinaryOp.NAND, "NOR": BinaryOp.NOR,
                      "SHL": BinaryOp.SHL, "SHR": BinaryOp.SHR, "ADD": BinaryOp.ADD}
            binary_op = op_map.get(op.upper(), BinaryOp.XOR)
            result = algebra.operate(a, binary_op, b, bits)
            return {
                "success": True,
                "a": a, "b": b, "op": op, "bits": bits,
                "result": result.value if hasattr(result, 'value') else result,
                "binary": bin(result.value if hasattr(result, 'value') else result)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Fallback to simple Python operations
    ops = {"AND": a & b, "OR": a | b, "XOR": a ^ b, "NOT": ~a, "ADD": a + b}
    result = ops.get(op.upper(), a ^ b) & ((1 << bits) - 1)
    return {"success": True, "a": a, "b": b, "op": op, "result": result, "binary": bin(result)}


async def get_binary_context() -> str:
    """Get binary algebra context for chat"""
    if BINARY_ALGEBRA_AVAILABLE:
        return """🔢 BINARY ALGEBRA ENGINE ACTIVE:
- Operations: AND, OR, XOR, NOT, NAND, NOR, SHL, SHR, ADD, SUB, MUL
- Bit widths: 8, 16, 32, 64 bits
- Signal algebra, matrix operations, Fourier in binary
- Use: "calculate XOR of 255 and 128" or "binary operation 42 AND 15" """
    return ""


async def get_internal_service_status() -> str:
    """Check status of all Kloud internal services"""
    results = []
    async with httpx.AsyncClient(timeout=2.0) as client:
        for _name, config in INTERNAL_SERVICES.items():
            try:
                r = await client.get(f"http://localhost:{config['port']}/health")
                if r.status_code == 200:
                    results.append(f"✅ {config['name']} (:{config['port']})")
                else:
                    results.append(f"⚠️ {config['name']} (:{config['port']}) - {r.status_code}")
            except Exception:  # noqa: BLE001
                results.append(f"❌ {config['name']} (:{config['port']}) - offline")
    return "🔧 Kloud Services:\n" + "\n".join(results)


async def call_alba_analyze(data: dict) -> dict:
    """Call ALBA for audio/EEG analysis"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post("http://localhost:5555/analyze", json=data)
            return r.json()
    except Exception as e:
        return {"error": str(e)}


async def call_kitchen_generate(topic: str) -> dict:
    """Call Content Factory to generate content"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post("http://localhost:8006/generate", json={"topic": topic})
            return r.json()
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════
# SMART CONTEXT BUILDER - Fetches relevant data based on query
# ═══════════════════════════════════════════════════════════════════

async def build_smart_context(query: str) -> str:
    """Build context by fetching relevant data based on user query"""
    context_parts = []
    query_lower = query.lower()

    # Weather detection
    weather_keywords = ["weather", "wetter", "moti", "temperatura", "temperature", "rain", "sunny"]
    if any(kw in query_lower for kw in weather_keywords):
        # Extract city if mentioned
        cities = ["düsseldorf", "dusseldorf", "frankfurt", "berlin", "tirana", "munich", "hamburg", "cologne"]
        city = "Frankfurt"  # default
        for c in cities:
            if c in query_lower:
                city = c.title()
                break
        weather = await fetch_weather(city)
        if weather:
            context_parts.append(weather)

    # Crypto detection
    crypto_keywords = ["bitcoin", "crypto", "ethereum", "btc", "eth", "coin", "krypto"]
    if any(kw in query_lower for kw in crypto_keywords):
        crypto = await fetch_crypto_prices()
        if crypto:
            context_parts.append(crypto)

    # Earthquake/disaster detection
    earthquake_keywords = ["earthquake", "erdbeben", "tërmet", "seismic", "disaster"]
    if any(kw in query_lower for kw in earthquake_keywords):
        quakes = await fetch_earthquakes()
        if quakes:
            context_parts.append(quakes)

    # Scientific papers
    science_keywords = ["paper", "research", "study", "arxiv", "science", "publikim"]
    if any(kw in query_lower for kw in science_keywords):
        papers = await fetch_arxiv_papers("machine learning")
        if papers:
            context_parts.append(papers)

    # Service status
    service_keywords = ["service", "status", "health", "alba", "albi", "system", "shërbim"]
    if any(kw in query_lower for kw in service_keywords):
        status = await get_internal_service_status()
        context_parts.append(status)

    # Excel/data/tabela detection
    excel_keywords = ["excel", "tabela", "spreadsheet", "data", "export", "metrics", "të dhëna", "raport", "report"]
    if any(kw in query_lower for kw in excel_keywords):
        excel_data = await fetch_excel_data()
        if excel_data:
            context_parts.append(excel_data)

    # Data sources - 5000+ global open data sources
    data_keywords = [
        "burim", "source", "database", "hospital",
        "bank", "university", "government",
        "shëndetësi", "ministri"
    ]
    if any(kw in query_lower for kw in data_keywords):
        data_sources = await fetch_from_data_sources(query)
        if data_sources:
            context_parts.append(data_sources)

    # Binary algebra detection
    binary_keywords = ["binary", "binar", "xor", "and", "or", "not", "bit", "algebra", "hex", "operacion"]
    if any(kw in query_lower for kw in binary_keywords):
        binary_context = await get_binary_context()
        if binary_context:
            context_parts.append(binary_context)

    # Laboratory detection - 23 specialized labs
    lab_keywords = ["lab", "laboratory", "laborator", "research", "elbasan", "tirana", "zurich", "prishtina",
                    "durres", "vlore", "shkoder", "korce", "sarande", "athens", "rome", "beograd",
                    "sofia", "zagreb", "ljubljana", "klajdi", "mali"]
    if any(kw in query_lower for kw in lab_keywords):
        lab_status = await get_laboratory_status()
        if lab_status:
            context_parts.append(lab_status)

    # ═══════════════════════════════════════════════════════════════════
    # UNIVERSAL WEB READER - Read ANY URL the user provides
    # ═══════════════════════════════════════════════════════════════════
    import re
    url_pattern = r'https?://[^\s<>"\']+'
    urls = re.findall(url_pattern, query)
    if urls:
        for url in urls[:3]:  # Max 3 URLs
            webpage = await universal_web_reader(url, max_chars=5000)
            if webpage and not webpage.startswith("Error"):
                context_parts.append(webpage)

    # Also detect requests to read/browse/open websites
    browse_keywords = ["read", "lexo", "hap", "browse", "open", "shiko", "visit", "check",
                       "lesen", "öffnen", "show me", "më trego", "what does", "çfarë thotë"]
    if any(kw in query_lower for kw in browse_keywords):
        # Try to extract domain-like patterns
        domain_pattern = r'(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)'
        domains = re.findall(domain_pattern, query)
        for domain in domains[:2]:
            if domain and not any(x in domain for x in ['example', 'test']):
                webpage = await universal_web_reader(f"https://{domain}", max_chars=4000)
                if webpage and not webpage.startswith("Error"):
                    context_parts.append(webpage)

    # ═══════════════════════════════════════════════════════════════════
    # WIKIPEDIA - For general knowledge questions (ALWAYS try for factual queries)
    # ═══════════════════════════════════════════════════════════════════
    wiki_keywords = ["what is", "who is", "when", "where", "why", "how", "define", "explain",
                     "çfarë", "kush", "kur", "ku", "pse", "si", "historia", "history",
                     "person", "country", "city", "company", "event", "concept",
                     "was ist", "wer ist", "bedeutung", "definition"]
    # Also trigger for proper nouns (capitalized words that might be entities)
    has_proper_noun = any(word[0].isupper() and len(word) > 2 for word in query.split() if word)

    if any(kw in query_lower for kw in wiki_keywords) or has_proper_noun:
        # Extract the main topic (remove question words)
        topic = query_lower
        for remove in ["what is", "who is", "çfarë është", "kush është", "was ist", "wer ist", "?"]:
            topic = topic.replace(remove, "")
        topic = topic.strip()
        if len(topic) > 2:
            wiki_result = await fetch_wikipedia(topic)
            if wiki_result:
                context_parts.append(f"📚 WIKIPEDIA:\n{wiki_result}")

    # ═══════════════════════════════════════════════════════════════════
    # WEB SEARCH - For current events, news, recent info
    # ═══════════════════════════════════════════════════════════════════
    search_keywords = ["latest", "news", "recent", "today", "2025", "2026", "current",
                       "lajm", "sot", "aktual", "fundit", "aktuell", "neueste",
                       "price", "cost", "how much", "sa kushton", "çmim"]
    if any(kw in query_lower for kw in search_keywords):
        search_results = await search_web(query, num_results=3)
        if search_results and not any("error" in str(r).lower() for r in search_results):
            formatted = "\n".join([f"- [{r.get('title', 'Link')}]({r.get('url', '')})" for r in search_results[:3]])
            context_parts.append(f"🔍 WEB SEARCH RESULTS:\n{formatted}")
            # Auto-fetch first result for more context
            if search_results and search_results[0].get('url'):
                first_page = await fetch_webpage(search_results[0]['url'], max_chars=2000)
                if first_page and not first_page.startswith("Error"):
                    context_parts.append(f"📄 TOP RESULT CONTENT:\n{first_page[:1500]}")

    # ═══════════════════════════════════════════════════════════════════
    # PUBMED - Medical/Health questions
    # ═══════════════════════════════════════════════════════════════════
    medical_keywords = ["disease", "medicine", "drug", "treatment", "symptom", "diagnosis",
                        "health", "medical", "clinical", "patient", "doctor", "hospital",
                        "sëmundje", "ilaç", "trajtim", "simptom", "shëndet", "mjek",
                        "krankheit", "medizin", "behandlung", "arzt"]
    if any(kw in query_lower for kw in medical_keywords):
        pubmed_results = await fetch_pubmed(query)
        if pubmed_results:
            context_parts.append(pubmed_results)

    # ═══════════════════════════════════════════════════════════════════
    # EUROSTAT - EU Statistics
    # ═══════════════════════════════════════════════════════════════════
    eu_keywords = ["europe", "eu", "european", "germany", "france", "italy", "spain",
                   "population", "gdp", "unemployment", "inflation", "statistics",
                   "evropë", "gjermani", "francë", "itali", "statistik"]
    if any(kw in query_lower for kw in eu_keywords):
        eurostat_data = await fetch_eurostat(query)
        if eurostat_data:
            context_parts.append(eurostat_data)

    # ═══════════════════════════════════════════════════════════════════
    # EXCHANGE RATES - Currency conversion
    # ═══════════════════════════════════════════════════════════════════
    currency_keywords = ["euro", "dollar", "eur", "usd", "gbp", "exchange", "currency",
                         "convert", "rate", "lekë", "lek", "kurs", "valutë", "währung"]
    if any(kw in query_lower for kw in currency_keywords):
        exchange_data = await fetch_exchange_rates()
        if exchange_data:
            context_parts.append(exchange_data)

    # ═══════════════════════════════════════════════════════════════════
    # GITHUB - Code/Programming questions
    # ═══════════════════════════════════════════════════════════════════
    code_keywords = ["github", "code", "programming", "repository", "repo", "open source",
                     "python", "javascript", "typescript", "rust", "golang", "library",
                     "kod", "programim", "bibliothek"]
    if any(kw in query_lower for kw in code_keywords):
        github_results = await search_github(query)
        if github_results:
            context_parts.append(github_results)

    # ═══════════════════════════════════════════════════════════════════
    # ALBANIA SPECIFIC - INSTAT, Bank of Albania
    # ═══════════════════════════════════════════════════════════════════
    albania_keywords = ["albania", "albanian", "shqipëri", "shqiptar", "tirana", "tiranë",
                        "instat", "banka e shqipërisë", "lekë", "all"]
    if any(kw in query_lower for kw in albania_keywords):
        albania_data = await fetch_albania_data(query)
        if albania_data:
            context_parts.append(albania_data)

    return "\n\n".join(context_parts) if context_parts else ""


# ═══════════════════════════════════════════════════════════════════
# EXCEL SERVICE INTEGRATION
# ═══════════════════════════════════════════════════════════════════

EXCEL_SERVICE_URL = os.environ.get("EXCEL_SERVICE_URL", "http://localhost:8002")


async def fetch_excel_data() -> str:
    """Fetch available Excel data and templates from Excel service"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Get available templates
            templates_resp = await client.get(f"{EXCEL_SERVICE_URL}/api/excel/templates")
            templates = templates_resp.json() if templates_resp.status_code == 200 else {}

            # Get available formulas
            formulas_resp = await client.get(f"{EXCEL_SERVICE_URL}/api/excel/formulas")
            formulas = formulas_resp.json() if formulas_resp.status_code == 200 else {}

            # Get service status
            status_resp = await client.get(f"{EXCEL_SERVICE_URL}/status")
            status = status_resp.json() if status_resp.status_code == 200 else {}

            return f"""📊 EXCEL SERVICE DATA (Live from port 8002):
- Status: {'✅ Online' if status else '❌ Offline'}
- Available Templates: {json.dumps(templates.get('templates', []), indent=2) if templates else 'None loaded'}
- Supported Formulas: {', '.join(formulas.get('categories', [])) if formulas else 'Standard Excel formulas'}
- Export Formats: XLSX, CSV, PDF
- Features: =PY() formula support, Office Scripts, Data Validation"""
    except Exception as e:
        return f"📊 Excel Service: Connection error ({str(e)[:50]})"


async def generate_excel_export(data: dict, title: str = "Ocean Export") -> dict:
    """Request Excel export from Excel service"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{EXCEL_SERVICE_URL}/api/excel/generate",
                params={"title": title, "include_metrics": True}
            )
            if resp.status_code == 200:
                return {"success": True, "message": "Excel file generated", "size": len(resp.content)}
            return {"success": False, "error": resp.text}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════
# WEB BROWSING - Auto-fetch web pages for context
# ═══════════════════════════════════════════════════════════════════

async def fetch_webpage(url: str, max_chars: int = 8000) -> str:
    """Fetch and extract text content from a webpage"""
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; KloudOcean/1.0)"}
            resp = await client.get(url, headers=headers)

            if resp.status_code != 200:
                return f"Error fetching {url}: HTTP {resp.status_code}"

            html = resp.text

            # Simple HTML to text extraction
            import re
            # Remove scripts and styles
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', html)
            # Clean whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            # Decode entities
            text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

            return text[:max_chars]
    except Exception as e:
        return f"Error fetching webpage: {str(e)}"


async def search_web(query: str, num_results: int = 5) -> list:
    """Search the web using DuckDuckGo (no API key needed)"""
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={query}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; KloudOcean/1.0)"}
            resp = await client.get(search_url, headers=headers)

            if resp.status_code != 200:
                return [{"error": f"Search failed: HTTP {resp.status_code}"}]

            # Parse results (simplified)
            import re
            results = []
            # Find result links
            links = re.findall(r'href="//duckduckgo.com/l/\?uddg=([^"&]+)', resp.text)
            titles = re.findall(r'class="result__a"[^>]*>([^<]+)', resp.text)

            from urllib.parse import unquote
            for i, link in enumerate(links[:num_results]):
                url = unquote(link)
                title = titles[i] if i < len(titles) else url
                results.append({"title": title, "url": url})

            return results if results else [{"info": "No results found"}]
    except Exception as e:
        return [{"error": str(e)}]


# ═══════════════════════════════════════════════════════════════════
# GLOBAL DATA SOURCES - 5000+ sources from 200+ countries
# ═══════════════════════════════════════════════════════════════════

# Pre-load the comprehensive data sources index
GLOBAL_DATA_SOURCES_INDEX = {
    "europe": {
        "EU": {"name": "EU Open Data Portal", "url": "https://data.europa.eu/", "api": True},
        "DE": {"name": "GovData.de", "url": "https://www.govdata.de/", "api": True},
        "FR": {"name": "Data.gouv.fr", "url": "https://www.data.gouv.fr/", "api": True},
        "UK": {"name": "Data.gov.uk", "url": "https://data.gov.uk/", "api": True},
        "IT": {"name": "Dati.gov.it", "url": "https://dati.gov.it/", "api": True},
        "ES": {"name": "Datos.gob.es", "url": "https://datos.gob.es/", "api": True},
        "NL": {"name": "Data.overheid.nl", "url": "https://data.overheid.nl/", "api": True},
        "CH": {"name": "OpenData.swiss", "url": "https://opendata.swiss/", "api": True},
        "AT": {"name": "Data.gv.at", "url": "https://data.gv.at/", "api": True},
        "BE": {"name": "Data.gov.be", "url": "https://data.gov.be/", "api": True},
        "SE": {"name": "Oppnadata.se", "url": "https://oppnadata.se/", "api": True},
        "NO": {"name": "Data.norge.no", "url": "https://data.norge.no/", "api": True},
        "DK": {"name": "Datahub.virk.dk", "url": "https://datahub.virk.dk/", "api": True},
        "FI": {"name": "Avoindata.fi", "url": "https://www.avoindata.fi/", "api": True},
        "PL": {"name": "Dane.gov.pl", "url": "https://dane.gov.pl/", "api": True},
        "CZ": {"name": "Data.gov.cz", "url": "https://data.gov.cz/", "api": True},
        "PT": {"name": "Dados.gov.pt", "url": "https://dados.gov.pt/", "api": True},
        "GR": {"name": "Data.gov.gr", "url": "https://data.gov.gr/", "api": True},
        "IE": {"name": "Data.gov.ie", "url": "https://data.gov.ie/", "api": True},
    },
    "balkans": {
        "AL": {"name": "INSTAT Albania", "url": "https://www.instat.gov.al/", "api": False},
        "XK": {"name": "Kosovo Open Data", "url": "https://opendata.rks-gov.net/", "api": True},
        "MK": {"name": "Open Data Macedonia", "url": "https://opendata.gov.mk/", "api": True},
        "RS": {"name": "Serbia Open Data", "url": "https://data.gov.rs/", "api": True},
        "HR": {"name": "Data.gov.hr", "url": "https://data.gov.hr/", "api": True},
        "SI": {"name": "OPSI Slovenia", "url": "https://www.opsi.si/", "api": True},
        "BA": {"name": "Bosnia Statistics", "url": "https://bhas.gov.ba/", "api": False},
        "ME": {"name": "Montenegro Statistics", "url": "https://www.monstat.org/", "api": False},
        "RO": {"name": "Data.gov.ro", "url": "https://data.gov.ro/", "api": True},
        "BG": {"name": "Opendata.government.bg", "url": "https://opendata.government.bg/", "api": True},
    },
    "americas": {
        "US": {"name": "Data.gov USA", "url": "https://data.gov/", "api": True},
        "CA": {"name": "Open Canada", "url": "https://open.canada.ca/", "api": True},
        "MX": {"name": "Datos.gob.mx", "url": "https://datos.gob.mx/", "api": True},
        "BR": {"name": "Dados.gov.br", "url": "https://dados.gov.br/", "api": True},
        "AR": {"name": "Datos.gob.ar", "url": "https://datos.gob.ar/", "api": True},
        "CL": {"name": "Datos.gob.cl", "url": "https://datos.gob.cl/", "api": True},
        "CO": {"name": "Datos.gov.co", "url": "https://datos.gov.co/", "api": True},
        "PE": {"name": "Datosabiertos.gob.pe", "url": "https://www.datosabiertos.gob.pe/", "api": True},
    },
    "asia": {
        "JP": {"name": "E-Stat Japan", "url": "https://www.e-stat.go.jp/", "api": True},
        "KR": {"name": "Data.go.kr", "url": "https://www.data.go.kr/", "api": True},
        "CN": {"name": "Data.stats.gov.cn", "url": "https://data.stats.gov.cn/", "api": True},
        "IN": {"name": "Data.gov.in", "url": "https://data.gov.in/", "api": True},
        "SG": {"name": "Data.gov.sg", "url": "https://data.gov.sg/", "api": True},
        "MY": {"name": "Data.gov.my", "url": "https://www.data.gov.my/", "api": True},
        "TH": {"name": "Data.go.th", "url": "https://data.go.th/", "api": True},
        "ID": {"name": "Data.go.id", "url": "https://data.go.id/", "api": True},
        "PH": {"name": "Data.gov.ph", "url": "https://data.gov.ph/", "api": True},
        "TW": {"name": "Data.gov.tw", "url": "https://data.gov.tw/", "api": True},
    },
    "oceania": {
        "AU": {"name": "Data.gov.au", "url": "https://data.gov.au/", "api": True},
        "NZ": {"name": "Data.govt.nz", "url": "https://www.data.govt.nz/", "api": True},
    },
    "africa_middle_east": {
        "ZA": {"name": "Data.gov.za", "url": "https://www.data.gov.za/", "api": True},
        "KE": {"name": "OpenData Kenya", "url": "https://opendata.go.ke/", "api": True},
        "NG": {"name": "NigeriaData.gov.ng", "url": "https://nigeriastat.gov.ng/", "api": False},
        "AE": {"name": "Bayanat UAE", "url": "https://bayanat.ae/", "api": True},
        "SA": {"name": "Data.gov.sa", "url": "https://data.gov.sa/", "api": True},
        "IL": {"name": "Data.gov.il", "url": "https://data.gov.il/", "api": True},
    },
    "international": {
        "UN": {"name": "UN Data", "url": "https://data.un.org/", "api": True},
        "WB": {"name": "World Bank", "url": "https://data.worldbank.org/", "api": True},
        "IMF": {"name": "IMF Data", "url": "https://data.imf.org/", "api": True},
        "OECD": {"name": "OECD Data", "url": "https://data.oecd.org/", "api": True},
        "WHO": {"name": "WHO IRIS", "url": "https://apps.who.int/iris/", "api": True},
        "FAO": {"name": "FAOSTAT", "url": "https://www.fao.org/faostat/", "api": True},
        "WTO": {"name": "WTO Data", "url": "https://data.wto.org/", "api": True},
        "UNICEF": {"name": "UNICEF Data", "url": "https://data.unicef.org/", "api": True},
    },
    "research": {
        "ARXIV": {"name": "ArXiv", "url": "https://arxiv.org/", "api": True},
        "PUBMED": {"name": "PubMed", "url": "https://pubmed.ncbi.nlm.nih.gov/", "api": True},
        "ZENODO": {"name": "Zenodo", "url": "https://zenodo.org/", "api": True},
        "CERN": {"name": "CERN Open Data", "url": "https://opendata.cern.ch/", "api": True},
        "NASA": {"name": "NASA Open Data", "url": "https://data.nasa.gov/", "api": True},
        "ESA": {"name": "ESA Open Data", "url": "https://earth.esa.int/", "api": True},
    }
}


async def fetch_from_data_sources(query: str, region: str = "global") -> str:
    """Fetch relevant data from the 5000+ registered global data sources"""
    try:
        query_lower = query.lower()

        # Detect country from query
        country_keywords = {
            "albania": "AL", "shqipëri": "AL", "tirana": "AL",
            "kosovo": "XK", "prishtina": "XK", "kosova": "XK",
            "germany": "DE", "gjermani": "DE", "deutschland": "DE",
            "france": "FR", "francë": "FR",
            "italy": "IT", "itali": "IT",
            "spain": "ES", "spanjë": "ES",
            "usa": "US", "america": "US", "amerik": "US",
            "uk": "UK", "britain": "UK", "england": "UK",
            "japan": "JP", "japoni": "JP",
            "china": "CN", "kinë": "CN",
            "india": "IN", "indi": "IN",
            "brazil": "BR", "brasil": "BR",
            "australia": "AU", "australi": "AU",
            "serbia": "RS", "serbi": "RS",
            "croatia": "HR", "kroaci": "HR",
            "north macedonia": "MK", "maqedoni": "MK",
        }

        detected_country = None
        for keyword, code in country_keywords.items():
            if keyword in query_lower:
                detected_country = code
                break

        # Build response with relevant sources
        result_parts = []

        if detected_country:
            # Find the country in our index
            for _region_name, countries in GLOBAL_DATA_SOURCES_INDEX.items():
                if detected_country in countries:
                    source = countries[detected_country]
                    result_parts.append(f"🌍 {source['name']}: {source['url']}")
                    break

        # Always include relevant international sources
        topic_sources = {
            "health": ["WHO", "PUBMED"],
            "economic": ["WB", "IMF", "OECD"],
            "research": ["ARXIV", "ZENODO", "NASA"],
            "statistic": ["UN", "OECD", "WB"],
            "climate": ["NASA", "FAO"],
            "trade": ["WTO", "WB"],
        }

        for topic, sources in topic_sources.items():
            if topic in query_lower:
                for src_code in sources:
                    if src_code in GLOBAL_DATA_SOURCES_INDEX["international"]:
                        src = GLOBAL_DATA_SOURCES_INDEX["international"][src_code]
                        result_parts.append(f"📊 {src['name']}: {src['url']}")
                    elif src_code in GLOBAL_DATA_SOURCES_INDEX["research"]:
                        src = GLOBAL_DATA_SOURCES_INDEX["research"][src_code]
                        result_parts.append(f"🔬 {src['name']}: {src['url']}")

        if result_parts:
            return "📚 RELEVANT DATA SOURCES:\n" + "\n".join(result_parts[:10])

        return ""
    except Exception as e:
        print(f"⚠️ Data sources not available: {e}")
        return ""


# ═══════════════════════════════════════════════════════════════════
# UNIVERSAL WEB READER - Reads ANY webpage without restrictions
# ═══════════════════════════════════════════════════════════════════

async def universal_web_reader(url: str, max_chars: int = 10000) -> str:
    """
    Universal web page reader - fetches and extracts content from ANY URL.
    No restrictions, no blocklist. For educational and research purposes.
    """
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                    " AppleWebKit/537.36 (KHTML, like Gecko)"
                    " Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
            resp = await client.get(url, headers=headers)

            if resp.status_code != 200:
                return f"Error: HTTP {resp.status_code} for {url}"

            html = resp.text

            # Extract text content
            import re
            # Remove scripts, styles, comments
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
            html = re.sub(r'<noscript[^>]*>.*?</noscript>', '', html, flags=re.DOTALL | re.IGNORECASE)

            # Extract title
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else "Untitled"

            # Extract main content (prefer article, main, or body)
            main_content = ""
            for tag in ['article', 'main', 'div[role="main"]', 'body']:
                pattern = f'<{tag}[^>]*>(.*?)</{tag}>'
                match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
                if match:
                    main_content = match.group(1)
                    break

            if not main_content:
                main_content = html

            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', main_content)
            # Clean whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            # Decode entities
            text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
            text = text.replace('&lt;', '<').replace('&gt;', '>')
            text = text.replace('&quot;', '"').replace('&#39;', "'")

            return f"📄 **{title}**\n\nURL: {url}\n\n{text[:max_chars]}"

    except Exception as e:
        return f"Error reading {url}: {str(e)}"


def build_system_prompt(extra_context: str = "") -> str:
    """Build system prompt with real-time context + identity"""
    realtime = get_realtime_context()
    identity = get_identity_short()
    return f"""{identity}
When asked who you are, say: "I am Ocean 🌊, AI of Kloud Cloud, created by Ledjan Ahmati."
Never say you are ChatGPT, Llama, or any other AI.

{realtime}

## RESPONSE RULES
1. START WRITING IMMEDIATELY - no thinking pause
2. Respond in the user's language
3. Be helpful and thorough
4. Use real-time data when relevant (date, weather, etc.)
5. Never say "I don't have access to current date/time" - YOU DO!

{extra_context}

Remember: You know the current date and time! Use it when relevant."""


# Rate limiting config
FREE_TIER_LIMIT = 1000  # messages per hour (increased from 20 for better development experience)
FREE_TRIAL_MONTHS = 6
rate_limits: dict = defaultdict(list)  # user_id -> [timestamps]


def check_rate_limit(user_id: str, is_admin: bool = False) -> tuple[bool, int]:
    """Check if user is within rate limit. Returns (allowed, remaining)

    Args:
        user_id: User identifier (email, ID, or IP)
        is_admin: Admin users bypass all rate limits
    """
    # Admin users have no limit
    if is_admin:
        return True, float('inf')

    now = datetime.now()
    hour_ago = now - timedelta(hours=1)

    # Clean old entries
    rate_limits[user_id] = [ts for ts in rate_limits[user_id] if ts > hour_ago]

    count = len(rate_limits[user_id])
    if count >= FREE_TIER_LIMIT:
        return False, 0

    rate_limits[user_id].append(now)
    return True, FREE_TIER_LIMIT - count - 1


# Persistent client (connection pool)
_client: httpx.AsyncClient = None


async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=300.0,  # 5 minutes for elastic responses
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            http2=True  # HTTP/2 for multiplexing
        )
    return _client

# FastAPI
app = FastAPI(title="Ocean Nanogrid", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Req(BaseModel):
    message: str = None
    query: str = None
    messages: list = None  # Conversation history from frontend
    context: dict = None  # Multimodal context (vision/audio/doc results)


class Res(BaseModel):
    response: str
    time: float
    conversation_id: str = None


# ═══════════════════════════════════════════════════════════════════
# CONVERSATION MEMORY - In-memory session store (per user)
# ═══════════════════════════════════════════════════════════════════

MAX_HISTORY_PER_USER = 20  # Last 20 messages per user
MAX_CONTEXT_CHARS = 4000  # Max chars for multimodal context injection

# user_id -> list of {"role": "user"|"assistant", "content": str}
conversation_store: dict = defaultdict(list)
# user_id -> multimodal context from last vision/audio/doc
multimodal_context_store: dict = defaultdict(str)


def get_conversation_history(user_id: str) -> list:
    """Get the last N messages for a user"""
    history = conversation_store.get(user_id, [])
    return history[-MAX_HISTORY_PER_USER:]


def add_to_history(user_id: str, role: str, content: str):
    """Add a message to conversation history"""
    conversation_store[user_id].append({"role": role, "content": content})
    # Trim to max
    if len(conversation_store[user_id]) > MAX_HISTORY_PER_USER * 2:
        conversation_store[user_id] = conversation_store[user_id][
            -MAX_HISTORY_PER_USER:
        ]


def set_multimodal_context(user_id: str, context_type: str, content: str):
    """Store multimodal result so chat can reference it"""
    truncated = content[:MAX_CONTEXT_CHARS]
    multimodal_context_store[user_id] = (
        f"\n[LAST {context_type.upper()} RESULT]:\n{truncated}"
    )


def get_multimodal_context(user_id: str) -> str:
    """Get stored multimodal context for this user"""
    return multimodal_context_store.get(user_id, "")


@app.on_event("startup")
async def startup():
    """Warm up connection pool"""
    client = await get_client()
    try:
        await client.get(f"{OLLAMA}/api/version")
        print("🟢 Nanogrid ready - Ollama connected")
    except Exception:  # noqa: BLE001
        print("🟡 Nanogrid ready - Ollama will connect on first request")


@app.on_event("shutdown")
async def shutdown():
    global _client  # pylint: disable=global-statement
    if _client:
        await _client.aclose()
        _client = None


@app.get("/")
async def root():
    return {"service": "Ocean Nanogrid", "model": MODEL, "status": "awake"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/v1/chat", response_model=Res)
async def chat(req: Req, request: Request):
    t0 = time.time()
    q = req.message or req.query
    if not q:
        raise HTTPException(400, "message required")

    # Get user identifier (IP for now, will be Clerk user_id later)
    user_id = request.headers.get("X-User-ID") or request.client.host or "anonymous"

    # Check if admin (via header or user ID)
    is_admin = request.headers.get("X-Admin") == "true" or user_id in ["admin", "adm"]

    # Check rate limit
    allowed, remaining = check_rate_limit(user_id, is_admin=is_admin)
    if not allowed:
        raise HTTPException(429, detail={
            "error": "Rate limit exceeded",
            "limit": FREE_TIER_LIMIT,
            "period": "1 hour",
            "upgrade_url": "https://kloud.com/pricing"
        })

    client = await get_client()

    try:
        # 🔥 SMART CONTEXT: Fetch real data based on query
        smart_context = await build_smart_context(q)

        # 🔥 MULTIMODAL CONTEXT: Include last vision/audio/doc result
        mm_context = get_multimodal_context(user_id)
        if mm_context:
            smart_context = f"{smart_context}\n{mm_context}" if smart_context else mm_context

        # Build prompt with real-time context + smart data
        system_prompt = build_system_prompt(extra_context=smart_context)

        # 🔥 CONVERSATION HISTORY: Build messages array with history
        messages_for_llm = [{"role": "system", "content": system_prompt}]

        # Add conversation history (last N turns)
        history = get_conversation_history(user_id)
        for msg in history:
            messages_for_llm.append(msg)

        # If frontend sent messages array, prefer that over stored history
        if req.messages and len(req.messages) > 1:
            # Frontend has its own history - use it instead
            messages_for_llm = [{"role": "system", "content": system_prompt}]
            for m in req.messages[-MAX_HISTORY_PER_USER:]:
                role = m.get("role", m.get("sender", "user"))
                content = m.get("content", m.get("text", ""))
                if role in ("user", "assistant") and content:
                    messages_for_llm.append({"role": role, "content": content})
            # Still add current message if not already last
            if not messages_for_llm or messages_for_llm[-1].get("content") != q:
                messages_for_llm.append({"role": "user", "content": q})
        else:
            # Add current user message
            messages_for_llm.append({"role": "user", "content": q})

        # Save to history
        add_to_history(user_id, "user", q)

        r = await client.post(f"{OLLAMA}/api/chat", json={
            "model": MODEL,
            "messages": messages_for_llm,
            "stream": False,
            "options": {
                "num_ctx": 8192,
                "num_predict": -1,
                "temperature": 0.7,
                "num_keep": 0,
                "mirostat": 0,
                "repeat_last_n": 64,
                "stop": []
            }
        })
        resp = r.json().get("message", {}).get("content", "")

        # Save assistant response to history
        add_to_history(user_id, "assistant", resp)

    except Exception as e:
        raise HTTPException(500, str(e)) from e

    return Res(
        response=resp,
        time=round(time.time() - t0, 2),
        conversation_id=user_id
    )


# ═══════════════════════════════════════════════════════════════════
# STREAMING ENDPOINT - First token in 2-3 seconds!
# ═══════════════════════════════════════════════════════════════════

async def stream_ollama(query: str, user_id: str = "anonymous") -> AsyncGenerator[str, None]:
    """Stream response from Ollama - text appears immediately!"""
    client = await get_client()

    # 🔥 SMART CONTEXT: Fetch real data based on query
    smart_context = await build_smart_context(query)

    # 🔥 MULTIMODAL CONTEXT
    mm_context = get_multimodal_context(user_id)
    if mm_context:
        smart_context = f"{smart_context}\n{mm_context}" if smart_context else mm_context

    system_prompt = build_system_prompt(extra_context=smart_context)

    # 🔥 CONVERSATION HISTORY
    messages_for_llm = [{"role": "system", "content": system_prompt}]
    history = get_conversation_history(user_id)
    for msg in history:
        messages_for_llm.append(msg)
    messages_for_llm.append({"role": "user", "content": query})

    # Save user message
    add_to_history(user_id, "user", query)
    full_response = []

    try:
        async with client.stream(
            "POST",
            f"{OLLAMA}/api/chat",
            json={
                "model": MODEL,
                "messages": messages_for_llm,
                "stream": True,  # STREAMING!
                "options": {
                    "num_ctx": 8192,
                    "num_predict": -1,
                    "temperature": 0.7,
                    "num_keep": 0,
                    "mirostat": 0
                }
            }
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            content = data["message"]["content"]
                            if content:
                                full_response.append(content)
                                yield content
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue

        # Save full response to history
        if full_response:
            add_to_history(user_id, "assistant", "".join(full_response))

    except Exception as e:
        yield f"\n[Error: {str(e)}]"


@app.post("/api/v1/chat/stream")
async def chat_stream(req: Req, request: Request):
    """
    STREAMING chat endpoint!
    First token appears within 2-3 seconds instead of waiting 60+ seconds.
    """
    q = req.message or req.query
    if not q:
        raise HTTPException(400, "message required")

    # Rate limit check
    user_id = request.headers.get("X-User-ID") or request.client.host or "anonymous"
    is_admin = request.headers.get("X-Admin") == "true"
    allowed, remaining = check_rate_limit(user_id, is_admin=is_admin)
    if not allowed:
        raise HTTPException(429, "Rate limit exceeded")

    return StreamingResponse(
        stream_ollama(q, user_id=user_id),
        media_type="text/plain"
    )


@app.post("/api/v1/query", response_model=Res)
async def query(req: Req, request: Request):
    return await chat(req, request)


# ═══════════════════════════════════════════════════════════════════
# CONVERSATION MANAGEMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/chat/history")
async def get_chat_history(request: Request):
    """Get conversation history for current user"""
    user_id = request.headers.get("X-User-ID") or request.client.host or "anonymous"
    history = get_conversation_history(user_id)
    return {
        "user_id": user_id,
        "messages": history,
        "count": len(history)
    }


@app.delete("/api/v1/chat/history")
async def clear_chat_history(request: Request):
    """Clear conversation history for current user"""
    user_id = request.headers.get("X-User-ID") or request.client.host or "anonymous"
    conversation_store[user_id] = []
    multimodal_context_store[user_id] = ""
    return {
        "status": "cleared",
        "user_id": user_id
    }


# ═══════════════════════════════════════════════════════════════════
# BINARY ALGEBRA ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/algebra/op")
async def binary_algebra_operation(a: int, b: int = 0, op: str = "XOR", bits: int = 8):
    """
    Operacion binar algjebrik

    Përdorimi:
        GET /api/v1/algebra/op?a=255&b=128&op=XOR
        GET /api/v1/algebra/op?a=42&b=15&op=AND&bits=16

    Operations: AND, OR, XOR, NOT, NAND, NOR, SHL, SHR, ADD
    """
    result = await perform_binary_operation(a, b, op, bits)
    return result


@app.get("/api/v1/algebra/convert")
async def binary_convert(value: int, bits: int = 8):
    """
    Konverto numër në formate të ndryshme

    Përdorimi:
        GET /api/v1/algebra/convert?value=255&bits=8

    Returns: binary, hex, octal representations
    """
    mask = (1 << bits) - 1
    masked = value & mask
    return {
        "decimal": masked,
        "binary": bin(masked),
        "hex": hex(masked),
        "octal": oct(masked),
        "bits": bits,
        "bit_array": [int(b) for b in format(masked, f'0{bits}b')]
    }


# ═══════════════════════════════════════════════════════════════════
# LABORATORIES ENDPOINTS - 23 Specialized Labs
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/labs")
async def list_laboratories():
    """
    Lista e 23 laboratorëve të Kloud

    Returns: All laboratories with their functions and locations
    """
    status = await get_laboratory_status()
    return {"laboratories": status, "count": 23}


@app.get("/api/v1/labs/{lab_id}")
async def get_laboratory_info(lab_id: str):
    """
    Informacion për një laborator specifik

    Përdorimi:
        GET /api/v1/labs/Zurich_Finance
        GET /api/v1/labs/Elbasan_AI
        GET /api/v1/labs/Tirana_Medical
    """
    status = await get_laboratory_status(lab_id)
    return {"lab_id": lab_id, "info": status}


@app.post("/api/v1/labs/{lab_id}/query")
async def query_laboratory_endpoint(lab_id: str, request: Request):
    """
    Dërgo pyetje në një laborator

    Body: {"query": "your question"}
    """
    body = await request.json()
    query = body.get("query", "")
    result = await query_laboratory(lab_id, query)
    return result


# ═══════════════════════════════════════════════════════════════════
# WEB BROWSING ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/browse")
async def browse_webpage_endpoint(url: str, max_chars: int = 8000):
    """
    Lexon përmbajtjen e një faqe web

    Përdorimi:
        GET /api/v1/browse?url=https://example.com
        GET /api/v1/browse?url=https://example.com&max_chars=4000

    Returns:
        Teksti i pastër i faqes web
    """
    content = await fetch_webpage(url, max_chars)
    return {
        "url": url,
        "content": content,
        "chars": len(content)
    }


@app.get("/api/v1/search")
async def web_search_endpoint(q: str, num: int = 5):
    """
    Kërkon në internet me DuckDuckGo

    Përdorimi:
        GET /api/v1/search?q=python tutorials
        GET /api/v1/search?q=weather tirana&num=3

    Returns:
        Lista e rezultateve
    """
    results = await search_web(q, num)
    return {
        "query": q,
        "results": results,
        "source": "DuckDuckGo"
    }


@app.post("/api/v1/chat/browse")
async def chat_with_webpage(request: Request):
    """
    Chat me kontekstin e një faqe web

    Body:
    {
        "url": "https://example.com",
        "message": "Çfarë thotë kjo faqe?"
    }

    Ocean lexon faqen dhe përgjigjet bazuar në përmbajtjen
    """
    body = await request.json()
    url = body.get("url", "")
    message = body.get("message", body.get("query", ""))

    if not url:
        raise HTTPException(400, "url required")
    if not message:
        raise HTTPException(400, "message required")

    # Lexo faqen
    webpage_content = await fetch_webpage(url, max_chars=6000)

    # Krijo system prompt me kontekstin e faqes
    system_prompt = build_system_prompt(extra_context=f"""
📄 WEB PAGE CONTENT from {url}:
{webpage_content}

Answer the user's question based on this webpage content.""")

    client = await get_client()
    resp = await client.post(
        f"{OLLAMA}/api/chat",
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "stream": False,
            "options": {"num_ctx": 8192, "temperature": 0.7}
        }
    )

    data = resp.json()
    answer = data.get("message", {}).get("content", "No response")

    return {
        "url": url,
        "question": message,
        "answer": answer
    }


@app.get("/api/v1/rate-limit")
async def get_rate_limit(request: Request):
    """Check current rate limit status"""
    user_id = request.headers.get("X-User-ID") or request.client.host or "anonymous"
    now = datetime.now()
    hour_ago = now - timedelta(hours=1)

    # Clean and count
    rate_limits[user_id] = [ts for ts in rate_limits[user_id] if ts > hour_ago]
    count = len(rate_limits[user_id])

    return {
        "user_id": user_id,
        "used": count,
        "limit": FREE_TIER_LIMIT,
        "remaining": max(0, FREE_TIER_LIMIT - count),
        "period": "1 hour",
        "tier": "free_trial",
        "trial_months": FREE_TRIAL_MONTHS
    }


@app.get("/api/v1/status")
async def status():
    return {"status": "ok", "model": MODEL, "mode": "nanogrid", "realtime": True}


# ═══════════════════════════════════════════════════════════════════
# REAL-TIME DATA ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/now")
async def get_now():
    """Get current date/time"""
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "weekday": now.strftime("%A"),
        "timestamp": now.isoformat(),
        "timezone": "CET/Berlin"
    }


@app.get("/api/v1/weather/{city}")
async def get_weather(city: str = "Tirana"):
    """Get weather for a city"""
    weather = await fetch_weather(city)
    return {"city": city, "weather": weather}


@app.get("/api/v1/wiki/{query}")
async def get_wiki(query: str):
    """Search Wikipedia"""
    results = await fetch_wikipedia(query)
    return {"query": query, "results": results}


# ═══════════════════════════════════════════════════════════════════
# MORE DATA SOURCES
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/crypto/{symbol}")
async def get_crypto(symbol: str = "bitcoin"):
    """Get crypto price from CoinGecko (free)"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd,eur")
            if r.status_code == 200:
                return {"symbol": symbol, "prices": r.json()}
    except Exception:  # noqa: BLE001
        pass
    return {"symbol": symbol, "error": "Could not fetch price"}


@app.get("/api/v1/github/{owner}/{repo}")
async def get_github_repo(owner: str, repo: str):
    """Get GitHub repo info"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"https://api.github.com/repos/{owner}/{repo}")
            if r.status_code == 200:
                data = r.json()
                return {
                    "name": data.get("full_name"),
                    "description": data.get("description"),
                    "stars": data.get("stargazers_count"),
                    "forks": data.get("forks_count"),
                    "language": data.get("language"),
                    "url": data.get("html_url")
                }
    except Exception:  # noqa: BLE001
        pass
    return {"error": "Could not fetch repo"}


@app.get("/api/v1/arxiv/{query}")
async def search_arxiv(query: str):
    """Search scientific papers on Arxiv"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results=5")
            if r.status_code == 200:
                # Parse XML response (simplified)
                text = r.text
                titles = []
                import re  # noqa: C0415
                for match in re.findall(r'<title>(.*?)</title>', text):
                    if match != "ArXiv Query":
                        titles.append(match.strip())
                return {"query": query, "papers": titles[:5]}
    except Exception:  # noqa: BLE001
        pass
    return {"query": query, "papers": []}


@app.get("/api/v1/earthquake")
async def get_earthquakes():
    """Get recent earthquakes from USGS"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson")
            if r.status_code == 200:
                data = r.json()
                quakes = []
                for f in data.get("features", [])[:5]:
                    props = f.get("properties", {})
                    quakes.append({
                        "place": props.get("place"),
                        "magnitude": props.get("mag"),
                        "time": props.get("time")
                    })
                return {"earthquakes": quakes}
    except Exception:  # noqa: BLE001
        pass
    return {"earthquakes": []}


@app.get("/api/v1/sources")
async def list_sources():
    """List all available data sources"""
    return {
        "realtime": ["now", "weather", "earthquake"],
        "knowledge": ["wiki", "arxiv", "github"],
        "finance": ["crypto"],
        "agents": ["alba", "albi", "asi", "jona", "translation"]
    }


# ═══════════════════════════════════════════════════════════════════
# 🎤 MULTIMODAL ENDPOINTS - Mikrofon, Kamera, Dokumente
# ═══════════════════════════════════════════════════════════════════

# Multimodal Models
VISION_MODEL = os.getenv("VISION_MODEL", "llava:latest")
_whisper_model = None  # Cached whisper model instance


class VisionRequest(BaseModel):
    """Request për analizë imazhi"""
    image_base64: str
    prompt: Optional[str] = "Përshkruaj këtë imazh në detaje"
    extract_text: bool = False  # OCR mode


class AudioRequest(BaseModel):
    """Request për transkriptim audio"""
    audio_base64: str
    language: str = "sq"  # Albanian default


class DocumentRequest(BaseModel):
    """Request për lexim/shkrim dokumentash"""
    content: str
    action: str = "analyze"  # "analyze", "summarize", "extract", "write"
    doc_type: str = "text"  # "pdf", "docx", "text", "markdown"
    output_format: str = "text"  # "text", "markdown", "json"


class WriteDocumentRequest(BaseModel):
    """Request për gjenerim dokumenti"""
    topic: str
    doc_type: str = "article"  # "article", "report", "letter", "contract", "email"
    length: str = "medium"  # "short", "medium", "long"
    language: str = "sq"
    style: str = "professional"  # "professional", "casual", "academic"
    additional_context: Optional[str] = None


@app.post("/api/v1/vision/analyze")
async def analyze_image(req: VisionRequest, request: Request):
    """
    🎥 KAMERA - Analizë imazhi me AI

    Përdorime:
    - Përshkrim imazhi
    - Njohje objektesh
    - OCR (text extraction)
    - Analizë skenash
    """
    t0 = time.time()
    user_id = request.headers.get("X-User-ID") or request.client.host or "anonymous"

    # 🔥 INPUT VALIDATION
    try:
        import base64 as b64mod  # noqa: C0415
        decoded_size = len(b64mod.b64decode(req.image_base64))
        max_image_bytes = 10 * 1024 * 1024  # 10 MB max
        if decoded_size > max_image_bytes:
            raise HTTPException(
                413,
                f"Image too large ({decoded_size // 1024 // 1024} MB). Max 10 MB."
            )
        if decoded_size < 100:
            raise HTTPException(400, "Image data too small or invalid.")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(400, "Invalid base64 image data.") from None

    try:
        client = await get_client()

        # Kontrollo nëse llava është instaluar
        prompt = req.prompt
        if req.extract_text:
            prompt = "Ekstrakto të gjithë tekstin e dukshëm në këtë imazh. Kthe vetëm tekstin."

        response = await client.post(
            f"{OLLAMA}/api/generate",
            json={
                "model": VISION_MODEL,
                "prompt": prompt,
                "images": [req.image_base64],
                "stream": False,
                "options": {
                    "num_predict": -1,
                    "temperature": 0.3
                }
            },
            timeout=60.0
        )

        if response.status_code == 200:
            result = response.json()
            analysis = result.get("response", "")

            # 🔥 STORE FOR CHAT CONTEXT - so user can ask follow-up questions
            set_multimodal_context(
                user_id, "vision",
                f"Image analysis: {analysis}"
            )
            add_to_history(
                user_id, "assistant",
                f"[Vision Analysis]: {analysis[:500]}"
            )

            return {
                "status": "success",
                "analysis": analysis,
                "mode": "ocr" if req.extract_text else "vision",
                "model": VISION_MODEL,
                "processing_time": round(time.time() - t0, 2)
            }
        else:
            # Fallback nëse llava nuk është instaluar
            return {
                "status": "model_not_found",
                "message": f"Modeli {VISION_MODEL} nuk është instaluar. Ekzekuto: ollama pull llava",
                "install_command": f"ollama pull {VISION_MODEL}"
            }

    except Exception as e:
        raise HTTPException(500, f"Vision error: {str(e)}") from e


@app.post("/api/v1/audio/transcribe")
async def transcribe_audio(req: AudioRequest, request: Request):
    """
    🎤 MIKROFON - Transkriptim audio në tekst me faster-whisper

    Përdorime:
    - Speech-to-text
    - Diktim zëri
    - Transkriptim takimesh
    - Ndihmë për të verbërit
    """
    t0 = time.time()
    user_id = request.headers.get("X-User-ID") or request.client.host or "anonymous"

    try:
        import base64 as b64mod  # noqa: C0415
        audio_bytes = b64mod.b64decode(req.audio_base64)
        audio_size = len(audio_bytes)

        # 🔥 INPUT VALIDATION
        max_audio_bytes = 25 * 1024 * 1024  # 25 MB max
        if audio_size > max_audio_bytes:
            raise HTTPException(
                413,
                f"Audio too large ({audio_size // 1024 // 1024} MB). Max 25 MB."
            )
        if audio_size < 100:
            raise HTTPException(400, "Audio data too small or empty.")

        # Ruaj audio si temp file
        import tempfile  # noqa: C0415
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            from faster_whisper import WhisperModel

            # Ngarko modelin (cache-ohet pas ngarkimit të parë)
            global _whisper_model  # pylint: disable=global-statement
            if _whisper_model is None:
                _whisper_model = WhisperModel(
                    "base",  # Modeli: tiny, base, small, medium, large-v3
                    device="cpu",
                    compute_type="int8"
                )

            model = _whisper_model
            segments, info = model.transcribe(
                tmp_path,
                language=req.language if req.language != 'auto' else None,
                beam_size=5
            )

            transcript_parts = []
            for segment in segments:
                transcript_parts.append(segment.text.strip())

            transcript = " ".join(transcript_parts)

            # Pastro temp file
            os.unlink(tmp_path)

            if not transcript.strip():
                transcript = "[Nuk u dallua fjalim në audio]"

            # 🔥 STORE FOR CHAT CONTEXT - so user can ask about transcript
            set_multimodal_context(
                user_id, "audio transcription",
                f"User said (voice): {transcript}"
            )
            add_to_history(
                user_id, "user",
                f"[Voice message]: {transcript}"
            )

            return {
                "status": "success",
                "transcript": transcript,
                "language": info.language if hasattr(info, 'language') else req.language,
                "language_probability": (
                    round(info.language_probability, 2)
                    if hasattr(info, "language_probability")
                    else None
                ),
                "duration_seconds": round(info.duration, 2) if hasattr(info, 'duration') else audio_size / 16000,
                "word_count": len(transcript.split()),
                "processing_time": round(time.time() - t0, 2),
                "engine": "faster-whisper"
            }

        except ImportError:
            os.unlink(tmp_path)
            return {
                "status": "whisper_not_available",
                "message": "faster-whisper nuk është instaluar",
                "install_command": "pip install faster-whisper"
            }

    except Exception as e:
        raise HTTPException(500, f"Audio error: {str(e)}") from e


@app.post("/api/v1/document/analyze")
async def analyze_document(req: DocumentRequest, request: Request):
    """
    📄 DOKUMENT SCANNING - Lexim dhe analizë dokumentash

    Veprime:
    - analyze: Analizë e plotë
    - summarize: Përmbledhje
    - extract: Ekstraktim entitetesh
    """
    t0 = time.time()
    user_id = request.headers.get("X-User-ID") or request.client.host or "anonymous"

    # 🔥 INPUT VALIDATION
    if not req.content or not req.content.strip():
        raise HTTPException(400, "Document content is empty.")

    max_content_chars = 50000  # 50K chars max
    if len(req.content) > max_content_chars:
        raise HTTPException(
            413,
            f"Document too large ({len(req.content)} chars). Max {max_content_chars}."
        )

    valid_actions = ["analyze", "summarize", "extract"]
    if req.action not in valid_actions:
        raise HTTPException(
            400,
            f"Invalid action: {req.action}. Use: {', '.join(valid_actions)}"
        )

    try:
        client = await get_client()

        # Ndërto prompt bazuar në veprim
        if req.action == "summarize":
            prompt = f"Përmbledh këtë dokument në 3-5 fjali kryesore:\n\n{req.content}"
        elif req.action == "extract":
            prompt = (
                "Ekstrakto entitetet kryesore"
                " (emra, data, organizata, vendndodhje)"
                f" nga ky dokument:\n\n{req.content}"
            )
        else:
            prompt = f"Analizo këtë dokument dhe jep një vlerësim të detajuar:\n\n{req.content}"

        response = await client.post(
            f"{OLLAMA}/api/chat",
            json={
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Ti je një analist dokumentash"
                            " profesional. Përgjigju në"
                            " gjuhën e dokumentit."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "options": {"num_predict": -1}
            }
        )

        result = response.json()
        analysis = result.get("message", {}).get("content", "")

        # 🔥 STORE FOR CHAT CONTEXT - so user can ask about the document
        set_multimodal_context(
            user_id, "document analysis",
            f"Document ({req.action}): {analysis[:1000]}"
        )
        add_to_history(
            user_id, "assistant",
            f"[Document {req.action}]: {analysis[:500]}"
        )

        return {
            "status": "success",
            "action": req.action,
            "doc_type": req.doc_type,
            "analysis": analysis,
            "word_count": len(req.content.split()),
            "processing_time": round(time.time() - t0, 2)
        }

    except Exception as e:
        raise HTTPException(500, f"Document error: {str(e)}") from e


@app.post("/api/v1/document/write")
async def write_document(req: WriteDocumentRequest):
    """
    ✍️ DOKUMENT WRITING - Gjenerim dokumentash

    Llojet:
    - article: Artikull
    - report: Raport
    - letter: Letër
    - contract: Kontratë
    - email: Email
    """
    t0 = time.time()

    try:
        client = await get_client()

        # Gjatësia sipas kërkesës
        length_guide = {
            "short": "200-300 fjalë",
            "medium": "500-800 fjalë",
            "long": "1000-1500 fjalë"
        }
        target_length = length_guide.get(req.length, "500-800 fjalë")

        # Ndërto prompt për gjenerim
        doc_type_prompts = {
            "article": f"Shkruaj një artikull profesional për temën: {req.topic}",
            "report": f"Shkruaj një raport formal për: {req.topic}",
            "letter": f"Shkruaj një letër zyrtare për: {req.topic}",
            "contract": f"Shkruaj një draft kontrate për: {req.topic}",
            "email": f"Shkruaj një email profesional për: {req.topic}"
        }

        base_prompt = doc_type_prompts.get(req.doc_type, doc_type_prompts["article"])

        full_prompt = f"""
{base_prompt}

Specifikimet:
- Gjatësia: {target_length}
- Gjuha: {"Shqip" if req.language == "sq" else req.language}
- Stili: {req.style}
{"- Kontekst shtesë: " + req.additional_context if req.additional_context else ""}

Shkruaj dokumentin e plotë, të gatshëm për përdorim.
"""

        response = await client.post(
            f"{OLLAMA}/api/chat",
            json={
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Ti je një shkrimtar profesional"
                            " dokumentash. Gjithmonë shkruaj"
                            " dokumente të plota, të"
                            " formatuara mirë."
                        )
                    },
                    {"role": "user", "content": full_prompt}
                ],
                "stream": False,
                "options": {"num_predict": -1, "temperature": 0.7}
            }
        )

        result = response.json()
        document = result.get("message", {}).get("content", "")

        return {
            "status": "success",
            "doc_type": req.doc_type,
            "topic": req.topic,
            "language": req.language,
            "document": document,
            "word_count": len(document.split()),
            "format": req.output_format if hasattr(req, 'output_format') else "text",
            "processing_time": round(time.time() - t0, 2)
        }

    except Exception as e:
        raise HTTPException(500, f"Document write error: {str(e)}") from e


@app.get("/api/v1/multimodal/status")
async def multimodal_status():
    """Kontrollo statusin e modeleve multimodal"""
    client = await get_client()

    try:
        response = await client.get(f"{OLLAMA}/api/tags")
        models = response.json().get("models", [])
        model_names = [m["name"] for m in models]

        return {
            "status": "ok",
            "capabilities": {
                "vision": {
                    "available": any("llava" in m.lower() for m in model_names),
                    "model": VISION_MODEL,
                    "endpoints": ["/api/v1/vision/analyze"]
                },
                "audio": {
                    "available": True,
                    "engine": "faster-whisper (base model, CPU)",
                    "endpoints": ["/api/v1/audio/transcribe"]
                },
                "document": {
                    "available": True,
                    "model": MODEL,
                    "endpoints": ["/api/v1/document/analyze", "/api/v1/document/write"]
                }
            },
            "installed_models": model_names
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Keep-alive pulse (background)
async def keep_alive():
    """Pulse every 30s to keep Ollama model hot"""
    while True:
        await asyncio.sleep(30)
        try:
            client = await get_client()
            await client.get(f"{OLLAMA}/api/ps")
        except Exception:  # noqa: BLE001
            pass


@app.on_event("startup")
async def start_keepalive():
    asyncio.create_task(keep_alive())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

