"""
===========================================================
API_MANAGER_ULTRA v6.0 â€” CENTRALIZED TELEMETRY LINKED
===========================================================
Industrial control and monitoring node for Kloud Cloud.
Each local log, event, and service status is auto-synced with
AGIEMCore (/api/telemetry). Zero fake, zero delay, total sync.
===========================================================
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psutil, subprocess, requests, os, time, threading, json, platform
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
AGIEM_URL = "http://127.0.0.1:8020/api/telemetry"
LOG_PATH = "C:/Kloud-cloud/backend/logs/api_manager_ultra.log"
SYNC_INTERVAL = 5  # seconds

SERVICES = {
    "backend_main": {"port": 8001, "path": "C:/Kloud-cloud/app/main.py"},
    "agiem_core": {"port": 8020, "path": "C:/Kloud-cloud/backend/app/agiem_core.py"},
    "alba_collector": {"port": 8010, "path": "C:/Kloud-cloud/packages/alba-collector/src/server.ts"},
    "dashboard": {"port": 5173, "path": "C:/Kloud-cloud/dashboard"},
}

# =========================================================
# FASTAPI INIT
# =========================================================
app = FastAPI(title="API_MANAGER_ULTRA", version="6.0-industrial")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LOCK = threading.Lock()
LOG_QUEUE = []
STATUS = {}
METRICS = {"requests": 0, "avg_latency_ms": 0.0}

# =========================================================
# LOGGING + AGIEM TELEMETRY SYNC
# =========================================================
def log(message: str, level="INFO"):
    line = f"[{datetime.utcnow().isoformat()}] [{level}] {message}"
    with LOCK:
        LOG_QUEUE.append({"timestamp": datetime.utcnow().isoformat(), "level": level, "message": message})
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def send_to_agiem(data):
    try:
        requests.post(AGIEM_URL, json=data, timeout=2)
    except Exception:
        pass

def telemetry_sync():
    """Continuously push logs + system stats to AGIEMCore."""
    while True:
        if LOG_QUEUE:
            with LOCK:
                logs = LOG_QUEUE.copy()
                LOG_QUEUE.clear()
            payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "source": "api_manager_ultra",
                "system": platform.node(),
                "logs": logs,
                "metrics": metrics_snapshot(),
            }
            send_to_agiem(payload)
        time.sleep(SYNC_INTERVAL)

# =========================================================
# UTILITIES
# =========================================================
def service_running(port: int):
    for p in psutil.process_iter(["connections"]):
        for c in p.info["connections"]:
            if c.laddr and c.laddr.port == port:
                return True
    return False

def launch(path: str, name: str):
    try:
        if path.endswith(".py"):
            subprocess.Popen(["python", path], creationflags=subprocess.CREATE_NEW_CONSOLE)
        elif path.endswith(".ts"):
            subprocess.Popen(["ts-node", path], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(["powershell", "-Command", path])
        log(f"Service started: {name}")
        return True
    except Exception as e:
        log(f"Failed to start {name}: {e}", "ERROR")
        return False

def stop(name: str):
    info = SERVICES.get(name)
    if not info: return False
    port = info["port"]
    for p in psutil.process_iter(["pid", "connections"]):
        for c in p.info["connections"]:
            if c.laddr and c.laddr.port == port:
                p.terminate()
                log(f"Service stopped: {name} (PID {p.pid})", "WARN")
                return True
    return False

def metrics_snapshot():
    vm = psutil.virtual_memory()
    net = psutil.net_io_counters()
    return {
        "cpu": psutil.cpu_percent(interval=0.1),
        "ram": vm.percent,
        "disk": psutil.disk_usage("/").percent,
        "threads": threading.active_count(),
        "net_up": net.bytes_sent,
        "net_down": net.bytes_recv,
        "uptime_sec": int(time.time() - psutil.boot_time()),
    }

# =========================================================
# MODELS
# =========================================================
class Command(BaseModel):
    name: str
    action: str  # start|stop|restart|status

# =========================================================
# ROUTES
# =========================================================
@app.get("/status")
def full_status():
    start = time.time()
    METRICS["requests"] += 1
    data = {}
    for n, i in SERVICES.items():
        run = service_running(i["port"])
        data[n] = {"running": run, "port": i["port"], "timestamp": datetime.utcnow().isoformat()}
        STATUS[n] = data[n]
    METRICS["avg_latency_ms"] = (METRICS["avg_latency_ms"] + (time.time() - start) * 1000) / 2
    log("Status check executed")
    return {"node": platform.node(), "services": data, "metrics": metrics_snapshot()}

@app.get("/metrics/full")
def sys_metrics():
    log("Full metrics pulled")
    return metrics_snapshot()

@app.post("/control")
def control(cmd: Command):
    if cmd.name not in SERVICES:
        raise HTTPException(404, "unknown service")
    act = cmd.action
    if act == "status":
        return {"running": service_running(SERVICES[cmd.name]["port"])}
    if act == "start":
        return {"ok": launch(SERVICES[cmd.name]["path"], cmd.name)}
    if act == "stop":
        return {"ok": stop(cmd.name)}
    if act == "restart":
        stop(cmd.name); time.sleep(1); launch(SERVICES[cmd.name]["path"], cmd.name)
        log(f"Service restarted: {cmd.name}")
        return {"ok": True}
    raise HTTPException(400, "invalid action")

# =========================================================
# AUTOHEAL + TELEMETRY THREADS
# =========================================================
def autoheal():
    while True:
        for n, i in SERVICES.items():
            if not service_running(i["port"]):
                log(f"[AUTOHEAL] {n} down â€” restarting...", "CRIT")
                launch(i["path"], n)
        time.sleep(8)

threading.Thread(target=autoheal, daemon=True).start()
threading.Thread(target=telemetry_sync, daemon=True).start()

# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":
    import uvicorn
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    log("API_MANAGER_ULTRA 6.0 started", "SYS")
    uvicorn.run(app, host="0.0.0.0", port=8101, log_level="error")


