# Ingestion Pipeline Architecture

**Status**: 🔴 Not Started  
**Priority**: Critical - Data flow foundation  
**Timeline**: 3-4 weeks

---

## 📋 Overview

Build scalable data ingestion pipelines for batch (scientific literature, biomedical data) and streaming (industrial telemetry, IoT) sources with transformation, quality checks, and embedding generation.

---

## 🎯 Objectives

1. Ingest 32+ external data sources reliably
2. Process batch data (literature) via Apache Airflow
3. Stream real-time telemetry via Apache Kafka
4. Transform and harmonize schemas with dbt/Dagster
5. Generate embeddings for vector search
6. Ensure data quality and freshness

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                     │
├──────────────┬────────────────┬──────────────┬──────────────┤
│  Scientific  │  Biomedical    │  Industrial  │  Economic    │
│  (OpenAlex,  │  (OpenFDA,     │  (FIWARE,    │  (World Bank,│
│   ArXiv)     │   PubMed)      │   OPC UA)    │   NOAA)      │
└──────┬───────┴────────┬───────┴──────┬───────┴──────┬───────┘
       │                │              │              │
       ▼                ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Airflow    │ │   Airflow    │ │    Kafka     │ │   Airflow    │
│   DAGs       │ │   DAGs       │ │  Connectors  │ │   DAGs       │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │              │              │
       └────────────────┴──────────────┴──────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Raw Data Storage   │
              │  (MinIO: s3://       │
              │   knowledge-raw/)    │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Transformation      │
              │  Layer (dbt/Dagster) │
              │  - Schema Harmonize  │
              │  - Quality Checks    │
              │  - Parquet Export    │
              └──────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌───────────────┐ ┌─────────────┐ ┌──────────────┐
