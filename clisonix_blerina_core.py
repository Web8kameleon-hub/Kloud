#!/usr/bin/env python3
"""
Kloud BLERINA Core — System-Wide Quality & Documentation
=============================================================
Central BLERINA utilities for all Kloud services:
- Quality Selector for output validation across all engines
- Auto-Documentation generator for consistent reporting
- EAP Pipeline utilities
- Gap Detection helpers

This module provides shared BLERINA functionality to ensure
consistent quality across all Kloud services.

Author: Kloud Team
Date: 2026-02-08
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class GapType(Enum):
    """Gap types for knowledge detection."""
    STRUCTURAL = "structural"
    LOGICAL = "logical"
    DEFINITIONAL = "definitional"
    CONTEXTUAL = "contextual"
    TEMPORAL = "temporal"
    TECHNICAL = "technical"
    PROCEDURAL = "procedural"
    FACTUAL = "factual"
    DATA = "data"


class QualityTier(Enum):
    """Output quality tiers."""
    EXCELLENT = "excellent"   # Score >= 0.9
    GOOD = "good"             # Score >= 0.75
    ACCEPTABLE = "acceptable" # Score >= 0.6
    NEEDS_WORK = "needs_work" # Score < 0.6


class DocumentType(Enum):
    """Types of auto-generated documents."""
    REPORT = "report"
    ANALYSIS = "analysis"
    API_DOC = "api_documentation"
    TUTORIAL = "tutorial"
    FAQ = "faq"
    CHANGELOG = "changelog"
    SUMMARY = "summary"


class ServiceType(Enum):
    """Kloud service types."""
    OCEAN = "ocean"
    ALBA = "alba"
    ALBI = "albi"
    JONA = "jona"
    ASI_TRINITY = "asi_trinity"
    AI_ENGINE = "ai_engine"
    REPORTING = "reporting"
    PAYMENT = "payment"
    MONITORING = "monitoring"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Gap:
    """Represents a detected gap."""
    gap_type: GapType
    description: str
    severity: float
    source: str = "system"
    suggested_fill: Optional[str] = None
    context: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.gap_type.value,
            "description": self.description,
            "severity": self.severity,
            "source": self.source,
            "suggested_fill": self.suggested_fill,
            "context": self.context
        }


@dataclass
class QualityScore:
    """Quality assessment for outputs."""
    overall: float
    accuracy: float = 0.8
    completeness: float = 0.8
    clarity: float = 0.8
    relevance: float = 0.8
    timeliness: float = 0.9
    factual_grounding: float = 0.8
    tier: QualityTier = field(init=False)
    
    def __post_init__(self) -> None:
        if self.overall >= 0.9:
            self.tier = QualityTier.EXCELLENT
        elif self.overall >= 0.75:
            self.tier = QualityTier.GOOD
        elif self.overall >= 0.6:
            self.tier = QualityTier.ACCEPTABLE
        else:
            self.tier = QualityTier.NEEDS_WORK
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall": round(self.overall, 3),
            "accuracy": round(self.accuracy, 3),
            "completeness": round(self.completeness, 3),
            "clarity": round(self.clarity, 3),
            "relevance": round(self.relevance, 3),
            "timeliness": round(self.timeliness, 3),
            "factual_grounding": round(self.factual_grounding, 3),
            "tier": self.tier.value
        }
    
    @classmethod
    def from_metrics(cls, metrics: Dict[str, float]) -> "QualityScore":
        """Create QualityScore from a metrics dictionary."""
        overall = metrics.get("overall", 0.8)
        return cls(
            overall=overall,
            accuracy=metrics.get("accuracy", 0.8),
            completeness=metrics.get("completeness", 0.8),
            clarity=metrics.get("clarity", 0.8),
            relevance=metrics.get("relevance", 0.8),
            timeliness=metrics.get("timeliness", 0.9),
            factual_grounding=metrics.get("factual_grounding", 0.8)
        )


@dataclass
class QualityValidation:
    """Result of quality validation."""
    passes: bool
    score: QualityScore
    gaps: List[Gap]
    recommendations: List[str]
    sanitized_output: Optional[Any] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "passes": self.passes,
            "score": self.score.to_dict(),
            "gaps": [g.to_dict() for g in self.gaps],
            "recommendations": self.recommendations,
            "has_sanitized_output": self.sanitized_output is not None,
            "timestamp": self.timestamp
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM-WIDE QUALITY SELECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class QualitySelector:
    """
    System-wide Quality Selector for Kloud.
    Ensures consistent quality validation across all services.
    """
    
    def __init__(self, 
                 min_tier: QualityTier = QualityTier.ACCEPTABLE,
                 service: ServiceType = ServiceType.AI_ENGINE) -> None:
        self.min_tier = min_tier
        self.service = service
        self.tier_order = [
            QualityTier.EXCELLENT,
            QualityTier.GOOD,
            QualityTier.ACCEPTABLE,
            QualityTier.NEEDS_WORK
        ]
        
        # Service-specific quality weights
        self.service_weights = {
            ServiceType.OCEAN: {"accuracy": 0.3, "clarity": 0.3, "relevance": 0.2, "factual_grounding": 0.2},
            ServiceType.ALBA: {"accuracy": 0.4, "timeliness": 0.3, "completeness": 0.2, "relevance": 0.1},
            ServiceType.ALBI: {"accuracy": 0.35, "completeness": 0.25, "timeliness": 0.2, "relevance": 0.2},
            ServiceType.JONA: {"timeliness": 0.35, "accuracy": 0.25, "completeness": 0.2, "relevance": 0.2},
            ServiceType.ASI_TRINITY: {"accuracy": 0.25, "completeness": 0.25, "timeliness": 0.25, "relevance": 0.25},
            ServiceType.AI_ENGINE: {"accuracy": 0.3, "completeness": 0.25, "clarity": 0.25, "relevance": 0.2},
            ServiceType.REPORTING: {"clarity": 0.35, "completeness": 0.3, "accuracy": 0.2, "relevance": 0.15},
            ServiceType.PAYMENT: {"accuracy": 0.5, "timeliness": 0.3, "completeness": 0.2},
            ServiceType.MONITORING: {"timeliness": 0.4, "accuracy": 0.3, "completeness": 0.2, "relevance": 0.1}
        }
    
    def calculate_score(self, 
                        output: Dict[str, Any],
                        gaps: Optional[List[Gap]] = None) -> QualityScore:
        """
        Calculate quality score for an output.
        
        Args:
            output: The output to score
            gaps: Optional list of detected gaps
        
        Returns:
            QualityScore with tier assignment
        """
        gaps = gaps or []
        weights = self.service_weights.get(self.service, 
                    {"accuracy": 0.25, "completeness": 0.25, "clarity": 0.25, "relevance": 0.25})
        
        # Base scores
        accuracy = 0.85 if output else 0.5
        completeness = 0.8
        clarity = 0.85
        relevance = 0.8
        timeliness = 0.95
        factual_grounding = 0.85
        
        # Adjust based on output content
        if isinstance(output, dict):
            # More complete outputs get higher scores
            field_count = len(output)
            if field_count > 10:
                completeness = 0.9
            elif field_count > 5:
                completeness = 0.85
            elif field_count < 2:
                completeness = 0.6
            
            # Check for error indicators
            if output.get("error") or output.get("status") == "error":
                accuracy = 0.4
                completeness = 0.5
        
        # Gap penalties
        gap_penalty = sum(g.severity * 0.1 for g in gaps)
        
        # Calculate weighted overall
        overall = (
            accuracy * weights.get("accuracy", 0.25) +
            completeness * weights.get("completeness", 0.25) +
            clarity * weights.get("clarity", 0.25) +
            relevance * weights.get("relevance", 0.25) +
            timeliness * weights.get("timeliness", 0) +
            factual_grounding * weights.get("factual_grounding", 0)
        )
        
        # Normalize if weights don't sum to 1
        total_weight = sum(weights.values())
        if total_weight > 0:
            overall = overall / total_weight
        
        overall = max(0.0, min(1.0, overall - gap_penalty))
        
        return QualityScore(
            overall=round(overall, 3),
            accuracy=round(accuracy, 3),
            completeness=round(completeness, 3),
            clarity=round(clarity, 3),
            relevance=round(relevance, 3),
            timeliness=round(timeliness, 3),
            factual_grounding=round(factual_grounding, 3)
        )
    
    def validate(self, 
                 output: Any,
                 gaps: Optional[List[Gap]] = None,
                 sanitize: bool = True) -> QualityValidation:
        """
        Validate output quality and optionally sanitize.
        
        Args:
            output: The output to validate
            gaps: Optional list of detected gaps
            sanitize: Whether to attempt output sanitization
        
        Returns:
            QualityValidation result
        """
        gaps = gaps or []
        
        # Convert to dict if possible
        output_dict = output if isinstance(output, dict) else {"value": output}
        
        # Calculate score
        score = self.calculate_score(output_dict, gaps)
        
        # Check if passes minimum tier
        passes = self._tier_meets_minimum(score.tier)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(score, gaps)
        
        # Sanitize if needed
        sanitized = None
        if sanitize and not passes:
            sanitized = self._sanitize_output(output, gaps)
        
        return QualityValidation(
            passes=passes,
            score=score,
            gaps=gaps,
            recommendations=recommendations,
            sanitized_output=sanitized
        )
    
    def select_best(self, 
                    candidates: List[Tuple[Any, QualityScore]]) -> Optional[Any]:
        """
        Select the best candidate from a list.
        
        Args:
            candidates: List of (output, score) tuples
        
        Returns:
            Best output or None if none pass quality threshold
        """
        if not candidates:
            return None
        
        # Filter by minimum tier
        valid = [
            (item, score) for item, score in candidates
            if self._tier_meets_minimum(score.tier)
        ]
        
        if not valid:
            return None
        
        # Sort by overall score
        valid.sort(key=lambda x: x[1].overall, reverse=True)
        return valid[0][0]
    
    def _tier_meets_minimum(self, tier: QualityTier) -> bool:
        """Check if tier meets minimum requirement."""
        tier_idx = self.tier_order.index(tier)
        min_idx = self.tier_order.index(self.min_tier)
        return tier_idx <= min_idx
    
    def _generate_recommendations(self, 
                                   score: QualityScore,
                                   gaps: List[Gap]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if score.accuracy < 0.7:
            recommendations.append("Improve data accuracy - verify sources")
        
        if score.completeness < 0.7:
            recommendations.append("Increase output completeness - add missing fields")
        
        if score.clarity < 0.7:
            recommendations.append("Improve clarity - simplify complex outputs")
        
        if score.relevance < 0.7:
            recommendations.append("Improve relevance - focus on user query")
        
        for gap in gaps:
            if gap.severity > 0.5 and gap.suggested_fill:
                recommendations.append(f"Fill gap: {gap.suggested_fill}")
        
        if not recommendations and score.tier == QualityTier.EXCELLENT:
            recommendations.append("Output quality excellent - no improvements needed")
        
        return recommendations
    
    def _sanitize_output(self, output: Any, gaps: List[Gap]) -> Any:
        """Attempt to sanitize output based on gaps."""
        if isinstance(output, str):
            # Remove common issues
            sanitized = output
            # Add gap notices
            for gap in gaps:
                if gap.severity > 0.7:
                    sanitized += f"\n\n⚠️ Note: {gap.description}"
            return sanitized
        
        return output


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM-WIDE GAP DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class GapDetector:
    """
    System-wide Gap Detector for Kloud.
    Identifies gaps in data, knowledge, and outputs.
    """
    
    def __init__(self, service: ServiceType = ServiceType.AI_ENGINE) -> None:
        self.service = service
        self.detected_gaps: List[Gap] = []
    
    def detect(self, 
               content: Union[str, Dict[str, Any]],
               context: Optional[str] = None) -> List[Gap]:
        """
        Detect gaps in content.
        
        Args:
            content: Content to analyze (string or dict)
            context: Optional context information
        
        Returns:
            List of detected gaps
        """
        self.detected_gaps = []
        
        if isinstance(content, str):
            self._detect_text_gaps(content, context)
        elif isinstance(content, dict):
            self._detect_dict_gaps(content, context)
        
        return self.detected_gaps
    
    def _detect_text_gaps(self, text: str, context: Optional[str]) -> None:
        """Detect gaps in text content."""
        text_lower = text.lower()
        
        # Definitional gaps
        if any(phrase in text_lower for phrase in ["what is", "cfare eshte", "what does"]):
            self.detected_gaps.append(Gap(
                gap_type=GapType.DEFINITIONAL,
                description="Query seeking definition",
                severity=0.3,
                source=self.service.value,
                context=context
            ))
        
        # Procedural gaps
        if any(phrase in text_lower for phrase in ["how to", "si te", "how do"]):
            self.detected_gaps.append(Gap(
                gap_type=GapType.PROCEDURAL,
                description="Query seeking procedure",
                severity=0.3,
                source=self.service.value,
                context=context
            ))
        
        # Temporal gaps
        if any(word in text_lower for word in ["now", "current", "today", "latest", "tani", "sot"]):
            self.detected_gaps.append(Gap(
                gap_type=GapType.TEMPORAL,
                description="Time-sensitive query",
                severity=0.2,
                source=self.service.value,
                suggested_fill="Include current timestamp in response"
            ))
        
        # Empty or too short
        if len(text.strip()) < 3:
            self.detected_gaps.append(Gap(
                gap_type=GapType.STRUCTURAL,
                description="Insufficient content",
                severity=0.8,
                source=self.service.value,
                suggested_fill="Provide more detailed input"
            ))
    
    def _detect_dict_gaps(self, data: Dict[str, Any], context: Optional[str]) -> None:
        """Detect gaps in dictionary content."""
        # Empty data
        if not data:
            self.detected_gaps.append(Gap(
                gap_type=GapType.DATA,
                description="Empty data structure",
                severity=0.9,
                source=self.service.value,
                suggested_fill="Provide valid data"
            ))
            return
        
        # Missing common fields
        expected_fields = {
            ServiceType.OCEAN: ["response", "confidence"],
            ServiceType.ALBA: ["metrics", "data"],
            ServiceType.ALBI: ["analysis", "patterns"],
            ServiceType.JONA: ["status", "coordination"],
            ServiceType.ASI_TRINITY: ["agents", "combined_analysis"],
            ServiceType.AI_ENGINE: ["interpretation", "confidence"],
            ServiceType.REPORTING: ["metrics", "summary"],
            ServiceType.PAYMENT: ["status", "amount"],
            ServiceType.MONITORING: ["status", "metrics"]
        }
        
        required = expected_fields.get(self.service, [])
        for field_name in required:
            if field_name not in data:
                self.detected_gaps.append(Gap(
                    gap_type=GapType.STRUCTURAL,
                    description=f"Missing expected field: {field_name}",
                    severity=0.4,
                    source=self.service.value,
                    suggested_fill=f"Add '{field_name}' to output"
                ))
        
        # Check for error states
        if data.get("error") or data.get("status") == "error":
            self.detected_gaps.append(Gap(
                gap_type=GapType.TECHNICAL,
                description="Error state detected",
                severity=0.7,
                source=self.service.value,
                suggested_fill="Investigate and resolve error"
            ))


# ═══════════════════════════════════════════════════════════════════════════════
# AUTO-DOCUMENTATION GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class AutoDocGenerator:
    """
    System-wide Auto-Documentation Generator for Kloud.
    Generates consistent, professional documentation.
    """
    
    def __init__(self, service: ServiceType = ServiceType.AI_ENGINE) -> None:
        self.service = service
        self.version = "2.0.0-blerina"
    
    def generate(self, 
                 doc_type: DocumentType,
                 data: Dict[str, Any],
                 title: Optional[str] = None,
                 include_metadata: bool = True) -> str:
        """
        Generate documentation.
        
        Args:
            doc_type: Type of document to generate
            data: Data to document
            title: Optional custom title
            include_metadata: Whether to include generation metadata
        
        Returns:
            Markdown-formatted documentation
        """
        generators = {
            DocumentType.REPORT: self._generate_report,
            DocumentType.ANALYSIS: self._generate_analysis,
            DocumentType.API_DOC: self._generate_api_doc,
            DocumentType.FAQ: self._generate_faq,
            DocumentType.SUMMARY: self._generate_summary,
            DocumentType.CHANGELOG: self._generate_changelog,
            DocumentType.TUTORIAL: self._generate_tutorial
        }
        
        generator = generators.get(doc_type, self._generate_report)
        doc = generator(data, title)
        
        if include_metadata:
            doc = self._add_metadata(doc)
        
        return doc
    
    def _add_metadata(self, doc: str) -> str:
        """Add generation metadata to document."""
        metadata = f"""
