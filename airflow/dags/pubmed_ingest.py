from datetime import datetime
import os
import json
import xml.etree.ElementTree as ET
import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY", "changeme")
PUBMED_BASE = os.getenv("PUBMED_BASE", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils")


def fetch_pubmed(**context):
    query = "neuroscience"
    id_response = requests.get(
        f"{PUBMED_BASE}/esearch.fcgi",
        params={"db": "pubmed", "term": query, "retmax": 25, "retmode": "json"},
        timeout=30,
    )
    id_response.raise_for_status()
    id_list = id_response.json()["esearchresult"].get("idlist", [])
    if not id_list:
        return ""

    xml_response = requests.get(
        f"{PUBMED_BASE}/efetch.fcgi",
        params={"db": "pubmed", "id": ",".join(id_list), "retmode": "xml"},
        timeout=30,
    )
    xml_response.raise_for_status()
    return xml_response.text


def upsert_weaviate_pubmed(**context):
    xml_doc = context["ti"].xcom_pull(task_ids="fetch_pubmed")
    if not xml_doc:
        return

    root = ET.fromstring(xml_doc)
    objects = []
    for article in root.findall('.//PubmedArticle'):
        title = (article.findtext('.//ArticleTitle') or '').strip()
        abstract = (article.findtext('.//Abstract/AbstractText') or '').strip()
        obj = {
            "class": "Paper",
            "properties": {
                "title": title,
                "abstract": abstract,
                "authors": [],
                "year": 0,
                "source": "pubmed",
                "doi": ""
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
}

with DAG(
    dag_id="pubmed_ingest",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
) as dag:
    fetch_task = PythonOperator(task_id="fetch_pubmed", python_callable=fetch_pubmed)
    upsert_task = PythonOperator(task_id="upsert_weaviate_pubmed", python_callable=upsert_weaviate_pubmed)

    fetch_task >> upsert_task


