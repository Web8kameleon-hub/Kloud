# API Fabric Implementation

**Status**: 🔴 Not Started  
**Priority**: Critical - External API exposure  
**Timeline**: 3-4 weeks

---

## 📋 Overview

Build FastAPI-based knowledge API service with specialized routers for scientific search, biomedical queries, telemetry access, clinical data, and concept gap discovery. Integrate with Kong API Gateway, Keycloak authentication, and OpenTelemetry observability.

---

## 🎯 Objectives

1. Develop FastAPI service `services/knowledge-api`
2. Implement routers for all data access patterns
3. Deploy Kong API Gateway for routing, auth, rate limiting
4. Integrate Keycloak for OIDC authentication
5. Instrument with OpenTelemetry for tracing
6. Auto-generate and publish OpenAPI specs
7. Setup monitoring dashboards in Grafana

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT APPLICATIONS                     │
│              (Alba, Albi, Jona, ASI, External)              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Kong Gateway   │
                  │  - Routing      │
                  │  - Auth (OIDC)  │
                  │  - Rate Limit   │
                  │  - Logging      │
                  └────────┬────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Keycloak (Identity)  │
              │   - OIDC Provider      │
              │   - Role Management    │
              └────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  FastAPI        │
                  │  Knowledge API  │
                  └────────┬────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  ┌──────────┐      ┌──────────┐      ┌──────────┐
  │ Weaviate │      │  Neo4j   │      │Timescale │
  │ (Vector) │      │ (Graph)  │      │  (TS)    │
  └──────────┘      └──────────┘      └──────────┘
        │                  │                  │
        └──────────────────┴──────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Jaeger/Tempo   │
                  │  (Tracing)      │
                  └─────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Prometheus     │
                  │  (Metrics)      │
                  └─────────────────┘
```

---

## 🚀 Component 1: FastAPI Knowledge Service

### **Project Structure**

```
services/knowledge-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── scientific.py
│   │   ├── clinical.py
│   │   ├── telemetry.py
│   │   └── concepts.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── search.py          # /search/scientific, /search/bio
│   │   ├── clinical.py        # /clinical/drugs, /clinical/trials
│   │   ├── telemetry.py       # /telemetry/{source}
│   │   ├── concepts.py        # /concepts/gaps, /concepts/new
│   │   └── health.py          # /health, /metrics
│   ├── services/
│   │   ├── __init__.py
│   │   ├── weaviate_client.py
│   │   ├── neo4j_client.py
│   │   ├── timescale_client.py
│   │   └── postgres_client.py
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py
│       ├── logging.py
│       └── tracing.py
├── tests/
│   ├── test_search.py
│   ├── test_clinical.py
│   └── test_telemetry.py
├── Dockerfile
├── requirements.txt
└── pyproject.toml
```

### **Main Application**

**File**: `services/knowledge-api/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from prometheus_fastapi_instrumentator import Instrumentator

from app.routers import search, clinical, telemetry, concepts, health
from app.config import settings
from app.middleware.auth import JWTBearer
from app.middleware.logging import setup_logging

# Initialize tracing
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name=settings.JAEGER_HOST,
    agent_port=settings.JAEGER_PORT,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Kloud Knowledge API",
    description="Unified API for scientific literature, clinical data, and industrial telemetry",
    version="1.0.0",
    docs_url=None,  # Disable default to customize
    redoc_url=None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication dependency
auth_bearer = JWTBearer(keycloak_url=settings.KEYCLOAK_URL)

# Include routers
app.include_router(
    search.router,
    prefix="/search",
    tags=["Search"],
    dependencies=[Depends(auth_bearer)]
)
app.include_router(
    clinical.router,
    prefix="/clinical",
    tags=["Clinical"],
    dependencies=[Depends(auth_bearer)]
)
app.include_router(
    telemetry.router,
    prefix="/telemetry",
    tags=["Telemetry"],
    dependencies=[Depends(auth_bearer)]
)
app.include_router(
    concepts.router,
    prefix="/concepts",
    tags=["Concepts"],
    dependencies=[Depends(auth_bearer)]
)
app.include_router(
    health.router,
    tags=["Health"]
)

# Instrument for Prometheus
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Instrument for OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

# Custom docs with auth
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(auth: str = Depends(auth_bearer)):
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - Swagger UI",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html(auth: str = Depends(auth_bearer)):
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - ReDoc",
    )

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Kloud Knowledge API")
    # Initialize database connections
    await init_database_pools()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Kloud Knowledge API")
    # Close database connections
    await close_database_pools()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