---

**Generated:** {datetime.now(timezone.utc).isoformat()}
**Service:** {self.service.value}
**Engine:** Kloud BLERINA v{self.version}

---

"""
        return metadata + doc
    
    def _generate_report(self, data: Dict[str, Any], title: Optional[str]) -> str:
        """Generate a report document."""
        doc_title = title or f"{self.service.value.upper()} Report"
        
        doc = f"# {doc_title}\n\n"
        
        # Status section
        if "status" in data:
            doc += f"**Status:** {data['status']}\n\n"
        
        # Main content
        doc += "## Overview\n\n"
        
        # Convert data to table if possible
        if isinstance(data, dict):
            doc += "| Field | Value |\n|-------|-------|\n"
            for key, value in data.items():
                if not isinstance(value, (dict, list)):
                    doc += f"| {key} | {value} |\n"
            doc += "\n"
            
            # Nested sections
            for key, value in data.items():
                if isinstance(value, dict):
                    doc += f"### {key.replace('_', ' ').title()}\n\n"
                    doc += "| Field | Value |\n|-------|-------|\n"
                    for k, v in value.items():
                        doc += f"| {k} | {v} |\n"
                    doc += "\n"
                elif isinstance(value, list):
                    doc += f"### {key.replace('_', ' ').title()}\n\n"
                    for item in value:
                        doc += f"- {item}\n"
                    doc += "\n"
        
        return doc
    
    def _generate_analysis(self, data: Dict[str, Any], title: Optional[str]) -> str:
        """Generate an analysis document."""
        doc_title = title or f"{self.service.value.upper()} Analysis"
        
        doc = f"# {doc_title}\n\n"
        doc += "## Analysis Summary\n\n"
        
        if "analysis" in data:
            doc += f"{data['analysis']}\n\n"
        
        if "metrics" in data:
            doc += "## Metrics\n\n"
            doc += "| Metric | Value |\n|--------|-------|\n"
            for k, v in data.get("metrics", {}).items():
                doc += f"| {k} | {v} |\n"
            doc += "\n"
        
        if "recommendations" in data:
            doc += "## Recommendations\n\n"
            for rec in data.get("recommendations", []):
                doc += f"- {rec}\n"
            doc += "\n"
        
        return doc
    
    def _generate_api_doc(self, data: Dict[str, Any], title: Optional[str]) -> str:
        """Generate API documentation."""
        doc_title = title or f"{self.service.value.upper()} API Documentation"
        
        doc = f"# {doc_title}\n\n"
        doc += "## Endpoints\n\n"
        
        for endpoint in data.get("endpoints", []):
            doc += f"### `{endpoint.get('method', 'GET')} {endpoint.get('path', '/')}`\n\n"
            doc += f"{endpoint.get('description', 'No description')}\n\n"
            
            if endpoint.get("parameters"):
                doc += "**Parameters:**\n\n"
                doc += "| Name | Type | Required | Description |\n"
                doc += "|------|------|----------|-------------|\n"
                for param in endpoint.get("parameters", []):
                    doc += f"| {param.get('name')} | {param.get('type')} | {param.get('required', False)} | {param.get('description', '')} |\n"
                doc += "\n"
            
            if endpoint.get("response"):
                doc += "**Response:**\n\n```json\n"
                doc += json.dumps(endpoint.get("response"), indent=2)
                doc += "\n```\n\n"
        
        return doc
    
    def _generate_faq(self, data: Dict[str, Any], title: Optional[str]) -> str:
        """Generate FAQ document."""
        doc_title = title or f"{self.service.value.upper()} FAQ"
        
        doc = f"# {doc_title}\n\n"
        
        for qa in data.get("questions", []):
            doc += f"## Q: {qa.get('question', 'Question')}\n\n"
            doc += f"**A:** {qa.get('answer', 'Answer not available.')}\n\n"
        
        return doc
    
    def _generate_summary(self, data: Dict[str, Any], title: Optional[str]) -> str:
        """Generate summary document."""
        doc_title = title or f"{self.service.value.upper()} Summary"
        
        doc = f"# {doc_title}\n\n"
        doc += data.get("summary", "No summary available.") + "\n\n"
        
        if data.get("key_points"):
            doc += "## Key Points\n\n"
            for point in data.get("key_points", []):
                doc += f"- {point}\n"
        
        return doc
    
    def _generate_changelog(self, data: Dict[str, Any], title: Optional[str]) -> str:
        """Generate changelog document."""
        doc_title = title or f"{self.service.value.upper()} Changelog"
        
        doc = f"# {doc_title}\n\n"
        
        for version in data.get("versions", []):
            doc += f"## [{version.get('version', '0.0.0')}] - {version.get('date', 'Unknown')}\n\n"
            
            for change_type in ["added", "changed", "fixed", "removed"]:
                changes = version.get(change_type, [])
                if changes:
                    doc += f"### {change_type.title()}\n\n"
                    for change in changes:
                        doc += f"- {change}\n"
                    doc += "\n"
        
        return doc
    
    def _generate_tutorial(self, data: Dict[str, Any], title: Optional[str]) -> str:
        """Generate tutorial document."""
        doc_title = title or f"{self.service.value.upper()} Tutorial"
        
        doc = f"# {doc_title}\n\n"
        doc += data.get("introduction", "Welcome to this tutorial.") + "\n\n"
        
        for i, step in enumerate(data.get("steps", []), 1):
            doc += f"## Step {i}: {step.get('title', f'Step {i}')}\n\n"
            doc += f"{step.get('content', '')}\n\n"
            
            if step.get("code"):
                doc += f"```{step.get('language', 'python')}\n"
                doc += step.get("code")
                doc += "\n```\n\n"
        
        return doc


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_quality_selector(service: str = "ai_engine",
                            min_tier: str = "acceptable") -> QualitySelector:
    """Create a quality selector for a service."""
    service_type = ServiceType(service) if service in [s.value for s in ServiceType] else ServiceType.AI_ENGINE
    quality_tier = QualityTier(min_tier) if min_tier in [t.value for t in QualityTier] else QualityTier.ACCEPTABLE
    return QualitySelector(quality_tier, service_type)


def create_gap_detector(service: str = "ai_engine") -> GapDetector:
    """Create a gap detector for a service."""
    service_type = ServiceType(service) if service in [s.value for s in ServiceType] else ServiceType.AI_ENGINE
    return GapDetector(service_type)


def create_doc_generator(service: str = "ai_engine") -> AutoDocGenerator:
    """Create a doc generator for a service."""
    service_type = ServiceType(service) if service in [s.value for s in ServiceType] else ServiceType.AI_ENGINE
    return AutoDocGenerator(service_type)


def validate_output(output: Any, 
                    service: str = "ai_engine",
                    min_tier: str = "acceptable") -> QualityValidation:
    """Convenience function to validate any output."""
    selector = create_quality_selector(service, min_tier)
    detector = create_gap_detector(service)
    
    gaps = detector.detect(output)
    return selector.validate(output, gaps)


def generate_doc(data: Dict[str, Any],
                 doc_type: str = "report",
                 service: str = "ai_engine",
                 title: Optional[str] = None) -> str:
    """Convenience function to generate documentation."""
    generator = create_doc_generator(service)
    dtype = DocumentType(doc_type) if doc_type in [d.value for d in DocumentType] else DocumentType.REPORT
    return generator.generate(dtype, data, title)


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════════

def blerina_health() -> Dict[str, Any]:
    """Return BLERINA core health status."""
    return {
        "status": "healthy",
        "version": "2.0.0-blerina",
        "components": {
            "quality_selector": "active",
            "gap_detector": "active",
            "auto_doc_generator": "active"
        },
        "services_supported": [s.value for s in ServiceType],
        "document_types": [d.value for d in DocumentType],
        "quality_tiers": [t.value for t in QualityTier],
        "gap_types": [g.value for g in GapType],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    print("Testing Kloud BLERINA Core...")
    
    # Test quality validation
    test_output = {
        "response": "This is a test response",
        "confidence": 0.85,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    validation = validate_output(test_output, "ocean")
    print("\nQuality Validation:")
    print(f"  Passes: {validation.passes}")
    print(f"  Score: {validation.score.overall}")
    print(f"  Tier: {validation.score.tier.value}")
    print(f"  Recommendations: {validation.recommendations}")
    
    # Test documentation generation
    doc = generate_doc(test_output, "report", "ocean", "Test Report")
    print("\nGenerated Documentation Preview:")
    print(doc[:500] + "...")
    
    print(f"\nHealth: {blerina_health()}")

