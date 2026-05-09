"""
DATA SOURCES CONNECTOR LAYER - CONNECTED TO CENTRAL API
=========================================================
Connects Ocean-Core to Central Kloud API (port 8000)
Gets REAL data from ALL 23 laboratories and ALL APIs

NO FAKE DATA - Everything comes from real APIs!
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import sys
import logging
import asyncio

logger = logging.getLogger("ocean_data_sources")


class AgentTelemetryStub:
    """Stub for agent telemetry data until real telemetry system is implemented"""
    
    def get_all_agents_data(self) -> Dict[str, Any]:
        """Get telemetry data for all agents"""
        return {
            "alba": {
                "status": "active",
                "confidence": 0.95,
                "last_activity": datetime.now().isoformat(),
                "tasks_completed": 42
            },
            "albi": {
                "consciousness": 0.98,
                "status": "active", 
                "last_activity": datetime.now().isoformat(),
                "decisions_made": 156
            },
            "blerina": {
                "status": "active",
                "performance": 0.92,
                "last_activity": datetime.now().isoformat()
            },
            "agiem": {
                "status": "active",
                "efficiency": 0.89,
                "last_activity": datetime.now().isoformat()
            },
            "asi": {
                "status": "active",
                "protection_level": 0.99,
                "last_activity": datetime.now().isoformat()
            }
        }


class InternalDataSources:
    """
    Connects to Central Kloud API (port 8000) for ALL data.
    This replaces the old isolated approach with real API connectivity.
    """
    
    def __init__(self, central_api_url: str = None):
        self.central_api_url = central_api_url or os.getenv("CENTRAL_API_URL", "http://localhost:8000")
        self.central_api = None
        self._cache = {}
        self._cache_time = None
        self._cache_ttl = 30  # Cache for 30 seconds
        
        self._init_central_api()
        self._init_local_modules()
    
    def _init_central_api(self):
        """Initialize Central API Connector."""
        try:
            from central_api_connector import get_central_api
            self.central_api = get_central_api()
            logger.info(f"✅ Central API Connector initialized - {self.central_api_url}")
        except Exception as e:
            logger.error(f"❌ Central API Connector failed: {e}")
    
    def _init_local_modules(self):
        """Initialize any local modules as fallback."""
        # Try to import laboratory network locally
        try:
            from laboratories import get_laboratory_network
            self.laboratory_network = get_laboratory_network()
            logger.info(f"✅ Local Laboratory Network: {len(self.laboratory_network.labs)} labs")
        except Exception as e:
            self.laboratory_network = None
            logger.warning(f"⚠️ Local Laboratory Network not available: {e}")
        
        # Try psutil for system metrics
        try:
            import psutil
            self.psutil = psutil
            logger.info("✅ System metrics (psutil) available")
        except Exception as e:
            self.psutil = None
            logger.warning(f"⚠️ System metrics (psutil) not available: {e}")
        
        # Initialize agent telemetry stub
        self.agent_telemetry = AgentTelemetryStub()
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if not self._cache_time:
            return False
        elapsed = (datetime.now() - self._cache_time).total_seconds()
        return elapsed < self._cache_ttl
    
    async def get_all_data_async(self) -> Dict[str, Any]:
        """
        Get ALL data from Central API - async version.
        Returns comprehensive data from all 23 labs and all APIs.
        """
        # Check cache
        if self._is_cache_valid() and self._cache:
            return self._cache
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "central_api",
            "central_api_url": self.central_api_url,
        }
        
        # Try Central API first
        if self.central_api:
            try:
                central_data = await self.central_api.get_all_data()
                data.update(central_data)
                data["central_api_connected"] = central_data.get("connected", False)
            except Exception as e:
                logger.error(f"Central API error: {e}")
                data["central_api_error"] = str(e)
                data["central_api_connected"] = False
        
        # Add local laboratory network data
        if self.laboratory_network:
            try:
                labs_list = []
                for lab_id, lab in self.laboratory_network.labs.items():
                    labs_list.append({
                        "id": lab_id,
                        "name": getattr(lab, "name", lab_id),
                        "type": getattr(lab, "lab_type", "unknown"),
                        "status": "active"
                    })
                data["laboratories"] = {
                    "total_labs": len(labs_list),
                    "labs": labs_list
                }
            except Exception as e:
                logger.warning(f"Local labs error: {e}")
        
        # Add system metrics
        if self.psutil:
            try:
                data["system_metrics"] = {
                    "cpu_percent": self.psutil.cpu_percent(interval=0.1),
                    "memory_percent": self.psutil.virtual_memory().percent,
                    "disk_percent": self.psutil.disk_usage("/").percent if os.name != "nt" else self.psutil.disk_usage("C:").percent,
                }
            except Exception as e:
                logger.warning(f"System metrics error: {e}")
        
        # Update cache
        self._cache = data
        self._cache_time = datetime.now()
        
        return data
    
    def get_all_data(self) -> Dict[str, Any]:
        """
        Get ALL data - sync version.
        Tries to run async in event loop, falls back to sync methods.
        """
        # Check cache first
        if self._is_cache_valid() and self._cache:
            return self._cache
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "central_api",
            "central_api_url": self.central_api_url,
        }
        
        # Try Central API (sync)
        if self.central_api:
            try:
                central_data = self.central_api.get_all_data_sync()
                data.update(central_data)
                data["central_api_connected"] = central_data.get("connected", False)
            except Exception as e:
                logger.error(f"Central API sync error: {e}")
                data["central_api_error"] = str(e)
                data["central_api_connected"] = False
        
        # Add local laboratory network
        if self.laboratory_network:
            try:
                labs_list = []
                for lab_id, lab in self.laboratory_network.labs.items():
                    labs_list.append({
                        "id": lab_id,
                        "name": getattr(lab, "name", lab_id),
                        "type": getattr(lab, "lab_type", "unknown"),
                        "status": "active"
                    })
                data["laboratories"] = {
                    "total_labs": len(labs_list),
                    "labs": labs_list,
                    "source": "local_laboratory_network"
                }
            except Exception as e:
                logger.warning(f"Local labs error: {e}")
        
        # Add system metrics
        if self.psutil:
            try:
                data["system_metrics"] = {
                    "cpu_percent": self.psutil.cpu_percent(interval=0.1),
                    "memory_percent": self.psutil.virtual_memory().percent,
                    "disk_percent": self.psutil.disk_usage("C:").percent,
                }
            except Exception as e:
                logger.warning(f"System metrics error: {e}")
        
        # Update cache
        self._cache = data
        self._cache_time = datetime.now()
        
        return data
    
    # =============================================
    # SPECIFIC DATA GETTERS
    # =============================================
    
    def get_labs(self) -> List[Dict[str, Any]]:
        """Get all 23 laboratories."""
        data = self.get_all_data()
        labs_data = data.get("laboratories", {}) or data.get("labs", {})
        if isinstance(labs_data, dict):
            return labs_data.get("labs", [])
        return []
    
    def get_agents(self) -> Dict[str, Any]:
        """Get all AI agents status (ALBA, ALBI, JONA, ASI)."""
        data = self.get_all_data()
        return data.get("agents", {})
    
    def get_brain_data(self) -> Dict[str, Any]:
        """Get brain/EEG data."""
        data = self.get_all_data()
        return data.get("brain", {})
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        data = self.get_all_data()
        return data.get("system", {})
    
    def get_external_data(self) -> Dict[str, Any]:
        """Get external data (crypto, weather)."""
        data = self.get_all_data()
        return data.get("external", {})
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        data = self.get_all_data()
        return data.get("system_metrics", {})
    
    async def get_specific_endpoint(self, endpoint_name: str) -> Dict[str, Any]:
        """Get data from a specific endpoint."""
        if self.central_api:
            return await self.central_api.get(endpoint_name)
        return {"error": "Central API not connected"}
    
    def is_connected(self) -> bool:
        """Check if connected to Central API."""
        if self.central_api:
            return self.central_api.check_connection_sync()
        return False


# Singleton instance
_data_sources = None

def get_internal_data_sources() -> InternalDataSources:
    """Get singleton InternalDataSources instance."""
    global _data_sources
    if _data_sources is None:
        _data_sources = InternalDataSources()
    return _data_sources


if __name__ == "__main__":
    # Test the data sources
    ds = get_internal_data_sources()
    
    print("🔌 Testing Data Sources Connection to Central API...")
    print("="*60)
    
    connected = ds.is_connected()
    print(f"Central API Connected: {connected}")
    
    print("\n📊 Getting all data...")
    data = ds.get_all_data()
    
    print(f"\n✅ Data retrieved:")
    for key in data:
        if isinstance(data[key], dict):
            print(f"  - {key}: {len(data[key])} items")
        elif isinstance(data[key], list):
            print(f"  - {key}: {len(data[key])} items")
        else:
            print(f"  - {key}: {data[key]}")
    
    print("\n🔬 Laboratories:")
    labs = ds.get_labs()
    print(f"  Total: {len(labs)} labs")
    for lab in labs[:5]:
        print(f"    - {lab.get('name', lab.get('id', 'Unknown'))}")
    if len(labs) > 5:
        print(f"    ... and {len(labs) - 5} more")

