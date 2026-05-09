"""
Generate test traces for Tempo visualization
Sends sample OpenTelemetry traces to populate Grafana Tempo
"""

import time
import random
import requests
from datetime import datetime, timezone

TEMPO_OTLP_HTTP = "http://localhost:4318/v1/traces"

def generate_trace_id():
    """Generate random 32-char hex trace ID"""
    return ''.join(random.choices('0123456789abcdef', k=32))

def generate_span_id():
    """Generate random 16-char hex span ID"""
    return ''.join(random.choices('0123456789abcdef', k=16))

def create_otlp_trace(service_name: str, operation: str, duration_ms: int, status: str = "OK"):
    """Create OTLP-formatted trace"""
    now_ns = int(time.time() * 1_000_000_000)
    trace_id = generate_trace_id()
    span_id = generate_span_id()
    
    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": service_name}},
                        {"key": "service.version", "value": {"stringValue": "1.0.0"}},
                        {"key": "deployment.environment", "value": {"stringValue": "production"}}
                    ]
                },
                "scopeSpans": [
                    {
                        "scope": {
                            "name": "kloud-tracer",
                            "version": "1.0.0"
                        },
                        "spans": [
                            {
                                "traceId": trace_id,
                                "spanId": span_id,
                                "name": operation,
                                "kind": 1,  # SPAN_KIND_INTERNAL
                                "startTimeUnixNano": str(now_ns - duration_ms * 1_000_000),
                                "endTimeUnixNano": str(now_ns),
                                "attributes": [
                                    {"key": "http.method", "value": {"stringValue": "POST"}},
                                    {"key": "http.status_code", "value": {"intValue": "200"}},
                                    {"key": "operation.type", "value": {"stringValue": operation}},
                                    {"key": "agent.active", "value": {"boolValue": True}}
                                ],
                                "status": {
                                    "code": 1 if status == "OK" else 2  # STATUS_CODE_OK or ERROR
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }

def send_trace(trace_data):
    """Send trace to Tempo via OTLP HTTP"""
    try:
        response = requests.post(
            TEMPO_OTLP_HTTP,
            json=trace_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Failed to send trace: {e}")
        return False

def main():
    print("\n╔═══════════════════════════════════════════════════════════════╗")
    print("║  GENERATING TEST TRACES FOR TEMPO                            ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")
    
    services = [
        ("orchestrator", ["agent_registration", "agent_scaling", "api_docs_generation", "health_check"]),
        ("alba-collector", ["telemetry_ingest", "metrics_collection", "network_analysis"]),
        ("albi-processor", ["analytics_processing", "neural_computation", "insight_generation"]),
        ("jona-coordinator", ["data_synthesis", "coordination_event", "pipeline_orchestration"]),
        ("agiem-agent", ["pipeline_execution", "quality_control", "resource_management"]),
        ("asi-agent", ["realtime_processing", "adaptive_learning", "stream_management"])
    ]
    
    total_traces = 0
    successful = 0
    
    print("📊 Generating traces for each service...\n")
    
    for service_name, operations in services:
        print(f"   Service: {service_name}")
        
        for operation in operations:
            # Generate 3-5 traces per operation
            num_traces = random.randint(3, 5)
            
            for i in range(num_traces):
                duration_ms = random.randint(50, 500)
                status = "OK" if random.random() > 0.1 else "ERROR"  # 10% error rate
                
                trace = create_otlp_trace(service_name, operation, duration_ms, status)
                
                if send_trace(trace):
                    successful += 1
                    status_emoji = "✅" if status == "OK" else "⚠️"
                    print(f"      {status_emoji} {operation}: {duration_ms}ms ({status})")
                
                total_traces += 1
                time.sleep(0.1)  # Small delay between traces
        
        print()
    
    print(f"\n{'='*65}")
    print(f"✅ Generated {successful}/{total_traces} traces successfully")
    print(f"{'='*65}\n")
    print("🔍 Check Grafana Tempo at http://localhost:3000")
    print("   Data Source: Tempo")
    print("   Service Graph should now show:")
    for service_name, _ in services:
        print(f"      • {service_name}")
    print()

if __name__ == "__main__":
    main()


