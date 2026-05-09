import os, json
from datetime import datetime

try:
    import redis  # pip install redis
except ImportError:
    redis = None

class TelemetryService:
    def __init__(self):
        self.ns = "kloud:nodes"
        self.mem = {}
        self.r = None
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        if redis:
            try:
                self.r = redis.Redis.from_url(url, decode_responses=True)
                self.r.ping()
            except Exception:
                self.r = None

    def save(self, node_id: str, payload: dict):
        rec = {
            "id": node_id,
            "status": payload.get("status","active"),
            "metrics": payload.get("metrics", {}),
            "apis": payload.get("apis", {}),
            "hostname": payload.get("hostname"),
            "ip": payload.get("ip"),
            "timestamp": payload.get("timestamp") or datetime.utcnow().isoformat()
        }
        if self.r:
            self.r.set(f"{self.ns}:{node_id}", json.dumps(rec))
            try:
                self.r.publish("telemetry_stream", json.dumps(rec))
            except Exception:
                pass
        else:
            self.mem[node_id] = rec
        return rec

    def get(self, node_id: str):
        if self.r:
            raw = self.r.get(f"{self.ns}:{node_id}")
            return json.loads(raw) if raw else None
        return self.mem.get(node_id)

    def get_all(self):
        if self.r:
            out=[]
            try:
                for key in self.r.keys(f"{self.ns}:*"):
                    raw = self.r.get(key)
                    if raw: out.append(json.loads(raw))
            except Exception:
                pass
            return out
        return list(self.mem.values())



