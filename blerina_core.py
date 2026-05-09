"""
B.L.E.R.I.N.A - Bits Labor Enhanced Recreation Intelligence Neural Array
=========================================================================

Gap-Detector & Conceptual Reconstruction Engine

Blerina lexon dokumente të vjetra, gjen boshllëqet konceptuale,
dhe krijon dokumente të reja me konceptet që mungonin.

Funksionet kryesore:
- extract_gaps(): Gjen boshllëqet në dokumente
- detect_discontinuity(): Identifikon discontinuity strukturore
- reconstruct_concept(): Rindërton konceptin që mungon
- generate_signal(): Krijon sinjal për Trinity/Ocean

Author: Ledjan Ahmati (CEO, ABA GmbH)
System: Kloud Cloud
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

# Try to import httpx for API calls
try:
    import httpx
except ImportError:
    httpx = None  # type: ignore[assignment]

logger = logging.getLogger("blerina")
logger.setLevel(logging.INFO)


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS & DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

class GapType(str, Enum):
    """Llojet e boshllëqeve konceptuale"""
    STRUCTURAL = "structural"           # Boshllëk në strukturë
    LOGICAL = "logical"                 # Boshllëk në logjikë
    DEFINITIONAL = "definitional"       # Mungon përkufizimi
    PROCEDURAL = "procedural"           # Mungon procesi
    REGULATORY = "regulatory"           # Mungon rregullimi
    ACCOUNTABILITY = "accountability"   # Mungon llogaridhënia
    SOVEREIGNTY = "sovereignty"         # Çështje sovraniteti
    INTEROPERABILITY = "interop"        # Mungon ndërveprimi
    TEMPORAL = "temporal"               # Boshllëk në kohë/afat


class DiscontinuityLevel(str, Enum):
    """Niveli i discontinuity"""
    MINOR = "minor"           # E vogël, lehtësisht e adresueshme
    MODERATE = "moderate"     # E mesme, kërkon ndërhyrje
    MAJOR = "major"           # E madhe, kërkon reformë
    CRITICAL = "critical"     # Kritike, rrezikon sistemin


class DocumentType(str, Enum):
    """Llojet e dokumenteve që Blerina lexon"""
    LAW = "law"                   # Ligje, akte normative
    POLICY = "policy"             # Politika, udhëzime
    TECHNICAL = "technical"       # Dokumentacion teknik
    NEWS = "news"                 # Lajme, artikuj
    RESEARCH = "research"         # Studime, kërkime
    REPORT = "report"             # Raporte, analiza
    REGULATION = "regulation"     # Rregullore


@dataclass
class Gap:
    """Struktura e një boshllëku konceptual"""
    id: str
    gap_type: GapType
    description: str
    severity: DiscontinuityLevel
    location: str                      # Ku u gjet në dokument
    missing_concept: str               # Çfarë mungon
    implications: List[str]            # Pasojat
    reconstruction_hint: str           # Si mund të adresohet
    confidence: float = 0.0            # 0.0 - 1.0


@dataclass
class DiscontinuityAnalysis:
    """Analiza e discontinuity"""
    id: str
    source_documents: List[str]
    gaps: List[Gap]
    discontinuity_level: DiscontinuityLevel
    structural_void: str               # Boshllëku strukturor kryesor
    missing_systemic_function: str     # Funksioni sistemik që mungon
    propagation_risks: List[str]       # Si përhapet risku
    reconstruction_needed: str         # Çfarë duhet ndërtuar
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class BlerinaSignal:
    """Sinjali që Blerina i dërgon Trinity/Ocean"""
    id: str
    signal_type: str                   # "gap_detected", "discontinuity_found", "reconstruction_ready"
    gaps: List[Gap]
    analysis: DiscontinuityAnalysis
    eap_ready: bool                    # Gati për EAP processing
    priority: str                      # "low", "medium", "high", "critical"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# BLERINA CORE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class BlerinaCore:
    """
    B.L.E.R.I.N.A - Bits Labor Enhanced Recreation Intelligence Neural Array
    
    Gap-Detector dhe Conceptual Reconstruction Engine.
    
    Ky modul:
    1. Lexon dokumente (ligje, lajme, raporte, etj.)
    2. Identifikon boshllëqet konceptuale
    3. Analizon discontinuity strukturore
    4. Gjeneron sinjale për EAP/Trinity/Ocean
    
    Usage:
        blerina = BlerinaCore()
        
        # Lexo dhe analizo dokument
        gaps = await blerina.extract_gaps(document_text, doc_type="law")
        
        # Analizo discontinuity
        analysis = await blerina.detect_discontinuity(documents=[doc1, doc2, doc3])
        
        # Gjenero sinjal për Trinity
        signal = blerina.generate_signal(gaps, analysis)
    """
    
    def __init__(self, ollama_url: Optional[str] = None):
        # Auto-detect Ollama URL from environment or use sensible defaults
        import os
        if ollama_url:
            self.ollama_url = ollama_url
        else:
            self.ollama_url = os.environ.get(
                "OLLAMA_HOST",
                os.environ.get("OLLAMA_URL", "http://localhost:11434")
            )
        self.model = os.environ.get("MODEL", "llama3.1:8b")
        self._processed_documents: List[str] = []
        self._gaps_found: List[Gap] = []
        self._signals_generated: int = 0
        
        # Gap detection patterns
        self._gap_patterns = self._init_gap_patterns()
        
        # Domain knowledge for gap detection
        self._domain_knowledge = self._init_domain_knowledge()
    
    def _init_gap_patterns(self) -> Dict[GapType, List[str]]:
        """Inicializo pattern-et për detektimin e boshllëqeve"""
        return {
            GapType.STRUCTURAL: [
                r"without\s+(?:clear|defined|explicit)\s+(?:structure|framework|architecture)",
                r"no\s+(?:mechanism|system|process)\s+for",
                r"lacks?\s+(?:a\s+)?(?:clear|defined)\s+(?:structure|hierarchy)",
                r"(?:missing|absent)\s+(?:governance|oversight)\s+(?:structure|layer)",
            ],
            GapType.ACCOUNTABILITY: [
                r"(?:no|without)\s+(?:clear\s+)?accountability",
                r"(?:unclear|undefined)\s+(?:responsibility|liability)",
                r"who\s+is\s+(?:responsible|accountable)",
                r"(?:lack|absence)\s+of\s+(?:transparency|oversight)",
            ],
            GapType.SOVEREIGNTY: [
                r"(?:loss|erosion)\s+of\s+(?:sovereignty|control)",
                r"(?:delegates?|transfers?)\s+(?:authority|control)\s+to\s+(?:private|external)",
                r"(?:state|government|public)\s+(?:loses?|cedes?)\s+(?:control|authority)",
                r"(?:cross-border|transnational)\s+(?:without|lacking)\s+(?:sovereignty|oversight)",
            ],
            GapType.REGULATORY: [
                r"(?:no|without|lacking)\s+(?:regulation|regulatory\s+framework)",
                r"(?:regulatory|legal)\s+(?:vacuum|void|gap)",
                r"(?:unregulated|non-regulated)\s+(?:area|domain|space)",
                r"(?:absence|lack)\s+of\s+(?:legal|regulatory)\s+(?:framework|basis)",
            ],
            GapType.INTEROPERABILITY: [
                r"(?:no|without)\s+(?:interoperability|compatibility)",
                r"(?:fragmented|siloed)\s+(?:systems?|data|infrastructure)",
                r"(?:cannot|unable\s+to)\s+(?:communicate|interact)\s+with",
                r"(?:proprietary|closed)\s+(?:format|protocol|standard)",
            ],
        }
    
    def _init_domain_knowledge(self) -> Dict[str, List[str]]:
        """Inicializo domain knowledge për analiza të thella"""
        return {
            "governance": [
                "accountability", "transparency", "oversight", "audit",
                "compliance", "regulation", "enforcement", "authority"
            ],
            "ai_systems": [
                "model architecture", "training data", "bias", "explainability",
                "auditability", "decision-making", "algorithmic", "opacity"
            ],
            "identity": [
                "authentication", "verification", "sovereignty", "privacy",
                "cross-border", "digital identity", "biometric", "credentials"
            ],
            "financial": [
                "systemic risk", "liquidity", "solvency", "contagion",
                "interconnection", "dependency", "exposure", "leverage"
            ],
            "legal": [
                "jurisdiction", "liability", "enforcement", "precedent",
                "harmonization", "conflict of laws", "extraterritorial"
            ],
        }
    
    # ─────────────────────────────────────────────────────────────────────────
    # GAP EXTRACTION
    # ─────────────────────────────────────────────────────────────────────────
    
    async def extract_gaps(
        self,
        document: str,
        doc_type: DocumentType = DocumentType.TECHNICAL,
        context: Optional[str] = None
    ) -> List[Gap]:
        """
        Lexo dokumentin dhe nxirr boshllëqet konceptuale.
        
        Args:
            document: Teksti i dokumentit
            doc_type: Lloji i dokumentit
            context: Kontekst shtesë për analizën
            
        Returns:
            List[Gap]: Lista e boshllëqeve të gjetura
        """
        gaps: List[Gap] = []
        
        # Step 1: Pattern-based gap detection
        pattern_gaps = self._detect_gaps_by_pattern(document)
        gaps.extend(pattern_gaps)
        
        # Step 2: Semantic gap detection (via LLM if available)
        if httpx:
            semantic_gaps = await self._detect_gaps_semantically(document, doc_type, context)
            gaps.extend(semantic_gaps)
        
        # Step 3: Domain-specific gap detection
        domain_gaps = self._detect_domain_gaps(document)
        gaps.extend(domain_gaps)
        
        # Deduplicate and rank
        gaps = self._deduplicate_gaps(gaps)
        gaps = self._rank_gaps(gaps)
        
        # Store for later use
        self._gaps_found.extend(gaps)
        self._processed_documents.append(hashlib.md5(document.encode()).hexdigest()[:12])
        
        logger.info(f"📊 Blerina extracted {len(gaps)} gaps from document")
        return gaps
    
    def _detect_gaps_by_pattern(self, document: str) -> List[Gap]:
        """Detekto boshllëqe duke përdorur pattern-e regex"""
        gaps = []
        doc_lower = document.lower()
        
        for gap_type, patterns in self._gap_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, doc_lower, re.IGNORECASE)
                for match in matches:
                    # Extract context around the match
                    start = max(0, match.start() - 100)
                    end = min(len(document), match.end() + 100)
                    _ = document[start:end]  # context for future use
                    
                    gap = Gap(
                        id=f"gap_{hashlib.md5(match.group().encode()).hexdigest()[:8]}",
                        gap_type=gap_type,
                        description=f"Detected: {match.group()}",
                        severity=DiscontinuityLevel.MODERATE,
                        location=f"Position {match.start()}-{match.end()}",
                        missing_concept=self._infer_missing_concept(gap_type, match.group()),
                        implications=self._infer_implications(gap_type),
                        reconstruction_hint=self._get_reconstruction_hint(gap_type),
                        confidence=0.7
                    )
                    gaps.append(gap)
        
        return gaps
    
    async def _detect_gaps_semantically(
        self,
        document: str,
        doc_type: DocumentType,
        context: Optional[str]
    ) -> List[Gap]:
        """Detekto boshllëqe duke përdorur LLM për analizë semantike"""
        if not httpx:
            return []
        
        prompt = f"""Analyze this {doc_type.value} document and identify conceptual gaps.

