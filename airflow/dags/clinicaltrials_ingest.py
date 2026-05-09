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
CLINICALTRIALS_API = "https://clinicaltrials.gov/api/v2/studies"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS clinical_trials(
  nct_id TEXT PRIMARY KEY,
  title TEXT,
  status TEXT,
  conditions TEXT[],
  phases TEXT[],
  start_date DATE,
  last_update DATE
);
"""

UPSERT_SQL = """
INSERT INTO clinical_trials(nct_id, title, status, conditions, phases, start_date, last_update)
VALUES(%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (nct_id) DO UPDATE SET
  title = excluded.title,
  status = excluded.status,
  conditions = excluded.conditions,
  phases = excluded.phases,
  start_date = excluded.start_date,
  last_update = excluded.last_update;
"""


def load_trials():
    connection = psycopg2.connect(**PG_CONFIG)
    cursor = connection.cursor()
    cursor.execute(CREATE_TABLE_SQL)
    connection.commit()

    response = requests.get(
        CLINICALTRIALS_API,
        params={"pageSize": 100, "sort": "-LastUpdatePostDate"},
        timeout=60,
    )
    response.raise_for_status()
    studies = response.json().get("studies", [])

    for study in studies:
        protocol = study.get("protocolSection", {})
        id_module = protocol.get("identificationModule", {})
        status_module = protocol.get("statusModule", {})
        design_module = protocol.get("designModule", {})

        nct_id = id_module.get("nctId")
        title = id_module.get("briefTitle")
        status = status_module.get("overallStatus")
        conditions = protocol.get("conditionsModule", {}).get("conditions", [])
        phases = design_module.get("phases", []) or []
        start_date = status_module.get("startDateStruct", {}).get("date")
        last_update = status_module.get("lastUpdatePostDateStruct", {}).get("date")

        cursor.execute(
            UPSERT_SQL,
            (nct_id, title, status, conditions, phases, start_date, last_update),
        )

    connection.commit()
    cursor.close()
    connection.close()


with DAG(
    dag_id="clinicaltrials_ingest",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    PythonOperator(task_id="load_trials", python_callable=load_trials)


