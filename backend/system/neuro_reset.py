"""
Kloud Neuro Reset — controlled creative revival
- 5' mute / 7' random sensory / 3' scripting instinct (defaults, configurable)
- objective measures: CPU, mem, latency (optional: URL for /health)
- stores each session in runtime/neuro_reset_sessions.json
- exposes a small FastAPI router for integration with the orchestrator (port 5555)
- also usable as a CLI: python neuro_reset.py --start
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import os, json, time
from typing import Optional, Dict, Any

try:
    import psutil
except Exception:  # lightweight fallback if psutil isn't installed during some runs
    psutil = None

try:
    import requests
except Exception:
    requests = None

BASE = Path(__file__).resolve().parent
RUNTIME = BASE / "runtime"
RUNTIME.mkdir(exist_ok=True)
SESS_FILE = RUNTIME / "neuro_reset_sessions.json"

DEFAULTS = {
    "mute_minutes": float(os.getenv("NR_MUTE_MIN", "5")),
    "sensory_minutes": float(os.getenv("NR_SENS_MIN", "7")),
    "script_minutes": float(os.getenv("NR_SCRIPT_MIN", "3")),
    "latency_url": os.getenv("NR_LAT_URL", "http://127.0.0.1:7777/health"),
}


@dataclass
class Snapshot:
    ts: float
    cpu: Optional[float]
    ram: Optional[float]
    latency_ms: Optional[float] = None


@dataclass
class Session:
    id: str
    started_at: float
    ended_at: Optional[float]
    plan: Dict[str, float]
    before: Snapshot
    after: Optional[Snapshot]
    notes: str = ""
    success: Optional[bool] = None


class NeuroReset:
    def __init__(self, sessions_path: Path = SESS_FILE):
        self.sessions_path = sessions_path
        self.sessions = self._load()

    # ---------- storage ----------
    def _load(self):
        if self.sessions_path.exists():
            try:
                return json.loads(self.sessions_path.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    def _save(self):
        self.sessions_path.write_text(json.dumps(self.sessions, indent=2), encoding="utf-8")

    # ---------- metrics ----------
    ALLOWED_LATENCY_HOSTS = frozenset(["api.kloud.com", "localhost", "127.0.0.1"])
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL to prevent SSRF attacks"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False
            if parsed.hostname not in self.ALLOWED_LATENCY_HOSTS:
                return False
            return True
        except Exception:
            return False
    
    def _latency(self, url: Optional[str]) -> Optional[float]:
        if not url or requests is None:
            return None
        # SECURITY: Validate URL to prevent SSRF
        if not self._validate_url(url):
            return None
        t0 = time.time()
        try:
            requests.get(url, timeout=2.0)
            return round((time.time() - t0) * 1000, 2)
        except Exception:
            return None

    def snapshot(self, latency_url: Optional[str]) -> Snapshot:
        cpu = None
        ram = None
        if psutil is not None:
            try:
                cpu = psutil.cpu_percent(interval=0.2)
                ram = psutil.virtual_memory().percent
            except Exception:
                cpu = None
                ram = None

        lat = self._latency(latency_url)
        return Snapshot(ts=time.time(), cpu=cpu, ram=ram, latency_ms=lat)

    # ---------- API ----------
    def plan(self,
             mute_min: float = DEFAULTS["mute_minutes"],
             sensory_min: float = DEFAULTS["sensory_minutes"],
             script_min: float = DEFAULTS["script_minutes"]) -> Dict[str, float]:
        return {"mute": mute_min, "sensory": sensory_min, "script": script_min}

    def start(self, notes: str = "", latency_url: Optional[str] = DEFAULTS["latency_url"],
              mute_min: float = DEFAULTS["mute_minutes"],
              sensory_min: float = DEFAULTS["sensory_minutes"],
              script_min: float = DEFAULTS["script_minutes"]) -> Dict[str, Any]:
        sid = f"NR-{int(time.time() * 1000)}"
        sess = Session(
            id=sid,
            started_at=time.time(),
            ended_at=None,
            plan=self.plan(mute_min, sensory_min, script_min),
            before=self.snapshot(latency_url),
            after=None,
            notes=notes,
            success=None
        )
        self.sessions.append(self._to_json(sess))
        self._save()
        return {"ok": True, "id": sid, "plan": sess.plan, "tips": self._tips()}

    def stop(self, session_id: str, success: Optional[bool] = None,
             latency_url: Optional[str] = DEFAULTS["latency_url"], notes: str = "") -> Dict[str, Any]:
        for s in self.sessions:
            if s.get("id") == session_id and s.get("ended_at") is None:
                s["ended_at"] = time.time()
                snap = asdict(self.snapshot(latency_url))
                s["after"] = snap
                if notes:
                    s["notes"] = (s.get("notes") or "") + (" | " if s.get("notes") else "") + notes
                s["success"] = bool(success) if success is not None else None
                self._save()
                return {"ok": True, "session": s, "delta": self._delta(s)}
        return {"ok": False, "error": "session_not_found_or_already_closed"}

    def last(self, n: int = 5) -> Dict[str, Any]:
        return {"sessions": self.sessions[-n:]}

    # ---------- helpers ----------
    def _to_json(self, sess: Session) -> Dict[str, Any]:
        obj = {
            "id": sess.id,
            "started_at": sess.started_at,
            "ended_at": sess.ended_at,
            "plan": sess.plan,
            "before": asdict(sess.before),
            "after": asdict(sess.after) if sess.after else None,
            "notes": sess.notes,
            "success": sess.success
        }
        return obj

    def _delta(self, s: Dict[str, Any]) -> Dict[str, Optional[float]]:
        b, a = s.get("before"), s.get("after")
        if not (b and a):
            return {}
        return {
            "cpu_delta": round((a["cpu"] - b["cpu"]), 2) if a["cpu"] is not None and b["cpu"] is not None else None,
            "ram_delta": round((a["ram"] - b["ram"]), 2) if a["ram"] is not None and b["ram"] is not None else None,
            "latency_delta_ms": round((a["latency_ms"] - b["latency_ms"]), 2) if (a["latency_ms"] is not None and b["latency_ms"] is not None) else None
        }

    def _tips(self) -> list[str]:
        return [
            "1) 5′ mute: turn off sounds, close secondary displays.",
            "2) 7′ sensory: play unfamiliar music/photos/video (no analysis).",
            "3) 3′ scripting: write without judgement (pseudo, ideas, sentences)."
        ]


# ---------------- FastAPI router ----------------
from fastapi import APIRouter, Body

router = APIRouter(prefix="/neuro", tags=["neuro-reset"])
nr = NeuroReset()


@router.post("/reset/start")
def neuro_start(payload: Dict[str, Any] = Body(None)):
    notes = (payload or {}).get("notes", "")
    latency_url = (payload or {}).get("latency_url", DEFAULTS["latency_url"])
    return nr.start(notes=notes, latency_url=latency_url)


@router.post("/reset/stop")
def neuro_stop(payload: Dict[str, Any] = Body(...)):
    return nr.stop(payload.get("id"), success=payload.get("success", None), notes=payload.get("notes", ""))


@router.get("/reset/last")
def neuro_last(n: int = 5):
    return nr.last(n)


