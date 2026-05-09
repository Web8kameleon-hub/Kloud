# -*- coding: utf-8 -*-
"""
Kloud Distributed Pulse Balancer (Industrial)
- Real UDP heartbeat & peer discovery
- Simple leader election
- Token-bucket rate limiting per client
- Circuit breaker for redirect targets
- Real health metrics via psutil
- HTTP API (FastAPI+Uvicorn) for /balancer/request, /balancer/status
- Graceful shutdown & rotating logs

Business: Ledjan Ahmati - WEB8euroweb GmbH
REAL DATA ONLY â€¢ NO MOCK â€¢ NO RANDOM
"""

import os, sys, json, time, uuid, hmac, hashlib, socket, threading, signal, logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple, List

import psutil
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from kloud.colored_logger import setup_logger

# =========================
# Config
# =========================
CLUSTER_KEY = os.getenv("NSX_CLUSTER_KEY", "CHANGE_ME_SECURE_KEY")
NODE_NAME   = os.getenv("NSX_NODE_NAME", socket.gethostname())
NODE_ID     = os.getenv("NSX_NODE_ID", str(uuid.uuid4()))
API_HOST    = os.getenv("NSX_API_HOST", "0.0.0.0")
API_PORT    = int(os.getenv("NSX_API_PORT", "8091"))
HB_PORT     = int(os.getenv("NSX_HB_PORT", "42999"))
HB_INTERVAL = float(os.getenv("NSX_HB_INTERVAL", "3.0"))
HB_TIMEOUT  = float(os.getenv("NSX_HB_TIMEOUT", "10.0"))
BROADCAST_IP= os.getenv("NSX_BCAST_IP", "255.255.255.255")
DATA_DIR    = os.getenv("NSX_DATA_DIR", r"C:\Kloud-cloud")
LOG_DIR     = os.path.join(DATA_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_PATH = os.path.join(LOG_DIR, "balancer.log")
logger = logging.getLogger("nsx.balancer")
logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler(LOG_PATH, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(file_handler)

# Attach colored console logging without interfering with existing file handler
setup_logger("nsx.balancer")

# =========================
# Globals (thread-safe via simple discipline)
# =========================
PEERS: Dict[str, Dict[str, Any]] = {}   # node_id -> info
PEERS_LOCK = threading.Lock()
STOP_EVENT = threading.Event()

# Token-bucket per client
RATE_LIMIT: Dict[str, Dict[str, Any]] = {}
RATE_LOCK = threading.Lock()

# Circuit-breaker per target node_id
CB: Dict[str, Dict[str, Any]] = {}
CB_LOCK = threading.Lock()

# =========================
# Helpers
# =========================
def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()
def hmac_sign(payload: dict) -> str:
    msg = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hmac.new(CLUSTER_KEY.encode("utf-8"), msg, hashlib.sha256).hexdigest()

def verify_signature(payload: dict, signature: str) -> bool:
    try:
        calc = hmac_sign(payload)
        return hmac.compare_digest(calc, signature)
    except Exception:
        return False

def system_metrics() -> Dict[str, Any]:
    try:
        cpu = psutil.cpu_percent(interval=0.2)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        ni = psutil.net_io_counters()
        return {
            "cpu": cpu,
            "mem": mem,
            "disk": disk,
            "net_sent_MB": round(ni.bytes_sent / (1024**2), 2),
            "net_recv_MB": round(ni.bytes_recv / (1024**2), 2),
            "procs": len(psutil.pids()),
            "uptime_sec": int(time.time() - psutil.boot_time())
        }
    except Exception as e:
        logger.exception(f"system_metrics error: {e}")
        return {"cpu": 0, "mem": 0, "disk": 0, "net_sent_MB": 0, "net_recv_MB": 0, "procs": 0, "uptime_sec": 0}

def capacity_score(m: Dict[str, Any]) -> float:
    """
    Lower is better (more free capacity).
    Composite score with weight on CPU/MEM/DISK.
    """
    return 0.6 * m.get("cpu", 100) + 0.35 * m.get("mem", 100) + 0.05 * m.get("disk", 100)

def is_peer_alive(peer: Dict[str, Any]) -> bool:
    last = datetime.fromisoformat(peer["last_seen"])
    return (datetime.now(timezone.utc) - last).total_seconds() < HB_TIMEOUT

def elect_leader() -> Tuple[str, Dict[str, Any]]:
    """
    Deterministic: pick alive peer with smallest (node_name, node_id) lexicographically, including self.
    """
    with PEERS_LOCK:
        candidates = []
        # include self as a "peer"
        self_info = {
            "node_id": NODE_ID, "node_name": NODE_NAME, "last_seen": now_utc(),
            "metrics": system_metrics(), "api": f"http://{socket.gethostbyname(socket.gethostname())}:{API_PORT}"
        }
        candidates.append(self_info)
        for p in PEERS.values():
            if is_peer_alive(p):
                candidates.append(p)
        leader = sorted(candidates, key=lambda x: (x["node_name"], x["node_id"]))[0]
        return leader["node_id"], leader

def pick_target_for_work(exclude: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Choose the best alive node by capacity score, excluding CB-open nodes and optional list.
    """
    if exclude is None:
        exclude = []
    with PEERS_LOCK, CB_LOCK:
        candidates = []

        # self candidate
        self_m = system_metrics()
        if not CB.get(NODE_ID, {}).get("open", False) and NODE_ID not in exclude:
            candidates.append({
                "node_id": NODE_ID,
                "node_name": NODE_NAME,
                "last_seen": now_utc(),
                "metrics": self_m,
                "api": f"http://{socket.gethostbyname(socket.gethostname())}:{API_PORT}"
            })

        # peer candidates
        for p in PEERS.values():
            if not is_peer_alive(p): 
                continue
            if p["node_id"] in exclude: 
                continue
            if CB.get(p["node_id"], {}).get("open", False):
                continue
            candidates.append(p)

        if not candidates:
            return None

        best = sorted(candidates, key=lambda x: capacity_score(x["metrics"]))[0]
        return best

def circuit_fail(node_id: str, threshold: int = 5, cool_sec: int = 30):
    with CB_LOCK:
        entry = CB.setdefault(node_id, {"fails": 0, "open": False, "opened_at": None})
        entry["fails"] += 1
        if entry["fails"] >= threshold and not entry["open"]:
            entry["open"] = True
            entry["opened_at"] = time.time()
            logger.warning(f"Circuit OPEN for {node_id}")

        # if already open, keep it open until cooldown passes (see circuit_tick)

def circuit_success(node_id: str):
    with CB_LOCK:
        CB[node_id] = {"fails": 0, "open": False, "opened_at": None}

def circuit_tick(cool_sec: int = 30):
    with CB_LOCK:
        for nid, entry in list(CB.items()):
            if entry.get("open") and entry.get("opened_at"):
                if (time.time() - entry["opened_at"]) >= cool_sec:
                    # half-open -> allow next try by closing it (we'll re-open upon failure)
                    logger.info(f"Circuit CLOSE for {nid}")
                    CB[nid] = {"fails": 0, "open": False, "opened_at": None}

def rate_allow(key: str, rate: float = 10.0, burst: float = 20.0) -> bool:
    """
    Token-bucket: rate tokens/sec, max bucket 'burst'
    """
    now = time.time()
    with RATE_LOCK:
        b = RATE_LIMIT.get(key)
        if not b:
            RATE_LIMIT[key] = {"tokens": burst, "ts": now}
            return True
        elapsed = now - b["ts"]
        b["ts"] = now
        b["tokens"] = min(burst, b["tokens"] + elapsed * rate)
        if b["tokens"] >= 1.0:
            b["tokens"] -= 1.0
            return True
        return False

# =========================
# Heartbeat: sender
# =========================
def heartbeat_sender():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ip = socket.gethostbyname(socket.gethostname())
    payload_base = {
        "node_id": NODE_ID,
        "node_name": NODE_NAME,
        "api": f"http://{ip}:{API_PORT}",
    }
    logger.info(f"Heartbeat sender on UDP {BROADCAST_IP}:{HB_PORT} (IP {ip})")
    while not STOP_EVENT.is_set():
        try:
            m = system_metrics()
            payload = dict(payload_base)
            payload["metrics"] = m
            payload["ts"] = now_utc()
            sig = hmac_sign(payload)
            packet = {"payload": payload, "sig": sig}
            sock.sendto(json.dumps(packet).encode("utf-8"), (BROADCAST_IP, HB_PORT))
        except Exception as e:
            logger.exception(f"heartbeat_sender error: {e}")
        # circuit breaker maintenance
        circuit_tick()
        STOP_EVENT.wait(HB_INTERVAL)

# =========================
# Heartbeat: receiver
# =========================
def heartbeat_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", HB_PORT))
    logger.info(f"Heartbeat receiver listening UDP 0.0.0.0:{HB_PORT}")
    while not STOP_EVENT.is_set():
        try:
            sock.settimeout(1.0)
            try:
                data, addr = sock.recvfrom(65535)
            except socket.timeout:
                continue
            packet = json.loads(data.decode("utf-8"))
            payload = packet.get("payload", {})
            sig = packet.get("sig", "")
            # reject self
            if payload.get("node_id") == NODE_ID:
                continue
            # verify sig
            if not verify_signature(payload, sig):
                logger.warning(f"HB signature invalid from {addr}")
                continue

            peer = {
                "node_id": payload["node_id"],
                "node_name": payload["node_name"],
                "api": payload.get("api"),
                "metrics": payload.get("metrics", {}),
                "last_seen": now_utc()
            }
            with PEERS_LOCK:
                PEERS[peer["node_id"]] = peer
        except Exception as e:
            logger.exception(f"heartbeat_receiver error: {e}")

# =========================
# FastAPI app
# =========================
app = FastAPI(
    title="Kloud Distributed Pulse Balancer",
    version="1.0.0-industrial",
    description="Cluster-aware balancer with real metrics, rate limit, and circuit breaker."
)

# =========================
# Prometheus Metrics Endpoint
# =========================
@app.get("/metrics")
def prometheus_metrics():
    """
    📊 Prometheus-compatible metrics endpoint for Grafana
    Scrape this endpoint with Prometheus to visualize in Grafana
    """
    from fastapi.responses import PlainTextResponse
    
    me = system_metrics()
    leader_id, leader = elect_leader()
    is_leader = leader_id == NODE_ID
    
    with PEERS_LOCK:
        peer_count = len(PEERS)
        alive_peers = sum(1 for p in PEERS.values() if is_peer_alive(p))
    
    with CB_LOCK:
        open_circuits = sum(1 for c in CB.values() if c.get("open", False))
    
    capacity = capacity_score(me)
    
    lines = [
        "# HELP kloud_balancer_cpu_percent CPU usage percentage",
        "# TYPE kloud_balancer_cpu_percent gauge",
        f'kloud_balancer_cpu_percent{{node="{NODE_NAME}"}} {me.get("cpu", 0)}',
        "",
        "# HELP kloud_balancer_mem_percent Memory usage percentage",
        "# TYPE kloud_balancer_mem_percent gauge",
        f'kloud_balancer_mem_percent{{node="{NODE_NAME}"}} {me.get("mem", 0)}',
        "",
        "# HELP kloud_balancer_disk_percent Disk usage percentage",
        "# TYPE kloud_balancer_disk_percent gauge",
        f'kloud_balancer_disk_percent{{node="{NODE_NAME}"}} {me.get("disk", 0)}',
        "",
        "# HELP kloud_balancer_net_sent_mb Network bytes sent (MB)",
        "# TYPE kloud_balancer_net_sent_mb counter",
        f'kloud_balancer_net_sent_mb{{node="{NODE_NAME}"}} {me.get("net_sent_MB", 0)}',
        "",
        "# HELP kloud_balancer_net_recv_mb Network bytes received (MB)",
        "# TYPE kloud_balancer_net_recv_mb counter",
        f'kloud_balancer_net_recv_mb{{node="{NODE_NAME}"}} {me.get("net_recv_MB", 0)}',
        "",
        "# HELP kloud_balancer_procs Number of processes",
        "# TYPE kloud_balancer_procs gauge",
        f'kloud_balancer_procs{{node="{NODE_NAME}"}} {me.get("procs", 0)}',
        "",
        "# HELP kloud_balancer_uptime_seconds System uptime in seconds",
        "# TYPE kloud_balancer_uptime_seconds counter",
        f'kloud_balancer_uptime_seconds{{node="{NODE_NAME}"}} {me.get("uptime_sec", 0)}',
        "",
        "# HELP kloud_balancer_capacity_score Capacity score (lower is better)",
        "# TYPE kloud_balancer_capacity_score gauge",
        f'kloud_balancer_capacity_score{{node="{NODE_NAME}"}} {round(capacity, 2)}',
        "",
        "# HELP kloud_balancer_is_leader Whether this node is cluster leader",
        "# TYPE kloud_balancer_is_leader gauge",
        f'kloud_balancer_is_leader{{node="{NODE_NAME}"}} {1 if is_leader else 0}',
        "",
        "# HELP kloud_balancer_peer_count Total known peers",
        "# TYPE kloud_balancer_peer_count gauge",
        f'kloud_balancer_peer_count{{node="{NODE_NAME}"}} {peer_count}',
        "",
        "# HELP kloud_balancer_alive_peers Alive peers count",
        "# TYPE kloud_balancer_alive_peers gauge",
        f'kloud_balancer_alive_peers{{node="{NODE_NAME}"}} {alive_peers}',
        "",
        "# HELP kloud_balancer_open_circuits Number of open circuit breakers",
        "# TYPE kloud_balancer_open_circuits gauge",
        f'kloud_balancer_open_circuits{{node="{NODE_NAME}"}} {open_circuits}',
        "",
    ]
    
    # Add peer metrics
    with PEERS_LOCK:
        for pid, peer in PEERS.items():
            pm = peer.get("metrics", {})
            pname = peer.get("node_name", pid)
            alive = 1 if is_peer_alive(peer) else 0
            lines.append(f'kloud_balancer_peer_alive{{node="{NODE_NAME}",peer="{pname}"}} {alive}')
            lines.append(f'kloud_balancer_peer_cpu{{node="{NODE_NAME}",peer="{pname}"}} {pm.get("cpu", 0)}')
            lines.append(f'kloud_balancer_peer_mem{{node="{NODE_NAME}",peer="{pname}"}} {pm.get("mem", 0)}')
    
    return PlainTextResponse("\n".join(lines), media_type="text/plain; charset=utf-8")


@app.get("/balancer/status")
def balancer_status():
    leader_id, leader = elect_leader()
    with PEERS_LOCK:
        peers = list(PEERS.values())
    me = {
        "node_id": NODE_ID,
        "node_name": NODE_NAME,
        "api": f"http://{socket.gethostbyname(socket.gethostname())}:{API_PORT}",
        "metrics": system_metrics(),
        "last_seen": now_utc()
    }
    return JSONResponse({
        "ok": True,
        "now": now_utc(),
        "leader_id": leader_id,
        "leader": leader,
        "self": me,
        "peers": peers
    })

@app.post("/balancer/request")
async def balancer_request(request: Request):
    """
    Decide where to process a 'pulse' (unit of work).
    - Rate limit per client
    - Only leader makes cross-node routing decisions; followers self-accept unless overloaded
    - Circuit breaker protection for bad targets
    Body (JSON):
      { "work_id": "abc", "weight": 1.0, "exclude": ["node_id1", ...] }
    """
    client_ip = request.client.host
    if not rate_allow(f"rl:{client_ip}", rate=10, burst=20):
        raise HTTPException(status_code=429, detail="rate_limited")

    body = await request.json()
    work_id = str(body.get("work_id", str(uuid.uuid4())))
    weight = float(body.get("weight", 1.0))
    exclude = body.get("exclude", [])
    # sanity
    if weight <= 0:
        weight = 1.0

    leader_id, leader = elect_leader()
    me_metrics = system_metrics()
    me_score = capacity_score(me_metrics)

    # If I'm the leader â†’ choose best target among all alive nodes
    if leader_id == NODE_ID:
        target = pick_target_for_work(exclude=exclude)
        if target is None:
            # no candidates, accept locally if possible
            decision = "accepted_local"
            target_api = f"http://{socket.gethostbyname(socket.gethostname())}:{API_PORT}"
        else:
            target_api = target.get("api")
            if target["node_id"] == NODE_ID:
                decision = "accepted_local"
            else:
                decision = "redirect"
        resp = {
            "ok": True,
            "decision": decision,
            "work_id": work_id,
            "target": target_api,
            "leader_id": leader_id,
            "self_score": round(me_score, 2),
            "ts": now_utc()
        }
        if decision == "redirect":
            # optimistic success; real confirmation done by client
            circuit_success(target["node_id"])
        return JSONResponse(resp)

    # If I'm a follower:
    # - If my score is good (< 70 threshold heuristic) accept locally, else ask to redirect to leader's chosen
    if me_score < 70.0:
        return JSONResponse({
            "ok": True,
            "decision": "accepted_local",
            "work_id": work_id,
            "target": f"http://{socket.gethostbyname(socket.gethostname())}:{API_PORT}",
            "leader_id": leader_id,
            "self_score": round(me_score, 2),
            "ts": now_utc()
        })
    else:
        # suggest redirect to leader API, client will call leader /balancer/request again
        return JSONResponse({
            "ok": True,
            "decision": "redirect_to_leader",
            "work_id": work_id,
            "leader_api": leader.get("api"),
            "self_score": round(me_score, 2),
            "ts": now_utc()
        })

@app.post("/balancer/feedback")
async def balancer_feedback(request: Request):
    """
    Client reports result of a redirect attempt:
      { "node_id": "...", "success": true/false }
    Used to trip/close circuit breaker.
    """
    body = await request.json()
    node_id = body.get("node_id")
    success = bool(body.get("success", False))
    if not node_id:
        raise HTTPException(status_code=400, detail="missing node_id")

    if success:
        circuit_success(node_id)
        return {"ok": True, "state": "closed"}
    else:
        circuit_fail(node_id)
        return {"ok": True, "state": "maybe_open"}

# =========================
# Threads & lifecycle
# =========================
def start_threads():
    t1 = threading.Thread(target=heartbeat_sender, name="hb_sender", daemon=True)
    t2 = threading.Thread(target=heartbeat_receiver, name="hb_receiver", daemon=True)
    t1.start(); t2.start()
    return [t1, t2]

def stop_all(*_args):
    logger.info("Shutdown signal received. Stopping...")
    STOP_EVENT.set()

# =========================
# Main
# =========================
if __name__ == "__main__":
    signal.signal(signal.SIGINT, stop_all)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, stop_all)

    logger.info(f"Starting Distributed Pulse Balancer on {API_HOST}:{API_PORT} | "
                f"HB UDP {BROADCAST_IP}:{HB_PORT} | NODE {NODE_NAME}/{NODE_ID}")

    threads = start_threads()

    try:
        uvicorn.run(
            "distributed_pulse_balancer:app",
            host=API_HOST,
            port=API_PORT,
            log_level="warning",
            reload=False
        )
    finally:
        STOP_EVENT.set()
        for t in threads:
            t.join(timeout=2.0)
        logger.info("Balancer stopped.")



