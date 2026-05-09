from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json, time, os

app = FastAPI(title="Mesh HQ - Kloud Real Telemetry")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATUS_FILE = os.path.join(os.path.dirname(__file__), "nodes_status.json")

def save_status(data):
    if not os.path.exists(STATUS_FILE):
        json.dump([], open(STATUS_FILE, "w"))
    all_data = json.load(open(STATUS_FILE))
    found = False
    for node in all_data:
        if node.get("id") == data.get("id"):
            node.update(data)
            found = True
    if not found:
        all_data.append(data)
    with open(STATUS_FILE, "w") as f:
        json.dump(all_data, f, indent=2)

@app.post("/mesh/register")
async def register_node(req: Request):
    body = await req.json()
    save_status(body)
    return {"ok": True, "registered": body.get("id"), "timestamp": time.time()}

@app.post("/mesh/status")
async def mesh_status(req: Request):
    body = await req.json()
    save_status(body)
    return {"ok": True, "updated": body.get("id"), "timestamp": time.time()}

@app.get("/mesh/nodes")
async def mesh_nodes():
    if os.path.exists(STATUS_FILE):
        data = json.load(open(STATUS_FILE))
        return JSONResponse(data)
    return JSONResponse([])

@app.get("/health")
async def health():
    return {"service": "mesh-service", "status": "healthy", "timestamp": time.time()}

@app.get("/")
async def dashboard():
    html_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    if os.path.exists(html_path):
        return HTMLResponse(open(html_path, "r", encoding="utf-8").read())
    return HTMLResponse("<html><body><h1>Mesh HQ</h1></body></html>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7777)


