"""Multi-Tenant Manager API - Kloud Cloud."""
import os

import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Kloud Multi-Tenant Manager", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "multi-tenant"}


@app.get("/")
def root():
    return {"message": "Multi-Tenant Manager", "version": "1.0.0"}


@app.get("/tenants")
def list_tenants():
    return {"tenants": [], "total": 0}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8090))
    uvicorn.run(app, host="0.0.0.0", port=port)

