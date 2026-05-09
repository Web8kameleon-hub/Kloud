#!/usr/bin/env python3
import asyncio
import json
import os
import socket
import ssl
import struct
import time
import uuid
import hmac
import hashlib
from aiohttp import web, ClientSession

# =========================
# Config & defaults
# =========================
MCAST_GRP = os.getenv("CLX_MCAST_GRP", "239.255.0.1")
MCAST_PORT = int(os.getenv("CLX_MCAST_PORT", "50000"))
HEARTBEAT_INTERVAL = float(os.getenv("CLX_HEARTBEAT_INTERVAL", "2.0"))
PEER_TTL = float(os.getenv("CLX_PEER_TTL", "10.0"))  # seconds without heartbeat -> peer considered dead
SHARED_SECRET = os.getenv("CLX_SHARED_SECRET", "change-me-super-secret")  # HMAC key
HOST = os.getenv("CLX_HOST", "0.0.0.0")
PORT = int(os.getenv("CLX_PORT", "8001"))

TLS_CERT = os.getenv("CLX_TLS_CERT")  # path to PEM cert (optional but recommended)
TLS_KEY = os.getenv("CLX_TLS_KEY")    # path to PEM private key (optional but recommended)
TLS_CA = os.getenv("CLX_TLS_CA")      # optional CA bundle; if omitted we still encrypt but skip identity verification

# =========================
# Helpers: HMAC signing
# =========================
def sign_payload(secret: str, ts: str, body: bytes) -> str:
    mac = hmac.new(secret.encode("utf-8"), digestmod=hashlib.sha256)
    mac.update(ts.encode("utf-8"))
    mac.update(body)
    return mac.hexdigest()

def verify_signature(secret: str, ts: str, body: bytes, signature: str, skew: int = 15) -> bool:
    try:
        ts_i = int(ts)
    except Exception:
        return False
    # freshness
    now = int(time.time())
    if abs(now - ts_i) > skew:
        return False
    expected = sign_payload(secret, ts, body)
    return hmac.compare_digest(expected, signature)

# =========================
# Memory shard (in-memory KV)
# =========================
class MemoryShard:
    def __init__(self):
        self._data = {}
        self._lock = asyncio.Lock()

    async def set(self, key, value):
        async with self._lock:
            self._data[key] = value

    async def get(self, key):
        async with self._lock:
            return self._data.get(key)

    async def dump(self):
        async with self._lock:
            return dict(self._data)

# =========================
# Peer registry with TTL
# =========================
class PeerRegistry:
    def __init__(self):
        self._peers = {}  # peer_id -> {"addr": "ip:port", "last": ts}
        self._lock = asyncio.Lock()

    async def upsert(self, peer_id: str, addr: str):
        async with self._lock:
            self._peers[peer_id] = {"addr": addr, "last": time.time()}

    async def cull(self, ttl: float):
        now = time.time()
        async with self._lock:
            dead = [pid for pid, meta in self._peers.items() if now - meta["last"] > ttl]
            for pid in dead:
                self._peers.pop(pid, None)

    async def list_addrs(self, exclude_id: str):
        async with self._lock:
            return [meta["addr"] for pid, meta in self._peers.items() if pid != exclude_id]

    async def snapshot(self):
        async with self._lock:
            return dict(self._peers)

