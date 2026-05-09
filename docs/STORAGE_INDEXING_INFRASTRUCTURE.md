# Storage & Indexing Infrastructure

**Status**: 🔴 Not Started  
**Priority**: Critical - Data persistence layer  
**Timeline**: 2-3 weeks

---

## 📋 Overview

Deploy and configure specialized storage systems for vector search (Weaviate), graph relationships (Neo4j), time-series telemetry (TimescaleDB), object storage (MinIO), and relational data (PostgreSQL).

---

## 🎯 Objectives

1. Deploy Weaviate cluster for vector similarity search
2. Setup Neo4j for knowledge graph relationships
3. Configure TimescaleDB for high-cardinality telemetry
4. Provision MinIO for object storage (PDFs, large datasets)
5. Optimize Postgres for catalog and normalized data
6. Implement backup, replication, and monitoring

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│          (FastAPI, Alba, Albi, Jona, ASI)                   │
└──────────┬──────────────┬──────────────┬────────────────┬───┘
           │              │              │                │
           ▼              ▼              ▼                ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ Weaviate │   │  Neo4j   │   │Timescale │   │  MinIO   │
    │ (Vector) │   │ (Graph)  │   │  (Time)  │   │ (Object) │
    └──────────┘   └──────────┘   └──────────┘   └──────────┘
           │              │              │                │
           └──────────────┴──────────────┴────────────────┘
                         │
                         ▼
                  ┌──────────┐
                  │Postgres  │
                  │(Catalog) │
                  └──────────┘
```

---

## 🔍 Component 1: Weaviate (Vector Store)

### **Purpose**
- Store embeddings for scientific documents, clinical data, policy docs
- Semantic search across literature
- Similarity-based retrieval

### **Docker Compose Configuration**

**File**: `docker-compose.weaviate.yml`

```yaml
version: '3.8'

services:
  weaviate:
    image: cr.weaviate.io/semitechnologies/weaviate:1.23.0
    ports:
      - "8080:8080"
      - "50051:50051"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'false'
      AUTHENTICATION_APIKEY_ENABLED: 'true'
      AUTHENTICATION_APIKEY_ALLOWED_KEYS: '${WEAVIATE_API_KEY}'
      AUTHENTICATION_APIKEY_USERS: 'alba-agent,albi-agent,jona-engine,asi-core'
      AUTHORIZATION_ADMINLIST_ENABLED: 'true'
      AUTHORIZATION_ADMINLIST_USERS: 'asi-core'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'none'  # We provide embeddings
      ENABLE_MODULES: 'text2vec-transformers,generative-openai'
      CLUSTER_HOSTNAME: 'weaviate-node1'
      BACKUP_S3_ENDPOINT: 'minio:9000'
      BACKUP_S3_BUCKET: 'weaviate-backups'
      BACKUP_S3_ACCESS_KEY_ID: '${MINIO_ACCESS_KEY}'
      BACKUP_S3_SECRET_ACCESS_KEY: '${MINIO_SECRET_KEY}'
      BACKUP_S3_USE_SSL: 'false'
    volumes:
      - weaviate-data:/var/lib/weaviate
    restart: unless-stopped

volumes:
  weaviate-data:
```

### **Schema Definition**

**File**: `services/knowledge-api/schemas/weaviate_schema.py`

```python
import weaviate

