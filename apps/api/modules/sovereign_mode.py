from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

Mode = Literal["normal", "degraded", "sovereign"]

router = APIRouter(tags=["sovereign-mode"])


class SovereignSwitchRequest(BaseModel):
    mode: Mode
    reason: str = "manual_switch"


class SovereignEvaluateRequest(BaseModel):
    cloud_reachable: bool
    cloud_latency_ms: float = Field(default=0.0, ge=0.0)


class SovereignEventRequest(BaseModel):
    event_type: str = Field(min_length=3)
    payload: Dict[str, Any] = Field(default_factory=dict)


class SovereignState:
    def __init__(self) -> None:
        self._lock = Lock()
        self.mode: Mode = "normal"
        self.last_cloud_ok_at = ""
        self.last_cloud_error_at = ""
        self.last_reason = "startup"
        self.local_llm_active = False
        self.node_db_mode = "cloud"
        self.pipeline_mode = "cloud"
        self.cloud_timeout_ms = float(os.getenv("SOVEREIGN_CLOUD_TIMEOUT_MS", "1500"))
        self.wal_path = Path(
            os.getenv("SOVEREIGN_WAL_PATH", "./storage/sovereign_events.jsonl")
        ).resolve()
        self.wal_path.parent.mkdir(parents=True, exist_ok=True)

    def _utcnow(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _append_wal(self, event: Dict[str, Any]) -> None:
        try:
            with self.wal_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        except OSError:
            return

    def _set_mode(self, mode: Mode, reason: str) -> None:
        self.mode = mode
        self.last_reason = reason
        self.local_llm_active = mode in ("degraded", "sovereign")
        self.node_db_mode = "local" if mode == "sovereign" else "cloud"
        self.pipeline_mode = (
            "local"
            if mode == "sovereign"
            else ("hybrid" if mode == "degraded" else "cloud")
        )
        self._append_wal(
            {
                "event_type": "sovereign.mode.changed",
                "timestamp": self._utcnow(),
                "payload": {
                    "mode": mode,
                    "reason": reason,
                    "local_llm_active": self.local_llm_active,
                    "node_db_mode": self.node_db_mode,
                    "pipeline_mode": self.pipeline_mode,
                },
            }
        )

    def evaluate_cloud(
        self, cloud_reachable: bool, cloud_latency_ms: float
    ) -> Dict[str, Any]:
        with self._lock:
            if cloud_reachable and cloud_latency_ms <= self.cloud_timeout_ms:
                self.last_cloud_ok_at = self._utcnow()
                if self.mode != "normal":
                    self._set_mode("normal", "cloud_recovered")
            elif cloud_reachable and cloud_latency_ms > self.cloud_timeout_ms:
                self.last_cloud_error_at = self._utcnow()
                if self.mode == "normal":
                    self._set_mode("degraded", "cloud_slow")
            else:
                self.last_cloud_error_at = self._utcnow()
                self._set_mode("sovereign", "cloud_unreachable")
            return self.snapshot()

    def switch(self, mode: Mode, reason: str) -> Dict[str, Any]:
        with self._lock:
            self._set_mode(mode, reason)
            return self.snapshot()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "local_llm_active": self.local_llm_active,
            "node_db_mode": self.node_db_mode,
            "pipeline_mode": self.pipeline_mode,
            "last_reason": self.last_reason,
            "last_cloud_ok_at": self.last_cloud_ok_at,
            "last_cloud_error_at": self.last_cloud_error_at,
            "cloud_timeout_ms": self.cloud_timeout_ms,
            "wal_path": str(self.wal_path),
        }

    def append_local_event(
        self, event_type: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        event = {
            "event_type": event_type,
            "timestamp": self._utcnow(),
            "payload": payload,
        }
        with self._lock:
            self._append_wal(event)
        return event

    def replay_wal(self, limit: int = 1000) -> List[Dict[str, Any]]:
        limit = max(1, min(limit, 5000))
        if not self.wal_path.exists():
            return []
        try:
            with self.wal_path.open("r", encoding="utf-8") as handle:
                lines = handle.readlines()[-limit:]
        except OSError:
            return []
        events: List[Dict[str, Any]] = []
        seen = set()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            fingerprint = json.dumps(event, sort_keys=True, ensure_ascii=False)
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            events.append(event)
        return events


STATE = SovereignState()


@router.get("/v1/sovereign/status")
def sovereign_status():
    return {"ok": True, "state": STATE.snapshot()}


@router.post("/v1/sovereign/switch")
def sovereign_switch(payload: SovereignSwitchRequest):
    state = STATE.switch(payload.mode, payload.reason)
    return {"ok": True, "state": state}


@router.post("/v1/sovereign/evaluate")
def sovereign_evaluate(payload: SovereignEvaluateRequest):
    state = STATE.evaluate_cloud(payload.cloud_reachable, payload.cloud_latency_ms)
    return {"ok": True, "state": state}


@router.post("/v1/sovereign/events")
def sovereign_local_event(payload: SovereignEventRequest):
    event = STATE.append_local_event(payload.event_type, payload.payload)
    return {"ok": True, "event": event}


@router.post("/v1/sovereign/resync")
def sovereign_resync(max_events: int = 1000):
    events = STATE.replay_wal(limit=max_events)
    return {
        "ok": True,
        "resync": {
            "events_replayed": len(events),
            "idempotent": True,
            "mode_after": STATE.snapshot()["mode"],
        },
        "events": events,
    }
