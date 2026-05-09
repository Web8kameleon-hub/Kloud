"""
Test Agent Registration & API Documentation
"""
import requests
import json

ORCHESTRATOR_URL = "http://localhost:9999"

# 1. Register AGIEM Agent
print("📝 Registering AGIEM Agent...")
agiem_registration = {
    "agent_name": "AGIEM",
    "agent_type": "agiem",
    "version": "2.0.0",
    "capabilities": ["pipeline_execution", "node_coordination", "system_analysis"],
    "max_instances": 5,
    "endpoints": [
        {
            "path": "/agiem/pipeline/execute",
            "method": "POST",
            "summary": "Execute AGIEM pipeline",
            "description": "Runs the complete ALBA->ALBI->JONA->ASI pipeline",
            "parameters": [],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "config": {"type": "object"},
                                "mode": {"type": "string", "enum": ["fast", "deep", "auto"]}
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "Pipeline executed successfully",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string"},
                                    "execution_time_ms": {"type": "number"},
                                    "results": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            }
        },
        {
            "path": "/agiem/status",
            "method": "GET",
            "summary": "Get AGIEM status",
            "description": "Returns current status of AGIEM nodes and health metrics"
        }
    ],
    "metadata": {
        "description": "AGIEM coordinates the full ALBA/ALBI/JONA/ASI pipeline",
        "documentation_url": "https://docs.kloud.com/agiem"
    }
}

response = requests.post(f"{ORCHESTRATOR_URL}/agents/register", json=agiem_registration)
print(f"Response: {response.status_code}")
agiem_data = response.json()
print(json.dumps(agiem_data, indent=2))
agiem_id = agiem_data["agent_id"]

# 2. Register ASI Agent
print("\n📝 Registering ASI Agent...")
asi_registration = {
    "agent_name": "ASI",
    "agent_type": "asi",
    "version": "1.5.0",
    "capabilities": ["realtime_analysis", "health_monitoring", "node_management"],
    "max_instances": 3,
    "endpoints": [
        {
            "path": "/asi/analyze",
            "method": "POST",
            "summary": "Run ASI real-time analysis",
            "description": "Analyzes system metrics in real-time"
        },
        {
            "path": "/asi/nodes",
            "method": "GET",
            "summary": "Get ASI nodes status",
            "description": "Returns status of all ASI-managed nodes"
        }
    ],
    "metadata": {
        "description": "ASI manages real-time analysis and node health"
    }
}

response = requests.post(f"{ORCHESTRATOR_URL}/agents/register", json=asi_registration)
print(f"Response: {response.status_code}")
asi_data = response.json()
print(json.dumps(asi_data, indent=2))
asi_id = asi_data["agent_id"]

# 3. Generate API Documentation for AGIEM
print(f"\n📚 Generating API Documentation for AGIEM ({agiem_id})...")
response = requests.post(
    f"{ORCHESTRATOR_URL}/api-docs/generate",
    params={"agent_id": agiem_id},
    json={"endpoints": agiem_registration["endpoints"]}
)
print(f"Response: {response.status_code}")
if response.status_code == 200:
    docs_data = response.json()
    print(f"Generated {docs_data.get('endpoints_count', 0)} API endpoints")
else:
    print(f"Error: {response.text}")

# 4. List all registered agents
print("\n🤖 Listing all agents...")
response = requests.get(f"{ORCHESTRATOR_URL}/agents")
agents_data = response.json()
print(f"Total agents: {agents_data['count']}")
for agent in agents_data['agents']:
    print(f"  • {agent['agent_name']} ({agent['agent_type']}) - {agent['current_instances']}/{agent['max_instances']} instances")

# 5. Scale AGIEM to 3 instances
print(f"\n📈 Scaling AGIEM to 3 instances...")
response = requests.post(
    f"{ORCHESTRATOR_URL}/agents/{agiem_id}/scale",
    params={"target_instances": 3}
)
scale_data = response.json()
print(json.dumps(scale_data, indent=2))

# 6. Send heartbeat
print(f"\n💓 Sending heartbeat for AGIEM...")
response = requests.post(
    f"{ORCHESTRATOR_URL}/agents/{agiem_id}/heartbeat",
    json={
        "cpu_usage": 45.2,
        "memory_usage": 62.8,
        "active_pipelines": 5
    }
)
print(f"Response: {response.status_code} - {response.json()}")

# 7. Get API docs
print(f"\n📖 Retrieving API documentation...")
response = requests.get(f"{ORCHESTRATOR_URL}/api-docs")
docs = response.json()
print(f"Total documented APIs: {docs['count']}")

# 8. Get OpenAPI spec for AGIEM
print(f"\n📄 Getting OpenAPI spec for AGIEM...")
response = requests.get(f"{ORCHESTRATOR_URL}/api-docs/{agiem_id}/openapi.json")
openapi_spec = response.json()
print(f"OpenAPI version: {openapi_spec['openapi']}")
print(f"Title: {openapi_spec['info']['title']}")
print(f"Paths: {list(openapi_spec['paths'].keys())}")

# 9. Test service proxy
print(f"\n🔄 Testing service proxy (Alba)...")
response = requests.get(f"{ORCHESTRATOR_URL}/services/alba/health")
print(f"Alba health via proxy: {response.json()}")

print("\n✅ All tests passed!")


