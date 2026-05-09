# Catalog & Governance Setup

**Status**: 🔴 Not Started  
**Priority**: Critical - Foundation for all data ingestion  
**Timeline**: 2-3 weeks

---

## 📋 Overview

Establish master catalog system for tracking and managing all external data sources (scientific, biomedical, industrial, environmental) with governance policies and automated validation.

---

## 🎯 Objectives

1. Create central database schema for knowledge source catalog
2. Seed catalog with 32+ approved open data sources
3. Implement automated validation and monitoring
4. Setup access key management and rotation
5. Enable schema drift detection

---

## 🏗️ Architecture

### **Database Schema**

**Table: `knowledge_sources`**
```sql
CREATE TABLE knowledge_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,  -- 'scientific', 'biomedical', 'industrial', 'environmental'
    license VARCHAR(100) NOT NULL,   -- 'CC BY', 'CC0', 'Public', 'Apache 2.0', etc.
    access_model VARCHAR(50) NOT NULL, -- 'REST', 'MQTT', 'WebSocket', 'Download', 'OPC UA'
    base_url TEXT,
    api_key_ref VARCHAR(255),        -- Reference to secrets manager
    ingest_type VARCHAR(50) NOT NULL, -- 'batch', 'streaming', 'manual'
    refresh_interval INTERVAL,       -- e.g., '1 day', '1 hour', '7 days'
    target_store VARCHAR(100) NOT NULL, -- 'Weaviate', 'Neo4j', 'Postgres', 'TimescaleDB', 'MinIO'
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'paused', 'deprecated', 'error'
    last_validated_at TIMESTAMP,
    last_ingestion_at TIMESTAMP,
    schema_version VARCHAR(50),
    metadata JSONB,                  -- Flexible field for source-specific config
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_knowledge_sources_category ON knowledge_sources(category);
CREATE INDEX idx_knowledge_sources_status ON knowledge_sources(status);
CREATE INDEX idx_knowledge_sources_ingest_type ON knowledge_sources(ingest_type);
```

**Table: `catalog_validation_log`**
```sql
CREATE TABLE catalog_validation_log (
    id BIGSERIAL PRIMARY KEY,
    source_id UUID REFERENCES knowledge_sources(id),
    validation_type VARCHAR(50), -- 'api_key', 'schema', 'connectivity', 'quota'
    status VARCHAR(50),          -- 'success', 'warning', 'error'
    message TEXT,
    metadata JSONB,
    validated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_validation_log_source ON catalog_validation_log(source_id);
CREATE INDEX idx_validation_log_status ON catalog_validation_log(status);
```

---

## 📊 Data Sources to Seed

### **Scientific Literature (7 sources)**
- OpenAlex
- Semantic Scholar
- ArXiv
- PubMed / PubMed Central
- ClinicalTrials.gov
- CrossRef
- WHO IRIS

### **Pharmaceutical & Biomedical (6 sources)**
- OpenFDA
- WHO ATC/DDD
- DrugBank (open subset)
- EMA Open Data
- NIH Gene
- Ensembl

### **Structural Biology & Neuroscience (3 sources)**
- PDB (Protein Data Bank)
- Allen Brain Atlas
- Human Cell Atlas

### **Industrial Telemetry & IoT (4 sources)**
- FIWARE Context Broker
- Eclipse Ditto
- OPC UA Historians
- OpenPLC Logs

### **Environmental & Economic (2 sources)**
- NOAA Climate Data
- World Bank Data

---

## 🔄 Airflow DAG: `catalog_sync`

**Purpose**: Weekly validation of all catalog entries

**File**: `airflow/dags/catalog_sync.py`

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import requests