│  Embedding    │ │   Kafka     │ │  Target      │
│  Services     │ │   Streams   │ │  Stores      │
│  (SciBERT,    │ │   /Flink    │ │  (Weaviate,  │
│   Ray)        │ │             │ │   Neo4j,     │
│               │ │             │ │   TimescaleDB│
└───────┬───────┘ └──────┬──────┘ └──────┬───────┘
        │                │               │
        └────────────────┴───────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Final Storage      │
              │   - Weaviate Vector  │
              │   - Neo4j Graph      │
              │   - TimescaleDB TS   │
              │   - Postgres RDBMS   │
              └──────────────────────┘
```

---

## 📦 Component 1: Batch Ingestion (Airflow)

### **Use Cases**
- Scientific literature (OpenAlex, ArXiv, PubMed)
- Pharmaceutical data (OpenFDA, DrugBank)
- Static datasets (World Bank, NOAA)

### **Apache Airflow Setup**

**Docker Compose** (`docker-compose.airflow.yml`):
```yaml
version: '3.8'

services:
  airflow-postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: ${AIRFLOW_DB_PASSWORD}
      POSTGRES_DB: airflow
    volumes:
      - airflow-postgres-data:/var/lib/postgresql/data

  airflow-redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  airflow-webserver:
    image: apache/airflow:2.8.0-python3.11
    depends_on:
      - airflow-postgres
      - airflow-redis
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:${AIRFLOW_DB_PASSWORD}@airflow-postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://airflow-redis:6379/0
      AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:${AIRFLOW_DB_PASSWORD}@airflow-postgres/airflow
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/plugins:/opt/airflow/plugins
      - ./airflow/logs:/opt/airflow/logs
    ports:
      - "8080:8080"
    command: webserver

  airflow-scheduler:
    image: apache/airflow:2.8.0-python3.11
    depends_on:
      - airflow-postgres
      - airflow-redis
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:${AIRFLOW_DB_PASSWORD}@airflow-postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://airflow-redis:6379/0
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/plugins:/opt/airflow/plugins
      - ./airflow/logs:/opt/airflow/logs
    command: scheduler

  airflow-worker:
    image: apache/airflow:2.8.0-python3.11
    depends_on:
      - airflow-postgres
      - airflow-redis
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:${AIRFLOW_DB_PASSWORD}@airflow-postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://airflow-redis:6379/0
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/plugins:/opt/airflow/plugins
      - ./airflow/logs:/opt/airflow/logs
    command: celery worker

volumes:
  airflow-postgres-data:
```

### **Example DAG: OpenAlex Ingestion**

**File**: `airflow/dags/openalex_daily_sync.py`

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime, timedelta
import requests
import json

default_args = {
    'owner': 'alba-agent',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'email': ['data-eng@kloud.com'],
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'openalex_daily_sync',
    default_args=default_args,
    description='Daily sync of OpenAlex works and concepts',
    schedule_interval='0 3 * * *',  # Daily at 3 AM UTC
    catchup=False,
    tags=['scientific', 'literature', 'openalex']
)

def fetch_openalex_works(**context):
    """Fetch new works from OpenAlex API"""
    base_url = "https://api.openalex.org/works"
    
    # Fetch works from last 24 hours
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    params = {
        'filter': f'from_publication_date:{yesterday}',
        'per-page': 200,
        'mailto': 'api@kloud.com'  # OpenAlex polite pool
    }
    
    works = []
    page = 1
    
    while True:
        params['page'] = page
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = data.get('results', [])
        
        if not results:
            break
        
        works.extend(results)
        page += 1
        
        # Rate limiting
        if page > 10:  # Limit to 2000 works per run
            break
    
    # Store raw JSON to MinIO
    s3_hook = S3Hook(aws_conn_id='minio_conn')
    key = f"knowledge-raw/openalex/works/{yesterday}.json"
    s3_hook.load_string(
        string_data=json.dumps(works),
        key=key,
        bucket_name='knowledge-raw',
        replace=True
    )
    
    context['ti'].xcom_push(key='works_count', value=len(works))
    context['ti'].xcom_push(key='s3_key', value=key)
    
    return len(works)

def transform_to_parquet(**context):
    """Convert JSON to Parquet for analytics"""
    import pandas as pd
    from pyarrow import parquet as pq
    
    ti = context['ti']
    s3_key = ti.xcom_pull(key='s3_key', task_ids='fetch_openalex_works')
    
    # Load from MinIO
    s3_hook = S3Hook(aws_conn_id='minio_conn')
    json_data = s3_hook.read_key(key=s3_key, bucket_name='knowledge-raw')
    works = json.loads(json_data)
    
    # Flatten to DataFrame
    df = pd.json_normalize(works)
    
    # Write Parquet
    parquet_key = s3_key.replace('.json', '.parquet')
    parquet_buffer = df.to_parquet()
    
    s3_hook.load_bytes(
        bytes_data=parquet_buffer,
        key=parquet_key,
        bucket_name='knowledge-processed',
        replace=True
    )
    
    return parquet_key

def generate_embeddings(**context):
    """Generate embeddings for vector search"""
    # This would call embedding service (see Component 4)
    # For now, placeholder
    pass

# Define tasks
fetch_task = PythonOperator(
    task_id='fetch_openalex_works',
    python_callable=fetch_openalex_works,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_to_parquet',
    python_callable=transform_to_parquet,
    dag=dag
)

embed_task = PythonOperator(
    task_id='generate_embeddings',
    python_callable=generate_embeddings,
    dag=dag
)

fetch_task >> transform_task >> embed_task
```

---

## 🌊 Component 2: Streaming Ingestion (Kafka)

### **Use Cases**
- Industrial telemetry (FIWARE, OPC UA)
- IoT sensor data (Eclipse Ditto)
- Real-time control signals (OpenPLC)

### **Kafka Setup**

**Docker Compose** (`docker-compose.kafka.yml`):
```yaml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    volumes:
      - zookeeper-data:/var/lib/zookeeper/data
      - zookeeper-logs:/var/lib/zookeeper/log

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    volumes:
      - kafka-data:/var/lib/kafka/data

  kafka-connect:
    image: confluentinc/cp-kafka-connect:7.5.0
    depends_on:
      - kafka
    ports:
      - "8083:8083"
    environment:
      CONNECT_BOOTSTRAP_SERVERS: kafka:9092
      CONNECT_REST_PORT: 8083
      CONNECT_GROUP_ID: kloud-connect
      CONNECT_CONFIG_STORAGE_TOPIC: connect-configs
      CONNECT_OFFSET_STORAGE_TOPIC: connect-offsets
      CONNECT_STATUS_STORAGE_TOPIC: connect-status
      CONNECT_KEY_CONVERTER: org.apache.kafka.connect.json.JsonConverter
      CONNECT_VALUE_CONVERTER: org.apache.kafka.connect.json.JsonConverter
    volumes:
      - ./kafka/connectors:/usr/share/java/kafka-connectors

volumes:
  zookeeper-data:
  zookeeper-logs:
  kafka-data:
```

### **Kafka Topics**
```bash
# Create topics
kafka-topics --create --topic telemetry.fiware.raw --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
kafka-topics --create --topic telemetry.opcua.raw --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
kafka-topics --create --topic telemetry.openplc.raw --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
kafka-topics --create --topic telemetry.processed --bootstrap-server localhost:9092 --partitions 6 --replication-factor 1
```

### **FIWARE Source Connector**

**File**: `kafka/connectors/fiware-source-connector.json`

```json
{
  "name": "fiware-source",
  "config": {
    "connector.class": "org.apache.kafka.connect.http.HttpSourceConnector",
    "tasks.max": "1",
    "http.api.url": "http://fiware-orion:1026/v2/entities",
    "http.request.method": "GET",
    "http.request.headers": "Fiware-Service:kloud",
    "http.timer.interval.ms": "5000",
    "kafka.topic": "telemetry.fiware.raw",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false"
  }
}
```

---

## 🔄 Component 3: Transformation Layer (dbt)

### **dbt Project Structure**
```
dbt_project/
├── models/
│   ├── staging/
│   │   ├── stg_openalex_works.sql
│   │   ├── stg_pubmed_articles.sql
│   │   └── stg_fiware_telemetry.sql
│   ├── intermediate/
│   │   ├── int_normalized_literature.sql
│   │   └── int_telemetry_enriched.sql
│   └── marts/
│       ├── scientific_documents.sql
│       └── telemetry_metrics.sql
├── tests/
│   ├── assert_no_nulls.sql
│   └── assert_freshness.sql
└── dbt_project.yml
```

### **Example Model: Normalized Literature**

**File**: `dbt_project/models/marts/scientific_documents.sql`

```sql
{{
  config(
    materialized='incremental',
    unique_key='document_id',
    indexes=[
      {'columns': ['publication_date']},
      {'columns': ['domain', 'category']}
    ]
  )
}}

WITH openalex_docs AS (
    SELECT
        id AS document_id,
        'openalex' AS source,
        doi,
        title,
        abstract,
        publication_date,
        'scientific' AS domain,
        primary_topic AS category,
        cited_by_count,
        metadata
    FROM {{ ref('stg_openalex_works') }}
    {% if is_incremental() %}
    WHERE ingested_at > (SELECT MAX(ingested_at) FROM {{ this }})
    {% endif %}
),

pubmed_docs AS (
    SELECT
        pmid AS document_id,
        'pubmed' AS source,
        doi,
        article_title AS title,
        abstract,
        pub_date AS publication_date,
        'biomedical' AS domain,
        mesh_terms[1] AS category,
        0 AS cited_by_count,
        metadata
    FROM {{ ref('stg_pubmed_articles') }}
    {% if is_incremental() %}
    WHERE ingested_at > (SELECT MAX(ingested_at) FROM {{ this }})
    {% endif %}
)

SELECT * FROM openalex_docs
UNION ALL
SELECT * FROM pubmed_docs
```

---

## 🤖 Component 4: Embedding Services

### **Architecture**

**Embedding Worker** (Ray Cluster):

**File**: `services/embedding-worker/worker.py`

```python
import ray
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import psycopg2
from pgvector.psycopg2 import register_vector

ray.init(address="auto")

@ray.remote(num_gpus=1)
class EmbeddingWorker:
    def __init__(self, model_name: str = "allenai/scibert_scivocab_uncased"):
        self.model = SentenceTransformer(model_name)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts"""
        return self.model.encode(texts, batch_size=32, show_progress_bar=True).tolist()
    
    def process_document_batch(self, documents: List[Dict]) -> None:
        """Process batch of documents and store in Weaviate"""
        texts = [f"{doc['title']} {doc['abstract']}" for doc in documents]
        embeddings = self.generate_embeddings(texts)
        
        # Store in Weaviate
        import weaviate
        client = weaviate.Client("http://weaviate:8080")
        
        for doc, embedding in zip(documents, embeddings):
            client.data_object.create(
                data_object={
                    "document_id": doc['document_id'],
                    "title": doc['title'],
                    "abstract": doc['abstract'],
                    "source": doc['source'],
                    "domain": doc['domain']
                },
                class_name="ScientificDocument",
                vector=embedding
            )

# Deploy workers
workers = [EmbeddingWorker.remote() for _ in range(4)]

# Example usage
def embed_batch(documents: List[Dict]):
    futures = [worker.process_document_batch.remote(documents) for worker in workers]
    ray.get(futures)
```

---

## ✅ Implementation Checklist

### Phase 1: Infrastructure (Week 1)
- [ ] Deploy Apache Airflow (webserver, scheduler, workers)
- [ ] Deploy Kafka cluster (Zookeeper, brokers, Connect)
- [ ] Setup MinIO buckets (`knowledge-raw`, `knowledge-processed`)
- [ ] Configure network and security groups

### Phase 2: Batch Pipelines (Week 2)
- [ ] Develop Airflow DAGs for top 5 sources (OpenAlex, ArXiv, PubMed, OpenFDA, World Bank)
- [ ] Test end-to-end ingestion flow
- [ ] Setup monitoring and alerting

### Phase 3: Streaming Pipelines (Week 3)
- [ ] Deploy Kafka connectors (FIWARE, OPC UA)
- [ ] Implement stream processing logic
- [ ] Write to TimescaleDB

### Phase 4: Transformation (Week 3-4)
- [ ] Setup dbt project
- [ ] Develop staging and mart models
- [ ] Run data quality tests
- [ ] Schedule dbt runs

### Phase 5: Embeddings (Week 4)
- [ ] Deploy Ray cluster
- [ ] Train/fine-tune embedding models
- [ ] Integrate with Weaviate
- [ ] Optimize batch processing

---

**Previous**: [Catalog & Governance Setup](./CATALOG_GOVERNANCE_SETUP.md)  
**Next**: [Storage & Indexing Infrastructure](./STORAGE_INDEXING_INFRASTRUCTURE.md)

