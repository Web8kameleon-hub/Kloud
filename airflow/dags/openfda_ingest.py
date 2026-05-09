from datetime import datetime
import os
import psycopg2
import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

PG_CONFIG = {
    "host": os.getenv("PGHOST", "postgres"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "postgres"),
    "dbname": os.getenv("PGDATABASE", "Kloud"),
}
OPENFDA_API = "https://api.fda.gov/drug/label.json"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS drug_labels(
  id TEXT PRIMARY KEY,
  brand_name TEXT[],
  generic_name TEXT[],
  purpose TEXT[],
  indications TEXT,
  route TEXT[]
);
"""

UPSERT_SQL = """
INSERT INTO drug_labels(id, brand_name, generic_name, purpose, indications, route)
VALUES(%s, %s, %s, %s, %s, %s)
ON CONFLICT (id) DO UPDATE SET
  brand_name = excluded.brand_name,
  generic_name = excluded.generic_name,
  purpose = excluded.purpose,
  indications = excluded.indications,
  route = excluded.route;
"""


def load_drug_labels():
    connection = psycopg2.connect(**PG_CONFIG)
    cursor = connection.cursor()
    cursor.execute(CREATE_TABLE_SQL)
    connection.commit()

    response = requests.get(OPENFDA_API, params={"limit": 100}, timeout=60)
    response.raise_for_status()
    results = response.json().get("results", [])

    for entry in results:
        openfda_data = entry.get("openfda", {})
        cursor.execute(
            UPSERT_SQL,
            (
                entry.get("id"),
                openfda_data.get("brand_name", []),
                openfda_data.get("generic_name", []),
                entry.get("purpose", []),
                (entry.get("indications_and_usage") or [""])[0],
                openfda_data.get("route", []),
            ),
        )

    connection.commit()
    cursor.close()
    connection.close()


with DAG(
    dag_id="openfda_ingest",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@weekly",
    catchup=False,
) as dag:
    PythonOperator(task_id="load_drug_labels", python_callable=load_drug_labels)


