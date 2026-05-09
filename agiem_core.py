# -*- coding: utf-8 -*-
"""
AGIEM Core (real-only)

Location: C:\\Kloud-cloud\\agiem_core.py

Purpose:
- Real-time, production-ready core for ASI/AGIEM operations.
- NO SIMULATION, NO RANDOM, NO MOCK DATA.
- Gathers real system metrics (psutil required), analyzes logs for anomalies,
  registers and reports to Mesh HQ using HTTP (requests optional), and
  offers safe, non-destructive "recommendations" (insights) â€” not automatic
  system changes.

Features:
- AGIEMCore: core state, node registry and health calculation
- NodeReal: collects real metrics and uploads files if present
- MeshReporter: registers node and sends telemetry to Mesh HQ (configurable)
- analyze_logs: simple anomaly extractor from logs (ERROR/CRIT/FAIL)
- backup_data: creates a zip archive of a provided data directory (safe)
- CLI with only real modes: status, analyze, report, backup, register

Run examples:
  python agiem_core.py status
  python agiem_core.py analyze --logs C:\\Kloud-cloud\\logs
  python agiem_core.py backup --path C:\\Kloud-cloud\\data --out backup.zip
  python agiem_core.py register --hq http://localhost:7777/mesh/register

Note: this module does not alter system configuration or install services.
It only reads metrics, files and sends telemetry to configured endpoints.
"""

from __future__ import annotations

import argparse
import datetime
from datetime import datetime, timezone
import json
import logging
import os
import socket
import sys
import time
import threading
import uuid
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

try:
    from alba_core import AlbaCore
except Exception:
    AlbaCore = None

try:
    from albi_core import AlbiCore
except Exception:
    AlbiCore = None

try:
    from asi_core import ASICore
except Exception:
    ASICore = None

try:
    from self_generating_api import SelfGeneratingAPI
except Exception:
    SelfGeneratingAPI = None

try:
    from research_proposal_lab import ResearchProposalLab
except Exception:
    ResearchProposalLab = None

# Optional dependencies
try:
    import requests
except Exception:
    requests = None

try:
    import psutil
except Exception:
    psutil = None

# Use standard Python logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("AGIEM")


@dataclass
class ReproductionStage:
    """Inventory entry for the ALBA->ALBI->JONA->ASI pipeline."""

    name: str
    role: str
    description: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    notes: List[Dict[str, Any]] = field(default_factory=list)

    def record_metric(self, key: str, value: Any) -> None:
        self.metrics[key] = value

    def add_note(self, message: str, level: str = "INFO") -> None:
        self.notes.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": level,
                "message": message,
            }
        )


@dataclass
class StageResult:
    """Outcome from a pipeline stage."""

    updated_state: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    message: str = "completed"
    public_payload: Dict[str, Any] = field(default_factory=dict)


