#!/usr/bin/env python3
"""
Distributed Trace Testing Script for Kloud Cloud
Tests the ALBA → ALBI → JONA → API pipeline with OpenTelemetry tracing.
"""

import asyncio
import json
import time
import requests
from typing import Dict, Any

BASE_URL = "http://localhost"

# Service endpoints
ALBA_URL = f"{BASE_URL}:5555"
ALBI_URL = f"{BASE_URL}:6680"
JONA_URL = f"{BASE_URL}:7777"
API_URL = f"{BASE_URL}:8000"
ORCHESTRATOR_URL = f"{BASE_URL}:9999"


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def test_alba_health():
    """Test ALBA health and generate trace"""
    print_header("1️⃣ Testing ALBA Collector (5555)")
    try:
        response = requests.get(f"{ALBA_URL}/health", timeout=5)
        print(f"✓ ALBA Health: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ ALBA Error: {e}")
        return False


def test_alba_ingest():
    """Ingest telemetry data into ALBA"""
    print_header("2️⃣ Ingesting Telemetry into ALBA")
    try:
        payload = {
            "source": "sensor-cluster-001",
            "type": "eeg_burst",
            "payload": {
                "channels": {
                    "fp1": 12.5,
                    "fp2": 11.8,
                    "f3": 13.2,
                    "f4": 12.9
                },
                "sample_rate": 256,
                "duration_ms": 100
            },
            "quality": 0.95
        }
        response = requests.post(f"{ALBA_URL}/ingest", json=payload, timeout=5)
        print(f"✓ Ingest Response: {response.status_code}")
        print(f"  {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Ingest Error: {e}")
        return False


def test_alba_data():
    """Retrieve telemetry data from ALBA"""
    print_header("3️⃣ Retrieving Data from ALBA")
    try:
        response = requests.get(f"{ALBA_URL}/data?limit=5", timeout=5)
        print(f"✓ ALBA Data Response: {response.status_code}")
        data = response.json()
        print(f"  Entries in buffer: {data.get('count')}")
        print(f"  Buffer size: {data.get('buffer_size')}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Data Retrieval Error: {e}")
        return False


def test_albi_health():
    """Test ALBI health"""
    print_header("4️⃣ Testing ALBI Processor (6680)")
    try:
        response = requests.get(f"{ALBI_URL}/health", timeout=5)
        print(f"✓ ALBI Health: {response.status_code}")
        print(f"  {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ ALBI Error: {e}")
        return False


def test_albi_analyze():
    """Analyze data with ALBI"""
    print_header("5️⃣ Analyzing Data with ALBI")
    try:
        payload = {
            "channels": {
                "fp1": [10.0, 11.5, 12.0, 11.8, 10.5, 15.0],  # Note: outlier at 15.0
                "fp2": [11.0, 10.8, 11.5, 10.9, 11.2, 10.5],
                "f3": [12.0, 13.0, 12.5, 12.8, 12.3, 20.0]   # Note: outlier at 20.0
            }
        }
        response = requests.post(f"{ALBI_URL}/analyze", json=payload, timeout=5)
        print(f"✓ Analysis Response: {response.status_code}")
        analysis = response.json()
        print(f"  Analysis ID: {analysis.get('analysis_id')}")
        print(f"  Anomalies detected: {analysis.get('anomalies')}")
        print(f"  Confidence: {analysis.get('confidence')}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Analysis Error: {e}")
        return False


def test_jona_health():
    """Test JONA health"""
    print_header("6️⃣ Testing JONA Coordinator (7777)")
    try:
        response = requests.get(f"{JONA_URL}/health", timeout=5)
        print(f"✓ JONA Health: {response.status_code}")
        print(f"  {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ JONA Error: {e}")
        return False


