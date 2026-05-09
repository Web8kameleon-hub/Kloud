#!/usr/bin/env python3
"""
BALANCER DATA SERVICE (Port 3337)
Persistent data storage for balancer state and metrics
"""

from fastapi import FastAPI, HTTPException
import uvicorn
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import json
from cors_policy import apply_standard_cors

# Initialize FastAPI
app = FastAPI(
    title="Balancer Data",
    description="Persistent data storage for balancer configuration and state",
    version="1.0.0",
)

# Add CORS
apply_standard_cors(app)

# Data storage
DATA_STORE: Dict[str, Dict[str, Any]] = {}
COLLECTIONS: Dict[str, List[Dict]] = {}
METRICS_HISTORY: List[Dict] = []
SERVICE_START = datetime.now(timezone.utc).isoformat()


@app.post("/data/documents")
async def create_document(
    collection: str, docId: Optional[str] = None, data: Optional[Dict] = None
):
    """Create new document"""
    if not collection:
        raise HTTPException(status_code=400, detail="collection name required")

    if collection not in COLLECTIONS:
        COLLECTIONS[collection] = []

    resolved_doc_id = (
        docId or f"doc_{len(COLLECTIONS[collection])}__{datetime.now().timestamp()}"
    )

    doc: Dict[str, Any] = {
        "docId": resolved_doc_id,
        "collection": collection,
        "data": data or {},
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "version": 1,
    }

    COLLECTIONS[collection].append(doc)
    DATA_STORE[resolved_doc_id] = doc

    return {
        "success": True,
        "message": f"Document created in {collection}",
        "docId": resolved_doc_id,
        "document": doc,
    }


@app.get("/data/documents/{docId}")
async def get_document(docId: str):
    """Get document by ID"""
    if docId not in DATA_STORE:
        raise HTTPException(status_code=404, detail=f"Document {docId} not found")

    return {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "document": DATA_STORE[docId],
    }


@app.get("/data/collections/{collection}")
async def get_collection(collection: str, limit: Optional[int] = None):
    """Get all documents in collection"""
    if collection not in COLLECTIONS:
        raise HTTPException(
            status_code=404, detail=f"Collection {collection} not found"
        )

    docs = COLLECTIONS[collection]
    if limit:
        docs = docs[-limit:]

    return {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "collection": collection,
        "totalDocuments": len(COLLECTIONS[collection]),
        "returnedDocuments": len(docs),
        "documents": docs,
    }


@app.put("/data/documents/{docId}")
async def update_document(docId: str, data: Dict):
    """Update document"""
    if docId not in DATA_STORE:
        raise HTTPException(status_code=404, detail=f"Document {docId} not found")

    doc = DATA_STORE[docId]
    doc["data"].update(data)
    doc["updatedAt"] = datetime.now(timezone.utc).isoformat()
    doc["version"] += 1

    return {
        "success": True,
        "message": "Document updated",
        "docId": docId,
        "document": doc,
    }


@app.delete("/data/documents/{docId}")
async def delete_document(docId: str):
    """Delete document"""
    if docId not in DATA_STORE:
        raise HTTPException(status_code=404, detail=f"Document {docId} not found")

    doc = DATA_STORE.pop(docId)
    collection = doc["collection"]
    if collection in COLLECTIONS:
        COLLECTIONS[collection] = [
            d for d in COLLECTIONS[collection] if d["docId"] != docId
        ]

    return {
        "success": True,
        "message": f"Document {docId} deleted",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/data/metrics")
async def store_metrics(nodeId: str, metrics: Dict):
    """Store metrics for node"""
    metric_entry = {
        "nodeId": nodeId,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
    }

    METRICS_HISTORY.append(metric_entry)

    # Keep only last 10000 entries
    if len(METRICS_HISTORY) > 10000:
        METRICS_HISTORY.pop(0)

    return {
        "success": True,
        "message": f"Metrics stored for {nodeId}",
        "timestamp": metric_entry["timestamp"],
    }


@app.get("/data/metrics/{nodeId}")
async def get_metrics(nodeId: str, limit: Optional[int] = None):
    """Get metrics for node"""
    node_metrics = [m for m in METRICS_HISTORY if m["nodeId"] == nodeId]

    if limit:
        node_metrics = node_metrics[-limit:]

    return {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "nodeId": nodeId,
        "metricCount": len(node_metrics),
        "metrics": node_metrics,
    }


@app.post("/data/config")
async def store_config(configId: str, config: Dict):
    """Store configuration"""
    config_doc = {
        "configId": configId,
        "config": config,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": 1,
    }

    DATA_STORE[f"config_{configId}"] = config_doc

    return {
        "success": True,
        "message": f"Configuration {configId} stored",
        "configId": configId,
    }


@app.get("/data/config/{configId}")
async def get_config(configId: str):
    """Get configuration"""
    key = f"config_{configId}"
    if key not in DATA_STORE:
        raise HTTPException(
            status_code=404, detail=f"Configuration {configId} not found"
        )

    return {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config": DATA_STORE[key],
    }


@app.get("/data/collections")
async def list_collections():
    """List all collections"""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "totalCollections": len(COLLECTIONS),
        "collections": {name: len(docs) for name, docs in COLLECTIONS.items()},
    }