# =========================
# Peer Node
# =========================
class PeerNode:
    def __init__(self, host: str, port: int):
        self.id = os.getenv("CLX_NODE_ID", str(uuid.uuid4())[:8])
        self.host = host
        self.port = port
        self.memory = MemoryShard()
        self.peers = PeerRegistry()
        self.server_ssl = None
        self.client_ssl = None

    # ---------- TLS contexts ----------
    def build_ssl_contexts(self):
        if TLS_CERT and TLS_KEY:
            # Server-side TLS
            server_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            server_ctx.load_cert_chain(TLS_CERT, TLS_KEY)
            self.server_ssl = server_ctx
        else:
            self.server_ssl = None  # HTTP (unencrypted) fallback, not recommended

        # Client-side TLS (for outbound replication)
        client_ctx = ssl.create_default_context()
        if TLS_CA:
            client_ctx.load_verify_locations(TLS_CA)
        else:
            # Still encrypt, but skip server identity verification (not ideal; use HMAC for auth)
            client_ctx.check_hostname = False
            client_ctx.verify_mode = ssl.CERT_NONE
        self.client_ssl = client_ctx

    # ---------- HTTP Handlers ----------
    async def handle_get(self, request):
        key = request.match_info["key"]
        val = await self.memory.get(key)
        return web.json_response({"key": key, "value": val})

    async def handle_dump(self, request):
        data = await self.memory.dump()
        peers = await self.peers.snapshot()
        return web.json_response({"node": self.id, "data": data, "peers": peers})

    async def handle_set(self, request):
        body_bytes = await request.read()
        ts = request.headers.get("X-Timestamp", "")
        sig = request.headers.get("X-Signature", "")
        if not verify_signature(SHARED_SECRET, ts, body_bytes, sig):
            return web.json_response({"error": "unauthorized"}, status=401)

        try:
            body = json.loads(body_bytes.decode("utf-8"))
            key = body["key"]; value = body["value"]
        except Exception:
            return web.json_response({"error": "bad_request"}, status=400)

        await self.memory.set(key, value)
        # replicate to others
        asyncio.create_task(self.replicate_to_peers(key, value))
        return web.json_response({"status": "ok", "key": key})

    async def handle_replicate(self, request):
        body_bytes = await request.read()
        ts = request.headers.get("X-Timestamp", "")
        sig = request.headers.get("X-Signature", "")
        if not verify_signature(SHARED_SECRET, ts, body_bytes, sig):
            return web.json_response({"error": "unauthorized"}, status=401)

        try:
            body = json.loads(body_bytes.decode("utf-8"))
            key = body["key"]; value = body["value"]
        except Exception:
            return web.json_response({"error": "bad_request"}, status=400)

        await self.memory.set(key, value)
        return web.json_response({"replicated": key})

    async def replicate_to_peers(self, key, value):
        payload = json.dumps({"key": key, "value": value}).encode("utf-8")
        ts = str(int(time.time()))
        sig = sign_payload(SHARED_SECRET, ts, payload)
        headers = {"Content-Type": "application/json", "X-Timestamp": ts, "X-Signature": sig}

        addrs = await self.peers.list_addrs(self.id)
        if not addrs:
            return

        async with ClientSession() as session:
            tasks = []
            for addr in addrs:
                scheme = "https" if self.client_ssl else "http"
                url = f"{scheme}://{addr}/replicate"
                tasks.append(session.post(url, data=payload, headers=headers, ssl=self.client_ssl))
            # fire-and-forget, but consume exceptions
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Optional: log failures
            # for r in results: ...

    # ---------- UDP multicast: heartbeat + discovery ----------
    async def heartbeat_sender(self):
        # UDP socket for sending multicast heartbeats
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            ttl_bin = struct.pack('@i', 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
        except Exception:
            pass

        while True:
            payload = {
                "id": self.id,
                "addr": f"{self.get_advertise_ip()}:{self.port}",
                "ts": int(time.time())
            }
            raw = json.dumps(payload).encode("utf-8")
            ts = str(payload["ts"])
            sig = sign_payload(SHARED_SECRET, ts, raw)
            packet = json.dumps({"p": payload, "sig": sig}).encode("utf-8")
            try:
                sock.sendto(packet, (MCAST_GRP, MCAST_PORT))
            except Exception:
                pass
            await asyncio.sleep(HEARTBEAT_INTERVAL)

    async def heartbeat_listener(self):
        # UDP socket for receiving multicast heartbeats
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('', MCAST_PORT))
        except OSError:
            # some OSes require binding to group explicitly
            sock.bind((MCAST_GRP, MCAST_PORT))

        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.setblocking(False)

        loop = asyncio.get_running_loop()
        while True:
            try:
                data, _ = await loop.run_in_executor(None, sock.recvfrom, 65536)
                obj = json.loads(data.decode("utf-8"))
                p = obj.get("p", {})
                sig = obj.get("sig", "")
                ts = str(p.get("ts", "0"))
                raw = json.dumps(p).encode("utf-8")
                if not verify_signature(SHARED_SECRET, ts, raw, sig):
                    continue
                if p.get("id") == self.id:
                    continue  # ignore our own hb
                await self.peers.upsert(p["id"], p["addr"])
            except Exception:
                await asyncio.sleep(0.05)

    async def peer_reaper(self):
        while True:
            await self.peers.cull(PEER_TTL)
            await asyncio.sleep(1.0)

    # ---------- Utils ----------
    def get_advertise_ip(self) -> str:
        # Best-effort: find a non-loopback IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    # ---------- Server ----------
    async def start(self):
        self.build_ssl_contexts()

        app = web.Application()
        app.add_routes([
            web.get("/get/{key}", self.handle_get),
            web.get("/dump", self.handle_dump),
            web.post("/set", self.handle_set),
            web.post("/replicate", self.handle_replicate),
        ])

        print(f"[Kloud Node {self.id}] {self.host}:{self.port} | TLS={'on' if self.server_ssl else 'off'} | "
              f"MCast {MCAST_GRP}:{MCAST_PORT}")

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port, ssl_context=self.server_ssl)
        await site.start()

        # background tasks
        asyncio.create_task(self.heartbeat_sender())
        asyncio.create_task(self.heartbeat_listener())
        asyncio.create_task(self.peer_reaper())

        # keep alive
        while True:
            await asyncio.sleep(3600)


# =========================
# Entrypoint
# =========================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Kloud Peer Node (Mesh Core v1)")
    parser.add_argument("--host", default=HOST, help="bind host, default 0.0.0.0")
    parser.add_argument("--port", type=int, default=PORT, help="bind port, default 8001")
    args = parser.parse_args()

    node = PeerNode(args.host, args.port)
    asyncio.run(node.start())


