"""
Simplified Distributed Pulse Balancer
- UDP heartbeat discovery
- Leader election 
- Task routing with load distribution
"""
import os, sys, json, time, uuid, hmac, hashlib, socket, threading, logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
import psutil
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("balancer")

# Configuration
CLUSTER_KEY = os.getenv("NSX_CLUSTER_KEY", "kloud-secure-key")
NODE_ID = str(uuid.uuid4())[:8]
NODE_NAME = os.getenv("NSX_NODE_NAME", "BalancerNode-" + NODE_ID)
API_PORT = int(os.getenv("NSX_API_PORT", "8091"))
HB_PORT = int(os.getenv("NSX_HB_PORT", "42999"))
HB_INTERVAL = 3.0
HB_TIMEOUT = 10.0

# State
PEERS = {}
PEERS_LOCK = threading.Lock()
STOP_EVENT = threading.Event()

def system_metrics():
    return {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "load": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0,
    }

def hmac_sign(payload):
    msg = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hmac.new(CLUSTER_KEY.encode(), msg, hashlib.sha256).hexdigest()

def verify_signature(payload, sig):
    try:
        return hmac.compare_digest(hmac_sign(payload), sig)
    except:
        return False

def elect_leader():
    """Deterministic leader election"""
    with PEERS_LOCK:
        candidates = [{"node_id": NODE_ID, "node_name": NODE_NAME}]
        candidates.extend([p for p in PEERS.values() if time.time() - p.get("last_seen", 0) < HB_TIMEOUT])
    leader = sorted(candidates, key=lambda x: (x["node_name"], x["node_id"]))[0]
    return leader

def capacity_score(metrics):
    """Lower is better"""
    return metrics.get("cpu", 50) + metrics.get("memory", 50) / 2 + metrics.get("disk", 50) / 3

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "balancer-active", "node": NODE_NAME, "timestamp": datetime.utcnow().isoformat()}

@app.get("/status")
async def status():
    leader = elect_leader()
    with PEERS_LOCK:
        peers = list(PEERS.values())
    return {
        "ok": True,
        "node_id": NODE_ID,
        "node_name": NODE_NAME,
        "leader": leader,
        "peers": len(peers),
        "metrics": system_metrics(),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/balance")
async def balance_request(request: Request):
    """Route work to best available node"""
    body = await request.json()
    work_id = str(body.get("work_id", str(uuid.uuid4())))
    weight = float(body.get("weight", 1.0))
    
    leader = elect_leader()
    metrics = system_metrics()
    score = capacity_score(metrics)
    
    decision = "local" if score < 70 else "redirect"
    
    return {
        "ok": True,
        "work_id": work_id,
        "decision": decision,
        "leader": leader["node_name"],
        "score": round(score, 2),
        "timestamp": datetime.utcnow().isoformat()
    }

def heartbeat_receiver():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", HB_PORT))
    logger.info(f"Heartbeat listener on UDP :{HB_PORT}")
    
    while not STOP_EVENT.is_set():
        try:
            sock.settimeout(1.0)
            data, addr = sock.recvfrom(65535)
            packet = json.loads(data.decode())
            payload = packet.get("payload", {})
            
            if payload.get("node_id") == NODE_ID:
                continue
            if not verify_signature(payload, packet.get("sig", "")):
                continue
                
            with PEERS_LOCK:
                PEERS[payload["node_id"]] = {
                    "node_id": payload["node_id"],
                    "node_name": payload["node_name"],
                    "metrics": payload.get("metrics", {}),
                    "last_seen": time.time()
                }
        except socket.timeout:
            continue
        except Exception as e:
            logger.warning(f"HB receive error: {e}")

def heartbeat_sender():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    logger.info(f"Heartbeat sender on UDP broadcast :{HB_PORT}")
    
    while not STOP_EVENT.is_set():
        try:
            payload = {
                "node_id": NODE_ID,
                "node_name": NODE_NAME,
                "metrics": system_metrics(),
                "ts": datetime.utcnow().isoformat()
            }
            packet = {"payload": payload, "sig": hmac_sign(payload)}
            sock.sendto(json.dumps(packet).encode(), ("255.255.255.255", HB_PORT))
        except Exception as e:
            logger.warning(f"HB send error: {e}")
        STOP_EVENT.wait(HB_INTERVAL)

def start_threads():
    threads = []
    t1 = threading.Thread(target=heartbeat_sender, daemon=True)
    t2 = threading.Thread(target=heartbeat_receiver, daemon=True)
    t1.start()
    t2.start()
    threads.extend([t1, t2])
    return threads

if __name__ == "__main__":
    threads = start_threads()
    logger.info(f"Distributed Pulse Balancer starting on 0.0.0.0:{API_PORT}")
    logger.info(f"  - Node: {NODE_NAME}")
    logger.info(f"  - UDP Heartbeat: :{HB_PORT}")
    logger.info(f"  - Endpoints: /status, /balance")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=API_PORT, log_level="info")
    finally:
        STOP_EVENT.set()
        for t in threads:
            t.join(timeout=2)


