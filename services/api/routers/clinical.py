import os
from typing import Any, Iterable, List

import psycopg2
from fastapi import APIRouter, Depends, HTTPException

from ..deps import oidc_guard


router = APIRouter(prefix="/clinical", tags=["clinical"])

PG_CONFIG = {
    "host": os.getenv("PGHOST", "postgres"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "postgres"),
    "dbname": os.getenv("PGDATABASE", "kloud"),
}


def _fetch_all(query: str, params: Iterable[Any] | None = None) -> List[dict[str, Any]]:
    connection = psycopg2.connect(**PG_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or tuple())
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        connection.close()


@router.get("/trials")
async def list_trials(q: str | None = None, status: str | None = None, user=Depends(oidc_guard)):
    clauses = []
    params: List[Any] = []
    if q:
        clauses.append("title ILIKE %s")
        params.append(f"%{q}%")
    if status:
        clauses.append("status = %s")
        params.append(status)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    query = (
        "SELECT nct_id, title, status, conditions, phases, start_date, last_update "
        "FROM clinical_trials "
        f"{where} ORDER BY last_update DESC LIMIT 200"
    )
    return _fetch_all(query, params)


@router.get("/drug-labels/{label_id}")
async def get_drug_label(label_id: str, user=Depends(oidc_guard)):
    records = _fetch_all(
        "SELECT id, brand_name, generic_name, purpose, indications, route FROM drug_labels WHERE id = %s",
        [label_id],
    )
    if not records:
        raise HTTPException(status_code=404, detail="Drug label not found")
    return records[0]


@router.get("/drug-labels")
async def list_drug_labels(limit: int = 50, user=Depends(oidc_guard)):
    limit = max(1, min(limit, 200))
    return _fetch_all(
        "SELECT id, brand_name, generic_name, route FROM drug_labels ORDER BY id DESC LIMIT %s",
        [limit],
    )


