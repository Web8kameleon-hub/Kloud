#!/usr/bin/env python3
"""
Ocean BLERINA Core — Advanced Processing Architecture
======================================================
Integrates BLERINA-level capabilities into Ocean:
- EAP Pipeline (Evresi → Analysi → Proposi)
- Gap Detection for knowledge gaps
- Quality Selector for response validation
- Auto-documentation generation
- Structured knowledge base

This module enhances Ocean's responses with professional-grade output.

Author: Kloud Team
Date: 2026-02-08
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════════════════
# BLERINA-STYLE ENUMS & DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════


class GapType(Enum):
    """Gap types for knowledge detection — inspired by BLERINA."""
    STRUCTURAL = "structural"      # Missing component or section
    LOGICAL = "logical"            # Reasoning gap or inconsistency
    DEFINITIONAL = "definitional"  # Undefined term or concept
    CONTEXTUAL = "contextual"      # Missing background information
    TEMPORAL = "temporal"          # Outdated or time-sensitive gap
    TECHNICAL = "technical"        # Missing technical detail
    PROCEDURAL = "procedural"      # Missing step or process
    FACTUAL = "factual"            # Missing or incorrect facts


class QualityTier(Enum):
    """Output quality tiers for selection."""
    EXCELLENT = "excellent"   # Score >= 0.9
    GOOD = "good"             # Score >= 0.75
    ACCEPTABLE = "acceptable" # Score >= 0.6
    NEEDS_WORK = "needs_work" # Score < 0.6


class AnalysisPhase(Enum):
    """EAP Pipeline phases."""
    EVRESI = "evresi"       # Discovery/Input phase
    ANALYSI = "analysi"     # Analysis/Processing phase
    PROPOSI = "proposi"     # Proposal/Output phase


class ResponseMode(Enum):
    """Ocean response modes with BLERINA enhancement."""
    CURIOUS = "curious"     # Exploratory, inquisitive
    GENIUS = "genius"       # Deep analysis, thorough
    WILD = "wild"           # Creative, unexpected
    CHAOS = "chaos"         # Energetic, chaotic
    PROFESSIONAL = "professional"  # Business-grade output
    DOCUMENTATION = "documentation"  # Auto-doc generation


@dataclass
class Gap:
    """Represents a detected knowledge gap."""
    gap_type: GapType
    description: str
    severity: float  # 0.0 to 1.0
    suggested_fill: Optional[str] = None
    context: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.gap_type.value,
            "description": self.description,
            "severity": self.severity,
            "suggested_fill": self.suggested_fill,
            "context": self.context
        }


@dataclass
class QualityScore:
    """Quality assessment for outputs."""
    overall: float
    accuracy: float
    completeness: float
    clarity: float
    relevance: float
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
            "overall": self.overall,
            "accuracy": self.accuracy,
            "completeness": self.completeness,
            "clarity": self.clarity,
            "relevance": self.relevance,
            "factual_grounding": self.factual_grounding,
            "tier": self.tier.value
        }


@dataclass
class EAPResult:
    """Result from EAP Pipeline processing."""
    phase: AnalysisPhase
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    gaps_detected: List[Gap]
    quality: QualityScore
    processing_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "gaps_detected": [g.to_dict() for g in self.gaps_detected],
            "quality": self.quality.to_dict(),
            "processing_time_ms": self.processing_time_ms,
            "metadata": self.metadata
        }


# ═══════════════════════════════════════════════════════════════════════════════
# OCEAN KNOWLEDGE BASE — VERIFIED FACTS ONLY
# ═══════════════════════════════════════════════════════════════════════════════

OCEAN_KNOWLEDGE_BASE = {
    # Creator & Company Information - VERIFIED
    "ledjan_ahmati": {
        "role": "Creator & CEO",
        "company": "ABA GmbH",
        "title": None,  # No "Doktor" title - don't fabricate
        "created": ["Kloud Cloud", "Ocean AI", "ALBA", "ALBI", "JONA", "ASI Trinity"],
        "blog": "https://ledjanahmati.github.io/kloud-blog/",
        "publications": True,  # Has 150+ blog articles on EEG, AI, healthcare
        "verified": True
    },
    
    # Platform Information - VERIFIED
    "kloud": {
        "name": "Kloud Cloud",
        "type": "Industrial IoT & Neural Analysis Platform",
        "website": "kloud.cloud",
        "features": [
            "EEG Analysis (ALBA, ALBI)",
            "Audio Analysis",
            "Industrial IoT (JONA)",
            "AI Coordination (ASI Trinity)",
            "Real-time Monitoring"
        ],
        "verified": True
    },
    
    # Agents - VERIFIED
    "agents": {
        "ALBA": {
            "name": "Audio Lab Biometric Analyzer",
            "port": 5555,
            "function": "Audio and EEG signal processing"
        },
        "ALBI": {
            "name": "Audio Lab Biometric Intelligence",
            "port": 6680,
            "function": "Neural biofeedback and pattern analysis"
        },
        "JONA": {
            "name": "JONA Industrial Gateway",
            "function": "Industrial IoT coordination and data routing"
        },
        "ASI_Trinity": {
            "name": "Advanced System Intelligence Trinity",
            "components": ["ALBA", "ALBI", "JONA"],
            "function": "Coordinated AI analysis across all agents"
        },
        "Ocean": {
            "name": "Curiosity Ocean",
            "function": "Natural language AI interface",
            "model": "llama3.1:8b"
        }
    },
    
    # EEG Knowledge - VERIFIED SCIENTIFIC
    "eeg_bands": {
        "delta": {"range": (0.5, 4), "state": "Deep sleep", "unit": "Hz"},
        "theta": {"range": (4, 8), "state": "Relaxation/Meditation", "unit": "Hz"},
        "alpha": {"range": (8, 13), "state": "Calm alertness", "unit": "Hz"},
        "beta": {"range": (13, 30), "state": "Active thinking", "unit": "Hz"},
        "gamma": {"range": (30, 100), "state": "High cognition", "unit": "Hz"}
    },
    
    # BLERINA System - VERIFIED
    "blerina": {
        "name": "Bits Labor Enhanced Recreation Intelligence Neural Array",
        "function": "Gap-Detector & Conceptual Reconstruction Engine",
        "pipeline": "EAP (Evresi → Analysi → Proposi)",
        "capacity": "10-20 articles/day (manual), 300-500 docs/day (autopilot)"
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# HALLUCINATION PREVENTION - FORBIDDEN FABRICATIONS
# ═══════════════════════════════════════════════════════════════════════════════

FORBIDDEN_FABRICATIONS = [
    # Don't add titles that don't exist
    ("Doktor Ledjan", "Ledjan Ahmati (no doctorate title)"),
    ("Dr. Ledjan", "Ledjan Ahmati"),
    ("Professor Ledjan", "Ledjan Ahmati"),
    
    # Don't claim publications that don't exist
    ("published in Nature", "publishes on kloud-blog"),
    ("peer-reviewed journal", "technical blog articles"),
    ("scientific paper on consciousness", "blog articles on EEG and AI"),
    
    # Don't fabricate company details
    ("founded in Silicon Valley", "ABA GmbH, founded 2025 in Germany"),
    ("billion dollar", "technology company"),
    
    # Don't claim capabilities that don't exist
    ("read your mind", "analyze EEG patterns"),
    ("predict the future", "analyze trends and patterns"),
    ("cure diseases", "provide health monitoring data")
]


class HallucinationGuard:
    """Prevents Ocean from fabricating information."""
    
    @staticmethod
    def check_response(response: str) -> Tuple[bool, List[str]]:
        """
        Check response for potential hallucinations.
        
        Returns:
            Tuple of (is_clean, list_of_issues)
        """
        issues = []
        response_lower = response.lower()
        
        for forbidden, correction in FORBIDDEN_FABRICATIONS:
            if forbidden.lower() in response_lower:
                issues.append(f"Found '{forbidden}' - should be '{correction}'")
        
        return (len(issues) == 0, issues)
    
    @staticmethod
    def sanitize_response(response: str) -> str:
        """Remove or correct hallucinated content."""
        result = response
        
        for forbidden, correction in FORBIDDEN_FABRICATIONS:
            if forbidden.lower() in result.lower():
                # Case-insensitive replacement
                import re
                pattern = re.compile(re.escape(forbidden), re.IGNORECASE)
                result = pattern.sub(correction, result)
        
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# EAP PIPELINE FOR OCEAN
# ═══════════════════════════════════════════════════════════════════════════════

class OceanEAPPipeline:
    """
    EAP Pipeline for Ocean — Evresi → Analysi → Proposi
    Processes queries through structured phases for quality output.
    """
    
    def __init__(self) -> None:
        self.phases_completed: List[AnalysisPhase] = []
        self.gaps_collected: List[Gap] = []
        self.start_time: Optional[float] = None
        self.hallucination_guard = HallucinationGuard()
    
    def evresi(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Phase 1: Discovery — understand the query and gather context.
        """
        self.start_time = time.time()
        self.phases_completed = [AnalysisPhase.EVRESI]
        self.gaps_collected = []
        
        # Analyze query
        query_lower = query.lower()
        
        # Detect topic categories
        topics = []
        if any(w in query_lower for w in ["eeg", "brain", "neural", "tru"]):
            topics.append("neural")
        if any(w in query_lower for w in ["alba", "albi", "jona", "asi"]):
            topics.append("agents")
        if any(w in query_lower for w in ["ledjan", "krijues", "creator", "ceo"]):
            topics.append("creator")
        if any(w in query_lower for w in ["kloud", "platform", "cloud"]):
            topics.append("platform")
        if any(w in query_lower for w in ["weather", "time", "date", "moti"]):
            topics.append("realtime")
        
        # Detect language
        albanian_words = ["si", "cfare", "kush", "pse", "ku", "kur", "eshte", "jane"]
        is_albanian = any(w in query_lower.split() for w in albanian_words)
        
        # Detect question type
        question_type = "statement"
        if "?" in query or any(query_lower.startswith(w) for w in 
                               ["what", "how", "why", "when", "where", "who",
                                "cfare", "si", "pse", "kur", "ku", "kush"]):
            question_type = "question"
        
        # Check for knowledge gaps
        if not topics:
            self.gaps_collected.append(Gap(
                gap_type=GapType.CONTEXTUAL,
                description="Query topic not immediately clear",
                severity=0.3,
                suggested_fill="Provide more specific context"
            ))
        
        if "creator" in topics:
            # Ensure we use verified info only
            self.gaps_collected.append(Gap(
                gap_type=GapType.FACTUAL,
                description="Creator query - must use verified information only",
                severity=0.1,
                suggested_fill="Use OCEAN_KNOWLEDGE_BASE['ledjan_ahmati']"
            ))
        
        return {
            "query": query,
            "query_lower": query_lower,
            "topics": topics,
            "language": "albanian" if is_albanian else "english",
            "question_type": question_type,
            "context": context or {},
            "gaps": [g.to_dict() for g in self.gaps_collected],
            "phase": "evresi",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def analysi(self, evresi_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 2: Analysis — process the query and prepare response data.
        """
        self.phases_completed.append(AnalysisPhase.ANALYSI)
        
        topics = evresi_output.get("topics", [])
        _query = evresi_output.get("query", "")  # Prefixed with _ to indicate used later
        
        # Gather relevant knowledge
        knowledge_context: List[str] = []
        
        if "creator" in topics:
            creator = OCEAN_KNOWLEDGE_BASE["ledjan_ahmati"]
            knowledge_context.append(f"""
VERIFIED CREATOR INFO:
- Name: Ledjan Ahmati (NO titles like Dr. or Professor)
- Role: {creator['role']}
- Company: {creator['company']}
- Created: {', '.join(creator['created'])}
- Blog: {creator['blog']} (150+ articles on EEG, AI, healthcare)
""")
        
        if "agents" in topics:
            agents = OCEAN_KNOWLEDGE_BASE["agents"]
            agent_info = []
            for name, info in agents.items():
                agent_info.append(f"- {name}: {info.get('function', info.get('name', 'Agent'))}")
            knowledge_context.append("KLOUD AGENTS:\n" + "\n".join(agent_info))
        
        if "neural" in topics:
            eeg = OCEAN_KNOWLEDGE_BASE["eeg_bands"]
            eeg_info = []
            for band, info in eeg.items():
                eeg_info.append(f"- {band.upper()}: {info['range'][0]}-{info['range'][1]} Hz = {info['state']}")
            knowledge_context.append("EEG BANDS:\n" + "\n".join(eeg_info))
        
        if "platform" in topics:
            platform = OCEAN_KNOWLEDGE_BASE["kloud"]
            knowledge_context.append(f"""
KLOUD PLATFORM:
- Name: {platform['name']}
- Type: {platform['type']}
- Website: {platform['website']}
- Features: {', '.join(platform['features'][:3])}
""")
        
        # Response guidance
        response_guidance = []
        if evresi_output.get("language") == "albanian":
            response_guidance.append("Respond in Albanian (Shqip)")
        
        if "creator" in topics:
            response_guidance.append("Use ONLY verified facts about Ledjan Ahmati - NO fabricated titles or credentials")
        
        return {
            "evresi_data": evresi_output,
            "knowledge_context": knowledge_context,
            "response_guidance": response_guidance,
            "confidence": 0.9 if knowledge_context else 0.7,
            "phase": "analysi",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def proposi(self, analysi_output: Dict[str, Any]) -> EAPResult:
        """
        Phase 3: Proposal — finalize with quality scoring.
        """
        self.phases_completed.append(AnalysisPhase.PROPOSI)
        end_time = time.time()
        
        processing_ms = (end_time - (self.start_time or end_time)) * 1000
        
        # Calculate quality
        has_knowledge = bool(analysi_output.get("knowledge_context"))
        has_guidance = bool(analysi_output.get("response_guidance"))
        gap_count = len(self.gaps_collected)
        
        accuracy = 0.95 if has_knowledge else 0.7
        completeness = 0.9 if has_guidance else 0.75
        clarity = 0.88
        relevance = analysi_output.get("confidence", 0.8)
        factual = 0.95 if has_knowledge else 0.6
        
        overall = (accuracy + completeness + clarity + relevance + factual) / 5
        overall = max(0.0, min(1.0, overall - (gap_count * 0.05)))
        
        quality = QualityScore(
            overall=round(overall, 3),
            accuracy=round(accuracy, 3),
            completeness=round(completeness, 3),
            clarity=round(clarity, 3),
            relevance=round(relevance, 3),
            factual_grounding=round(factual, 3)
        )
        
        return EAPResult(
            phase=AnalysisPhase.PROPOSI,
            input_data=analysi_output.get("evresi_data", {}),
            output_data={
                "knowledge_context": analysi_output.get("knowledge_context", []),
                "response_guidance": analysi_output.get("response_guidance", [])
            },
            gaps_detected=self.gaps_collected,
            quality=quality,
            processing_time_ms=round(processing_ms, 2),
            metadata={
                "phases": [p.value for p in self.phases_completed],
                "topics": analysi_output.get("evresi_data", {}).get("topics", []),
                "language": analysi_output.get("evresi_data", {}).get("language", "english")
            }
        )
    
    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> EAPResult:
        """Run the full EAP pipeline."""
        evresi_out = self.evresi(query, context)
        analysi_out = self.analysi(evresi_out)
        return self.proposi(analysi_out)


# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY SELECTOR FOR OCEAN
# ═══════════════════════════════════════════════════════════════════════════════

class OceanQualitySelector:
    """
    Selects and validates Ocean responses for quality.
    """
    
    def __init__(self, min_tier: QualityTier = QualityTier.ACCEPTABLE) -> None:
        self.min_tier = min_tier
        self.hallucination_guard = HallucinationGuard()
    
    def validate_response(self, response: str, eap_result: EAPResult) -> Dict[str, Any]:
        """
        Validate a response for quality and hallucinations.
        
        Returns:
            Dict with validation results
        """
        # Check hallucinations
        is_clean, issues = self.hallucination_guard.check_response(response)
        
        # Sanitize if needed
        final_response = response
        if not is_clean:
            final_response = self.hallucination_guard.sanitize_response(response)
        
        # Quality check
        passes_quality = eap_result.quality.tier.value in ["excellent", "good", "acceptable"]
        
        return {
            "original_response": response,
            "final_response": final_response,
            "was_sanitized": not is_clean,
            "issues_found": issues,
            "quality_tier": eap_result.quality.tier.value,
            "quality_score": eap_result.quality.overall,
            "passes_quality": passes_quality,
            "ready_to_send": is_clean or len(issues) == 0
        }


# ═══════════════════════════════════════════════════════════════════════════════
# OCEAN GAP DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class OceanGapDetector:
    """
    Detects knowledge gaps in queries for better response preparation.
    """
    
    def __init__(self) -> None:
        self.knowledge_base = OCEAN_KNOWLEDGE_BASE
    
    def detect(self, query: str) -> List[Gap]:
        """Detect gaps in the query that need addressing."""
        gaps = []
        query_lower = query.lower()
        
        # Check for unclear pronouns
        if any(w in query_lower.split() for w in ["it", "this", "that", "they"]):
            if len(query.split()) < 10:  # Short query with pronouns
                gaps.append(Gap(
                    gap_type=GapType.CONTEXTUAL,
                    description="Query contains pronouns without clear context",
                    severity=0.4,
                    suggested_fill="Ask for clarification"
                ))
        
        # Check for time-sensitive queries
        time_words = ["now", "today", "current", "latest", "tani", "sot"]
        if any(w in query_lower for w in time_words):
            gaps.append(Gap(
                gap_type=GapType.TEMPORAL,
                description="Query is time-sensitive - needs current data",
                severity=0.3,
                suggested_fill="Include current date/time in response"
            ))
        
        # Check for unknown technical terms
        technical_terms = {"eeg", "fft", "bci", "neural", "amplitude", "frequency"}
        found_terms = set(query_lower.split()) & technical_terms
        
        for term in found_terms:
            if term not in self.knowledge_base.get("eeg_bands", {}):
                gaps.append(Gap(
                    gap_type=GapType.TECHNICAL,
                    description=f"Technical term '{term}' may need explanation",
                    severity=0.2,
                    suggested_fill=f"Define {term} if user seems unfamiliar"
                ))
        
        return gaps


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT BUILDER WITH BLERINA ENHANCEMENTS
# ═══════════════════════════════════════════════════════════════════════════════

def build_enhanced_system_prompt(
    base_identity: str,
    realtime_context: str,
    eap_result: Optional[EAPResult] = None,
    mode: ResponseMode = ResponseMode.CURIOUS
) -> str:
    """
    Build an enhanced system prompt with BLERINA-level guidance.
    
    Args:
        base_identity: Base Ocean identity text
        realtime_context: Current date/time/weather context
        eap_result: Optional EAP pipeline result for context
        mode: Response mode
    
    Returns:
        Enhanced system prompt
    """
    prompt = f"""{base_identity}

When asked who you are, say: "I am Ocean 🌊, AI of Kloud Cloud, created by Ledjan Ahmati."
NEVER say you are ChatGPT, Llama, or any other AI.

{realtime_context}

## CRITICAL RULES — BLERINA-LEVEL QUALITY

### 1. FACTUAL ACCURACY — NO HALLUCINATIONS
- About Ledjan Ahmati: Use ONLY these facts:
  • Creator & CEO of Kloud Cloud
  • Founder of ABA GmbH
  • NO doctorate, NO professor title — just "Ledjan Ahmati"
  • Has blog at ledjanahmati.github.io/kloud-blog with 150+ articles
  • Created: Ocean, ALBA, ALBI, JONA, ASI Trinity, BLERINA
  
- NEVER fabricate:
  • Academic titles (Dr., Professor, PhD)
  • Publications in scientific journals (has blog, not Nature/Science)
  • Medical claims about consciousness studies
  • Random unverified facts

### 2. RESPONSE QUALITY
- Start immediately — no "Let me think" delays
- Be helpful, thorough, accurate
- Match user's language (Albanian/English)
- Use real-time data when relevant

### 3. AGENT KNOWLEDGE
- ALBA (port 5555): Audio/EEG Analysis
- ALBI (port 6680): Neural Biofeedback  
- JONA: Industrial IoT Gateway
- ASI Trinity: Coordinated AI (ALBA+ALBI+JONA)
- Ocean: That's you! Natural language interface

"""

    # Add EAP context if available
    if eap_result:
        knowledge = eap_result.output_data.get("knowledge_context", [])
        guidance = eap_result.output_data.get("response_guidance", [])
        
        if knowledge:
            prompt += "\n## RELEVANT KNOWLEDGE FOR THIS QUERY\n"
            prompt += "\n".join(knowledge)
            prompt += "\n"
        
        if guidance:
            prompt += "\n## RESPONSE GUIDANCE\n"
            for g in guidance:
                prompt += f"- {g}\n"
    
    # Mode-specific additions
    mode_instructions = {
        ResponseMode.CURIOUS: "Be exploratory and inquisitive, ask follow-up questions.",
        ResponseMode.GENIUS: "Provide deep, thorough analysis with comprehensive explanations.",
        ResponseMode.WILD: "Be creative and unexpected while staying accurate.",
        ResponseMode.CHAOS: "Be energetic and dynamic while maintaining facts.",
        ResponseMode.PROFESSIONAL: "Use formal tone, structured responses, business-appropriate.",
        ResponseMode.DOCUMENTATION: "Generate well-formatted documentation with headers, tables, code blocks."
    }
    
    prompt += f"\n## RESPONSE MODE: {mode.value.upper()}\n"
    prompt += mode_instructions.get(mode, "")
    
    prompt += "\n\nRemember: Quality over speed. Accuracy over creativity. Facts over fabrication."
    
    return prompt


# ═══════════════════════════════════════════════════════════════════════════════
# OCEAN BLERINA INTEGRATION CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class OceanBlerina:
    """
    Main integration class for BLERINA-enhanced Ocean.
    """
    
    def __init__(self) -> None:
        self.pipeline = OceanEAPPipeline()
        self.quality_selector = OceanQualitySelector()
        self.gap_detector = OceanGapDetector()
        self.knowledge_base = OCEAN_KNOWLEDGE_BASE
        self.version = "2.0.0-blerina"
    
    def process_query(self, query: str, 
                      context: Optional[Dict[str, Any]] = None) -> EAPResult:
        """
        Process a query through the full BLERINA pipeline.
        """
        return self.pipeline.run(query, context)
    
    def validate_response(self, response: str, 
                         eap_result: EAPResult) -> Dict[str, Any]:
        """
        Validate and sanitize a response.
        """
        return self.quality_selector.validate_response(response, eap_result)
    
    def get_enhanced_prompt(self, 
                           base_identity: str,
                           realtime_context: str,
                           query: str,
                           mode: ResponseMode = ResponseMode.CURIOUS) -> str:
        """
        Get an enhanced system prompt for a query.
        """
        eap_result = self.process_query(query)
        return build_enhanced_system_prompt(
            base_identity, realtime_context, eap_result, mode
        )
    
    def health(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "status": "healthy",
            "version": self.version,
            "architecture": "BLERINA",
            "components": {
                "eap_pipeline": "active",
                "quality_selector": "active",
                "gap_detector": "active",
                "hallucination_guard": "active"
            },
            "knowledge_base_entries": len(self.knowledge_base),
            "forbidden_patterns": len(FORBIDDEN_FABRICATIONS),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Global instance
ocean_blerina = OceanBlerina()


def process_query(query: str, context: Optional[Dict[str, Any]] = None) -> EAPResult:
    """Process a query through BLERINA pipeline."""
    return ocean_blerina.process_query(query, context)


def validate_response(response: str, eap_result: EAPResult) -> Dict[str, Any]:
    """Validate an Ocean response."""
    return ocean_blerina.validate_response(response, eap_result)


def get_enhanced_prompt(base_identity: str, realtime_context: str, 
                        query: str, mode: str = "curious") -> str:
    """Get enhanced system prompt."""
    response_mode = ResponseMode(mode) if mode in [m.value for m in ResponseMode] else ResponseMode.CURIOUS
    return ocean_blerina.get_enhanced_prompt(base_identity, realtime_context, query, response_mode)


def health() -> Dict[str, Any]:
    """Get BLERINA health status."""
    return ocean_blerina.health()


if __name__ == "__main__":
    # Test the pipeline
    print("Testing Ocean BLERINA Core...")
    
    result = process_query("Kush është Ledjan Ahmati?")
    print("\nEAP Result for 'Kush është Ledjan Ahmati?':")
    print(f"Quality Tier: {result.quality.tier.value}")
    print(f"Quality Score: {result.quality.overall}")
    print(f"Topics: {result.metadata.get('topics', [])}")
    print(f"Language: {result.metadata.get('language', 'unknown')}")
    print(f"Processing Time: {result.processing_time_ms}ms")
    
    # Test hallucination detection
    test_response = "Doktor Ledjan Ahmati ka publikuar studime në Nature."
    validation = validate_response(test_response, result)
    print("\nHallucination Test:")
    print(f"Was sanitized: {validation['was_sanitized']}")
    print(f"Issues: {validation['issues_found']}")
    print(f"Final: {validation['final_response']}")
    
    print(f"\nHealth: {health()}")

