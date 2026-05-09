"""
Quick health check for Grafana observability stack
Checks: Grafana, Tempo, Loki, Prometheus/VictoriaMetrics
"""

import requests
import sys

CHECKS = [
    {
        "name": "Grafana",
        "url": "http://localhost:3001/api/health",
        "expected": 200
    },
    {
        "name": "Tempo (Query API)",
        "url": "http://localhost:3200/status",
        "expected": 200
    },
    {
        "name": "Tempo (Search Tags)",
        "url": "http://localhost:3200/api/v2/search/tags",
        "expected": 200
    },
    {
        "name": "Loki (Ready)",
        "url": "http://localhost:3100/ready",
        "expected": 200
    },
    {
        "name": "VictoriaMetrics",
        "url": "http://localhost:8428/health",
        "expected": 200
    },
    {
        "name": "Orchestrator",
        "url": "http://localhost:9999/health",
        "expected": 200
    },
    {
        "name": "Alba",
        "url": "http://localhost:5050/health",
        "expected": 200
    },
    {
        "name": "Albi",
        "url": "http://localhost:6060/health",
        "expected": 200
    },
    {
        "name": "Jona",
        "url": "http://localhost:7070/health",
        "expected": 200
    }
]

def check_service(name, url, expected_status):
    """Check if service is responding"""
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == expected_status:
            print(f"✅ {name:25s} → {response.status_code} OK")
            return True
        else:
            print(f"⚠️  {name:25s} → {response.status_code} (expected {expected_status})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name:25s} → Connection refused")
        return False
    except requests.exceptions.Timeout:
        print(f"⏱️  {name:25s} → Timeout")
        return False
    except Exception as e:
        print(f"❌ {name:25s} → {type(e).__name__}: {e}")
        return False

def check_tempo_traces():
    """Check if Tempo has traces"""
    try:
        response = requests.get(
            "http://localhost:3200/api/search?tags=",
            timeout=3
        )
        if response.status_code == 200:
            data = response.json()
            trace_count = len(data.get("traces", []))
            print(f"📊 Tempo traces stored      → {trace_count} traces")
            return trace_count > 0
        return False
    except:
        return False

def main():
    print("\n╔═══════════════════════════════════════════════════════════════╗")
    print("║  GRAFANA OBSERVABILITY STACK - HEALTH CHECK                  ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")
    
    results = []
    
    for check in CHECKS:
        result = check_service(check["name"], check["url"], check["expected"])
        results.append(result)
    
    print()
    has_traces = check_tempo_traces()
    
    total = len(results)
    passed = sum(results)
    
    print(f"\n{'='*65}")
    print(f"Summary: {passed}/{total} services healthy")
    
    if has_traces:
        print("✅ Tempo has trace data")
    else:
        print("⚠️  Tempo has no traces - run: python generate_test_traces.py")
    
    print(f"{'='*65}\n")
    
    if passed == total and has_traces:
        print("🎉 All systems operational!")
        print("🔍 Access Grafana: http://localhost:3001")
        print("   Username: admin")
        print("   Password: kloud123")
        return 0
    else:
        print("⚠️  Some services are not responding")
        return 1

if __name__ == "__main__":
    sys.exit(main())