```

### **Search Router**

**File**: `services/knowledge-api/app/routers/search.py`

```python
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.services.weaviate_client import WeaviateService
from app.services.neo4j_client import Neo4jService

router = APIRouter()

class SearchQuery(BaseModel):
    query: str
    limit: int = 10
    offset: int = 0
    filters: Optional[dict] = None

class SearchResult(BaseModel):
    document_id: str
    title: str
    abstract: str
    source: str
    publication_date: Optional[str]
    similarity_score: float
    metadata: dict

@router.post("/scientific", response_model=List[SearchResult])
async def search_scientific(
    query: SearchQuery,
    weaviate: WeaviateService = Depends()
):
    """
    Semantic search across scientific literature.
    
    Sources: OpenAlex, ArXiv, Semantic Scholar
    
    Example:
        POST /search/scientific
        {
            "query": "CRISPR gene editing in neural cells",
            "limit": 10,
            "filters": {"publication_date": {"gte": "2023-01-01"}}
        }
    """
    try:
        results = await weaviate.search_scientific(
            query=query.query,
            limit=query.limit,
            offset=query.offset,
            filters=query.filters
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/bio", response_model=List[SearchResult])
async def search_biomedical(
    query: SearchQuery,
    weaviate: WeaviateService = Depends(),
    neo4j: Neo4jService = Depends()
):
    """
    Combined vector + graph search for biomedical data.
    
    Sources: PubMed, ClinicalTrials.gov, OpenFDA
    
    Example:
        POST /search/bio
        {
            "query": "alzheimer disease treatments",
            "limit": 10
        }
    """
    try:
        # Step 1: Vector search in Weaviate
        vector_results = await weaviate.search_clinical(
            query=query.query,
            limit=query.limit * 2  # Get more candidates
        )
        
        # Step 2: Enrich with graph relationships from Neo4j
        doc_ids = [r.document_id for r in vector_results]
        graph_data = await neo4j.get_document_relationships(doc_ids)
        
        # Step 3: Merge results
        enriched_results = merge_vector_graph_results(
            vector_results,
            graph_data
        )
        
        return enriched_results[:query.limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/related/{document_id}")
async def get_related_documents(
    document_id: str,
    limit: int = Query(default=10, le=50),
    neo4j: Neo4jService = Depends()
):
    """
    Find documents related via citation graph.
    
    Example:
        GET /search/related/W3012345678?limit=10
    """
    try:
        related = await neo4j.find_related_publications(
            document_id=document_id,
            limit=limit
        )
        return related
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {str(e)}")
```

### **Clinical Router**

**File**: `services/knowledge-api/app/routers/clinical.py`

```python
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from app.services.postgres_client import PostgresService
from app.services.neo4j_client import Neo4jService

router = APIRouter()

class Drug(BaseModel):
    drug_id: str
    name: str
    generic_name: Optional[str]
    mechanism: Optional[str]
    indications: List[str]
    adverse_events: List[dict]
    atc_code: Optional[str]

class ClinicalTrial(BaseModel):
    nct_id: str
    title: str
    brief_summary: str
    condition: List[str]
    intervention: List[str]
    phase: Optional[str]
    status: str
    start_date: Optional[str]
    completion_date: Optional[str]
    enrollment: Optional[int]

@router.get("/drugs", response_model=List[Drug])
async def get_drugs(
    name: Optional[str] = Query(None, description="Drug name filter"),
    indication: Optional[str] = Query(None, description="Indication filter"),
    limit: int = Query(default=20, le=100),
    postgres: PostgresService = Depends()
):
    """
    Get pharmaceutical drug data from OpenFDA and DrugBank.
    
    Example:
        GET /clinical/drugs?indication=hypertension&limit=10
    """
    try:
        drugs = await postgres.fetch_drugs(
            name=name,
            indication=indication,
            limit=limit
        )
        return drugs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drugs/{drug_id}")
async def get_drug_details(
    drug_id: str,
    postgres: PostgresService = Depends(),
    neo4j: Neo4jService = Depends()
):
    """
    Get detailed drug information including relationships.
    
    Example:
        GET /clinical/drugs/DB00945
    """
    try:
        # Get drug data from Postgres
        drug = await postgres.fetch_drug_by_id(drug_id)
        
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        
        # Enrich with graph relationships (treats, interacts with)
        relationships = await neo4j.get_drug_relationships(drug_id)
        drug['relationships'] = relationships
        
        return drug
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trials", response_model=List[ClinicalTrial])
async def get_clinical_trials(
    condition: Optional[str] = Query(None),
    status: Optional[str] = Query(None, regex="^(Recruiting|Completed|Terminated)$"),
    phase: Optional[str] = Query(None, regex="^(Phase [1-4]|Early Phase 1)$"),
    limit: int = Query(default=20, le=100),
    postgres: PostgresService = Depends()
):
    """
    Search clinical trials from ClinicalTrials.gov.
    
    Example:
        GET /clinical/trials?condition=cancer&status=Recruiting&phase=Phase%203&limit=10
    """
    try:
        trials = await postgres.fetch_clinical_trials(
            condition=condition,
            status=status,
            phase=phase,
            limit=limit
        )
        return trials
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### **Telemetry Router**

**File**: `services/knowledge-api/app/routers/telemetry.py`

```python
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.services.timescale_client import TimescaleService

router = APIRouter()

class TelemetryQuery(BaseModel):
    node_id: Optional[str] = None
    metric: Optional[str] = None
    start_time: datetime
    end_time: datetime
    aggregation: Optional[str] = "raw"  # raw, hourly, daily
    downsample_interval: Optional[str] = None

class TelemetryData(BaseModel):
    time: datetime
    source: str
    node_id: str
    metric: str
    value: float
    unit: Optional[str]
    quality: Optional[int]

@router.get("/{source}", response_model=List[TelemetryData])
async def get_telemetry(
    source: str,
    node_id: Optional[str] = Query(None),
    metric: Optional[str] = Query(None),
    start_time: datetime = Query(default=None),
    end_time: datetime = Query(default=None),
    aggregation: str = Query(default="raw", regex="^(raw|hourly|daily)$"),
    limit: int = Query(default=1000, le=10000),
    timescale: TimescaleService = Depends()
):
    """
    Query industrial telemetry data.
    
    Sources: fiware, opcua, openplc, ditto
    
    Example:
        GET /telemetry/fiware?node_id=sensor-001&metric=temperature&start_time=2025-12-01T00:00:00Z&end_time=2025-12-13T23:59:59Z&aggregation=hourly
    """
    if source not in ["fiware", "opcua", "openplc", "ditto"]:
        raise HTTPException(status_code=400, detail=f"Invalid source: {source}")
    
    # Default time range: last 24 hours
    if not start_time:
        start_time = datetime.utcnow() - timedelta(days=1)
    if not end_time:
        end_time = datetime.utcnow()
    
    try:
        if aggregation == "raw":
            data = await timescale.fetch_raw_telemetry(
                source=source,
                node_id=node_id,
                metric=metric,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )
        elif aggregation == "hourly":
            data = await timescale.fetch_hourly_aggregate(
                source=source,
                node_id=node_id,
                metric=metric,
                start_time=start_time,
                end_time=end_time
            )
        elif aggregation == "daily":
            data = await timescale.fetch_daily_aggregate(
                source=source,
                node_id=node_id,
                metric=metric,
                start_time=start_time,
                end_time=end_time
            )
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/anomalies/{source}")
async def detect_anomalies(
    source: str,
    node_id: str,
    metric: str,
    lookback_hours: int = Query(default=24, le=168),
    sensitivity: float = Query(default=3.0, ge=1.0, le=5.0),
    timescale: TimescaleService = Depends()
):
    """
    Detect anomalies in telemetry data using statistical methods.
    
    Example:
        GET /telemetry/anomalies/fiware?node_id=sensor-001&metric=temperature&lookback_hours=48&sensitivity=3.0
    """
    try:
        anomalies = await timescale.detect_anomalies(
            source=source,
            node_id=node_id,
            metric=metric,
            lookback_hours=lookback_hours,
            sensitivity=sensitivity
        )
        return anomalies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🔐 Component 2: Kong API Gateway

### **Docker Compose Configuration**

**File**: `docker-compose.kong.yml`

```yaml
version: '3.8'

services:
  kong-database:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: kong
      POSTGRES_DB: kong
      POSTGRES_PASSWORD: ${KONG_PG_PASSWORD}
    volumes:
      - kong-postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "kong"]
      interval: 10s
      timeout: 5s
      retries: 5

  kong-migration:
    image: kong/kong-gateway:3.5
    depends_on:
      - kong-database
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: ${KONG_PG_PASSWORD}
    command: kong migrations bootstrap

  kong:
    image: kong/kong-gateway:3.5
    depends_on:
      - kong-database
      - kong-migration
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: ${KONG_PG_PASSWORD}
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: 0.0.0.0:8001
      KONG_ADMIN_GUI_LISTEN: 0.0.0.0:8002
      KONG_PLUGINS: bundled,oidc
    ports:
      - "8000:8000"  # Proxy
      - "8443:8443"  # Proxy SSL
      - "8001:8001"  # Admin API
      - "8002:8002"  # Admin GUI
    restart: unless-stopped

volumes:
  kong-postgres-data:
```

### **Kong Service Configuration**

**File**: `scripts/configure-kong.sh`

```bash
#!/bin/bash
set -e

KONG_ADMIN="http://localhost:8001"
KEYCLOAK_URL="http://keycloak:8080/realms/kloud"

# Create service
curl -i -X POST $KONG_ADMIN/services/ \
  --data name=knowledge-api \
  --data url='http://knowledge-api:8000'

# Create routes
curl -i -X POST $KONG_ADMIN/services/knowledge-api/routes \
  --data 'paths[]=/api/v1' \
  --data name=knowledge-api-route

# Add OIDC plugin
curl -i -X POST $KONG_ADMIN/services/knowledge-api/plugins \
  --data name=oidc \
  --data config.client_id=knowledge-api \
  --data config.client_secret=${KEYCLOAK_CLIENT_SECRET} \
  --data config.discovery=${KEYCLOAK_URL}/.well-known/openid-configuration \
  --data config.scope=openid \
  --data config.bearer_only=yes \
  --data config.realm=kloud \
  --data config.introspection_endpoint=${KEYCLOAK_URL}/protocol/openid-connect/token/introspect \
  --data config.logout_path=/logout

# Add rate limiting
curl -i -X POST $KONG_ADMIN/services/knowledge-api/plugins \
  --data name=rate-limiting \
  --data config.minute=100 \
  --data config.hour=1000 \
  --data config.policy=redis \
  --data config.redis_host=redis \
  --data config.redis_port=6379

# Add request logging
curl -i -X POST $KONG_ADMIN/services/knowledge-api/plugins \
  --data name=file-log \
  --data config.path=/var/log/kong/requests.log

echo "✅ Kong configured successfully"
```

---

## 🔑 Component 3: Keycloak (Identity)

### **Docker Compose**

**File**: `docker-compose.keycloak.yml`

```yaml
version: '3.8'

services:
  keycloak:
    image: quay.io/keycloak/keycloak:23.0
    environment:
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: ${KEYCLOAK_DB_PASSWORD}
      KC_HOSTNAME: keycloak.kloud.com
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD}
    ports:
      - "8080:8080"
    command: start-dev
    depends_on:
      - postgres
