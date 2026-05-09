"""
CENTRAL API CONNECTOR
======================
Connects Ocean-Core to the Central API (port 8000)
Gets REAL data from ALL 23 laboratories and ALL APIs

This is the bridge between Ocean-Core and the main Kloud API.
"""

import logging
import asyncio
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import requests

logger = logging.getLogger("central_api_connector")

# Get Central API URL from environment or default
CENTRAL_API_URL = os.getenv("CENTRAL_API_URL", "http://localhost:8000")


class CentralAPIConnector:
    """
    Connects to Central Kloud API (port 8000) 
    to get real data from all services.
    """
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or CENTRAL_API_URL
        self.connected = False
        self.last_check = None
        self._session = None
        
        # ALL API endpoints available in central API - COMPLETE LIST
        self.endpoints = {
            # ==================== SYSTEM STATUS ====================
            "health": "/health",
            "status": "/status",
            "system_status": "/api/system-status",
            "api_info": "/api",
            "system_metrics": "/api/system-metrics",
            
            # ==================== OCEAN / LABS ====================
            "ocean_status": "/api/ocean/status",
            "ocean_labs_list": "/api/ocean/labs/list",
            "ocean_cells": "/api/ocean/cells",
            "ocean_query": "/api/ocean/query",
            "labs_list": "/api/labs",
            "laboratories": "/api/laboratories",
            "laboratories_summary": "/api/laboratories/summary",
            "laboratories_types": "/api/laboratories/types",
            
            # ==================== ASI (Artificial Super Intelligence) ====================
            "asi_status": "/api/asi/status",
            "asi_health": "/api/asi/health",
            "asi_query": "/api/asi/query",
            "alba_metrics": "/api/asi/alba/metrics",
            "alba_status": "/api/asi/alba/status",
            "albi_metrics": "/api/asi/albi/metrics",
            "albi_status": "/api/asi/albi/status",
            "jona_metrics": "/api/asi/jona/metrics",
            "jona_status": "/api/asi/jona/status",
            
            # ==================== ALBI (Brain Interface) ====================
            "albi_eeg_analysis": "/api/albi/eeg/analysis",
            "albi_eeg_waves": "/api/albi/eeg/waves",
            "albi_eeg_quality": "/api/albi/eeg/quality",
            "albi_health": "/api/albi/health",
            "albi_biometrics": "/api/albi/biometrics",
            
            # ==================== JONA (Audio) ====================
            "jona_health": "/api/jona/health",
            "jona_audio_list": "/api/jona/audio/list",
            "jona_session": "/api/jona/session",
            
            # ==================== SPECTRUM ====================
            "spectrum_live": "/api/spectrum/live",
            "spectrum_bands": "/api/spectrum/bands",
            "spectrum_history": "/api/spectrum/history",
            
            # ==================== CYCLES & ALIGNMENTS ====================
            "cycles_status": "/api/cycles/status",
            "cycles_current": "/api/cycles/current",
            "cycles_history": "/api/cycles/history",
            "cycles_alignments": "/api/cycles/alignments",
            "alignments_planetary": "/api/alignments/planetary",
            "alignments_cosmic": "/api/alignments/cosmic",
            
            # ==================== GLOBAL REGIONS ====================
            "region_europe": "/api/regions/europe",
            "region_asia": "/api/regions/asia",
            "region_china": "/api/regions/china",
            "region_india": "/api/regions/india",
            "region_americas": "/api/regions/americas",
            "region_oceania": "/api/regions/oceania",
            "region_africa": "/api/regions/africa",
            "region_middle_east": "/api/regions/middle-east",
            
            # ==================== ALPHABET 61 LETTERS (AL-GR) ====================
            "alphabet_status": "/api/alphabet/status",
            "alphabet_layers": "/api/alphabet/layers",
            "alphabet_layer_0": "/api/alphabet/layer/0",
            "alphabet_layer_1": "/api/alphabet/layer/1",
            "alphabet_layer_2": "/api/alphabet/layer/2",
            "alphabet_all_letters": "/api/alphabet/all",
            "alphabet_albanian": "/api/alphabet/albanian",
            "alphabet_greek": "/api/alphabet/greek",
            
            # ==================== GIT & VERSION CONTROL ====================
            "git_status": "/api/git/status",
            "git_commits": "/api/git/commits",
            "git_branches": "/api/git/branches",
            "git_tags": "/api/git/tags",
            
            # ==================== DOCKER & CONTAINERS ====================
            "docker_status": "/api/docker/status",
            "docker_containers": "/api/docker/containers",
            "docker_images": "/api/docker/images",
            "docker_stats": "/api/docker/stats",
            "docker_networks": "/api/docker/networks",
            
            # ==================== CI/CD PIPELINE ====================
            "pipeline_status": "/api/pipeline/status",
            "pipeline_runs": "/api/pipeline/runs",
            "pipeline_workflows": "/api/pipeline/workflows",
            "github_actions": "/api/github/actions",
            
            # ==================== MONITORING ====================
            "monitoring_dashboards": "/api/monitoring/dashboards",
            "monitoring_metrics": "/api/monitoring/real-metrics-info",
            "monitoring_alerts": "/api/monitoring/alerts",
            
            # ==================== EXTERNAL DATA ====================
            "crypto_market": "/api/crypto/market",
            "crypto_prices": "/api/crypto/prices",
            "weather": "/api/weather",
            "weather_forecast": "/api/weather/forecast",
            "news": "/api/news",
            "stocks": "/api/stocks",
            
            # ==================== REAL DATA DASHBOARD ====================
            "realdata_dashboard": "/api/realdata/dashboard",
            "realdata_sources": "/api/realdata/sources",
            
            # ==================== AI AGENTS ====================
            "ai_health": "/api/ai/health",
            "ai_agents_status": "/api/ai/agents-status",
            "ai_agents_list": "/api/ai/agents",
            "ai_models": "/api/ai/models",
            
            # ==================== BEHAVIORAL & ANALYTICS ====================
            "behavioral_status": "/api/behavioral/status",
            "behavioral_analysis": "/api/behavioral/analysis",
            "analytics_dashboard": "/api/analytics/dashboard",
            
            # ==================== AVIATION WEATHER ====================
            "aviation_status": "/api/aviation/status",
            "aviation_metar": "/api/aviation/metar",
            "aviation_taf": "/api/aviation/taf",
            
            # ==================== EXCEL & REPORTING ====================
            "excel_status": "/api/excel/status",
            "excel_reports": "/api/excel/reports",
            "reporting_dashboard": "/api/reporting/dashboard",
            
            # ==================== MARKETPLACE ====================
            "marketplace_status": "/api/marketplace/status",
            "marketplace_products": "/api/marketplace/products",
            
            # ==================== ECONOMY ====================
            "economy_status": "/api/economy/status",
            "economy_indicators": "/api/economy/indicators",
            
            # ==================== BILLING ====================
            "billing_metering": "/api/billing/metering-status",
            "billing_usage": "/api/billing/usage",
            
            # ==================== DATABASE ====================
            "db_ping": "/db/ping",
            "redis_ping": "/redis/ping",
            "db_status": "/api/db/status",
            
            # ==================== METRICS ====================
            "metrics": "/metrics",
            "prometheus_metrics": "/api/metrics/prometheus",
        }
        
        logger.info(f"🌐 Central API Connector initialized - {len(self.endpoints)} endpoints available")
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        return self._session
    
    async def close(self):
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def check_connection(self) -> bool:
        """Check if central API is available."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/health") as response:
                self.connected = response.status == 200
                self.last_check = datetime.now()
                return self.connected
        except Exception as e:
            logger.warning(f"Central API not available: {e}")
            self.connected = False
            return False
    
    async def get(self, endpoint_name: str) -> Dict[str, Any]:
        """
        Get data from a named endpoint.
        
        Args:
            endpoint_name: Name of endpoint (e.g., "asi_status", "alba_metrics")
        
        Returns:
            JSON response from API
        """
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint_name}")
        
        url = f"{self.base_url}{self.endpoints[endpoint_name]}"
        
        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Endpoint {endpoint_name} returned {response.status}")
                    return {"error": f"Status {response.status}", "endpoint": endpoint_name}
        except Exception as e:
            logger.error(f"Error calling {endpoint_name}: {e}")
            return {"error": str(e), "endpoint": endpoint_name}
    
    async def get_url(self, url_path: str) -> Dict[str, Any]:
        """Get data from a direct URL path."""
        url = f"{self.base_url}{url_path}"
        
        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def post(self, endpoint_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST data to an endpoint."""
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint_name}")
        
        url = f"{self.base_url}{self.endpoints[endpoint_name]}"
        
        try:
            session = await self._get_session()
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    # =========================================
    # CONVENIENCE METHODS FOR COMMON DATA
    # =========================================
    
    async def get_all_agents_status(self) -> Dict[str, Any]:
        """Get status of all AI agents (ALBA, ALBI, JONA, ASI)."""
        results = {}
        
        # Fetch all in parallel
        tasks = {
            "asi": self.get("asi_status"),
            "alba": self.get("alba_metrics"),
            "albi": self.get("albi_metrics"),
            "jona": self.get("jona_metrics"),
            "albi_health": self.get("albi_health"),
            "jona_health": self.get("jona_health"),
        }
        
        responses = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        for name, response in zip(tasks.keys(), responses):
            if isinstance(response, Exception):
                results[name] = {"error": str(response)}
            else:
                results[name] = response
        
        return results
    
    async def get_all_labs(self) -> Dict[str, Any]:
        """Get all 23 laboratories data."""
        return await self.get("ocean_labs_list")
    
    async def get_brain_data(self) -> Dict[str, Any]:
        """Get brain/EEG related data."""
        results = {}
        
        tasks = {
            "eeg_analysis": self.get("albi_eeg_analysis"),
            "eeg_waves": self.get("albi_eeg_waves"),
            "eeg_quality": self.get("albi_eeg_quality"),
            "spectrum_live": self.get("spectrum_live"),
            "spectrum_bands": self.get("spectrum_bands"),
        }
        
        responses = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        for name, response in zip(tasks.keys(), responses):
            if isinstance(response, Exception):
                results[name] = {"error": str(response)}
            else:
                results[name] = response
        
        return results
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get complete system overview."""
        results = {}
        
        tasks = {
            "health": self.get("health"),
            "status": self.get("status"),
            "system_status": self.get("system_status"),
            "monitoring": self.get("monitoring_dashboards"),
            "metrics_info": self.get("monitoring_metrics"),
        }
        
        responses = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        for name, response in zip(tasks.keys(), responses):
            if isinstance(response, Exception):
                results[name] = {"error": str(response)}
            else:
                results[name] = response
        
        return results
    
    async def get_external_data(self) -> Dict[str, Any]:
        """Get external data (crypto, weather)."""
        results = {}
        
        tasks = {
            "crypto": self.get("crypto_market"),
            "weather": self.get("weather"),
        }
        
        responses = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        for name, response in zip(tasks.keys(), responses):
            if isinstance(response, Exception):
                results[name] = {"error": str(response)}
            else:
                results[name] = response
        
        return results
    
    async def get_all_data(self) -> Dict[str, Any]:
        """
        Get ALL data from ALL endpoints - comprehensive system snapshot.
        """
        all_data = {
            "timestamp": datetime.now().isoformat(),
            "central_api_url": self.base_url,
            "endpoints_available": len(self.endpoints),
        }
        
        # Check connection first
        connected = await self.check_connection()
        all_data["connected"] = connected
        
        if not connected:
            all_data["error"] = "Central API not available"
            return all_data
        
        # Get all major data categories in parallel
        tasks = {
            "agents": self.get_all_agents_status(),
            "labs": self.get_all_labs(),
            "brain": self.get_brain_data(),
            "system": self.get_system_overview(),
            "external": self.get_external_data(),
            "realdata": self.get("realdata_dashboard"),
            "ai_health": self.get("ai_health"),
            "ai_agents": self.get("ai_agents_status"),
        }
        
        responses = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        for name, response in zip(tasks.keys(), responses):
            if isinstance(response, Exception):
                all_data[name] = {"error": str(response)}
            else:
                all_data[name] = response
        
        return all_data
    
    # =========================================
    # SYNC METHODS (for non-async contexts)
    # =========================================
    
    def get_sync(self, endpoint_name: str) -> Dict[str, Any]:
        """Synchronous version of get()."""
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint_name}")
        
        url = f"{self.base_url}{self.endpoints[endpoint_name]}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Status {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def check_connection_sync(self) -> bool:
        """Synchronous connection check."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            self.connected = response.status_code == 200
            self.last_check = datetime.now()
            return self.connected
        except:
            self.connected = False
            return False
    
    def get_all_data_sync(self) -> Dict[str, Any]:
        """Synchronous version - gets key data."""
        all_data = {
            "timestamp": datetime.now().isoformat(),
            "central_api_url": self.base_url,
        }
        
        # Check connection
        connected = self.check_connection_sync()
        all_data["connected"] = connected
        
        if not connected:
            all_data["error"] = "Central API not available"
            return all_data
        
        # Get key endpoints
        for name in ["health", "status", "asi_status", "ocean_labs_list", "ai_agents_status"]:
            try:
                all_data[name] = self.get_sync(name)
            except Exception as e:
                all_data[name] = {"error": str(e)}
        
        return all_data


# Singleton instance
_connector = None

def get_central_api() -> CentralAPIConnector:
    """Get singleton Central API connector."""
    global _connector
    if _connector is None:
        _connector = CentralAPIConnector()
    return _connector


async def get_central_api_async() -> CentralAPIConnector:
    """Get Central API connector (async)."""
    return get_central_api()


if __name__ == "__main__":
    # Test the connector
    import asyncio
    
    async def test():
        connector = get_central_api()
        
        print("🌐 Testing Central API Connection...")
        print("="*60)
        
        connected = await connector.check_connection()
        print(f"Connected: {connected}")
        
        if connected:
            print("\n📊 Getting all data...")
            data = await connector.get_all_data()
            
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"\n{key}: {len(value)} items")
                else:
                    print(f"{key}: {value}")
        
        await connector.close()
    
    asyncio.run(test())