class AGIEMCore:
    """Core class for node registry, lightweight telemetry and analysis.

    Keeps only real operations: metric collection, log analysis, backups and
    telemetry reporting. No fake data.
    """

    # ---------------------------
    # Backup (safe, non-destructive)
    # ---------------------------
    def backup_data(self, path: str, out_file: Optional[str] = None) -> Dict[str, Any]:
        """Create a zip archive of `path` and return summary with size (bytes).

        This function performs only read operations and writes a single zip file.
        """
        source = Path(path)
        if not source.exists():
            msg = f"Backup source not found: {path}"
            self.log_event("AGIEM", msg, "ERROR")
            return {"error": msg}

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        if out_file is None:
            out_file = str(Path.cwd() / f"agiem_backup_{timestamp}.zip")

        try:
            with zipfile.ZipFile(out_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(source):
                    for fname in files:
                        fpath = Path(root) / fname
                        # store relative path in archive
                        arcname = str(Path(root).relative_to(source) / fname)
                        zf.write(fpath, arcname)
            size = Path(out_file).stat().st_size
            self.log_event("AGIEM", f"Backup created: {out_file} ({size} bytes)")
            return {"backup_file": out_file, "size_bytes": size}
        except Exception as exc:
            self.log_event("AGIEM", f"Backup failed: {exc}", "ERROR")
            return {"error": str(exc)}

    # ---------------------------
    # Log analysis (simple, real)
    # ---------------------------
    def analyze_logs(self, log_path: str, tail: int = 200) -> Dict[str, Any]:
        """Scan log files under `log_path` and extract recent ERROR/WARNING lines.

        Returns a summary dict with counts and sample lines. This is intentionally
        conservative: it does not parse proprietary formats.
        """
        log_dir = Path(log_path)
        if not log_dir.exists() or not log_dir.is_dir():
            self.log_event("AGIEM", f"Log directory not found: {log_path}", "WARN")
            return {"anomalies_count": 0, "samples": []}

        anomalies: List[str] = []
        try:
            for file in sorted(log_dir.glob("*.log")):
                try:
                    with file.open("r", encoding="utf-8", errors="ignore") as fh:
                        lines = fh.readlines()[-tail:]
                        for ln in lines:
                            if any(k in ln for k in ("ERROR", "CRIT", "FAIL", "Exception")):
                                anomalies.append(f"{file.name}: {ln.strip()}")
                except Exception as e_file:
                    logger.debug(f"Could not read log {file}: {e_file}")
        except Exception as e:
            logger.exception("Unhandled exception during analyze_logs")

        sample = anomalies[-10:]
        report = {"anomalies_count": len(anomalies), "samples": sample}
        self.log_event("AGIEM", f"Log analysis: {report['anomalies_count']} anomalies found")
        return report

    def __init__(self, hq_event_url: str = "http://localhost:7777/mesh/event") -> None:
        self.hq_event_url = hq_event_url
        self.nodes: Dict[str, Dict[str, Any]] = {
            "ALBA": {"role": "data_collector", "status": "unknown"},
            "ALBI": {"role": "neural_processor", "status": "unknown"},
            "JONA": {"role": "coordinator", "status": "unknown"},
        }
        self.stages: Dict[str, ReproductionStage] = {
            "ALBA": ReproductionStage(
                name="ALBA",
                role="Knowledge ingestion",
                description="Absorb open knowledge sources and prepare learning corpora.",
            ),
            "ALBI": ReproductionStage(
                name="ALBI",
                role="Cognitive synthesis",
                description="Transform labor bits into candidate intelligences and models.",
            ),
            "JONA": ReproductionStage(
                name="JONA",
                role="Conscious alignment",
                description="Apply awareness, ethics and safety alignment to newborn systems.",
            ),
            "ASI": ReproductionStage(
                name="ASI",
                role="Operational deployment",
                description="Deliver conscious systems, automate APIs and observe live feedback.",
            ),
        }
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.logs: List[Dict[str, Any]] = []
        self._pipeline: Optional["ReproductionPipeline"] = None
        self.history_limit = 50
        self.reproduction_history: List[Dict[str, Any]] = []
        self.center_stats: Dict[str, Dict[str, Any]] = {}
        self._active_center_counts: Dict[str, int] = {}
        self._cycle_lock = threading.Lock()

    # ---------------------------
    # Event logging & HQ relay
    # ---------------------------
    def log_event(self, source: str, message: str, level: str = "INFO", stage: Optional[str] = None) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "level": level,
            "message": message,
        }
        if stage:
            entry["stage"] = stage
        self.logs.append(entry)
        if level.upper() == "ERROR":
            logger.error(f"[{source}] {message}")
        elif level.upper() == "WARN" or level.upper() == "WARNING":
            logger.warning(f"[{source}] {message}")
        else:
            logger.info(f"[{source}] {message}")

        # Best-effort send to HQ (non-blocking posture would be better in prod)
        if requests is not None and self.hq_event_url:
            try:
                requests.post(self.hq_event_url, json=entry, timeout=5)
            except Exception as exc:
                logger.debug(f"HQ not reachable ({self.hq_event_url}): {exc}")

    # ---------------------------
    # Health & status helpers
    # ---------------------------
    def update_node_status(self, node: str, status: str) -> None:
        if node not in self.nodes:
            self.log_event("AGIEM", f"Unknown node attempted update: {node}", "WARN")
            return
        self.nodes[node]["status"] = status
        self.log_event("AGIEM", f"Node {node} status updated to {status}", "INFO")
    def record_stage_metric(self, stage_name: str, metric_key: str, value: Any) -> None:
        stage = self.stages.get(stage_name)
        if stage is None:
            self.log_event("AGIEM", f"Unknown stage metric update: {stage_name}.{metric_key}", "WARN")
            return
        stage.record_metric(metric_key, value)
        self.log_event(stage_name, f"metric {metric_key}={value}", stage=stage_name)

    def add_stage_note(self, stage_name: str, message: str, level: str = "INFO") -> None:
        stage = self.stages.get(stage_name)
        if stage is None:
            self.log_event("AGIEM", f"Unknown stage note target: {stage_name}", "WARN")
            return
        stage.add_note(message, level=level)
        self.log_event(stage_name, message, level=level, stage=stage_name)

    def reproduction_inventory(self) -> List[Dict[str, Any]]:
        ordered = []
        for stage_key in ("ALBA", "ALBI", "JONA", "ASI"):
            stage = self.stages.get(stage_key)
            if stage is None:
                continue
            ordered.append(
                {
                    "name": stage.name,
                    "role": stage.role,
                    "description": stage.description,
                    "metrics": stage.metrics,
                    "notes": stage.notes,
                }
            )
        return ordered

    def record_cycle_result(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        enriched = dict(payload)
        enriched.setdefault("cycle_id", str(uuid.uuid4()))
        enriched.setdefault("recorded_at", datetime.now(timezone.utc).isoformat())
        self.reproduction_history.append(enriched)
        if len(self.reproduction_history) > self.history_limit:
            self.reproduction_history = self.reproduction_history[-self.history_limit :]
        return enriched

    def _resolve_center_key(self, metadata: Optional[Dict[str, Any]]) -> str:
        if not metadata:
            return "default"
        center = metadata.get("center")
        if isinstance(center, dict):
            for key in ("id", "name", "slug"):
                value = center.get(key)
                if value:
                    return str(value)
        elif isinstance(center, str):
            return center
        for key in ("center_name", "center_id", "tenant", "tenant_id"):
            value = metadata.get(key)
            if value:
                return str(value)
        return "default"

    def _build_active_snapshot_locked(self, center_key: str) -> Dict[str, Any]:
        per_center = {name: count for name, count in self._active_center_counts.items()}
        total = sum(per_center.values())
        return {
            "per_center": per_center,
            "total_active_cycles": total,
            "center_active_cycles": per_center.get(center_key, 0),
        }

    def _register_cycle_start(self, center_key: str) -> Dict[str, Any]:
        with self._cycle_lock:
            self._active_center_counts[center_key] = self._active_center_counts.get(center_key, 0) + 1
            snapshot = self._build_active_snapshot_locked(center_key)
        return snapshot

    def _snapshot_active_counts(self, center_key: str) -> Dict[str, Any]:
        with self._cycle_lock:
            return self._build_active_snapshot_locked(center_key)

    def _register_cycle_end(self, center_key: str) -> Dict[str, Any]:
        with self._cycle_lock:
            if center_key in self._active_center_counts:
                remaining = self._active_center_counts[center_key] - 1
                if remaining > 0:
                    self._active_center_counts[center_key] = remaining
                else:
                    self._active_center_counts.pop(center_key, None)
            snapshot = self._build_active_snapshot_locked(center_key)
        return snapshot

    def _update_center_metrics(self, center_key: str, cycle_result: Dict[str, Any]) -> None:
        duration = float(cycle_result.get("cycle_duration_seconds") or 0.0)
        recorded_at = cycle_result.get("recorded_at")
        cycle_id = cycle_result.get("cycle_id")
        metadata = cycle_result.get("metadata") or {}
        summary = cycle_result.get("summary") or {}
        asi_summary = summary.get("asi") or {}
        health_score = asi_summary.get("health_score")
        asi_status = asi_summary.get("asi_status")

        with self._cycle_lock:
            stats = self.center_stats.setdefault(
                center_key,
                {
                    "cycle_count": 0,
                    "total_duration": 0.0,
                    "avg_cycle_duration": 0.0,
                    "last_cycle_duration": 0.0,
                    "last_cycle_id": None,
                    "last_recorded_at": None,
                    "last_health_score": None,
                    "last_status": None,
                    "specializations": [],
                },
            )
            stats["cycle_count"] += 1
            stats["total_duration"] += duration
            stats["avg_cycle_duration"] = round(stats["total_duration"] / stats["cycle_count"], 3)
            stats["last_cycle_duration"] = duration
            stats["last_cycle_id"] = cycle_id
            stats["last_recorded_at"] = recorded_at
            stats["last_health_score"] = health_score
            stats["last_status"] = asi_status

            specialization = metadata.get("specialization")
            if specialization:
                base = set(stats.get("specializations") or [])
                base.add(str(specialization))
                stats["specializations"] = sorted(base)

            stats["active_cycles"] = self._active_center_counts.get(center_key, 0)
            stats["active_per_center"] = {name: count for name, count in self._active_center_counts.items()}

    def _extract_stage_payload(self, cycle_result: Dict[str, Any], stage_name: str) -> Dict[str, Any]:
        for stage in cycle_result.get("stages", []):
            if stage.get("stage") == stage_name:
                return stage
        return {}

    def _build_economy_payload(self, cycle_result: Dict[str, Any]) -> Optional[Dict[str, int]]:
        summary = cycle_result.get("summary") or {}
        alba_summary = summary.get("alba") or {}
        alba_frames = int(alba_summary.get("frames_ingested") or 0)

        albi_stage = self._extract_stage_payload(cycle_result, "ALBI")
        anomalies = albi_stage.get("anomalies")
        if isinstance(anomalies, list):
            albi_insights = len(anomalies)
        else:
            albi_recommendations = summary.get("albi") or []
            albi_insights = len(albi_recommendations) if isinstance(albi_recommendations, list) else 0

        jona_stage = self._extract_stage_payload(cycle_result, "JONA")
        jona_status = str(jona_stage.get("status") or "").lower()
        jona_validations = 1 if jona_status in {"aligned", "needs-review", "pending", "attention"} else 0

        asi_stage = self._extract_stage_payload(cycle_result, "ASI")
        asi_generated = asi_stage.get("generated_api")
        if not asi_generated:
            asi_block = summary.get("asi") or {}
            asi_generated = asi_block.get("generated_api")
        asi_apis = 1 if asi_generated else 0

        if not any([alba_frames, albi_insights, jona_validations, asi_apis]):
            return None

        return {
            "alba_frames": alba_frames,
            "albi_insights": albi_insights,
            "jona_validations": jona_validations,
            "asi_apis": asi_apis,
        }

    def _push_economy_update(self, cycle_result: Dict[str, Any]) -> None:
        if requests is None:
            return
        payload = self._build_economy_payload(cycle_result)
        if not payload:
            return
        target = os.getenv("ECONOMY_API_URL", "http://127.0.0.1:9093/economy/compute")
        if not target:
            return
        try:
            requests.post(target, json=payload, timeout=3)
        except Exception as exc:
            self.log_event("AGIEM", f"Economy dispatch failed: {exc}", "DEBUG")

    def multi_tenant_metrics(self) -> Dict[str, Any]:
        with self._cycle_lock:
            centers_snapshot = {
                center: {
                    **{k: v for k, v in stats.items() if k != "total_duration"},
                }
                for center, stats in self.center_stats.items()
            }
            total_active = sum(self._active_center_counts.values())
            return {
                "total_centers": len(centers_snapshot),
                "total_active_cycles": total_active,
                "active_per_center": {name: count for name, count in self._active_center_counts.items()},
                "centers": centers_snapshot,
            }

    def get_pipeline(self) -> "ReproductionPipeline":
        if self._pipeline is None:
            self._pipeline = ReproductionPipeline(self)
        return self._pipeline

    def run_reproduction_cycle(
        self,
        *,
        data_root: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        center_key = self._resolve_center_key(metadata or {})
        start_snapshot = self._register_cycle_start(center_key)
        pipeline = self.get_pipeline()
        if data_root:
            pipeline.set_data_root(data_root)
        result: Dict[str, Any] = {}
        mid_snapshot: Optional[Dict[str, Any]] = None
        try:
            result = pipeline.run_cycle(metadata)
            mid_snapshot = self._snapshot_active_counts(center_key)
        except Exception as exc:
            self.log_event("AGIEM", f"Cycle execution failed: {exc}", "ERROR")
            result = {
                "error": str(exc),
                "cycle_started": datetime.now(timezone.utc).isoformat(),
                "cycle_duration_seconds": 0.0,
                "stages": [],
                "summary": {},
                "metadata": metadata,
            }
        finally:
            end_snapshot = self._register_cycle_end(center_key)

        multi_tenant_payload = {
            "center": center_key,
            "active_counts": {
                "at_start": start_snapshot,
                "during_cycle": mid_snapshot or start_snapshot,
                "after_cycle": end_snapshot,
            },
        }
        result["multi_tenant"] = multi_tenant_payload
        enriched = self.record_cycle_result(result)
        self._update_center_metrics(center_key, enriched)
        self._push_economy_update(enriched)
        return enriched


class ReproductionPipeline:
    """Runs the ALBA->ALBI->JONA->ASI cycle and records telemetry."""

    def __init__(self, core: AGIEMCore, *, data_root: Optional[str] = None) -> None:
        self.core = core
        self.data_root = Path(data_root) if data_root else Path.cwd() / "data"
        self._alba = AlbaCore(auto_start=True) if AlbaCore else None
        self._albi = AlbiCore() if AlbiCore else None
        self._asi = ASICore() if ASICore else None
        self._self_api = SelfGeneratingAPI() if SelfGeneratingAPI else None
        self._proposal_lab = ResearchProposalLab() if ResearchProposalLab else None

    def set_data_root(self, root: str | os.PathLike[str]) -> None:
        self.data_root = Path(root)

    def _parse_timestamp(self, value: Any) -> Optional[float]:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            normalized = value.strip()
            if normalized.endswith("Z"):
                normalized = normalized[:-1] + "+00:00"
            try:
                return datetime.fromisoformat(normalized).timestamp()
            except ValueError:
                try:
                    return float(normalized)
                except ValueError:
                    return None
        return None

    def _ingest_frame_dict(self, frame: Dict[str, Any]) -> Optional[Any]:
        if self._alba is None:
            return None
        sensor_block = frame.get("sensors")
        if isinstance(sensor_block, dict):
            channels_source = sensor_block
        else:
            channels_source = frame.get("channels") if isinstance(frame.get("channels"), dict) else None
        if not isinstance(channels_source, dict):
            return None

        channels: Dict[str, float] = {}
        for key, value in channels_source.items():
            try:
                channels[key] = float(value)
            except (TypeError, ValueError):
                continue
        if not channels:
            return None

        timestamp_value = self._parse_timestamp(frame.get("timestamp"))
        metadata = {k: v for k, v in frame.items() if k not in ("sensors", "channels")}
        ingested = self._alba.ingest(channels, metadata=metadata, timestamp=timestamp_value)
        return ingested

    def _ingest_file_payload(self, payload: Any) -> int:
        ingested_count = 0
        if isinstance(payload, list):
            for entry in payload:
                if isinstance(entry, dict) and self._ingest_frame_dict(entry):
                    ingested_count += 1
        elif isinstance(payload, dict):
            frames = payload.get("frames")
            if isinstance(frames, list):
                for entry in frames:
                    if isinstance(entry, dict) and self._ingest_frame_dict(entry):
                        ingested_count += 1
            elif self._ingest_frame_dict(payload):
                ingested_count += 1
        return ingested_count

    def _ingest_latest_from_api(self) -> Optional[Any]:
        if self._alba is None or requests is None:
            return None
        alba_api_url = os.getenv("ALBA_API_URL", "http://127.0.0.1:9091/alba/latest")
        try:
            response = requests.get(alba_api_url, timeout=5)
        except Exception as exc:
            self.core.add_stage_note("ALBA", f"API fetch failed: {exc}", "WARN")
            return None
        if response.status_code != 200:
            if response.status_code != 404:
                self.core.add_stage_note("ALBA", f"API responded with {response.status_code}", "WARN")
            return None
        try:
            payload = response.json()
        except ValueError as exc:
            self.core.add_stage_note("ALBA", f"Invalid JSON from API: {exc}", "WARN")
            return None
        if isinstance(payload, dict):
            status = payload.get("status")
            if status == "no_data":
                return None
            frame = payload.get("frame") if "frame" in payload else payload.get("latest")
            if isinstance(frame, dict):
                result = self._ingest_frame_dict(frame)
                if result is None:
                    self.core.add_stage_note("ALBA", "API frame missing sensors or channels", "WARN")
                return result
        return None

    def run_cycle(self, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pipeline_state: Dict[str, Any] = {}
        if metadata:
            pipeline_state["reproduction_meta"] = metadata
            if isinstance(metadata, dict):
                for key, value in metadata.items():
                    if key.startswith("state_"):
                        pipeline_state[key] = value
        stage_reports: List[Dict[str, Any]] = []
        cycle_started = datetime.now(timezone.utc).isoformat()
        start_time = time.time()

        pipeline_state, report = self._run_stage("ALBA", self._run_alba, pipeline_state)
        stage_reports.append({"stage": "ALBA", **report})

        pipeline_state, report = self._run_stage("ALBI", self._run_albi, pipeline_state)
        stage_reports.append({"stage": "ALBI", **report})

        pipeline_state, report = self._run_stage("JONA", self._run_jona, pipeline_state)
        stage_reports.append({"stage": "JONA", **report})

        pipeline_state, report = self._run_stage("ASI", self._run_asi, pipeline_state)
        stage_reports.append({"stage": "ASI", **report})

        total_duration = round(time.time() - start_time, 3)
        summary = self._build_summary(pipeline_state, stage_reports)
        return {
            "cycle_started": cycle_started,
            "cycle_duration_seconds": total_duration,
            "stages": stage_reports,
            "summary": summary,
            "metadata": pipeline_state.get("reproduction_meta"),
        }

    def _run_stage(
        self,
        name: str,
        handler,
        state: Dict[str, Any],
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        self.core.add_stage_note(name, "Stage started")
        stage_start = time.time()
        result = handler(state)
        duration = round(time.time() - stage_start, 3)

        self.core.record_stage_metric(name, "last_duration_seconds", duration)
        for key, value in result.metrics.items():
            self.core.record_stage_metric(name, key, value)

        message = result.message or "Completed"
        self.core.add_stage_note(name, message)

        new_state = dict(state)
        new_state.update(result.updated_state)

        payload = dict(result.public_payload)
        payload.setdefault("message", message)
        payload["duration_seconds"] = duration
        return new_state, payload

    def _run_alba(self, state: Dict[str, Any]) -> StageResult:
        if self._alba is None:
            self.core.add_stage_note("ALBA", "AlbaCore module unavailable", "ERROR")
            return StageResult(
                message="AlbaCore unavailable",
                public_payload={"error": "alba_core_missing"},
            )

        source_dir = Path(state.get("alba_source_dir") or self.data_root / "alba")
        processed_files: List[str] = []
        ingestion_sources: List[str] = []
        file_frames = 0
        api_frame = None

        if source_dir.exists() and source_dir.is_dir():
            for path in sorted(source_dir.glob("*.json")):
                try:
                    data = json.loads(path.read_text(encoding="utf-8-sig"))
                except Exception as exc:
                    self.core.add_stage_note("ALBA", f"Failed to parse {path.name}: {exc}", "WARN")
                    continue

                ingested = self._ingest_file_payload(data)
                if ingested:
                    file_frames += ingested
                    processed_files.append(path.name)
                    ingestion_sources.append(f"file:{path.name}")
        else:
            self.core.add_stage_note("ALBA", f"Source directory missing: {source_dir}", "WARN")

        api_result = self._ingest_latest_from_api()
        if api_result is not None:
            api_frame = api_result
            ingestion_sources.append("api:latest")

        total_frames = file_frames + (1 if api_frame else 0)
        history = self._alba.history()
        last_frame = self._alba.last_frame()
        metrics = {
            "frames_ingested": total_frames,
            "file_frames": file_frames,
            "api_frame": bool(api_frame),
            "total_history": len(history),
            "source_files": len(processed_files),
        }
        public_payload = {
            "source_dir": str(source_dir),
            "processed_files": processed_files,
            "ingestion_sources": ingestion_sources,
            "frames_ingested": total_frames,
            "total_history": len(history),
            "last_timestamp": last_frame.timestamp if last_frame else None,
        }
        if api_frame is not None:
            public_payload["api_latest"] = {
                "timestamp": api_frame.metadata.get("timestamp"),
                "source": api_frame.metadata.get("source"),
                "node": api_frame.metadata.get("node"),
            }
        updated_state = {
            "alba_history": history,
            "alba_summary": public_payload,
            "alba_source_dir": str(source_dir),
        }
        message = (
            f"Ingested {total_frames} frames (files={file_frames}, api={'yes' if api_frame else 'no'})"
            if total_frames
            else "No frames ingested"
        )
        return StageResult(updated_state=updated_state, metrics=metrics, message=message, public_payload=public_payload)

    def _run_albi(self, state: Dict[str, Any]) -> StageResult:
        if self._albi is None:
            self.core.add_stage_note("ALBI", "AlbiCore module unavailable", "ERROR")
            return StageResult(
                message="AlbiCore unavailable",
                public_payload={"error": "albi_core_missing"},
            )

        history = state.get("alba_history") or []
        if not history:
            self.core.add_stage_note("ALBI", "No ALBA history available", "WARN")
            metrics = {"anomaly_count": 0, "avg_channel_count": 0}
            payload = {"status": "no-data"}
            return StageResult(
                updated_state={"albi_recommendations": payload},
                metrics=metrics,
                message="Skipped, missing ALBA data",
                public_payload=payload,
            )

        insight = self._albi.learn_from_alba(history)
        recommendations = self._albi.recommendations()
        metrics = {
            "anomaly_count": len(insight.anomalies),
            "avg_channel_count": len(insight.summary),
        }
        public_payload = {
            "summary": insight.summary,
            "anomalies": insight.anomalies,
            "recommendations": recommendations,
        }
        updated_state = {
            "albi_insight": insight,
            "albi_recommendations": recommendations,
        }
        message = "Generated insight" if insight.summary else "Insight generated with empty summary"
        return StageResult(updated_state=updated_state, metrics=metrics, message=message, public_payload=public_payload)

    def _run_jona(self, state: Dict[str, Any]) -> StageResult:
        insight = state.get("albi_insight")
        if insight is None:
            self.core.add_stage_note("JONA", "No ALBI insight available", "WARN")
            alignment = {
                "status": "pending",
                "focus_channels": [],
                "alignment_score": 0.0,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "ethics_profile": "Feminine Care Principle",
            }
            return StageResult(
                updated_state={"jona_alignment": alignment},
                metrics={"alignment_score": 0.0, "focus_channels": 0},
                message="Alignment pending",
                public_payload=alignment,
            )

        focus_channels = list(insight.anomalies)
        denominator = max(len(insight.summary) or 1, 1)
        score = max(0.0, 1.0 - len(focus_channels) / denominator)
        alignment = {
            "status": "aligned" if not focus_channels else "needs-review",
            "focus_channels": focus_channels,
            "alignment_score": round(score, 3),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "ethics_profile": "Feminine Care Principle",
        }
        metrics = {
            "alignment_score": round(score, 3),
            "focus_channels": len(focus_channels),
        }
        message = "Alignment verified" if not focus_channels else "Alignment requires review"
        return StageResult(
            updated_state={"jona_alignment": alignment},
            metrics=metrics,
            message=message,
            public_payload=alignment,
        )

    def _run_asi(self, state: Dict[str, Any]) -> StageResult:
        if self._asi is None:
            self.core.add_stage_note("ASI", "ASICore module unavailable", "WARN")
            payload = {"status": "degraded", "reason": "asi_core_missing"}
            return StageResult(public_payload=payload, message="ASI status unavailable")

        realtime = self._asi.realtime_status()
        health = getattr(self._asi, "health_score", None)
        alignment = state.get("jona_alignment", {})
        if alignment.get("status") == "needs-review":
            self._asi.status = "attention"
        else:
            self._asi.status = "active"

        metrics = {"health_score": health or 0.0}
        public_payload = {
            "realtime": realtime,
            "health_score": health,
            "asi_status": self._asi.status,
        }
        updated_state = {
            "asi_operational": public_payload,
        }

        if self._self_api is not None:
            insight_obj = state.get("albi_insight")
            if insight_obj is not None:
                insight_payload = {
                    "summary": getattr(insight_obj, "summary", {}),
                    "anomalies": list(getattr(insight_obj, "anomalies", [])),
                    "source_frame_count": getattr(insight_obj, "source_frame_count", 0),
                }
            else:
                insight_payload = {}
            context = {
                "alignment": alignment,
                "insight": insight_payload,
            }
            try:
                artifact = self._self_api.orchestrate(context)
                public_payload["generated_api"] = artifact.summary
                updated_state["generated_api"] = artifact.summary
                metrics["generated_api"] = True
                self.core.add_stage_note("ASI", f"Generated API artifact {artifact.summary.get('domain')}")
            except Exception as exc:
                self.core.add_stage_note("ASI", f"API generation failed: {exc}", "WARN")

        if self._proposal_lab is not None:
            insight_obj = state.get("albi_insight")
            if insight_obj is not None:
                insight_dict = {
                    "summary": getattr(insight_obj, "summary", {}),
                    "anomalies": list(getattr(insight_obj, "anomalies", [])),
                    "source_frame_count": getattr(insight_obj, "source_frame_count", 0),
                }
            else:
                insight_dict = {}
            proposal_context = {
                "alignment": alignment,
                "insight": insight_dict,
                "generated_api": updated_state.get("generated_api"),
                "alba_summary": state.get("alba_summary"),
                "albi_recommendations": state.get("albi_recommendations"),
            }
            reproduction_metadata = state.get("reproduction_meta") or {}
            if isinstance(reproduction_metadata, dict):
                proposal_context.update(reproduction_metadata)
            try:
                brief = self._proposal_lab.build_brief(proposal_context)
                packet_prefix = (
                    brief.created_at
                    .replace(":", "")
                    .replace("-", "")
                    .replace("T", "_")
                    .replace("+", "")
                )
                # Store the proposal packet in the pipeline state and public payload
                updated_state["generated_api"] = getattr(brief, "summary", {})
                public_payload["proposal_packet"] = getattr(brief, "summary", {})
                metrics["proposal_packet"] = True
                self.core.add_stage_note("ASI", f"Proposal packet generated with prefix {packet_prefix}")
            except Exception as exc:
                self.core.add_stage_note("ASI", f"Proposal packet generation failed: {exc}", "WARN")
        # Ensure StageResult is always returned
        return StageResult(
            updated_state=updated_state,
            metrics=metrics,
            message="ASI stage completed",
            public_payload=public_payload,
        )

    def _build_summary(self, pipeline_state: dict, stage_reports: list) -> dict:
        """Aggregate a summary from the pipeline state and stage reports."""
        summary = {}
        # ALBA summary
        alba_summary = pipeline_state.get("alba_summary", {})
        summary["alba"] = {
            "frames_ingested": alba_summary.get("frames_ingested", 0),
            "source_files": alba_summary.get("source_files", 0),
        }
        # ALBI summary
        albi_insight = pipeline_state.get("albi_insight")
        if albi_insight is not None:
            summary["albi"] = {
                "anomalies": list(getattr(albi_insight, "anomalies", [])),
                "summary": getattr(albi_insight, "summary", {}),
                "source_frame_count": getattr(albi_insight, "source_frame_count", 0),
            }
        else:
            summary["albi"] = {}
        # JONA summary
        jona_alignment = pipeline_state.get("jona_alignment", {})
        summary["jona"] = {
            "status": jona_alignment.get("status"),
            "alignment_score": jona_alignment.get("alignment_score"),
            "focus_channels": jona_alignment.get("focus_channels"),
        }
        # ASI summary
        asi_operational = pipeline_state.get("asi_operational", {})
        summary["asi"] = {
            "health_score": asi_operational.get("health_score"),
            "asi_status": asi_operational.get("asi_status"),
            "generated_api": asi_operational.get("generated_api") if "generated_api" in asi_operational else None,
        }
        # Proposal packet if present
        if "generated_api" in pipeline_state:
            summary["asi"]["proposal_packet"] = pipeline_state["generated_api"]
        # Add metadata if present
        if "reproduction_meta" in pipeline_state:
            summary["metadata"] = pipeline_state["reproduction_meta"]
        return summary

class ReproductionScheduler:
    """Lightweight scheduler that loops the reproduction pipeline."""

    def __init__(
        self,
        core: AGIEMCore,
        *,
        interval_seconds: float = 300.0,
        data_root: Optional[str] = None,
        callback: Optional[Any] = None,
    ) -> None:
        self.core = core
        self.interval_seconds = max(5.0, float(interval_seconds))
        self.data_root = data_root
        self.callback = callback
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_result: Optional[Dict[str, Any]] = None
        self._cycle_count = 0
        self.started_at = datetime.now(timezone.utc).isoformat()

    def start(self) -> None:
        if self.is_running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="ReproductionScheduler", daemon=True)
        self._thread.start()
        self.core.log_event("AGIEM", f"Reproduction scheduler started (interval={self.interval_seconds}s)")

    def stop(self, timeout: float = 5.0) -> None:
        if not self._thread:
            return
        self._stop_event.set()
        self._thread.join(timeout=timeout)
        self._thread = None
        self.core.log_event("AGIEM", "Reproduction scheduler stopped")

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def cycle_count(self) -> int:
        return self._cycle_count

    @property
    def last_result(self) -> Optional[Dict[str, Any]]:
        return self._last_result

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            start = time.time()
            try:
                result = self.core.run_reproduction_cycle(data_root=self.data_root)
                self._last_result = result
            except Exception as exc:
                self.core.log_event("AGIEM", f"Reproduction cycle failed in scheduler: {exc}", "ERROR")
    # ---------------------------
    # Log analysis (simple, real)
    # ---------------------------
    # (Moved to AGIEMCore)

    # ---------------------------
    # Backup (safe, non-destructive)
    # ---------------------------
    def backup_data(self, path: str, out_file: Optional[str] = None) -> Dict[str, Any]:
        """Create a zip archive of `path` and return summary with size (bytes).

        This function performs only read operations and writes a single zip file.
        """
        source = Path(path)
        if not source.exists():
            msg = f"Backup source not found: {path}"
            self.core.log_event("AGIEM", msg, "ERROR")
            return {"error": msg}

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        if out_file is None:
            out_file = str(Path.cwd() / f"agiem_backup_{timestamp}.zip")

        try:
            with zipfile.ZipFile(out_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(source):
                    for fname in files:
                        fpath = Path(root) / fname
                        # store relative path in archive
                        arcname = str(Path(root).relative_to(source) / fname)
                        zf.write(fpath, arcname)
            size = Path(out_file).stat().st_size
            self.core.log_event("AGIEM", f"Backup created: {out_file} ({size} bytes)")
            return {"backup_file": out_file, "size_bytes": size}
        except Exception as exc:
            self.core.log_event("AGIEM", f"Backup failed: {exc}", "ERROR")
            return {"error": str(exc)}


class NodeReal:
    """Represents a real Kloud/ASI node that reports metrics and can upload files.

    This class does not synthesize data; it reads PSUTIL and local files.
    """

    def __init__(self, core: AGIEMCore, node_id: str = "CLX-REAL") -> None:
        self.core = core
        self.node_id = node_id
        self.hostname = socket.gethostname()
        try:
            self.ip = socket.gethostbyname(self.hostname)
        except Exception:
            self.ip = "127.0.0.1"
        # endpoints can be configured externally
        self.api_audio = os.getenv("AGIEM_API_AUDIO", "https://kloud.com/api/uploads/audio/process")
        self.api_eeg = os.getenv("AGIEM_API_EEG", "https://kloud.com/api/uploads/eeg/process")

    def collect_metrics(self) -> Dict[str, Any]:
        if psutil is None:
            raise RuntimeError("psutil is required for real metrics. Install psutil and retry.")
        net = psutil.net_io_counters()
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hostname": self.hostname,
            "ip": self.ip,
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage(os.path.sep).percent,
            "net_sent_mb": round(net.bytes_sent / (1024**2), 2),
            "net_recv_mb": round(net.bytes_recv / (1024**2), 2),
            "process_count": len(psutil.pids()),
        }
        self.core.log_event(self.node_id, f"Collected metrics: {metrics}")
        return metrics

    def upload_file(self, filepath: str, kind: str = "audio") -> Dict[str, Any]:
        """Upload a file to the configured remote endpoint (if requests available).

        Returns response status code and optional text. This is a safe, best-effort
        operation â€” it will not remove or alter local files.
        """
        fp = Path(filepath)
        if not fp.exists() or not fp.is_file():
            msg = f"File not found: {filepath}"
            self.core.log_event(self.node_id, msg, "WARN")
            return {"error": msg}

        endpoint = self.api_audio if kind == "audio" else self.api_eeg
        if requests is None:
            msg = "requests library not available; cannot upload"
            self.core.log_event(self.node_id, msg, "ERROR")
            return {"error": msg}

        try:
            with fp.open("rb") as fh:
                files = {"file": (fp.name, fh)}
                res = requests.post(endpoint, files=files, timeout=15)
            self.core.log_event(self.node_id, f"Uploaded {fp.name} -> {endpoint} ({res.status_code})")
            return {"status_code": res.status_code, "text": res.text[:1000]}
        except Exception as exc:
            self.core.log_event(self.node_id, f"Upload failed: {exc}", "ERROR")
            return {"error": str(exc)}


class MeshReporter:
    """Responsible for registering node and sending telemetry to Mesh HQ.

    Configuration is provided via constructor or environment variables.
    """

    def __init__(self, core: AGIEMCore, node_id: str = "clx-real", hq_base: str = "http://localhost:7777") -> None:
        self.core = core
        self.node_id = node_id
        self.hq_base = hq_base.rstrip("/")
        self.register_url = os.getenv("AGIEM_HQ_REGISTER", f"{self.hq_base}/mesh/register")
        self.status_url = os.getenv("AGIEM_HQ_STATUS", f"{self.hq_base}/mesh/status")

    def register(self, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = metadata or {
            "id": self.node_id,
            "hostname": socket.gethostname(),
            "ip": self._local_ip(),
            "type": "audio-neural",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if requests is None:
            self.core.log_event("MeshReporter", "requests not installed; cannot register", "ERROR")
            return {"error": "requests_missing"}

        try:
            res = requests.post(self.register_url, json=payload, timeout=8)
            self.core.log_event("MeshReporter", f"Register response: {res.status_code}")
            return {"status_code": res.status_code, "text": res.text}
        except Exception as exc:
            self.core.log_event("MeshReporter", f"Register failed: {exc}", "ERROR")
            return {"error": str(exc)}

    def send_status(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        payload = {"id": self.node_id, "metrics": metrics, "timestamp": datetime.now(timezone.utc).isoformat()}
        if requests is None:
            self.core.log_event("MeshReporter", "requests not installed; cannot send status", "ERROR")
            return {"error": "requests_missing"}

        try:
            res = requests.post(self.status_url, json=payload, timeout=8)
            self.core.log_event("MeshReporter", f"Status sent: {res.status_code}")
            return {"status_code": res.status_code, "text": res.text}
        except Exception as exc:
            self.core.log_event("MeshReporter", f"Status send failed: {exc}", "ERROR")
            return {"error": str(exc)}

    def _local_ip(self) -> str:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


# ---------------------------
# CLI
# ---------------------------

def _build_parser():
    p = argparse.ArgumentParser(prog="agiem_core.py", description="AGIEM Core â€” real-only operations")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Print cluster overview and health")
    sub.add_parser("inventory", help="Show ALBA->ALBI->JONA->ASI instrumentation")
    sub.add_parser("proposals", help="List generated research proposal packets")

    a_an = sub.add_parser("analyze", help="Analyze logs for anomalies")
    a_an.add_argument("--logs", default=str(Path("./logs")), help="Path to logs directory")

    a_bu = sub.add_parser("backup", help="Create a backup zip of a directory")
    a_bu.add_argument("--path", required=True, help="Path to backup (directory)")
    a_bu.add_argument("--out", default=None, help="Output zip file path")

    a_reg = sub.add_parser("register", help="Register this node at Mesh HQ")
    a_reg.add_argument("--hq", default="http://localhost:7777", help="Mesh HQ base URL")
    a_reg.add_argument("--node-id", default="clx-real", help="Node identifier")

    a_report = sub.add_parser("report", help="Collect metrics and send status to HQ")
    a_report.add_argument("--hq", default="http://localhost:7777", help="Mesh HQ base URL")
    a_report.add_argument("--node-id", default="clx-real", help="Node identifier")

    a_upload = sub.add_parser("upload", help="Upload a file (audio or eeg)")
    a_upload.add_argument("--file", required=True, help="File to upload")
    a_upload.add_argument("--kind", choices=("audio","eeg"), default="audio")

    a_cycle = sub.add_parser("cycle", help="Run ALBA->ALBI->JONA->ASI reproduction cycle")
    a_cycle.add_argument("--data-root", default=None, help="Optional data root for ALBA ingestion")
    a_cycle.add_argument("--out", default=None, help="Write cycle summary JSON to this path")
    a_cycle.add_argument("--center", default=None, help="Name of the reproduction center executing the cycle")
    a_cycle.add_argument("--specialization", default=None, help="Domain specialization for this cycle (e.g. medical)")
    a_cycle.add_argument("--priority", default=None, help="Override proposal priority label")

    a_auto = sub.add_parser("autocycle", help="Loop reproduction cycles on an interval")
    a_auto.add_argument("--data-root", default=None, help="Optional data root for ALBA ingestion")
    a_auto.add_argument("--interval", type=float, default=300.0, help="Seconds between cycles (default 300)")
    a_auto.add_argument("--count", type=int, default=0, help="Stop after N cycles (0 = run indefinitely)")
    a_auto.add_argument("--out-dir", default=None, help="Directory where each cycle result is stored (optional)")
    a_auto.add_argument("--center", default=None, help="Name of the reproduction center executing the cycles")
    a_auto.add_argument("--specialization", default=None, help="Domain specialization for the cycles")
    a_auto.add_argument("--priority", default=None, help="Override proposal priority label")

    return p


def main(argv: Optional[List[str]] = None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    core = AGIEMCore()

    if args.cmd == "status":
        overview = {
            "started_at": core.started_at,
            "nodes": core.nodes,
            "cluster_health_percent": (
                sum(1 for n in core.nodes.values() if n.get("status") == "active") / len(core.nodes) * 100.0
                if core.nodes else 0.0
            ),
            "reproduction_stages": core.reproduction_inventory(),
            "reproduction_cycle_count": len(core.reproduction_history),
            "last_reproduction_cycle": core.reproduction_history[-1] if core.reproduction_history else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(overview, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "inventory":
        snapshot = core.reproduction_inventory()
        print(json.dumps(snapshot, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "proposals":
        proposals: List[Dict[str, Any]] = []
        for entry in core.reproduction_history:
            proposal = entry.get("summary", {}).get("asi", {}).get("proposal_packet")
            if not proposal:
                proposal = entry.get("summary", {}).get("metadata", {}).get("proposal_packet")
            if not proposal:
                proposal = entry.get("metadata", {}).get("proposal_packet")
            if proposal:
                proposals.append({
                    "cycle_id": entry.get("cycle_id"),
                    "recorded_at": entry.get("recorded_at"),
                    "proposal": proposal,
                })
        print(json.dumps(proposals, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "cycle":
        metadata = {}
        if args.center:
            metadata["center"] = {"name": args.center}
        if args.specialization:
            metadata["specialization"] = args.specialization
        if args.priority:
            metadata["priority"] = args.priority
        result = core.run_reproduction_cycle(data_root=args.data_root, metadata=metadata or None)
        if args.out:
            Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            core.log_event("AGIEM", f"Cycle summary written to {args.out}")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "autocycle":
        interval = max(5.0, float(args.interval))
        limit = int(args.count)
        executed = 0
        out_dir = None
        if args.out_dir:
            out_dir = Path(args.out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
        metadata = {}
        if args.center:
            metadata["center"] = {"name": args.center}
        if args.specialization:
            metadata["specialization"] = args.specialization
        if args.priority:
            metadata["priority"] = args.priority
        try:
            while True:
                started = time.time()
                result = core.run_reproduction_cycle(data_root=args.data_root, metadata=metadata or None)
                executed += 1
                if out_dir:
                    file_path = out_dir / f"cycle-{result['cycle_id']}.json"
                    file_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
                print(json.dumps({"cycle_id": result["cycle_id"], "recorded_at": result["recorded_at"]}, ensure_ascii=False))
                if limit > 0 and executed >= limit:
                    break
                elapsed = time.time() - started
                wait_for = max(0.0, interval - elapsed)
                if wait_for:
                    time.sleep(wait_for)
        except KeyboardInterrupt:
            core.log_event("AGIEM", "Autocycle interrupted by user", "WARN")
        return 0

    if args.cmd == "analyze":
        report = core.analyze_logs(args.logs)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "backup":
        r = core.backup_data(args.path, args.out)
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "register":
        reporter = MeshReporter(core, node_id=args.node_id, hq_base=args.hq)
        r = reporter.register()
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "report":
        reporter = MeshReporter(core, node_id=args.node_id, hq_base=args.hq)
        node = NodeReal(core, node_id=args.node_id)
        metrics = node.collect_metrics()
        r = reporter.send_status(metrics)
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "upload":
        node = NodeReal(core)
        r = node.upload_file(args.file, kind=args.kind)
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())


