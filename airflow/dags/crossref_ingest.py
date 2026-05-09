from datetime import datetime, timedelta
import os
import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from weaviate import Client as WeaviateClient

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
CROSSREF_URL = "https://api.crossref.org/works"

DEFAULT_ARGS = {
    "owner": "Kloud",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def ensure_class():
    client = WeaviateClient(WEAVIATE_URL)
    schema = client.schema.get()
    classes = schema.get("classes", []) if schema else []
    if not any(cls.get("class") == "Paper" for cls in classes):
        client.schema.create_class(
            {
                "class": "Paper",
                "vectorizer": "text2vec-transformers",
                "moduleConfig": {
                    "text2vec-transformers": {"poolingStrategy": "masked_mean"}
                },
                "properties": [
                    {"name": "title", "dataType": ["text"]},
                    {"name": "doi", "dataType": ["text"], "tokenization": "field"},
                    {"name": "abstract", "dataType": ["text"]},
                    {"name": "published", "dataType": ["date"]},
                    {"name": "authors", "dataType": ["text[]"]},
                    {"name": "source", "dataType": ["text"]},
                ],
            }
        )
    client.close()


def fetch_and_load():
    client = WeaviateClient(WEAVIATE_URL)
    response = requests.get(
        CROSSREF_URL,
        params={"filter": "from-pub-date:2019-01-01,until-pub-date:2025-12-31", "rows": 200},
        timeout=60,
    )
    response.raise_for_status()
    items = response.json().get("message", {}).get("items", [])

    with client.batch as batch:
        batch.batch_size = 50
        for item in items:
            batch.add_data_object(
                {
                    "title": (item.get("title") or [""])[0],
                    "doi": item.get("DOI"),
                    "abstract": item.get("abstract") or "",
                    "published": item.get("created", {}).get("date-time", datetime.utcnow().isoformat()),
                    "authors": [
                        f"{author.get('given', '')} {author.get('family', '')}".strip()
                        for author in item.get("author", [])
                    ],
                    "source": "crossref",
                },
                class_name="Paper",
            )
    client.close()


with DAG(
    dag_id="crossref_ingest",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    max_active_runs=1,
) as dag:
    ensure = PythonOperator(task_id="ensure_class", python_callable=ensure_class)
    load = PythonOperator(task_id="fetch_and_load", python_callable=fetch_and_load)

    ensure >> load