def create_weaviate_schema(client: weaviate.Client):
    """Create Weaviate classes for knowledge storage"""
    
    # Scientific Documents
    scientific_class = {
        "class": "ScientificDocument",
        "description": "Scientific literature from OpenAlex, ArXiv, Semantic Scholar",
        "vectorizer": "none",  # Pre-computed embeddings
        "properties": [
            {
                "name": "document_id",
                "dataType": ["string"],
                "description": "Unique identifier from source",
                "indexInverted": True
            },
            {
                "name": "title",
                "dataType": ["text"],
                "description": "Document title",
                "indexInverted": True
            },
            {
                "name": "abstract",
                "dataType": ["text"],
                "description": "Document abstract or summary"
            },
            {
                "name": "publication_date",
                "dataType": ["date"],
                "description": "Publication date"
            },
            {
                "name": "source",
                "dataType": ["string"],
                "description": "Source platform (openalex, arxiv, etc.)"
            },
            {
                "name": "domain",
                "dataType": ["string"],
                "description": "Scientific domain"
            },
            {
                "name": "authors",
                "dataType": ["string[]"],
                "description": "List of author names"
            },
            {
                "name": "doi",
                "dataType": ["string"],
                "description": "Digital Object Identifier",
                "indexInverted": True
            },
            {
                "name": "cited_by_count",
                "dataType": ["int"],
                "description": "Citation count"
            },
            {
                "name": "metadata",
                "dataType": ["object"],
                "description": "Additional metadata (JSON)"
            }
        ]
    }
    
    # Clinical Documents
    clinical_class = {
        "class": "ClinicalDocument",
        "description": "Clinical trials, drug data, medical research",
        "vectorizer": "none",
        "properties": [
            {
                "name": "nct_id",
                "dataType": ["string"],
                "description": "ClinicalTrials.gov NCT ID"
            },
            {
                "name": "title",
                "dataType": ["text"]
            },
            {
                "name": "brief_summary",
                "dataType": ["text"]
            },
            {
                "name": "condition",
                "dataType": ["string[]"]
            },
            {
                "name": "intervention",
                "dataType": ["string[]"]
            },
            {
                "name": "phase",
                "dataType": ["string"]
            },
            {
                "name": "status",
                "dataType": ["string"]
            },
            {
                "name": "start_date",
                "dataType": ["date"]
            }
        ]
    }
    
    # Policy Documents
    policy_class = {
        "class": "PolicyDocument",
        "description": "WHO, government, regulatory documents",
        "vectorizer": "none",
        "properties": [
            {
                "name": "document_id",
                "dataType": ["string"]
            },
            {
                "name": "title",
                "dataType": ["text"]
            },
            {
                "name": "content",
                "dataType": ["text"]
            },
            {
                "name": "organization",
                "dataType": ["string"]
            },
            {
                "name": "country",
                "dataType": ["string"]
            },
            {
                "name": "policy_type",
                "dataType": ["string"]
            },
            {
                "name": "effective_date",
                "dataType": ["date"]
            }
        ]
    }
    
    # Create classes
    for class_obj in [scientific_class, clinical_class, policy_class]:
        if not client.schema.exists(class_obj["class"]):
            client.schema.create_class(class_obj)
            print(f"✅ Created class: {class_obj['class']}")

# Initialize
if __name__ == "__main__":
    client = weaviate.Client(
        url="http://localhost:8080",
        auth_client_secret=weaviate.AuthApiKey(api_key="your-api-key")
    )
    create_weaviate_schema(client)
```

---

## 🌐 Component 2: Neo4j (Graph Store)

### **Purpose**
- Store knowledge graph relationships
- Citation networks
- Drug-disease-gene mappings
- Concept ontologies

### **Docker Compose Configuration**

**File**: `docker-compose.neo4j.yml`

```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.15-enterprise
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_ACCEPT_LICENSE_AGREEMENT: 'yes'
      NEO4J_server_memory_heap_initial__size: '2G'
      NEO4J_server_memory_heap_max__size: '4G'
      NEO4J_server_memory_pagecache_size: '2G'
      NEO4J_dbms_security_procedures_unrestricted: 'apoc.*,gds.*'
      NEO4J_dbms_security_procedures_allowlist: 'apoc.*,gds.*'
      NEO4JLABS_PLUGINS: '["apoc", "graph-data-science"]'
    volumes:
      - neo4j-data:/data
      - neo4j-logs:/logs
      - neo4j-import:/var/lib/neo4j/import
      - neo4j-plugins:/plugins
    restart: unless-stopped

volumes:
  neo4j-data:
  neo4j-logs:
  neo4j-import:
  neo4j-plugins:
```

### **Graph Schema (Cypher)**

**File**: `services/knowledge-api/schemas/neo4j_schema.cypher`

```cypher
// Create constraints
CREATE CONSTRAINT publication_id IF NOT EXISTS FOR (p:Publication) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT drug_id IF NOT EXISTS FOR (d:Drug) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT gene_id IF NOT EXISTS FOR (g:Gene) REQUIRE g.id IS UNIQUE;
CREATE CONSTRAINT trial_id IF NOT EXISTS FOR (t:Trial) REQUIRE t.nct_id IS UNIQUE;
CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT telemetry_node_id IF NOT EXISTS FOR (tn:TelemetryNode) REQUIRE tn.id IS UNIQUE;

// Create indexes
CREATE INDEX publication_doi IF NOT EXISTS FOR (p:Publication) ON (p.doi);
CREATE INDEX publication_date IF NOT EXISTS FOR (p:Publication) ON (p.publication_date);
CREATE INDEX drug_name IF NOT EXISTS FOR (d:Drug) ON (d.name);
CREATE INDEX gene_symbol IF NOT EXISTS FOR (g:Gene) ON (g.symbol);
CREATE INDEX trial_status IF NOT EXISTS FOR (t:Trial) ON (t.status);