Document:
{document[:3000]}  # Limit to 3000 chars

{f"Additional context: {context}" if context else ""}

Identify:
1. Structural gaps (missing frameworks, undefined processes)
2. Accountability gaps (unclear responsibility)
3. Regulatory gaps (missing legal framework)
4. Sovereignty gaps (loss of control to private entities)
5. Interoperability gaps (fragmented systems)

For each gap found, provide:
- Type of gap
- Description
- What concept is missing
- Severity (minor/moderate/major/critical)
- Implications

Respond in JSON format:
{{"gaps": [{{"type": "...", "description": "...", "missing": "...", "severity": "...", "implications": ["..."]}}]}}
"""
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get("response", "{}")
                    
                    try:
                        data = json.loads(text)
                        return self._parse_llm_gaps(data.get("gaps", []))
                    except json.JSONDecodeError:
                        logger.warning("Could not parse LLM response as JSON")
                        return []
        except Exception as e:
            logger.error(f"Semantic gap detection failed: {e}")
            return []
        
        return []
    
    def _detect_domain_gaps(self, document: str) -> List[Gap]:
        """Detekto boshllëqe bazuar në domain knowledge"""
        gaps = []
        doc_lower = document.lower()
        
        for domain, keywords in self._domain_knowledge.items():
            # Count how many domain keywords are present
            present = [kw for kw in keywords if kw in doc_lower]
            missing = [kw for kw in keywords if kw not in doc_lower]
            
            # If domain is discussed but key concepts are missing
            if len(present) >= 2 and len(missing) >= 3:
                gap = Gap(
                    id=f"gap_domain_{domain}_{hashlib.md5(''.join(missing).encode()).hexdigest()[:6]}",
                    gap_type=GapType.DEFINITIONAL,
                    description=f"Document discusses {domain} but misses key concepts",
                    severity=DiscontinuityLevel.MODERATE,
                    location="Throughout document",
                    missing_concept=f"Missing {domain} concepts: {', '.join(missing[:3])}",
                    implications=[
                        f"Incomplete treatment of {domain}",
                        "May lead to implementation gaps",
                        "Stakeholders may have different interpretations"
                    ],
                    reconstruction_hint=f"Add sections addressing: {', '.join(missing[:3])}",
                    confidence=0.6
                )
                gaps.append(gap)
        
        return gaps
    
    def _parse_llm_gaps(self, llm_gaps: List[Dict]) -> List[Gap]:
        """Parse LLM response into Gap objects"""
        gaps = []
        
        type_mapping = {
            "structural": GapType.STRUCTURAL,
            "accountability": GapType.ACCOUNTABILITY,
            "regulatory": GapType.REGULATORY,
            "sovereignty": GapType.SOVEREIGNTY,
            "interoperability": GapType.INTEROPERABILITY,
            "logical": GapType.LOGICAL,
            "definitional": GapType.DEFINITIONAL,
            "procedural": GapType.PROCEDURAL,
        }
        
        severity_mapping = {
            "minor": DiscontinuityLevel.MINOR,
            "moderate": DiscontinuityLevel.MODERATE,
            "major": DiscontinuityLevel.MAJOR,
            "critical": DiscontinuityLevel.CRITICAL,
        }
        
        for g in llm_gaps:
            gap_type_str = g.get("type", "structural").lower()
            severity_str = g.get("severity", "moderate").lower()
            
            gap = Gap(
                id=f"gap_llm_{hashlib.md5(str(g).encode()).hexdigest()[:8]}",
                gap_type=type_mapping.get(gap_type_str, GapType.STRUCTURAL),
                description=g.get("description", "Unspecified gap"),
                severity=severity_mapping.get(severity_str, DiscontinuityLevel.MODERATE),
                location="Semantic analysis",
                missing_concept=g.get("missing", "Unspecified"),
                implications=g.get("implications", []),
                reconstruction_hint=f"Address the missing concept: {g.get('missing', '')}",
                confidence=0.8
            )
            gaps.append(gap)
        
        return gaps
    
    def _infer_missing_concept(self, gap_type: GapType, match_text: str) -> str:
        """Infer çfarë koncepti mungon bazuar në llojin e boshllëkut"""
        inferences = {
            GapType.STRUCTURAL: "Clear governance framework or system architecture",
            GapType.ACCOUNTABILITY: "Defined responsibility and liability chain",
            GapType.SOVEREIGNTY: "State control over critical infrastructure",
            GapType.REGULATORY: "Legal framework and enforcement mechanisms",
            GapType.INTEROPERABILITY: "Open standards and communication protocols",
            GapType.LOGICAL: "Logical consistency in reasoning",
            GapType.DEFINITIONAL: "Clear definitions and terminology",
            GapType.PROCEDURAL: "Step-by-step process documentation",
        }
        return inferences.get(gap_type, "Undefined concept")
    
    def _infer_implications(self, gap_type: GapType) -> List[str]:
        """Infer implications bazuar në llojin e boshllëkut"""
        implications = {
            GapType.STRUCTURAL: [
                "System fragmentation",
                "Unclear decision-making authority",
                "Difficulty in scaling or adapting"
            ],
            GapType.ACCOUNTABILITY: [
                "No clear liability in case of failure",
                "Reduced trust from stakeholders",
                "Potential for abuse without consequences"
            ],
            GapType.SOVEREIGNTY: [
                "Loss of control over critical systems",
                "Dependency on external actors",
                "Vulnerability to foreign influence"
            ],
            GapType.REGULATORY: [
                "Legal uncertainty",
                "Inconsistent enforcement",
                "Potential for abuse in regulatory vacuum"
            ],
            GapType.INTEROPERABILITY: [
                "Vendor lock-in",
                "Data silos",
                "Increased integration costs"
            ],
        }
        return implications.get(gap_type, ["Undefined implications"])
    
    def _get_reconstruction_hint(self, gap_type: GapType) -> str:
        """Get hint për si të rindërtohet koncepti që mungon"""
        hints = {
            GapType.STRUCTURAL: "Define clear architecture with separation of concerns",
            GapType.ACCOUNTABILITY: "Establish accountability chain with defined roles",
            GapType.SOVEREIGNTY: "Implement sovereign control mechanisms with audit trails",
            GapType.REGULATORY: "Create regulatory framework with enforcement provisions",
            GapType.INTEROPERABILITY: "Adopt open standards and publish interface specifications",
        }
        return hints.get(gap_type, "Address the identified gap through targeted intervention")
    
    def _deduplicate_gaps(self, gaps: List[Gap]) -> List[Gap]:
        """Remove duplicate gaps"""
        seen = set()
        unique = []
        
        for gap in gaps:
            key = (gap.gap_type, gap.missing_concept[:50])
            if key not in seen:
                seen.add(key)
                unique.append(gap)
        
        return unique
    
    def _rank_gaps(self, gaps: List[Gap]) -> List[Gap]:
        """Rank gaps by severity and confidence"""
        severity_order = {
            DiscontinuityLevel.CRITICAL: 4,
            DiscontinuityLevel.MAJOR: 3,
            DiscontinuityLevel.MODERATE: 2,
            DiscontinuityLevel.MINOR: 1,
        }
        
        return sorted(
            gaps,
            key=lambda g: (severity_order.get(g.severity, 0), g.confidence),
            reverse=True
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # DISCONTINUITY ANALYSIS
    # ─────────────────────────────────────────────────────────────────────────
    
    async def detect_discontinuity(
        self,
        documents: List[str],
        topic: str = "governance",
        horizon_years: int = 10
    ) -> DiscontinuityAnalysis:
        """
        Analizo discontinuity strukturore në një grup dokumentesh.
        
        Kjo funksion:
        1. Lexon disa dokumente njëherësh
        2. Gjen boshllëqet në secilin
        3. Identifikon discontinuity ndërmjet tyre
        4. Modelon propagimin e rrezikut në kohë
        
        Args:
            documents: Lista e dokumenteve për analizë
            topic: Tema kryesore
            horizon_years: Horizonti kohor për modelimin e rrezikut
            
        Returns:
            DiscontinuityAnalysis: Analiza e plotë
        """
        all_gaps: List[Gap] = []
        doc_hashes = []
        
        # Extract gaps from all documents
        for doc in documents:
            gaps = await self.extract_gaps(doc)
            all_gaps.extend(gaps)
            doc_hashes.append(hashlib.md5(doc.encode()).hexdigest()[:12])
        
        # Analyze discontinuity across documents
        structural_void = self._identify_structural_void(all_gaps, topic)
        missing_function = self._identify_missing_function(all_gaps, topic)
        propagation = self._model_risk_propagation(all_gaps, horizon_years)
        reconstruction = self._determine_reconstruction(all_gaps, topic)
        
        # Determine overall discontinuity level
        level = self._calculate_discontinuity_level(all_gaps)
        
        analysis = DiscontinuityAnalysis(
            id=f"disc_{hashlib.md5(''.join(doc_hashes).encode()).hexdigest()[:10]}",
            source_documents=doc_hashes,
            gaps=all_gaps,
            discontinuity_level=level,
            structural_void=structural_void,
            missing_systemic_function=missing_function,
            propagation_risks=propagation,
            reconstruction_needed=reconstruction
        )
        
        logger.info(f"🔍 Discontinuity analysis complete: {level.value} level, {len(all_gaps)} gaps")
        return analysis
    
    def _identify_structural_void(self, gaps: List[Gap], topic: str) -> str:
        """Identifiko boshllëkun strukturor kryesor"""
        structural_gaps = [g for g in gaps if g.gap_type == GapType.STRUCTURAL]
        
        if not structural_gaps:
            return f"No major structural void identified in {topic}"
        
        # Find most severe structural gap
        most_severe = max(structural_gaps, key=lambda g: g.confidence)
        return f"Structural void in {topic}: {most_severe.missing_concept}"
    
    def _identify_missing_function(self, gaps: List[Gap], topic: str) -> str:
        """Identifiko funksionin sistemik që mungon"""
        accountability_gaps = [g for g in gaps if g.gap_type == GapType.ACCOUNTABILITY]
        regulatory_gaps = [g for g in gaps if g.gap_type == GapType.REGULATORY]
        
        missing_functions = []
        
        if accountability_gaps:
            missing_functions.append("accountability mechanism")
        if regulatory_gaps:
            missing_functions.append("regulatory oversight")
        
        sovereignty_gaps = [g for g in gaps if g.gap_type == GapType.SOVEREIGNTY]
        if sovereignty_gaps:
            missing_functions.append("sovereignty preservation")
        
        if not missing_functions:
            return f"Core systemic functions appear intact for {topic}"
        
        return f"Missing systemic functions: {', '.join(missing_functions)}"
    
    def _model_risk_propagation(self, gaps: List[Gap], horizon_years: int) -> List[str]:
        """Modelo si përhapen rreziqet në kohë"""
        propagation = []
        
        # Short-term (1-3 years)
        if any(g.severity in [DiscontinuityLevel.CRITICAL, DiscontinuityLevel.MAJOR] for g in gaps):
            propagation.append("Years 1-3: Immediate operational risks from unaddressed gaps")
        
        # Medium-term (3-7 years)
        structural_gaps = [g for g in gaps if g.gap_type == GapType.STRUCTURAL]
        if structural_gaps:
            propagation.append("Years 3-7: Systemic fragmentation as structural gaps compound")
        
        # Long-term (7+ years)
        sovereignty_gaps = [g for g in gaps if g.gap_type == GapType.SOVEREIGNTY]
        if sovereignty_gaps:
            propagation.append(f"Years 7-{horizon_years}: Potential loss of sovereign control over critical systems")
        
        accountability_gaps = [g for g in gaps if g.gap_type == GapType.ACCOUNTABILITY]
        if accountability_gaps:
            propagation.append(f"Years 5-{horizon_years}: Erosion of trust due to accountability void")
        
        if not propagation:
            propagation.append(f"Risk propagation appears contained over {horizon_years}-year horizon")
        
        return propagation
    
    def _determine_reconstruction(self, gaps: List[Gap], topic: str) -> str:
        """Përcakto çfarë duhet rindërtuar"""
        if not gaps:
            return f"No reconstruction needed for {topic}"
        
        # Group by type
        gap_types = set(g.gap_type for g in gaps)
        
        reconstructions = []
        
        if GapType.STRUCTURAL in gap_types:
            reconstructions.append("governance architecture")
        if GapType.ACCOUNTABILITY in gap_types:
            reconstructions.append("accountability framework")
        if GapType.SOVEREIGNTY in gap_types:
            reconstructions.append("sovereign control mechanisms")
        if GapType.REGULATORY in gap_types:
            reconstructions.append("regulatory oversight layer")
        if GapType.INTEROPERABILITY in gap_types:
            reconstructions.append("interoperability standards")
        
        return f"Reconstruction needed: {', '.join(reconstructions)}"
    
    def _calculate_discontinuity_level(self, gaps: List[Gap]) -> DiscontinuityLevel:
        """Llogarit nivelin e përgjithshëm të discontinuity"""
        if not gaps:
            return DiscontinuityLevel.MINOR
        
        critical_count = sum(1 for g in gaps if g.severity == DiscontinuityLevel.CRITICAL)
        major_count = sum(1 for g in gaps if g.severity == DiscontinuityLevel.MAJOR)
        
        if critical_count >= 2 or (critical_count >= 1 and major_count >= 2):
            return DiscontinuityLevel.CRITICAL
        elif critical_count >= 1 or major_count >= 3:
            return DiscontinuityLevel.MAJOR
        elif major_count >= 1:
            return DiscontinuityLevel.MODERATE
        else:
            return DiscontinuityLevel.MINOR
    
    # ─────────────────────────────────────────────────────────────────────────
    # SIGNAL GENERATION (for Trinity/Ocean)
    # ─────────────────────────────────────────────────────────────────────────
    
    def generate_signal(
        self,
        gaps: List[Gap],
        analysis: DiscontinuityAnalysis,
        priority: str = "medium"
    ) -> BlerinaSignal:
        """
        Gjenero sinjal për Trinity/Ocean.
        
        Ky sinjal i thotë sistemit:
        - Çfarë boshllëqesh u gjetën
        - Sa kritike janë
        - Çfarë duhet rindërtuar
        - Nëse është gati për EAP processing
        
        Args:
            gaps: Boshllëqet e gjetura
            analysis: Analiza e discontinuity
            priority: Prioriteti i sinjalit
            
        Returns:
            BlerinaSignal: Sinjali për Trinity/Ocean
        """
        # Determine if ready for EAP
        eap_ready = len(gaps) > 0 and analysis.reconstruction_needed != ""
        
        # Auto-escalate priority if critical gaps found
        if analysis.discontinuity_level == DiscontinuityLevel.CRITICAL:
            priority = "critical"
        elif analysis.discontinuity_level == DiscontinuityLevel.MAJOR:
            priority = "high"
        
        signal = BlerinaSignal(
            id=f"bln_sig_{self._signals_generated + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            signal_type="gap_detected" if gaps else "no_gaps",
            gaps=gaps,
            analysis=analysis,
            eap_ready=eap_ready,
            priority=priority
        )
        
        self._signals_generated += 1
        logger.info(f"📡 Blerina signal generated: {signal.id} (priority: {priority}, EAP ready: {eap_ready})")
        
        return signal
    
    # ─────────────────────────────────────────────────────────────────────────
    # UTILITY METHODS
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Blerina statistics"""
        return {
            "documents_processed": len(self._processed_documents),
            "gaps_found": len(self._gaps_found),
            "signals_generated": self._signals_generated,
            "gap_types_distribution": self._get_gap_distribution(),
            "model": self.model,
            "status": "active"
        }
    
    def _get_gap_distribution(self) -> Dict[str, int]:
        """Get distribution of gap types"""
        distribution: Dict[str, int] = {}
        for gap in self._gaps_found:
            gap_type = gap.gap_type.value
            distribution[gap_type] = distribution.get(gap_type, 0) + 1
        return distribution
    
    def reset(self):
        """Reset Blerina state"""
        self._processed_documents = []
        self._gaps_found = []
        self._signals_generated = 0
        logger.info("🔄 Blerina state reset")


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Global instance
_blerina_instance: Optional[BlerinaCore] = None


