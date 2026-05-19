"""
🧠 Kloud NeuroTrigger+
Vetë-riparim dhe instinkt inteligjent:
- Zbulon problemet
- Rifillon modulet automatikisht
- Dërgon sinjal te HQ
"""

import json, os, time, threading, requests, subprocess
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
RUNTIME = BASE / "runtime"
HISTORY = RUNTIME / "history"
TRIGGERS_FILE = RUNTIME / "triggers.json"

RUNTIME.mkdir(exist_ok=True)
HISTORY.mkdir(exist_ok=True)

HQ_ENDPOINT = "http://127.0.0.1:7777/mesh/status"
NODE_ID = os.getenv("KLOUD_NODE_ID", "NEURO-LOCAL")


class NeuroTrigger:
    def __init__(self):
        self.triggers = self._load_existing()
        self.module_map = {
            "telemetry_service": "backend/mesh/telemetry_service.py",
            "signal_monitor": "backend/mesh/signal_monitor.py",
            "alert_service": "backend/mesh/alert_service.py",
            "ddos_guard": "backend/mesh/security/ddos_guard.py",
        }

    def _load_existing(self):
        if TRIGGERS_FILE.exists():
            try:
                return json.loads(TRIGGERS_FILE.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    def detect_event(self, category: str, message: str, details: dict = None):
        event = {
            "id": f"TRG-{int(time.time() * 1000)}",
            "node": NODE_ID,
            "category": category,
            "message": message,
            "details": details or {},
            "timestamp": time.time(),
            "readable_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        }
        self.triggers.append(event)
        self._save_local()
        threading.Thread(target=self.auto_heal, args=(event,), daemon=True).start()
        return event

    def _save_local(self):
        TRIGGERS_FILE.write_text(json.dumps(self.triggers, indent=2), encoding="utf-8")
        today = datetime.utcnow().strftime("%Y-%m-%d")
        (HISTORY / f"triggers_{today}.json").write_text(
            json.dumps(self.triggers, indent=2), encoding="utf-8"
        )

    def push_to_hq(self, payload: dict):
        try:
            requests.post(HQ_ENDPOINT, json=payload, timeout=2)
        except Exception:
            pass

    # === Intelligent auto-repair layer ===
    def restart_module(self, module_name: str):
        path = self.module_map.get(module_name)
        if not path or not Path(path).exists():
            return f"[NeuroTrigger] ❌ Module {module_name} not found."
        try:
            subprocess.Popen(["python", path])
            msg = f"[NeuroTrigger] 🔄 Restarted {module_name}"
            print(msg)
            self.push_to_hq({"event": msg})
            return msg
        except Exception as e:
            err = f"[NeuroTrigger] ⚠️ Restart failed for {module_name}: {e}"
            print(err)
            self.push_to_hq({"event": err})
            return err

    def fallback_module(self, module_name: str):
        fallback_path = f"{Path(self.module_map.get(module_name)).stem}_backup.py"
        if not Path(fallback_path).exists():
            return f"[NeuroTrigger] Backup not available for {module_name}"
        subprocess.Popen(["python", fallback_path])
        msg = f"[NeuroTrigger] Activated backup for {module_name}"
        print(msg)
        self.push_to_hq({"event": msg})
        return msg

    def auto_heal(self, event: dict):
        cat = event["category"].lower()
        mod = event["details"].get("module", "unknown")
        decision = None

        if "error" in cat or "crash" in event["message"].lower():
            decision = self.restart_module(mod)
        elif "timeout" in event["message"].lower():
            decision = self.fallback_module(mod)
        else:
            decision = "[NeuroTrigger] Monitoring only — no action required."

        payload = {
            "service": "neuro_trigger",
            "action": decision,
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
        }
        self.push_to_hq(payload)
        print(decision)
        return decision


if __name__ == "__main__":
    t = NeuroTrigger()
    t.detect_event("error", "Telemetry module crashed", {"module": "telemetry_service"})