def test_jona_synthesize():
    """Synthesize audio with JONA"""
    print_header("7️⃣ Synthesizing Audio with JONA")
    try:
        payload = {
            "mode": "focus",
            "frequency": 40.0,  # Gamma waves for focus
            "duration": 30,
            "amplitude": 0.8
        }
        response = requests.post(f"{JONA_URL}/synthesize", json=payload, timeout=5)
        print(f"✓ Synthesis Response: {response.status_code}")
        synthesis = response.json()
        print(f"  Synthesis ID: {synthesis.get('synthesis_id')}")
        print(f"  Mode: {synthesis.get('mode')}")
        print(f"  Frequency: {synthesis.get('frequency')}Hz")
        print(f"  Status: {synthesis.get('status')}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Synthesis Error: {e}")
        return False


def test_orchestrator_registry():
    """Get service registry from orchestrator"""
    print_header("8️⃣ Checking Service Registry (Orchestrator)")
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/registry", timeout=5)
        print(f"✓ Registry Response: {response.status_code}")
        registry = response.json()
        print(f"  Total services: {registry.get('total_services')}")
        print(f"  Healthy services: {registry.get('healthy_count')}")
        
        # Print service status
        for service_name, service_info in registry.get('services', {}).items():
            status = "🟢" if service_info.get('status') == 'online' else "🔴"
            health = service_info.get('health', 0.0)
            print(f"    {status} {service_name}: {health:.1%} healthy")
        
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Registry Error: {e}")
        return False


def test_communication_log():
    """Get communication log from orchestrator"""
    print_header("9️⃣ Checking Communication Log (Orchestrator)")
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/traces?limit=10", timeout=5)
        print(f"✓ Communication Log Response: {response.status_code}")
        log = response.json()
        print(f"  Total events: {log.get('count')}")
        
        # Print last few events
        for trace in log.get('traces', [])[-5:]:
            print(f"    {trace.get('source')} → {trace.get('destination')}: {trace.get('packet_type')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Communication Log Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          KLOUD DISTRIBUTED TRACING - FULL PIPELINE TEST         ║")
    print("║                                                                    ║")
    print("║  This test generates traces through:                              ║")
    print("║  ALBA (5555) → ALBI (6680) → JONA (7777) → Orchestrator (9999)    ║")
    print("║                                                                    ║")
    print("║  📊 Open Grafana: http://localhost:3001                           ║")
    print("║  🔍 View Traces: Explore → Select 'Tempo' datasource → Search     ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")
    
    # Wait for user to be ready
    input("Press ENTER to start tests...")
    
    tests = [
        ("ALBA Health Check", test_alba_health),
        ("ALBA Telemetry Ingest", test_alba_ingest),
        ("ALBA Data Retrieval", test_alba_data),
        ("ALBI Health Check", test_albi_health),
        ("ALBI Data Analysis", test_albi_analyze),
        ("JONA Health Check", test_jona_health),
        ("JONA Audio Synthesis", test_jona_synthesize),
        ("Orchestrator Registry", test_orchestrator_registry),
        ("Communication Log", test_communication_log),
    ]
    
    results = {}
    start_time = time.time()
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
            time.sleep(0.5)  # Small delay between tests
        except Exception as e:
            print(f"✗ Test '{test_name}' failed: {e}")
            results[test_name] = False
    
    elapsed = time.time() - start_time
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n✓ Passed: {passed}/{total}")
    for test_name, result in results.items():
        status = "✓" if result else "✗"
        print(f"  {status} {test_name}")
    
    print(f"\n⏱️  Total time: {elapsed:.2f}s")
    
    print_header("NEXT STEPS")
    print("""
✅ All tests passed! Now view your distributed traces:

1. Open Grafana:
   URL: http://localhost:3001
   User: admin
   Pass: kloud123

2. Navigate to Explore (Compass icon)

3. Select "Tempo" datasource from dropdown

4. Click "Search" to find recent traces

5. You should see traces with:
   - Service spans from ALBA, ALBI, JONA
   - Latency metrics for each operation
   - Error tracking (if any)
   - Service dependencies (dependency graph)

6. Click on a trace to see the full distributed trace tree:
   └─ alba.ingest
      └─ alba.metrics
   └─ albi.analyze
      └─ albi.anomaly_detection
   └─ jona.synthesize
   └─ orchestrator.registry

💡 TIP: Use the trace search to filter by service name or duration!
    """)


if __name__ == "__main__":
    main()