```

### **Realm Configuration**

**Roles**:
- `asi-core` - Full access
- `alba-agent` - Scientific data access
- `albi-agent` - Industrial telemetry access
- `jona-engine` - Decision data access
- `external-user` - Limited read-only

---

## ✅ Implementation Checklist

### Phase 1: FastAPI Service (Week 1-2)
- [ ] Setup project structure
- [ ] Implement search routers
- [ ] Implement clinical routers
- [ ] Implement telemetry routers
- [ ] Implement concepts router
- [ ] Add authentication middleware
- [ ] Add OpenTelemetry instrumentation
- [ ] Write unit tests
- [ ] Generate OpenAPI spec

### Phase 2: Kong Gateway (Week 2)
- [ ] Deploy Kong + Postgres
- [ ] Configure services and routes
- [ ] Setup OIDC plugin
- [ ] Configure rate limiting
- [ ] Test authentication flow

### Phase 3: Keycloak (Week 2-3)
- [ ] Deploy Keycloak
- [ ] Create realm and clients
- [ ] Define roles and policies
- [ ] Test token generation

### Phase 4: Integration (Week 3-4)
- [ ] Connect FastAPI to Kong
- [ ] Test end-to-end auth flow
- [ ] Load test API endpoints
- [ ] Setup monitoring dashboards
- [ ] Document API usage

---

**Previous**: [Storage & Indexing Infrastructure](./STORAGE_INDEXING_INFRASTRUCTURE.md)  
**Next**: Production Deployment