// Node labels:
// - Publication (scientific papers)
// - Drug (pharmaceutical compounds)
// - Gene (genomic data)
// - Trial (clinical trials)
// - Concept (knowledge concepts)
// - TelemetryNode (IoT/industrial sensors)
// - Author (paper authors)
// - Institution (research orgs)

// Relationship types:
// - CITES (Publication → Publication)
// - TREATS (Drug → Disease)
// - EXPRESSES (Gene → Protein)
// - MEASURES (TelemetryNode → Metric)
// - AUTHORED_BY (Publication → Author)
// - AFFILIATED_WITH (Author → Institution)
// - RELATED_TO (Concept → Concept)
// - INTERVENES_IN (Drug → Trial)
```

---

## ⏱️ Component 3: TimescaleDB (Time-Series)

### **Purpose**
- Industrial telemetry storage
- IoT sensor data
- High-cardinality metrics
- Continuous aggregates

### **Docker Compose Configuration**

**File**: `docker-compose.timescale.yml`

```yaml
version: '3.8'

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg16
    ports:
      - "5433:5432"
    environment:
      POSTGRES_PASSWORD: ${TIMESCALE_PASSWORD}
      POSTGRES_DB: telemetry
    volumes:
      - timescale-data:/var/lib/postgresql/data
    command: postgres -c shared_preload_libraries=timescaledb -c max_connections=200
    restart: unless-stopped

volumes:
  timescale-data:
```

### **Schema Definition**

**File**: `db/timescale_schema.sql`

```sql
-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Telemetry table
CREATE TABLE telemetry_raw (
    time TIMESTAMPTZ NOT NULL,
    source VARCHAR(50) NOT NULL,        -- 'fiware', 'opcua', 'openplc'
    node_id VARCHAR(255) NOT NULL,      -- Sensor/device identifier
    metric VARCHAR(100) NOT NULL,       -- Metric name
    value DOUBLE PRECISION,
    unit VARCHAR(50),
    quality INT,                        -- Data quality indicator (0-100)
    metadata JSONB
);

-- Convert to hypertable (time-series optimization)
SELECT create_hypertable('telemetry_raw', 'time', chunk_time_interval => INTERVAL '1 day');

-- Create indexes
CREATE INDEX idx_telemetry_source_node ON telemetry_raw (source, node_id, time DESC);
CREATE INDEX idx_telemetry_metric ON telemetry_raw (metric, time DESC);
CREATE INDEX idx_telemetry_metadata ON telemetry_raw USING GIN (metadata);

-- Continuous aggregate: hourly averages
CREATE MATERIALIZED VIEW telemetry_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    source,
    node_id,
    metric,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    STDDEV(value) AS stddev_value,
    COUNT(*) AS sample_count
FROM telemetry_raw
GROUP BY bucket, source, node_id, metric;

-- Continuous aggregate: daily summaries
CREATE MATERIALIZED VIEW telemetry_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    source,
    node_id,
    metric,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    COUNT(*) AS sample_count
FROM telemetry_raw
GROUP BY bucket, source, node_id, metric;

-- Retention policy: keep raw data for 90 days
SELECT add_retention_policy('telemetry_raw', INTERVAL '90 days');

-- Compression policy: compress data older than 7 days
ALTER TABLE telemetry_raw SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'source,node_id,metric'
);

SELECT add_compression_policy('telemetry_raw', INTERVAL '7 days');