def get_blerina() -> BlerinaCore:
    """Get or create Blerina instance"""
    global _blerina_instance
    if _blerina_instance is None:
        _blerina_instance = BlerinaCore()
    return _blerina_instance


async def extract_gaps(document: str, doc_type: str = "technical") -> List[Dict]:
    """Quick function to extract gaps from a document"""
    blerina = get_blerina()
    doc_type_enum = DocumentType(doc_type) if doc_type in [e.value for e in DocumentType] else DocumentType.TECHNICAL
    gaps = await blerina.extract_gaps(document, doc_type_enum)
    return [
        {
            "id": g.id,
            "type": g.gap_type.value,
            "description": g.description,
            "severity": g.severity.value,
            "missing_concept": g.missing_concept,
            "implications": g.implications,
            "confidence": g.confidence
        }
        for g in gaps
    ]


async def analyze_discontinuity(documents: List[str], topic: str = "governance") -> Dict:
    """Quick function to analyze discontinuity across documents"""
    blerina = get_blerina()
    analysis = await blerina.detect_discontinuity(documents, topic)
    return {
        "id": analysis.id,
        "level": analysis.discontinuity_level.value,
        "structural_void": analysis.structural_void,
        "missing_function": analysis.missing_systemic_function,
        "propagation_risks": analysis.propagation_risks,
        "reconstruction_needed": analysis.reconstruction_needed,
        "gaps_count": len(analysis.gaps)
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN (for testing)
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    async def test_blerina():
        print("=" * 70)
        print("🧬 B.L.E.R.I.N.A - Gap Detection Test")
        print("=" * 70)
        
        blerina = BlerinaCore()
        
        # Test document
        test_doc = """
        The new cross-border digital identity framework allows private AI companies 
        to authenticate citizens without disclosing their model architectures or 
        training data. This creates significant concerns about accountability and 
        transparency. There is no clear mechanism for oversight, and the regulatory 
        framework is still undefined. Citizens have no way to challenge AI decisions 
        about their identity. The state effectively delegates authority to opaque 
        private systems without maintaining sovereignty over critical infrastructure.
        """
        
        print("\n📄 Analyzing test document...")
        gaps = await blerina.extract_gaps(test_doc, DocumentType.POLICY)
        
        print(f"\n📊 Found {len(gaps)} gaps:")
        for i, gap in enumerate(gaps, 1):
            print(f"\n  [{i}] {gap.gap_type.value.upper()}")
            print(f"      Description: {gap.description}")
            print(f"      Missing: {gap.missing_concept}")
            print(f"      Severity: {gap.severity.value}")
            print(f"      Confidence: {gap.confidence:.2f}")
        
        # Test discontinuity analysis
        print("\n" + "=" * 70)
        print("🔍 Running Discontinuity Analysis...")
        
        analysis = await blerina.detect_discontinuity([test_doc], "digital identity governance", 15)
        
        print(f"\n📈 Discontinuity Level: {analysis.discontinuity_level.value.upper()}")
        print(f"📍 Structural Void: {analysis.structural_void}")
        print(f"⚙️  Missing Function: {analysis.missing_systemic_function}")
        print("🔮 Propagation Risks:")
        for risk in analysis.propagation_risks:
            print(f"   • {risk}")
        print(f"🔧 Reconstruction: {analysis.reconstruction_needed}")
        
        # Generate signal
        print("\n" + "=" * 70)
        print("📡 Generating Signal for Trinity/Ocean...")
        
        signal = blerina.generate_signal(gaps, analysis)
        print(f"   Signal ID: {signal.id}")
        print(f"   Priority: {signal.priority}")
        print(f"   EAP Ready: {signal.eap_ready}")
        
        # Stats
        print("\n" + "=" * 70)
        print("📊 Blerina Stats:")
        stats = blerina.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n✅ Blerina test complete!")
    
    asyncio.run(test_blerina())

