# Kloud Microservices Manifest - 76+ Services

## Core Infrastructure
- **Ollama LLM** (Port 11434) - Local language model engine
- **PostgreSQL** (Port 5432) - Primary relational database
- **Redis** (Port 6379) - Cache and session store
- **Neo4j** (Port 7474/7687) - Graph database for relationships
- **MinIO** (Port 9000/9001) - Object storage (S3-compatible)

## Critical Services (Must Always Run)
1. **Ocean Core Full** (Port 8030) - Knowledge orchestrator, ResponseOrchestratorV5
2. **AI Global 9999** (Port 9999) - Multimodal AI nanogrid (chat, music, vision, tasks)
3. **API Backend** (Port 8000) - JONA coordinator, main API gateway
4. **Excel Core** (Port 8002) - Excel operations microservice
5. **Frontend** (Port 3001) - Next.js React application

## ASI Trinity Engines
6. **ALBA** (Port 5555) - Analytical Intelligence
7. **ALBI** (Port 6680) - Binary Intelligence
8. **ALDA** (Port 8003) - Data Analysis
9. **ASI** (Port 8004) - Advanced Systems Intelligence
10. **Curiosity Admin** - Internal AGI administration

## Specialized Engines
11. **CYCLE** (Port 8005) - Cycle Analysis Engine
12. **JONA** (Port 8006) - Knowledge Coordinator
13. **LIAM** (Port 8007) - Learning Intelligence Agent Manager
14. **BLERINA** - Video Generation (BLERINA pipeline)
15. **Curiosity Ocean** - Curiosity reasoning engine

## Microservices
16. **Content Factory** (Port 8008) - Content generation and management
17. **Video Generator** (Port 8009) - Video production pipeline
18. **Reporting Engine** (Port 8010) - Report generation and publishing
19. **Intelligence Lab** (Port 8011) - ML model experimentation
20. **Marketplace** (Port 8012) - Service marketplace
21. **User Management** (Port 8013) - User authentication and profiles
22. **Worker Pool** (Port 8014) - Background job processing
23. **Blog Publisher** - GitHub-based documentation publishing

## Load Balancers & Coordinators
24. **Balancer Simple** (Port 3335) - Basic load balancer
25. **Balancer Cache** (Port 3336) - Cache-aware balancer
26. **Balancer Data** (Port 3337) - Data-aware load balancing
27. **Balancer TS** (Port 3338) - TypeScript-based balancer
28. **Balancer Nodes** (Port 3333/3334) - Node balancers

## Analytics & Monitoring
29. **Advanced Analytics API** - Complex data analysis
30. **Behavioral Science API** - Behavioral pattern analysis
31. **Compliance Checker** - Compliance validation
32. **API Scanner** - API endpoint discovery and testing

## Data Processing & Transformation
33. **Add Extra Functions Column** - Data column generation
34. **Advanced Cycle Alignments** - Cycle synchronization
35. **Auto Populate Excel** - Automated data population
36. **Cycle Frame Generator** - ALBA frame generation
37. **Blerina Frame Generator** - ALBA frame generation variant
38. **Blerina Reformatter** - Video frame reformatting

## AI & Agent Systems
39. **Agents** - Agent coordination system
40. **AGIEM Core** - AGI-Enabled Entity Manager
41. **AGIEM Telemetry** - Telemetry for AGI systems
42. **Agent Telemetry Service** - Agent monitoring
43. **AI Model Versioning** - Model version management
44. **AI AGI Pipeline** - AGI execution pipeline

## Integration & Coordination
45. **API Request Generator** - Dynamic API request generation
46. **API Root Patch** - API routing and patching
47. **Kloud Integration Runner** - Integration orchestration
48. **CLX Publisher** - Publication system
49. **Convert OpenAPI** - OpenAPI conversion utilities
50. **API Key Management** - API key lifecycle management
51. **API Key Middleware** - API authentication middleware

## Specialized Services
52. **Curiosity Chat** - Interactive curiosity conversations
53. **Curiosity Admin Chat** - Admin curiosity interface
54. **Curiosity Admin Auth** - Curiosity authorization
55. **Idle Chat (ALBA)** - ALBA idle chat interface
56. **ALBA Control Panel** - Web interface for ALBA
57. **API Control Panel** - Central API management
58. **ALBA Feeder Service** - Data feeding to ALBA

## Real-time & Streaming
59. **ASI Real-time Engine** (Port 8004+) - Real-time processing
60. **Advanced Cycle Alignments** - Real-time cycle sync
61. **Bio Signals Processing** - Biological signal processing
62. **Behavioral Patterns** - Pattern detection

## Development & Testing
63. **Check Grafana Stack** - Monitoring stack validation
64. **Kloud SDK (Python)** - Python SDK
65. **Kloud SDK (TypeScript)** - TypeScript SDK
66. **Test YouTube API** - YouTube integration testing
67. **Test Neurosonix API** - Neurosonix testing

## Utilities & Tools
68. **Compliance Report** - Compliance documentation
69. **API Documentation Generator** - Auto-generate API docs
70. **Healthcare Integrations** - Medical system connectors
71. **Payment Processing** - Stripe/PayPal integration
72. **Webhook Handlers** - Event webhook processing
73. **Cache Management** - Distributed caching
74. **Session Management** - User session handling
75. **Error Tracking** - Centralized error logging

## Administrative
76. **Health Check System** - Service health monitoring
77. **Logging Aggregation** - Centralized logging
78. **Metrics Collection** - Performance metrics

## Service Architecture Notes

### Port Mapping
- **3001**: Frontend (Next.js)
- **3335-3338**: Load Balancers
- **5555**: ALBA
- **6379**: Redis
- **6680**: ALBI
- **7474/7687**: Neo4j
- **8000**: API Backend
- **8002-8014**: Microservices
- **8030**: Ocean Core
- **9000**: MinIO
- **9999**: AI Global
- **11434**: Ollama

### Startup Sequence (Priority Order)
1. Infrastructure (Ollama, PostgreSQL, Redis, Neo4j, MinIO)
2. Ocean Core (8030) - Foundation
3. AI Global 9999 - Main engine
4. API Backend (8000) - Gateway
5. Excel Core (8002) - Data operations
6. ASI Trinity (ALBA, ALBI, ALDA, ASI)
7. Specialized Engines (CYCLE, JONA, LIAM)
8. Microservices (Content, Video, Reporting, etc.)
9. Load Balancers
10. Frontend (3001)

### Dependencies
- All Python services require: `requirements.txt` in service directory
- Node services require: `package.json` with build scripts
- FastAPI services expose: `/health`, `/status` endpoints
- All services log to: stdout (captured by orchestrator)

### Environment Variables (Global)
- `OLLAMA_HOST`: http://127.0.0.1:11434
- `OCEAN_CORE_URL`: http://127.0.0.1:8030
- `API_BACKEND_URL`: http://127.0.0.1:8000
- `REDIS_URL`: redis://127.0.0.1:6379
- `DATABASE_URL`: postgresql://kloud:kloud@127.0.0.1:5432/klouddb

### Health Check URLs
```bash
curl http://localhost:9999/health       # AI Global
curl http://localhost:8030/health       # Ocean Core
curl http://localhost:8000/health       # API Backend
curl http://localhost:3001              # Frontend
curl http://localhost:11434/api/health  # Ollama
```

### Status: Ready to Deploy
✅ All 76+ services configured and ready
✅ Orchestrator script created (START_ALL_SERVICES.ps1)
✅ Service manifest complete
✅ Dependencies verified