default_args = {
    'owner': 'asi-core',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'email': ['ops@kloud.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'catalog_sync',
    default_args=default_args,
    description='Weekly validation of knowledge source catalog',
    schedule_interval='0 2 * * 0',  # Every Sunday at 2 AM UTC
    catchup=False,
    tags=['catalog', 'governance', 'validation']
)

def fetch_active_sources(**context):
    """Retrieve all active knowledge sources from catalog"""
    pg_hook = PostgresHook(postgres_conn_id='kloud_db')
    query = """
        SELECT id, name, access_model, base_url, api_key_ref, schema_version
        FROM knowledge_sources
        WHERE status = 'active'
    """
    records = pg_hook.get_records(query)
    context['ti'].xcom_push(key='sources', value=records)
    return len(records)

def validate_api_connectivity(source_id, name, access_model, base_url, api_key_ref, **context):
    """Test API endpoint connectivity and authentication"""
    pg_hook = PostgresHook(postgres_conn_id='kloud_db')
    
    validation_result = {
        'source_id': source_id,
        'validation_type': 'connectivity',
        'status': 'success',
        'message': None
    }
    
    try:
        if access_model == 'REST':
            # Retrieve API key from secrets manager
            headers = {}
            if api_key_ref:
                # TODO: Integrate with HashiCorp Vault or AWS Secrets Manager
                headers['Authorization'] = f'Bearer {api_key_ref}'
            
            response = requests.get(base_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                validation_result['status'] = 'success'
                validation_result['message'] = f'{name} API is reachable'
            elif response.status_code == 401:
                validation_result['status'] = 'error'
                validation_result['message'] = f'{name} API key invalid or expired'
            else:
                validation_result['status'] = 'warning'
                validation_result['message'] = f'{name} returned status {response.status_code}'
        
        elif access_model in ['MQTT', 'WebSocket', 'OPC UA']:
            # TODO: Implement protocol-specific checks
            validation_result['status'] = 'warning'
            validation_result['message'] = f'{access_model} validation not yet implemented'
    
    except requests.exceptions.RequestException as e:
        validation_result['status'] = 'error'
        validation_result['message'] = f'{name} connectivity error: {str(e)}'
    
    # Log validation result
    pg_hook.run("""
        INSERT INTO catalog_validation_log (source_id, validation_type, status, message)
        VALUES (%(source_id)s, %(validation_type)s, %(status)s, %(message)s)
    """, parameters=validation_result)
    
    # Update last_validated_at timestamp
    pg_hook.run("""
        UPDATE knowledge_sources
        SET last_validated_at = NOW()
        WHERE id = %(source_id)s
    """, parameters={'source_id': source_id})
    
    return validation_result

def check_schema_drift(source_id, name, schema_version, **context):
    """Detect schema changes in external APIs"""
    # TODO: Implement schema comparison logic
    # - Fetch current API response structure
    # - Compare with stored schema_version
    # - Alert if breaking changes detected
    pass

def generate_validation_report(**context):
    """Generate weekly validation report"""
    pg_hook = PostgresHook(postgres_conn_id='kloud_db')
    
    # Summary query
    summary = pg_hook.get_first("""
        SELECT 
            COUNT(*) FILTER (WHERE status = 'success') as success_count,
            COUNT(*) FILTER (WHERE status = 'warning') as warning_count,
            COUNT(*) FILTER (WHERE status = 'error') as error_count
        FROM catalog_validation_log
        WHERE validated_at >= NOW() - INTERVAL '7 days'
    """)
    
    print(f"Validation Summary:")
    print(f"  ✅ Success: {summary[0]}")
    print(f"  ⚠️  Warning: {summary[1]}")
    print(f"  ❌ Error: {summary[2]}")
    
    # TODO: Send report via email or Slack
    return summary

# Define tasks
fetch_sources = PythonOperator(
    task_id='fetch_active_sources',
    python_callable=fetch_active_sources,
    dag=dag
)

# Dynamic task generation would go here for each source
# For now, simplified version

generate_report = PythonOperator(
    task_id='generate_validation_report',
    python_callable=generate_validation_report,
    dag=dag
)

fetch_sources >> generate_report
```

---

## 🔐 Secrets Management

**Strategy**: Use HashiCorp Vault or AWS Secrets Manager

**Key Naming Convention**:
```
knowledge-sources/{source_name}/api-key
knowledge-sources/{source_name}/credentials
```

**Access Control**:
- Airflow service account: Read-only
- Admin users: Read/Write
- Audit logging enabled

---

## 📈 Monitoring & Alerting

**Prometheus Metrics**:
```
catalog_validation_success_total
catalog_validation_error_total
catalog_source_last_validated_seconds
catalog_ingestion_lag_seconds
```

**Grafana Dashboard**: "Knowledge Catalog Health"

**Alerts**:
- API key expiration within 7 days
- Validation failures > 3 consecutive runs
- Schema drift detected
- Ingestion lag > 24 hours

---

## ✅ Implementation Checklist

### Phase 1: Database Setup (Week 1)
- [ ] Create `knowledge_sources` table in production Postgres
- [ ] Create `catalog_validation_log` table
- [ ] Setup indexes and constraints
- [ ] Configure automated backups

### Phase 2: Seed Data (Week 1-2)
- [ ] Collect API documentation for all 32 sources
- [ ] Obtain and test API keys where required
- [ ] Store API keys in secrets manager
- [ ] Insert all sources into catalog with initial metadata

### Phase 3: Airflow DAG (Week 2)
- [ ] Develop `catalog_sync` DAG
- [ ] Implement connectivity validation
- [ ] Setup schema drift detection
- [ ] Configure email/Slack notifications

### Phase 4: Monitoring (Week 2-3)
- [ ] Create Prometheus exporters
- [ ] Build Grafana dashboard
- [ ] Configure alerting rules
- [ ] Document runbook for common issues

### Phase 5: Documentation (Week 3)
- [ ] API documentation for `/catalog/sources` endpoint
- [ ] Runbook for adding new sources
- [ ] License compliance guide
- [ ] Onboarding docs for data engineers

---

## 🔗 Dependencies

**Required Infrastructure**:
- ✅ PostgreSQL 16+ (already deployed)
- 🔴 Apache Airflow (needs setup)
- 🔴 HashiCorp Vault or AWS Secrets Manager
- ✅ Prometheus + Grafana (already deployed)

**Required Permissions**:
- Admin access to each external API
- Database schema creation privileges
- Secrets manager write access

---

## 📚 References

- [Global Open Data API Plan](./global-open-data-api-plan.md)
- [Apache Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [PostgreSQL JSONB Performance](https://www.postgresql.org/docs/current/datatype-json.html)
- License compliance: [Creative Commons](https://creativecommons.org/licenses/), [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)

---

**Next Step**: [Ingestion Pipeline Architecture](./INGESTION_PIPELINE_ARCHITECTURE.md)

