from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import psutil
import yaml


ROOT_DIR = Path(__file__).resolve().parent.parent
SERVICES_FILE = ROOT_DIR / "ocean-core" / "services.yaml"
AGENTS_FILE = ROOT_DIR / "agents.py"
ASI_LOGS_FILE = ROOT_DIR / "asi_logs.json"


@dataclass
class SourceSnapshot:
    generated_at: str
    services_total: int
    labs_total: int
    agents_declared: int
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    telemetry_events: int
    telemetry_errors: int
    telemetry_warnings: int
    system_metric_points: List[Dict[str, Any]]


def _safe_read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _safe_read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _extract_services_and_labs() -> tuple[int, int]:
    data = _safe_read_yaml(SERVICES_FILE)
    services = data.get("services", {}) if isinstance(data, dict) else {}
    if not isinstance(services, dict):
        return 0, 0

    services_total = len(services)
    labs_total = len([name for name in services.keys() if str(name).lower().startswith("lab_")])
    return services_total, labs_total


def _count_declared_agents() -> int:
    if not AGENTS_FILE.exists():
        return 0
    text = AGENTS_FILE.read_text(encoding="utf-8", errors="ignore")
    matches = re.findall(r"class\s+([A-Za-z0-9_]+Agent)\s*\(", text)
    unique = {m for m in matches if m.lower() != "baseagent"}
    return len(unique)


def _parse_system_metrics_from_logs(logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    points: List[Dict[str, Any]] = []
    for item in logs:
        event_text = str(item.get("event", ""))
        if "System metrics:" not in event_text:
            continue

        _, metrics_text = event_text.split("System metrics:", 1)
        metrics_text = metrics_text.strip()
        try:
            parsed = ast.literal_eval(metrics_text)
            if isinstance(parsed, dict):
                cpu = float(parsed.get("cpu_percent", 0.0))
                ram = float(parsed.get("ram_percent", 0.0))
                disk = float(parsed.get("disk_percent", 0.0))
                ts = parsed.get("timestamp")
                points.append(
                    {
                        "timestamp": ts,
                        "cpu_percent": cpu,
                        "ram_percent": ram,
                        "disk_percent": disk,
                    }
                )
        except Exception:
            continue
    return points


def collect_real_snapshot() -> SourceSnapshot:
    now_iso = datetime.now(timezone.utc).isoformat()

    services_total, labs_total = _extract_services_and_labs()
    agents_declared = _count_declared_agents()

    cpu_percent = float(psutil.cpu_percent(interval=0.1))
    memory_percent = float(psutil.virtual_memory().percent)
    disk_percent = float(psutil.disk_usage("/").percent)

    logs_data = _safe_read_json(ASI_LOGS_FILE)
    logs: List[Dict[str, Any]] = logs_data if isinstance(logs_data, list) else []

    telemetry_events = len(logs)
    telemetry_errors = len([x for x in logs if str(x.get("level", "")).upper() == "ERROR"])
    telemetry_warnings = len([x for x in logs if str(x.get("level", "")).upper() in {"WARN", "WARNING"}])
    system_metric_points = _parse_system_metrics_from_logs(logs)

    return SourceSnapshot(
        generated_at=now_iso,
        services_total=services_total,
        labs_total=labs_total,
        agents_declared=agents_declared,
        cpu_percent=cpu_percent,
        memory_percent=memory_percent,
        disk_percent=disk_percent,
        telemetry_events=telemetry_events,
        telemetry_errors=telemetry_errors,
        telemetry_warnings=telemetry_warnings,
        system_metric_points=system_metric_points,
    )