-- Refresh policies for continuous aggregates
SELECT add_continuous_aggregate_policy('telemetry_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

SELECT add_continuous_aggregate_policy('telemetry_daily',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');
```

---

## 📦 Component 4: MinIO (Object Storage)

### **Purpose**
- Store PDFs, large datasets
- Raw data dumps
- Backup storage
- S3-compatible API

### **Docker Compose Configuration**

**File**: `docker-compose.minio.yml`

```yaml
version: '3.8'

services:
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    volumes:
      - minio-data:/data
    command: server /data --console-address ":9001"
    restart: unless-stopped

  minio-createbuckets:
    image: minio/mc:latest
    depends_on:
      - minio
    entrypoint: >
      /bin/sh -c "
      sleep 5;
      /usr/bin/mc alias set myminio http://minio:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD};
      /usr/bin/mc mb myminio/knowledge-raw --ignore-existing;
      /usr/bin/mc mb myminio/knowledge-processed --ignore-existing;
      /usr/bin/mc mb myminio/weaviate-backups --ignore-existing;
      /usr/bin/mc mb myminio/neo4j-backups --ignore-existing;
      /usr/bin/mc policy set download myminio/knowledge-raw;
      exit 0;
      "

volumes:
  minio-data:
```

### **Bucket Structure**
```
knowledge-raw/
├── openalex/
│   ├── works/
│   │   └── 2025-12-13.json
│   └── concepts/
├── arxiv/
│   └── papers/
│       └── 2025-12/
│           └── 1234.5678.pdf
├── pubmed/
│   └── articles/
└── fiware/
    └── telemetry/

knowledge-processed/
├── openalex/
│   └── works/
│       └── 2025-12-13.parquet
└── embeddings/
    └── scientific/
        └── batch_001.npy

weaviate-backups/
└── 2025-12-13_daily/

neo4j-backups/
└── 2025-12-13_daily/
```

---

## 🗄️ Component 5: PostgreSQL (Catalog & RDBMS)

### **Purpose**
- Knowledge source catalog
- Clinical trial structured data
- Pharmaceutical data
- User management

### **Optimization**

**File**: `db/postgresql.conf` (custom config)

```ini
# Memory
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
work_mem = 64MB

# Parallelism
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8

# Checkpoints
checkpoint_completion_target = 0.9
wal_buffers = 16MB
min_wal_size = 1GB
max_wal_size = 4GB

# Query planner
random_page_cost = 1.1  # SSD optimized
effective_io_concurrency = 200

# Logging
log_statement = 'mod'
log_duration = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0
```

---

## 📊 Monitoring & Backup

### **Prometheus Exporters**

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter
    environment:
      DATA_SOURCE_NAME: "postgresql://user:password@postgres:5432/kloud?sslmode=disable"
    ports:
      - "9187:9187"

  neo4j-exporter:
    image: neo4j/neo4j-prometheus-exporter:latest
    environment:
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: ${NEO4J_PASSWORD}
    ports:
      - "9188:9188"
```

### **Backup Script**

**File**: `scripts/backup-all-stores.sh`

```bash
#!/bin/bash
set -e

BACKUP_DIR="/backups/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

# Weaviate backup
echo "Backing up Weaviate..."
curl -X POST http://localhost:8080/v1/backups/s3 \
  -H "Content-Type: application/json" \
  -d '{"id":"weaviate-backup-'$(date +%Y%m%d)'"}'

# Neo4j backup
echo "Backing up Neo4j..."
docker exec neo4j neo4j-admin database dump neo4j \
  --to-path=/backups --overwrite-destination=true

# TimescaleDB backup
echo "Backing up TimescaleDB..."
docker exec timescaledb pg_dump -U postgres telemetry \
  | gzip > "$BACKUP_DIR/timescale.sql.gz"

# PostgreSQL backup
echo "Backing up PostgreSQL..."
docker exec postgres pg_dump -U postgres kloud \
  | gzip > "$BACKUP_DIR/postgres.sql.gz"

echo "✅ All backups completed: $BACKUP_DIR"
```

---

## ✅ Implementation Checklist

### Phase 1: Weaviate (Week 1)
- [ ] Deploy Weaviate container
- [ ] Create schema (classes + properties)
- [ ] Configure authentication
- [ ] Test vector ingestion
- [ ] Setup backup to MinIO

### Phase 2: Neo4j (Week 1)
- [ ] Deploy Neo4j container
- [ ] Apply graph schema (constraints, indexes)
- [ ] Install APOC + GDS plugins
- [ ] Test cypher queries
- [ ] Configure backups

### Phase 3: TimescaleDB (Week 2)
- [ ] Deploy TimescaleDB container
- [ ] Create hypertables
- [ ] Setup continuous aggregates
- [ ] Configure retention + compression
- [ ] Test write performance

### Phase 4: MinIO (Week 2)
- [ ] Deploy MinIO container
- [ ] Create buckets
- [ ] Configure access policies
- [ ] Test S3 API compatibility
- [ ] Setup lifecycle rules

### Phase 5: Integration (Week 3)
- [ ] Connect all stores to FastAPI
- [ ] Implement cross-store queries
- [ ] Setup monitoring exporters
- [ ] Automate backups
- [ ] Load test infrastructure

---

**Previous**: [Ingestion Pipeline Architecture](./INGESTION_PIPELINE_ARCHITECTURE.md)  
**Next**: [API Fabric Implementation](./API_FABRIC_IMPLEMENTATION.md)

