"""Self-generating API laboratory utilities.

This module orchestrates the pipeline that detects a domain need, drafts
an OpenAPI specification, scaffolds FastAPI code, and stores artifacts for
review. It intentionally avoids synthetic randomness: every artifact is
built from the provided context and deterministic templates so auditors
can reproduce the output.
"""

from __future__ import annotations

import hashlib
import json
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class NeedProfile:
    """Description of the detected API requirement."""

    domain: str
    purpose: str
    priority: str
    tags: List[str] = field(default_factory=list)
    reference_channels: List[str] = field(default_factory=list)
    source_notes: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedArtifact:
    """Paths to generated deliverables plus basic metadata."""

    spec_path: Optional[Path]
    code_path: Optional[Path]
    manifest_path: Optional[Path]
    summary: Dict[str, Any]


class SelfGeneratingAPI:
    """Pipeline that produces review-ready API artifacts."""

    def __init__(
        self,
        *,
        output_root: Path | str = Path("generated_apis"),
        template_module: str = "generated_service",
    ) -> None:
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.template_module = template_module

    def orchestrate(self, context: Dict[str, Any]) -> GeneratedArtifact:
        profile = self.detect_need(context)
        spec = self.design_api_specification(profile)
        paths = self.persist_spec(profile, spec)
        code_path = self.generate_api(profile, spec)
        manifest_path = self.persist_manifest(profile, spec, code_path, context)
        summary = {
            "domain": profile.domain,
            "priority": profile.priority,
            "tags": profile.tags,
            "spec_path": str(paths) if paths else None,
            "code_path": str(code_path) if code_path else None,
            "manifest": str(manifest_path) if manifest_path else None,
        }
        context_summary: Dict[str, Any] = {}
        for key in ("center", "specialization"):
            if key in context:
                context_summary[key] = context[key]
        if context_summary:
            summary["context"] = context_summary
        return GeneratedArtifact(paths, code_path, manifest_path, summary)

    def detect_need(self, context: Dict[str, Any]) -> NeedProfile:
        alignment = context.get("alignment", {})
        insight = context.get("insight") or {}
        specialization = context.get("specialization")
        focus_channels: List[str] = list(alignment.get("focus_channels", []))
        base_tags = {alignment.get("status", "aligned"), insight.get("status", "ok")}

        if specialization:
            domain = specialization
            purpose = context.get(
                "specialization_purpose",
                f"Deliver domain services for {specialization}",
            )
            priority = context.get("specialization_priority") or (
                "high" if alignment.get("status") == "needs-review" else "normal"
            )
            base_tags.add("specialized")
            base_tags.add(specialization)
        elif focus_channels:
            domain = "neural-alignment"
            purpose = "Expose alignment metrics for remediation workflows"
            priority = "high" if alignment.get("status") == "needs-review" else "normal"
        else:
            domain = "system-telemetry"
            purpose = "Provide consolidated health metrics for downstream consumers"
            priority = "normal"

        source_notes = {
            "alignment": alignment,
            "insight": insight,
        }
        if specialization:
            source_notes["specialization"] = specialization
        if "center" in context:
            source_notes["center"] = context["center"]
        reference_channels = focus_channels or list(context.get("reference_channels", []))
        tags = sorted(base_tags)
        return NeedProfile(domain, purpose, priority, tags, reference_channels, source_notes, context=context)

    def design_api_specification(self, profile: NeedProfile) -> Dict[str, Any]:
        title = f"Kloud {profile.domain.replace('-', ' ').title()} API"
        description = textwrap.dedent(
            f"""
            This specification was generated automatically. It addresses the
            detected requirement: {profile.purpose}. Review the manifest for the
            source context.
            """
        ).strip()
        base_path = "/api/{}/status".format(profile.domain.replace("-", "/"))
        center_context = profile.context.get("center")
        specialization_context = profile.context.get("specialization")
        spec = {
            "openapi": "3.1.0",
            "info": {
                "title": title,
                "version": "1.0.0",
                "description": description,
                "tags": profile.tags,
            },
            "paths": {
                base_path: {
                    "get": {
                        "summary": "Fetch current status payload",
                        "tags": [profile.domain],
                        "responses": {
                            "200": {
                                "description": "Current metrics payload",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/StatusEnvelope"
                                        }
                                    }
                                },
                            }
                        },
                    }
                }
            },
            "components": {
                "schemas": {
                    "StatusEnvelope": {
                        "type": "object",
                        "properties": {
                            "timestamp": {"type": "string", "format": "date-time"},
                            "domain": {"type": "string"},
                            "priority": {"type": "string"},
                            "metrics": {"type": "object"},
                            "source_tags": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["timestamp", "domain", "priority", "metrics"],
                    }
                }
            },
        }
        if center_context is not None:
            spec["info"]["x-center"] = center_context
        if profile.reference_channels:
            spec["components"]["schemas"]["StatusEnvelope"]["properties"]["focus_channels"] = {
                "type": "array",
                "items": {"type": "string"},
            }
        if center_context is not None:
            spec["components"]["schemas"]["StatusEnvelope"]["properties"]["center"] = {
                "type": "object",
                "description": "Reproduction center metadata for routing and auditing.",
                "additionalProperties": True,
            }
        if specialization_context:
            spec["info"]["x-specialization"] = specialization_context
            spec["components"]["schemas"]["StatusEnvelope"]["properties"]["specialization"] = {
                "type": "string",
                "description": "Specialization focus associated with the generated service.",
            }
        return spec

    def persist_spec(self, profile: NeedProfile, spec: Dict[str, Any]) -> Optional[Path]:
        file_name = f"{profile.domain.replace('-', '_')}_spec.json"
        spec_path = self.output_root / file_name
        spec_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
        return spec_path

    def generate_api(self, profile: NeedProfile, spec: Dict[str, Any]) -> Optional[Path]:
        module_dir = self.output_root / self.template_module
        module_dir.mkdir(parents=True, exist_ok=True)
        file_path = module_dir / f"{profile.domain.replace('-', '_')}_service.py"
        body = self._render_fastapi_module(profile, spec)
        file_path.write_text(body, encoding="utf-8")
        return file_path

    def persist_manifest(
        self,
        profile: NeedProfile,
        spec: Dict[str, Any],
        code_path: Optional[Path],
        context: Dict[str, Any],
    ) -> Optional[Path]:
        digest = hashlib.sha256(json.dumps(spec, sort_keys=True).encode("utf-8")).hexdigest()
        manifest_profile = {
            "domain": profile.domain,
            "purpose": profile.purpose,
            "priority": profile.priority,
            "tags": profile.tags,
            "reference_channels": profile.reference_channels,
            "source_notes": profile.source_notes,
        }
        manifest = {
            "profile": manifest_profile,
            "spec_hash": digest,
            "code_path": str(code_path) if code_path else None,
        }
        if context.get("center") is not None:
            manifest["center_metadata"] = context["center"]
        if context.get("specialization"):
            manifest_profile["specialization"] = context["specialization"]
        manifest_profile["context_keys"] = sorted(str(key) for key in context.keys())
        manifest_path = self.output_root / f"{profile.domain.replace('-', '_')}_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest_path

    def _render_fastapi_module(self, profile: NeedProfile, spec: Dict[str, Any]) -> str:
        imports: List[str] = [
            "from fastapi import APIRouter",
            "from datetime import datetime, timezone",
        ]
        center_details = profile.context.get("center")

        imports_block = "\n".join(imports)

        lines: List[str] = [
            f"router = APIRouter(prefix=\"/auto\", tags=[\"{profile.domain}\"])",
            "",
            f"@router.get(\"/{profile.domain}/status\")",
            "async def generated_status():",
            "    now = datetime.now(timezone.utc).isoformat()",
            "    payload = {",
            "        \"timestamp\": now,",
            f"        \"domain\": \"{profile.domain}\",",
            f"        \"priority\": \"{profile.priority}\",",
            "        \"metrics\": {}",
            "    }",
        ]

        if profile.reference_channels:
            lines.append(f"    payload[\"focus_channels\"] = {repr(profile.reference_channels)}")
        lines.append(f"    payload[\"source_tags\"] = {repr(profile.tags)}")

        if center_details is not None:
            lines.append(f"    payload[\"center\"] = {repr(center_details)}")

        specialization = profile.context.get("specialization")
        if specialization:
            lines.append(f"    payload[\"specialization\"] = {repr(specialization)}")

        lines.append("    return payload")

        router_block = "\n".join(lines)
        return imports_block + "\n\n\n" + router_block + "\n"


