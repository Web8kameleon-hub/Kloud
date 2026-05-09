from datetime import datetime, timedelta
import os
import json
import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY", "changeme")
OPENALEX_BASE = os.getenv("OPENALEX_BASE", "https://api.openalex.org")


def fetch_openalex(**context):
    query = "machine learning"
    response = requests.get(f"{OPENALEX_BASE}/works", params={"search": query, "per_page": 25}, timeout=30)
    response.raise_for_status()
    return response.json()


def upsert_weaviate(**context):
    data = context["ti"].xcom_pull(task_ids="fetch_openalex")
    objects = []
    for item in data.get("results", []):
        abstract = item.get("abstract", "")
        if not abstract and item.get("abstract_inverted_index"):
            abstract = " ".join(item["abstract_inverted_index"].keys())
        obj = {
            "class": "Paper",
            "properties": {
                "title": item.get("title"),
                "abstract": abstract,
                "authors": [a["author"]["display_name"] for a in item.get("authorships", [])],
                "year": item.get("publication_year") or 0,
                "source": "openalex",
                "doi": item.get("doi", "") or ""
            }
        }
        objects.append(obj)

    if not objects:
        return

    response = requests.post(
        f"{WEAVIATE_URL}/v1/batch/objects",
        headers={"X-API-KEY": WEAVIATE_API_KEY, "Content-Type": "application/json"},
        data=json.dumps({"objects": objects}),
        timeout=30,
    )
    response.raise_for_status()


default_args = {
    "owner": "Kloud",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="openalex_ingest",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    default_args=default_args,
    catchup=False,
) as dag:
    fetch_task = PythonOperator(task_id="fetch_openalex", python_callable=fetch_openalex)
    upsert_task = PythonOperator(task_id="upsert_weaviate", python_callable=upsert_weaviate)

    fetch_task >> upsert_task