@app.get("/data/stats")
async def get_storage_stats():
    """Get storage statistics"""
    total_docs = sum(len(docs) for docs in COLLECTIONS.values())

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "totalDocuments": total_docs,
        "totalCollections": len(COLLECTIONS),
        "totalConfigurations": sum(
            1 for k in DATA_STORE.keys() if k.startswith("config_")
        ),
        "metricsHistorySize": len(METRICS_HISTORY),
        "totalDataStoreEntries": len(DATA_STORE),
    }


@app.post("/data/export")
async def export_data(collection: Optional[str] = None):
    """Export data"""
    if collection:
        if collection not in COLLECTIONS:
            raise HTTPException(
                status_code=404, detail=f"Collection {collection} not found"
            )
        export_payload: Any = COLLECTIONS[collection]
    else:
        export_payload = {
            "collections": COLLECTIONS,
            "metrics": METRICS_HISTORY,
            "configurations": {
                k: v for k, v in DATA_STORE.items() if k.startswith("config_")
            },
        }

    return {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataSize": len(json.dumps(export_payload)),
        "data": export_payload,
    }


@app.post("/data/import")
async def import_data(collection: str, documents: List[Dict]):
    """Import documents to collection"""
    if collection not in COLLECTIONS:
        COLLECTIONS[collection] = []

    count = 0
    for doc_data in documents:
        doc = {
            "docId": doc_data.get(
                "docId",
                f"doc_{len(COLLECTIONS[collection])}__{datetime.now().timestamp()}",
            ),
            "collection": collection,
            "data": doc_data.get("data", {}),
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "version": 1,
        }
        COLLECTIONS[collection].append(doc)
        DATA_STORE[doc["docId"]] = doc
        count += 1

    return {
        "success": True,
        "message": f"Imported {count} documents",
        "collection": collection,
        "importedCount": count,
    }


@app.delete("/data/collections/{collection}")
async def delete_collection(collection: str):
    """Delete entire collection"""
    if collection not in COLLECTIONS:
        raise HTTPException(
            status_code=404, detail=f"Collection {collection} not found"
        )

    docs = COLLECTIONS.pop(collection)
    for doc in docs:
        DATA_STORE.pop(doc["docId"], None)

    return {
        "success": True,
        "message": f"Collection {collection} deleted",
        "deletedDocuments": len(docs),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "balancer-data-3337",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "storedDocuments": sum(len(docs) for docs in COLLECTIONS.values()),
        "metricsStored": len(METRICS_HISTORY),
        "collections": len(COLLECTIONS),
    }


@app.get("/info")
async def info():
    """Service information"""
    return {
        "service": "Balancer Data (Python)",
        "port": 3337,
        "type": "data-storage",
        "version": "1.0.0",
        "started_at": SERVICE_START,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "POST /data/documents": "Create document",
            "GET /data/documents/:docId": "Get document",
            "GET /data/collections/:collection": "Get collection",
            "PUT /data/documents/:docId": "Update document",
            "DELETE /data/documents/:docId": "Delete document",
            "POST /data/metrics": "Store metrics",
            "GET /data/metrics/:nodeId": "Get metrics",
            "POST /data/config": "Store configuration",
            "GET /data/config/:configId": "Get configuration",
            "GET /data/collections": "List collections",
            "GET /data/stats": "Storage statistics",
            "POST /data/export": "Export data",
            "POST /data/import": "Import data",
            "DELETE /data/collections/:collection": "Delete collection",
            "GET /health": "Health check",
            "GET /info": "Service info",
        },
    }


if __name__ == "__main__":
    port = int(os.getenv("BALANCER_DATA_PORT", "3337"))
    host = os.getenv("BALANCER_DATA_HOST", "0.0.0.0")

    print(f"\n{'=' * 60}")
    print("  BALANCER DATA SERVICE (Python)")
    print(f"  Listening on {host}:{port}")
    print("  Persistent data storage & state management")
    print(f"{'=' * 60}\n")

    uvicorn.run(app, host=host, port=port, log_level="info")
