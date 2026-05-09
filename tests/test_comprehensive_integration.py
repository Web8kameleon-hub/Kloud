"""
KLOUD CLOUD - COMPREHENSIVE TEST SUITE
Tests all components integration and functionality
"""

import pytest
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# ═══════════════════════════════════════════════════════════════════
# TEST FIXTURES
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture
def api_base_url():
    """Main API endpoint"""
    return "http://localhost:8000"

@pytest.fixture
def alba_url():
    """ALBA service endpoint"""
    return "http://localhost:5555"

@pytest.fixture
def albi_url():
    """ALBI service endpoint"""
    return "http://localhost:6680"

@pytest.fixture
def jona_url():
    """JONA service endpoint"""
    return "http://localhost:7777"

@pytest.fixture
def orchestrator_url():
    """Orchestrator endpoint"""
    return "http://localhost:9999"

# ═══════════════════════════════════════════════════════════════════
# API HEALTH TESTS
# ═══════════════════════════════════════════════════════════════════

class TestAPIHealth:
    """Test main API health and status"""
    
    def test_api_health(self, api_base_url):
        """Test API health endpoint"""
        import requests
        response = requests.get(f"{api_base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Kloud-industrial-backend-real"
        assert data["status"] == "operational"
    
    def test_api_status(self, api_base_url):
        """Test API status endpoint"""
        import requests
        response = requests.get(f"{api_base_url}/status")
        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        assert "timestamp" in data

# ═══════════════════════════════════════════════════════════════════
# SAAS SERVICES TESTS
# ═══════════════════════════════════════════════════════════════════

class TestAlbaService:
    """Test ALBA telemetry collector service"""
    
    def test_alba_health(self, alba_url):
        """Test ALBA health"""
        import requests
        response = requests.get(f"{alba_url}/health")
        assert response.status_code == 200
        assert response.json()["service"] == "alba-collector"
    
    def test_alba_ingest(self, alba_url):
        """Test ALBA data ingestion"""
        import requests
        payload = {
            "source": "sensor_001",
            "type": "telemetry",
            "payload": {"value": 42.5, "unit": "Hz"}
        }
        response = requests.post(f"{alba_url}/ingest", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "ingested"
    
    def test_alba_data_retrieval(self, alba_url):
        """Test ALBA data retrieval"""
        import requests
        response = requests.get(f"{alba_url}/data")
        assert response.status_code == 200
        assert "entries" in response.json()

class TestAlbiService:
    """Test ALBI neural processor service"""
    
    def test_albi_health(self, albi_url):
        """Test ALBI health"""
        import requests
        response = requests.get(f"{albi_url}/health")
        assert response.status_code == 200
        assert response.json()["service"] == "albi-processor"
    
    def test_albi_analyze(self, albi_url):
        """Test ALBI analysis"""
        import requests
        payload = {
            "channels": {
                "ch1": [1.0, 1.5, 1.2, 1.8, 1.3],
                "ch2": [2.0, 2.1, 2.05, 2.15, 2.08]
            }
        }
        response = requests.post(f"{albi_url}/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "analysis_id" in data
        assert "statistics" in data

class TestJonaService:
    """Test JONA data synthesis service"""
    
    def test_jona_health(self, jona_url):
        """Test JONA health"""
        import requests
        response = requests.get(f"{jona_url}/health")
        assert response.status_code == 200
        assert response.json()["service"] == "jona-coordinator"
    
    def test_jona_synthesize(self, jona_url):
        """Test JONA synthesis"""
        import requests
        payload = {
            "mode": "relax",
            "frequency": 10.0,
            "duration": 10,
            "amplitude": 0.7
        }
        response = requests.post(f"{jona_url}/synthesize", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "synthesis_id" in data
        assert data["mode"] == "relax"

# ═══════════════════════════════════════════════════════════════════
# ORCHESTRATOR TESTS
# ═══════════════════════════════════════════════════════════════════

class TestOrchestrator:
    """Test SAAS orchestrator"""
    
    def test_orchestrator_health(self, orchestrator_url):
        """Test orchestrator health"""
        import requests
        response = requests.get(f"{orchestrator_url}/health")
        assert response.status_code == 200
        assert response.json()["service"] == "saas-orchestrator"
    
    def test_service_registry(self, orchestrator_url):
        """Test service registry"""
        import requests
        response = requests.get(f"{orchestrator_url}/registry")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        assert "alba" in data["services"]
        assert "albi" in data["services"]
        assert "jona" in data["services"]
    
    def test_dashboard(self, orchestrator_url):
        """Test status dashboard"""
        import requests
        response = requests.get(f"{orchestrator_url}/status/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        assert "total_services" in data

# ═══════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════

class TestIntegration:
    """Test component integration"""
    
    def test_data_flow_alba_to_albi(self, alba_url, albi_url):
        """Test data flow from ALBA to ALBI"""
        import requests
        
        # 1. Ingest data into ALBA
        alba_payload = {
            "source": "sensor_test",
            "type": "integration_test",
            "payload": {"values": [1.0, 2.0, 3.0]}
        }
        alba_response = requests.post(f"{alba_url}/ingest", json=alba_payload)
        assert alba_response.status_code == 200
        
        # 2. Retrieve from ALBA
        alba_data = requests.get(f"{alba_url}/data", params={"limit": 1})
        assert alba_data.status_code == 200
        assert len(alba_data.json()["entries"]) > 0
        
        # 3. Send to ALBI for analysis
        albi_payload = {
            "channels": {
                "test": [1.0, 2.0, 3.0, 2.5, 2.0]
            }
        }
        albi_response = requests.post(f"{albi_url}/analyze", json=albi_payload)
        assert albi_response.status_code == 200
    
    def test_orchestrator_service_discovery(self, orchestrator_url):
        """Test service discovery via orchestrator"""
        import requests
        
        # Get registry
        registry = requests.get(f"{orchestrator_url}/registry")
        assert registry.status_code == 200
        
        services = registry.json()["services"]
        
        # Verify all services are registered
        for service_name in ["alba", "albi", "jona"]:
            assert service_name in services
            assert services[service_name]["status"] in ["online", "offline", "degraded"]

# ═══════════════════════════════════════════════════════════════════
# PERFORMANCE TESTS
# ═══════════════════════════════════════════════════════════════════

class TestPerformance:
    """Test system performance"""
    
    def test_api_response_time(self, api_base_url):
        """Test API response time"""
        import requests
        import time
        
        start = time.time()
        response = requests.get(f"{api_base_url}/health")
        elapsed = (time.time() - start) * 1000  # milliseconds
        
        assert response.status_code == 200
        assert elapsed < 1000  # Should respond in less than 1 second
    
    def test_alba_throughput(self, alba_url):
        """Test ALBA ingestion throughput"""
        import requests
        import time
        
        start = time.time()
        
        for i in range(100):
            payload = {
                "source": f"sensor_{i}",
                "type": "perf_test",
                "payload": {"value": i * 1.5}
            }
            response = requests.post(f"{alba_url}/ingest", json=payload)
            assert response.status_code == 200
        
        elapsed = time.time() - start
        throughput = 100 / elapsed
        
        print(f"\nALBA throughput: {throughput:.1f} entries/second")
        assert throughput > 10  # At least 10 entries per second

# ═══════════════════════════════════════════════════════════════════
# ERROR HANDLING TESTS
# ═══════════════════════════════════════════════════════════════════

class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_service(self, orchestrator_url):
        """Test requesting invalid service"""
        import requests
        response = requests.post(
            f"{orchestrator_url}/services/nonexistent/execute",
            json={"action": "test"}
        )
        assert response.status_code == 404
    
    def test_malformed_request(self, alba_url):
        """Test malformed request"""
        import requests
        response = requests.post(f"{alba_url}/ingest", json={"invalid": "data"})
        # Should either return 422 (validation error) or 200 with partial data
        assert response.status_code in [200, 422]

# ═══════════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Run with: pytest tests_comprehensive.py -v --tb=short
    pytest.main([__file__, "-v", "--tb=short", "-s"])


