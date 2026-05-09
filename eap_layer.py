"""
EAP LAYER - Evresi → Analysi → Proposi
======================================

Three-stage conceptual processing layer for Kloud Content Factory.

Layer 1: EVRESI (Observation)
    - Nxjerr faktet e ftohta
    - Pa opinion, pa interpretim
    - Vetëm çfarë ka ndodhur

Layer 2: ANALYSI (Gap & Risk)
    - Identifikon boshllëqet strukturore
    - Nxjerr rreziqet sistemike
    - Shpjegon çfarë mungon

Layer 3: PROPOSI (Reconstruction)
    - Ndërton konceptin që mungon
    - Jep arkitekturën e re
    - Jep zgjidhjen që nuk ekziston ende

Author: Ledjan Ahmati (CEO, ABA GmbH)
System: Kloud Cloud
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

# Import Blerina for gap detection
try:
    from blerina_core import (
        BlerinaCore,
        BlerinaSignal,
        DiscontinuityAnalysis,
        Gap,
        get_blerina,
    )
except ImportError:
    BlerinaCore = None  # type: ignore[assignment,misc]
    BlerinaSignal = None  # type: ignore[assignment,misc]
    Gap = None  # type: ignore[assignment,misc]
    DiscontinuityAnalysis = None  # type: ignore[assignment,misc]
    get_blerina = None  # type: ignore[assignment]

# Try to import httpx for LLM calls
try:
    import httpx
except ImportError:
    httpx = None  # type: ignore[assignment]

logger = logging.getLogger("eap_layer")
logger.setLevel(logging.INFO)


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS & DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

class EAPStage(str, Enum):
    """Fazat e EAP"""
    EVRESI = "evresi"       # Observation
    ANALYSI = "analysi"     # Analysis
    PROPOSI = "proposi"     # Proposal
    COMPLETE = "complete"   # All stages done


class DocumentFormat(str, Enum):
    """Formatet e dokumenteve"""
    MARKDOWN = "md"
    JSON = "json"
    HTML = "html"
    PLAIN = "txt"


@dataclass
class EvresiDocument:
    """
    Layer 1: EVRESI (Observation Document)
    
    Dokument faktik, pa opinion, vetëm vëzhgime të ftohta.
    """
    id: str
    title: str
    facts: List[str]                    # Faktet e ftohta
    context: str                        # Konteksti i ngjarjes
    source: str                         # Burimi (ligj, lajm, raport)
    source_date: Optional[str]          # Data e burimit
    entities: List[str]                 # Entitetet e përfshira
    locations: List[str]                # Vendndodhjet
    keywords: List[str]                 # Fjalët kyçe
    original_question: Optional[str]    # Pyetja origjinale (nëse ka)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_markdown(self) -> str:
        """Convert to markdown format"""
        md = f"# EVRESI: {self.title}\n\n"
        md += f"**Document ID:** `{self.id}`\n"
        md += f"**Source:** {self.source}\n"
        if self.source_date:
            md += f"**Source Date:** {self.source_date}\n"
        md += f"**Generated:** {self.timestamp}\n\n"
        
        md += "## Observation (Vëzhgim)\n\n"
        md += f"{self.context}\n\n"
        
        md += "## Facts (Fakte)\n\n"
        for fact in self.facts:
            md += f"- {fact}\n"
        
        if self.entities:
            md += "\n## Entities (Entitete)\n\n"
            md += ", ".join(self.entities) + "\n"
        
        if self.locations:
            md += "\n## Locations (Vendndodhje)\n\n"
            md += ", ".join(self.locations) + "\n"
        
        if self.keywords:
            md += "\n## Keywords (Fjalë Kyçe)\n\n"
            md += ", ".join(self.keywords) + "\n"
        
        if self.original_question:
            md += f"\n## Original Question\n\n{self.original_question}\n"
        
        return md


@dataclass
class AnalysiDocument:
    """
    Layer 2: ANALYSI (Gap & Risk Document)
    
    Dokument që identifikon boshllëqet, rreziqet, discontinuity.
    """
    id: str
    title: str
    evresi_id: str                      # Reference to Evresi document
    structural_gaps: List[Dict]          # Boshllëqet strukturore
    discontinuities: List[str]           # Discontinuity-t
    risks: List[Dict]                    # Rreziqet me severity
    missing_concepts: List[str]          # Konceptet që mungojnë
    implications: List[str]              # Pasojat
    propagation_timeline: List[Dict]     # Si përhapet risku në kohë
    severity_level: str                  # minor/moderate/major/critical
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_markdown(self) -> str:
        """Convert to markdown format"""
        md = f"# ANALYSI: {self.title}\n\n"
        md += f"**Document ID:** `{self.id}`\n"
        md += f"**Based on Evresi:** `{self.evresi_id}`\n"
        md += f"**Severity Level:** {self.severity_level.upper()}\n"
        md += f"**Generated:** {self.timestamp}\n\n"
        
        md += "## Structural Gaps (Boshllëqe Strukturore)\n\n"
        for gap in self.structural_gaps:
            md += f"### {gap.get('type', 'Unknown').upper()}\n"
            md += f"- **Description:** {gap.get('description', 'N/A')}\n"
            md += f"- **Severity:** {gap.get('severity', 'moderate')}\n"
            md += f"- **Missing:** {gap.get('missing', 'N/A')}\n\n"
        
        if self.discontinuities:
            md += "## Discontinuities\n\n"
            for disc in self.discontinuities:
                md += f"- {disc}\n"
            md += "\n"
        
        md += "## Risks (Rreziqe)\n\n"
        for risk in self.risks:
            md += f"- **{risk.get('category', 'General')}:** {risk.get('description', 'N/A')} "
            md += f"(Severity: {risk.get('severity', 'medium')})\n"
        
        if self.missing_concepts:
            md += "\n## Missing Concepts (Koncepte që Mungojnë)\n\n"
            for concept in self.missing_concepts:
                md += f"- {concept}\n"
        
        md += "\n## Implications (Pasoja)\n\n"
        for impl in self.implications:
            md += f"- {impl}\n"
        
        if self.propagation_timeline:
            md += "\n## Risk Propagation Timeline\n\n"
            for period in self.propagation_timeline:
                md += f"### {period.get('timeframe', 'Unknown')}\n"
                md += f"{period.get('description', 'N/A')}\n\n"
        
        return md


@dataclass
class ProposiDocument:
    """
    Layer 3: PROPOSI (Reconstruction Document)
    
    Dokument që ndërton konceptin e ri, arkitekturën, zgjidhjen.
    """
    id: str
    title: str
    evresi_id: str                      # Reference to Evresi
    analysi_id: str                     # Reference to Analysi
    paradigm_name: str                  # Emri i paradigmës së re
    paradigm_description: str           # Përshkrimi i paradigmës
    architecture: Dict                   # Arkitektura e propozuar
    principles: List[str]               # Parimet bazë
    implementation_steps: List[Dict]    # Hapat e implementimit
    expected_outcomes: List[str]        # Rezultatet e pritura
    addresses_gaps: List[str]           # Cilat boshllëqe adreson
    alternatives_considered: List[str]  # Alternativat e konsideruara
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_markdown(self) -> str:
        """Convert to markdown format"""
        md = f"# PROPOSI: {self.title}\n\n"
        md += f"**Document ID:** `{self.id}`\n"
        md += f"**Based on Evresi:** `{self.evresi_id}`\n"
        md += f"**Based on Analysi:** `{self.analysi_id}`\n"
        md += f"**Generated:** {self.timestamp}\n\n"
        
        md += f"## Proposed Paradigm: {self.paradigm_name}\n\n"
        md += f"{self.paradigm_description}\n\n"
        
        md += "## Core Principles (Parimet Bazë)\n\n"
        for i, principle in enumerate(self.principles, 1):
            md += f"{i}. {principle}\n"
        
        md += "\n## Architecture (Arkitektura)\n\n"
        md += "```\n"
        for component, details in self.architecture.items():
            if isinstance(details, dict):
                md += f"{component}:\n"
                for k, v in details.items():
                    md += f"  - {k}: {v}\n"
            else:
                md += f"{component}: {details}\n"
        md += "```\n\n"
        
        md += "## Implementation Steps (Hapat e Implementimit)\n\n"
        for i, step in enumerate(self.implementation_steps, 1):
            md += f"### Step {i}: {step.get('name', 'Unnamed')}\n"
            md += f"{step.get('description', 'N/A')}\n"
            if step.get('effort'):
                md += f"- **Effort:** {step['effort']}\n"
            if step.get('timeline'):
                md += f"- **Timeline:** {step['timeline']}\n"
            md += "\n"
        
        md += "## Expected Outcomes (Rezultate të Pritura)\n\n"
        for outcome in self.expected_outcomes:
            md += f"- {outcome}\n"
        
        md += "\n## Addresses Gaps (Adreson Boshllëqet)\n\n"
        for gap in self.addresses_gaps:
            md += f"- ✅ {gap}\n"
        
        if self.alternatives_considered:
            md += "\n## Alternatives Considered\n\n"
            for alt in self.alternatives_considered:
                md += f"- {alt}\n"
        
        return md


@dataclass
class EAPDocument:
    """
    Complete EAP Document (All 3 layers combined)
    
    Clieditorial - Artikulli final i gatshëm për publikim.
    """
    id: str
    title: str
    evresi: EvresiDocument
    analysi: AnalysiDocument
    proposi: ProposiDocument
    executive_summary: str
    author: str = "Kloud Cloud"
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    category: str = "analysis"
    publish_ready: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_markdown(self) -> str:
        """Convert complete EAP to markdown (Clieditorial format)"""
        md = f"# {self.title}\n\n"
        md += f"*Published by {self.author} | {self.timestamp[:10]}*\n\n"
        
        if self.tags:
            md += "**Tags:** " + ", ".join(f"`{tag}`" for tag in self.tags) + "\n\n"
        
        md += "---\n\n"
        
        md += "## Executive Summary\n\n"
        md += f"{self.executive_summary}\n\n"
        
        md += "---\n\n"
        
        # Evresi section
        md += "## 1. Observation (Evresi)\n\n"
        md += f"{self.evresi.context}\n\n"
        md += "### Key Facts\n\n"
        for fact in self.evresi.facts[:5]:  # Top 5 facts
            md += f"- {fact}\n"
        md += "\n"
        
        # Analysi section
        md += "## 2. Analysis (Analysi)\n\n"
        md += "### Identified Gaps\n\n"
        for gap in self.analysi.structural_gaps[:3]:  # Top 3 gaps
            md += f"**{gap.get('type', 'Unknown').title()}:** {gap.get('description', 'N/A')}\n\n"
        
        md += "### Key Risks\n\n"
        for risk in self.analysi.risks[:3]:  # Top 3 risks
            md += f"- {risk.get('description', 'N/A')}\n"
        md += "\n"
        
        md += "### Implications\n\n"
        for impl in self.analysi.implications[:3]:
            md += f"- {impl}\n"
        md += "\n"
        
        # Proposi section
        md += "## 3. Proposal (Proposi)\n\n"
        md += f"### {self.proposi.paradigm_name}\n\n"
        md += f"{self.proposi.paradigm_description}\n\n"
        
        md += "### Core Principles\n\n"
        for principle in self.proposi.principles:
            md += f"- {principle}\n"
        md += "\n"
        
        md += "### Implementation Path\n\n"
        for i, step in enumerate(self.proposi.implementation_steps[:3], 1):
            md += f"{i}. **{step.get('name', 'Step')}:** {step.get('description', 'N/A')}\n"
        md += "\n"
        
        md += "### Expected Outcomes\n\n"
        for outcome in self.proposi.expected_outcomes:
            md += f"- {outcome}\n"
        
        md += "\n---\n\n"
        md += f"*Document ID: `{self.id}` | Version: {self.version}*\n"
        
        return md
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "evresi": asdict(self.evresi),
            "analysi": asdict(self.analysi),
            "proposi": asdict(self.proposi),
            "executive_summary": self.executive_summary,
            "author": self.author,
            "version": self.version,
            "tags": self.tags,
            "category": self.category,
            "publish_ready": self.publish_ready,
            "timestamp": self.timestamp
        }


# ═══════════════════════════════════════════════════════════════════════════════
# EAP LAYER ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class EAPLayer:
    """
    EAP Layer - Evresi → Analysi → Proposi
    
    Three-stage conceptual processing for Kloud Content Factory.
    
    Usage:
        eap = EAPLayer()
        
        # Process with Blerina signal
        result = await eap.process(blerina_signal)
        
        # Or process raw document
        result = await eap.process_document(document, topic="governance")
        
        # Get individual layers
        evresi = await eap.generate_evresi(document, source="news")
        analysi = await eap.generate_analysi(evresi, gaps)
        proposi = await eap.generate_proposi(evresi, analysi)
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.1:8b"
        self._processed_count = 0
        self._documents_generated: List[str] = []
        
        # Get Blerina instance
        if BlerinaCore is not None:
            self.blerina = get_blerina()
        else:
            self.blerina = None
    
    # ─────────────────────────────────────────────────────────────────────────
    # MAIN PROCESSING
    # ─────────────────────────────────────────────────────────────────────────
    
    async def process(self, signal: Any) -> EAPDocument:  # signal is BlerinaSignal
        """
        Process a Blerina signal through all 3 EAP layers.
        
        Args:
            signal: BlerinaSignal from gap detection
            
        Returns:
            EAPDocument: Complete document with all 3 layers
        """
        if not signal.eap_ready:
            raise ValueError("Signal is not EAP-ready. Run gap detection first.")
        
        logger.info(f"🔄 Processing EAP for signal: {signal.id}")
        
        # Generate Evresi from signal analysis
        evresi = self._signal_to_evresi(signal)
        
        # Generate Analysi from gaps
        analysi = self._signal_to_analysi(signal, evresi)
        
        # Generate Proposi from analysis
        proposi = await self._generate_proposi_from_analysis(evresi, analysi, signal.analysis)
        
        # Combine into complete EAP document
        eap_doc = self._combine_to_eap(evresi, analysi, proposi)
        
        self._processed_count += 1
        self._documents_generated.append(eap_doc.id)
        
        logger.info(f"✅ EAP document generated: {eap_doc.id}")
        return eap_doc
    
    async def process_document(
        self,
        document: str,
        topic: str = "governance",
        source: str = "document",
        question: Optional[str] = None
    ) -> EAPDocument:
        """
        Process raw document through Blerina + EAP pipeline.
        
        Args:
            document: Raw document text
            topic: Topic for analysis
            source: Source type
            question: Original question if any
            
        Returns:
            EAPDocument: Complete document with all 3 layers
        """
        logger.info("📄 Processing document through EAP pipeline...")
        
        # Step 1: Run Blerina gap detection
        if self.blerina:
            gaps = await self.blerina.extract_gaps(document)
            analysis = await self.blerina.detect_discontinuity([document], topic)
            signal = self.blerina.generate_signal(gaps, analysis)
        else:
            # Fallback without Blerina
            signal = self._create_basic_signal(document, topic)
        
        # Step 2: Process through EAP
        return await self.process(signal)
    
    # ─────────────────────────────────────────────────────────────────────────
    # LAYER 1: EVRESI
    # ─────────────────────────────────────────────────────────────────────────
    
    async def generate_evresi(
        self,
        document: str,
        source: str = "document",
        source_date: Optional[str] = None,
        question: Optional[str] = None
    ) -> EvresiDocument:
        """
        Generate Evresi (Observation) document.
        
        Nxjerr faktet e ftohta, pa opinion, pa interpretim.
        """
        logger.info("📋 Generating Evresi (Observation)...")
        
        # Extract facts using LLM if available
        if httpx:
            facts_data = await self._extract_facts_with_llm(document)
        else:
            facts_data = self._extract_facts_basic(document)
        
        doc_id = f"clx.obs.{hashlib.md5(document[:100].encode()).hexdigest()[:8]}"
        
        evresi = EvresiDocument(
            id=doc_id,
            title=facts_data.get("title", "Observation Document"),
            facts=facts_data.get("facts", []),
            context=facts_data.get("context", document[:500]),
            source=source,
            source_date=source_date,
            entities=facts_data.get("entities", []),
            locations=facts_data.get("locations", []),
            keywords=facts_data.get("keywords", []),
            original_question=question
        )
        
        return evresi
    
    async def _extract_facts_with_llm(self, document: str) -> Dict:
        """Extract facts using LLM"""
        prompt = f"""Analyze this document and extract:
1. A clear title (max 10 words)
2. Key facts (as bullet points, objective, no opinion)
3. Context summary (2-3 sentences)
4. Named entities (people, organizations, systems)
5. Locations mentioned
6. Keywords

Document:
{document[:3000]}

Respond in JSON format:
{{
    "title": "...",
    "facts": ["fact 1", "fact 2", ...],
    "context": "...",
    "entities": ["entity1", "entity2"],
    "locations": ["location1"],
    "keywords": ["keyword1", "keyword2"]
}}
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
                        return json.loads(text)
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            logger.error(f"LLM fact extraction failed: {e}")
        
        return self._extract_facts_basic(document)
    
    def _extract_facts_basic(self, document: str) -> Dict:
        """Basic fact extraction without LLM"""
        sentences = document.split(". ")
        facts = [s.strip() + "." for s in sentences[:5] if len(s) > 20]
        
        # Basic keyword extraction
        words = document.lower().split()
        word_freq: Dict[str, int] = {}
        for word in words:
            if len(word) > 5:
                word_freq[word] = word_freq.get(word, 0) + 1
        keywords = sorted(word_freq, key=lambda w: word_freq[w], reverse=True)[:10]
        
        return {
            "title": "Document Analysis",
            "facts": facts,
            "context": document[:300],
            "entities": [],
            "locations": [],
            "keywords": keywords
        }
    
    def _signal_to_evresi(self, signal: Any) -> EvresiDocument:  # signal is BlerinaSignal
        """Convert Blerina signal to Evresi document"""
        analysis = signal.analysis
        
        # Extract facts from gaps
        facts = [
            f"Document analysis identified {len(signal.gaps)} conceptual gaps",
            f"Discontinuity level: {analysis.discontinuity_level.value}",
            f"Structural void identified: {analysis.structural_void}",
            f"Missing systemic function: {analysis.missing_systemic_function}"
        ]
        
        # Add gap descriptions as facts
        for gap in signal.gaps[:5]:
            facts.append(f"{gap.gap_type.value.title()} gap: {gap.description}")
        
        return EvresiDocument(
            id=f"clx.obs.{signal.id[:12]}",
            title=f"Observation: {analysis.structural_void[:50]}",
            facts=facts,
            context=f"Analysis of {len(analysis.source_documents)} documents revealed {len(signal.gaps)} gaps "
                    f"with {analysis.discontinuity_level.value} discontinuity level.",
            source="blerina_analysis",
            source_date=signal.timestamp[:10],
            entities=[],
            locations=[],
            keywords=[gap.gap_type.value for gap in signal.gaps],
            original_question=None
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # LAYER 2: ANALYSI
    # ─────────────────────────────────────────────────────────────────────────
    
    async def generate_analysi(
        self,
        evresi: EvresiDocument,
        gaps: List[Any],  # List[Gap]
        horizon_years: int = 10
    ) -> AnalysiDocument:
        """
        Generate Analysi (Gap & Risk) document.
        
        Identifikon boshllëqet strukturore dhe rreziqet sistemike.
        """
        logger.info("🔍 Generating Analysi (Gap & Risk)...")
        
        # Convert gaps to structured format
        structural_gaps = [
            {
                "type": gap.gap_type.value,
                "description": gap.description,
                "severity": gap.severity.value,
                "missing": gap.missing_concept
            }
            for gap in gaps
        ]
        
        # Extract discontinuities
        discontinuities = list(set(gap.missing_concept for gap in gaps))
        
        # Generate risks from gaps
        risks = self._gaps_to_risks(gaps)
        
        # Missing concepts
        missing_concepts = [gap.missing_concept for gap in gaps]
        
        # Implications
        implications = []
        for gap in gaps:
            implications.extend(gap.implications)
        implications = list(set(implications))[:10]
        
        # Propagation timeline
        propagation = self._generate_propagation_timeline(gaps, horizon_years)
        
        # Determine severity
        severity = self._calculate_overall_severity(gaps)
        
        doc_id = f"clx.gap.{evresi.id.split('.')[-1]}"
        
        return AnalysiDocument(
            id=doc_id,
            title=f"Analysis: {evresi.title}",
            evresi_id=evresi.id,
            structural_gaps=structural_gaps,
            discontinuities=discontinuities,
            risks=risks,
            missing_concepts=missing_concepts,
            implications=implications,
            propagation_timeline=propagation,
            severity_level=severity
        )
    
    def _signal_to_analysi(self, signal: Any, evresi: EvresiDocument) -> AnalysiDocument:  # signal is BlerinaSignal
        """Convert Blerina signal to Analysi document"""
        analysis = signal.analysis
        
        structural_gaps = [
            {
                "type": gap.gap_type.value,
                "description": gap.description,
                "severity": gap.severity.value,
                "missing": gap.missing_concept
            }
            for gap in signal.gaps
        ]
        
        risks = self._gaps_to_risks(signal.gaps)
        
        propagation = [
            {"timeframe": risk, "description": risk}
            for risk in analysis.propagation_risks
        ]
        
        return AnalysiDocument(
            id=f"clx.gap.{signal.id[:12]}",
            title=f"Gap Analysis: {analysis.structural_void[:50]}",
            evresi_id=evresi.id,
            structural_gaps=structural_gaps,
            discontinuities=[gap.missing_concept for gap in signal.gaps],
            risks=risks,
            missing_concepts=[gap.missing_concept for gap in signal.gaps],
            implications=[impl for gap in signal.gaps for impl in gap.implications],
            propagation_timeline=propagation,
            severity_level=analysis.discontinuity_level.value
        )
    
    def _gaps_to_risks(self, gaps: List[Any]) -> List[Dict]:  # List[Gap]
        """Convert gaps to risk descriptions"""
        risks = []
        
        for gap in gaps:
            risk = {
                "category": gap.gap_type.value,
                "description": f"Risk from {gap.gap_type.value} gap: {gap.missing_concept}",
                "severity": gap.severity.value,
                "implications": gap.implications[:2]
            }
            risks.append(risk)
        
        return risks
    
    def _generate_propagation_timeline(self, gaps: List[Any], horizon_years: int) -> List[Dict]:  # List[Gap]
        """Generate risk propagation timeline"""
        timeline = []
        
        # Short-term
        critical_gaps = [g for g in gaps if g.severity.value in ["critical", "major"]]
        if critical_gaps:
            timeline.append({
                "timeframe": "Years 1-3 (Short-term)",
                "description": f"Immediate risks from {len(critical_gaps)} critical/major gaps. "
                              f"Requires urgent intervention."
            })
        
        # Medium-term
        structural_gaps = [g for g in gaps if g.gap_type.value == "structural"]
        if structural_gaps:
            timeline.append({
                "timeframe": "Years 3-7 (Medium-term)",
                "description": f"Systemic fragmentation as {len(structural_gaps)} structural gaps compound. "
                              f"Architectural review needed."
            })
        
        # Long-term
        sovereignty_gaps = [g for g in gaps if g.gap_type.value == "sovereignty"]
        accountability_gaps = [g for g in gaps if g.gap_type.value == "accountability"]
        
        if sovereignty_gaps or accountability_gaps:
            timeline.append({
                "timeframe": f"Years 7-{horizon_years} (Long-term)",
                "description": f"Potential erosion of control and trust. "
                              f"{len(sovereignty_gaps)} sovereignty gaps and "
                              f"{len(accountability_gaps)} accountability gaps require paradigm shift."
            })
        
        return timeline
    
    def _calculate_overall_severity(self, gaps: List[Any]) -> str:  # List[Gap]
        """Calculate overall severity level"""
        if not gaps:
            return "minor"
        
        severity_scores = {"critical": 4, "major": 3, "moderate": 2, "minor": 1}
        total_score = sum(severity_scores.get(g.severity.value, 1) for g in gaps)
        avg_score = total_score / len(gaps)
        
        if avg_score >= 3.5:
            return "critical"
        elif avg_score >= 2.5:
            return "major"
        elif avg_score >= 1.5:
            return "moderate"
        else:
            return "minor"
    
    # ─────────────────────────────────────────────────────────────────────────
    # LAYER 3: PROPOSI
    # ─────────────────────────────────────────────────────────────────────────
    
    async def generate_proposi(
        self,
        evresi: EvresiDocument,
        analysi: AnalysiDocument
    ) -> ProposiDocument:
        """
        Generate Proposi (Reconstruction) document.
        
        Ndërton konceptin e ri, arkitekturën, zgjidhjen.
        """
        logger.info("🔧 Generating Proposi (Reconstruction)...")
        
        # Generate paradigm using LLM if available
        if httpx:
            paradigm = await self._generate_paradigm_with_llm(evresi, analysi)
        else:
            paradigm = self._generate_paradigm_basic(analysi)
        
        doc_id = f"clx.prop.{analysi.id.split('.')[-1]}"
        
        return ProposiDocument(
            id=doc_id,
            title=f"Proposal: {paradigm['name']}",
            evresi_id=evresi.id,
            analysi_id=analysi.id,
            paradigm_name=paradigm["name"],
            paradigm_description=paradigm["description"],
            architecture=paradigm["architecture"],
            principles=paradigm["principles"],
            implementation_steps=paradigm["steps"],
            expected_outcomes=paradigm["outcomes"],
            addresses_gaps=[g["type"] for g in analysi.structural_gaps],
            alternatives_considered=paradigm.get("alternatives", [])
        )
    
    async def _generate_proposi_from_analysis(
        self,
        evresi: EvresiDocument,
        analysi: AnalysiDocument,
        disc_analysis: Any  # DiscontinuityAnalysis
    ) -> ProposiDocument:
        """Generate Proposi from Blerina discontinuity analysis"""
        
        # Extract key info
        gaps_addressed = [g["type"] for g in analysi.structural_gaps]
        
        # Generate paradigm name
        paradigm_name = self._generate_paradigm_name(disc_analysis)
        
        # Generate architecture
        architecture = self._generate_architecture(disc_analysis)
        
        # Generate principles
        principles = self._generate_principles(disc_analysis)
        
        # Generate implementation steps
        steps = self._generate_implementation_steps(disc_analysis)
        
        # Generate outcomes
        outcomes = self._generate_outcomes(disc_analysis)
        
        return ProposiDocument(
            id=f"clx.prop.{analysi.id.split('.')[-1]}",
            title=f"Proposal: {paradigm_name}",
            evresi_id=evresi.id,
            analysi_id=analysi.id,
            paradigm_name=paradigm_name,
            paradigm_description=f"A new governance paradigm that addresses {disc_analysis.structural_void} "
                                f"by reconstructing the missing systemic function: {disc_analysis.missing_systemic_function}",
            architecture=architecture,
            principles=principles,
            implementation_steps=steps,
            expected_outcomes=outcomes,
            addresses_gaps=gaps_addressed,
            alternatives_considered=[
                "Incremental reform (rejected: insufficient for structural change)",
                "Regulatory patchwork (rejected: creates fragmentation)",
                "Status quo with monitoring (rejected: gaps will compound)"
            ]
        )
    
    def _generate_paradigm_name(self, analysis: Any) -> str:  # DiscontinuityAnalysis
        """Generate a paradigm name based on analysis"""
        # Extract key themes
        gap_types = set()
        for gap in analysis.gaps:
            gap_types.add(gap.gap_type.value)
        
        if "sovereignty" in gap_types:
            return "Sovereign-First Governance Framework (SFGF)"
        elif "accountability" in gap_types:
            return "Distributed Accountability Architecture (DAA)"
        elif "structural" in gap_types:
            return "Integrated Governance Fabric (IGF)"
        elif "interop" in gap_types:
            return "Open Interoperability Protocol (OIP)"
        else:
            return "Next-Generation Governance Paradigm (NGGP)"
    
    def _generate_architecture(self, analysis: Any) -> Dict:  # DiscontinuityAnalysis
        """Generate architecture based on gaps"""
        architecture = {
            "core_layer": {
                "name": "Governance Core",
                "function": "Central coordination without central control",
                "components": ["Policy Engine", "Compliance Monitor", "Audit Trail"]
            },
            "verification_layer": {
                "name": "Distributed Verification",
                "function": "Multi-party verification without single authority",
                "components": ["Validator Network", "Consensus Module", "Attestation Service"]
            },
            "accountability_layer": {
                "name": "Accountability Framework",
                "function": "Clear responsibility chains with enforcement",
                "components": ["Responsibility Registry", "Liability Tracker", "Enforcement Engine"]
            },
            "interop_layer": {
                "name": "Interoperability Bridge",
                "function": "Standards-based integration across systems",
                "components": ["Protocol Adapters", "Data Translators", "API Gateway"]
            }
        }
        
        return architecture
    
    def _generate_principles(self, analysis: Any) -> List[str]:  # DiscontinuityAnalysis
        """Generate principles based on gaps"""
        principles = [
            "Sovereignty Preservation: No system delegates authority without maintaining oversight",
            "Transparency by Design: All decision-making processes are auditable and explainable",
            "Distributed Accountability: Clear responsibility chains with multiple enforcement points",
            "Open Standards: Interoperability through open, inspectable protocols",
            "Resilience through Redundancy: No single point of failure or control"
        ]
        
        # Add gap-specific principles
        for gap in analysis.gaps[:3]:
            if gap.gap_type.value == "regulatory":
                principles.append("Regulatory Clarity: All actions operate within defined legal frameworks")
            elif gap.gap_type.value == "sovereignty":
                principles.append("Sovereign Override: Critical decisions remain under sovereign control")
        
        return principles[:7]  # Max 7 principles
    
    def _generate_implementation_steps(self, analysis: Any) -> List[Dict]:  # DiscontinuityAnalysis
        """Generate implementation steps"""
        return [
            {
                "name": "Foundation Phase",
                "description": "Establish governance framework and core principles. Define accountability chains.",
                "effort": "medium",
                "timeline": "Months 1-3"
            },
            {
                "name": "Architecture Phase",
                "description": "Design and implement core system architecture with verification and audit layers.",
                "effort": "high",
                "timeline": "Months 4-9"
            },
            {
                "name": "Integration Phase",
                "description": "Connect with existing systems through interoperability layer. Migrate critical functions.",
                "effort": "high",
                "timeline": "Months 10-15"
            },
            {
                "name": "Validation Phase",
                "description": "Test all components. Conduct security audits. Verify accountability mechanisms.",
                "effort": "medium",
                "timeline": "Months 16-18"
            },
            {
                "name": "Deployment Phase",
                "description": "Gradual rollout with monitoring. Establish feedback loops. Document lessons learned.",
                "effort": "medium",
                "timeline": "Months 19-24"
            }
        ]
    
    def _generate_outcomes(self, analysis: Any) -> List[str]:  # DiscontinuityAnalysis
        """Generate expected outcomes"""
        outcomes = [
            "Structural gaps closed through comprehensive governance architecture",
            "Clear accountability chains established with enforcement mechanisms",
            "Sovereignty preserved through distributed control mechanisms",
            "Interoperability achieved through open standards adoption",
            "Systemic risks reduced through redundancy and oversight",
            "Trust restored through transparency and auditability",
            "Scalable framework ready for future challenges"
        ]
        
        return outcomes
    
    async def _generate_paradigm_with_llm(self, evresi: EvresiDocument, analysi: AnalysiDocument) -> Dict:
        """Generate paradigm using LLM"""
        prompt = f"""Based on this analysis, propose a new governance paradigm:

Observation:
{evresi.context}

Gaps Found:
{json.dumps(analysi.structural_gaps[:3], indent=2)}

Risks:
{json.dumps(analysi.risks[:3], indent=2)}

Generate a complete proposal with:
1. Paradigm name (professional, descriptive)
2. Description (2-3 sentences)
3. Core architecture (components and their functions)
4. Principles (5-7 key principles)
5. Implementation steps (4-5 phases)
6. Expected outcomes (5-7 outcomes)

Respond in JSON format.
"""
        
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
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
                        return json.loads(text)
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            logger.error(f"LLM paradigm generation failed: {e}")
        
        return self._generate_paradigm_basic(analysi)
    
    def _generate_paradigm_basic(self, analysi: AnalysiDocument) -> Dict:
        """Generate paradigm without LLM"""
        return {
            "name": "Integrated Governance Framework (IGF)",
            "description": "A comprehensive governance framework that addresses identified gaps "
                          "through distributed accountability, transparency, and sovereign control.",
            "architecture": {
                "governance_core": "Central coordination layer",
                "verification_layer": "Multi-party verification",
                "accountability_layer": "Responsibility tracking",
                "interop_layer": "Standards-based integration"
            },
            "principles": [
                "Transparency by design",
                "Distributed accountability",
                "Sovereignty preservation",
                "Open standards",
                "Resilience through redundancy"
            ],
            "steps": [
                {"name": "Foundation", "description": "Establish core framework", "effort": "medium", "timeline": "Q1"},
                {"name": "Build", "description": "Implement architecture", "effort": "high", "timeline": "Q2-Q3"},
                {"name": "Integrate", "description": "Connect systems", "effort": "high", "timeline": "Q4"},
                {"name": "Deploy", "description": "Rollout and monitor", "effort": "medium", "timeline": "Q5"}
            ],
            "outcomes": [
                "Gaps closed",
                "Accountability established",
                "Sovereignty preserved",
                "Interoperability achieved",
                "Trust restored"
            ],
            "alternatives": []
        }
    
    # ─────────────────────────────────────────────────────────────────────────
    # COMBINE TO EAP
    # ─────────────────────────────────────────────────────────────────────────
    
    def _combine_to_eap(
        self,
        evresi: EvresiDocument,
        analysi: AnalysiDocument,
        proposi: ProposiDocument
    ) -> EAPDocument:
        """Combine all 3 layers into complete EAP document"""
        
        # Generate executive summary
        exec_summary = self._generate_executive_summary(evresi, analysi, proposi)
        
        # Generate tags
        tags = self._extract_tags(evresi, analysi)
        
        # Determine category
        category = self._determine_category(analysi)
        
        doc_id = f"clx.eap.{hashlib.md5((evresi.id + analysi.id + proposi.id).encode()).hexdigest()[:10]}"
        
        return EAPDocument(
            id=doc_id,
            title=proposi.title.replace("Proposal: ", ""),
            evresi=evresi,
            analysi=analysi,
            proposi=proposi,
            executive_summary=exec_summary,
            author="Kloud Cloud",
            version="1.0",
            tags=tags,
            category=category,
            publish_ready=True
        )
    
    def _generate_executive_summary(
        self,
        evresi: EvresiDocument,
        analysi: AnalysiDocument,
        proposi: ProposiDocument
    ) -> str:
        """Generate executive summary"""
        summary = f"This analysis examines {evresi.title.lower()} and identifies "
        summary += f"{len(analysi.structural_gaps)} structural gaps with "
        summary += f"{analysi.severity_level} severity. "
        summary += f"Key findings include: {', '.join(analysi.missing_concepts[:3])}. "
        summary += f"We propose the {proposi.paradigm_name} as a comprehensive solution "
        summary += f"that addresses these gaps through {proposi.principles[0].lower()}."
        
        return summary
    
    def _extract_tags(self, evresi: EvresiDocument, analysi: AnalysiDocument) -> List[str]:
        """Extract tags from documents"""
        tags = set(evresi.keywords[:5])
        tags.update(g["type"] for g in analysi.structural_gaps[:3])
        tags.add(analysi.severity_level)
        return list(tags)[:10]
    
    def _determine_category(self, analysi: AnalysiDocument) -> str:
        """Determine document category"""
        gap_types = [g["type"] for g in analysi.structural_gaps]
        
        if "sovereignty" in gap_types:
            return "governance"
        elif "regulatory" in gap_types:
            return "policy"
        elif "accountability" in gap_types:
            return "compliance"
        else:
            return "analysis"
    
    def _create_basic_signal(self, document: str, topic: str) -> Any:
        """Create basic signal when Blerina is not available"""
        # This is a simplified version without full Blerina
        from dataclasses import dataclass as dc
        from dataclasses import field as fld
        
        @dc
        class SimpleGap:
            id: str = "gap_basic"
            gap_type: Any = None
            description: str = "Basic gap detected"
            severity: Any = None
            location: str = "document"
            missing_concept: str = "Detailed analysis needed"
            implications: List[str] = fld(default_factory=list)
            reconstruction_hint: str = "Run full Blerina analysis"
            confidence: float = 0.5
        
        @dc
        class SimpleAnalysis:
            id: str = "analysis_basic"
            source_documents: List[str] = fld(default_factory=list)
            gaps: List[Any] = fld(default_factory=list)
            discontinuity_level: Any = None
            structural_void: str = "Analysis needed"
            missing_systemic_function: str = "Full analysis required"
            propagation_risks: List[str] = fld(default_factory=list)
            reconstruction_needed: str = "Run Blerina for details"
            timestamp: str = ""
        
        @dc
        class SimpleSignal:
            id: str = "signal_basic"
            signal_type: str = "basic"
            gaps: List[Any] = fld(default_factory=list)
            analysis: Any = None
            eap_ready: bool = True
            priority: str = "medium"
            timestamp: str = ""
        
        analysis = SimpleAnalysis()
        return SimpleSignal(analysis=analysis)
    
    # ─────────────────────────────────────────────────────────────────────────
    # UTILITY METHODS
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_stats(self) -> Dict[str, Any]:
        """Get EAP Layer statistics"""
        return {
            "documents_processed": self._processed_count,
            "documents_generated": len(self._documents_generated),
            "model": self.model,
            "blerina_connected": self.blerina is not None,
            "status": "active"
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Global instance
_eap_instance: Optional[EAPLayer] = None


def get_eap() -> EAPLayer:
    """Get or create EAP Layer instance"""
    global _eap_instance
    if _eap_instance is None:
        _eap_instance = EAPLayer()
    return _eap_instance


async def process_eap(document: str, topic: str = "governance") -> Dict:
    """Quick function to process document through EAP"""
    eap = get_eap()
    result = await eap.process_document(document, topic)
    return result.to_dict()


async def generate_clieditorial(document: str, topic: str = "governance") -> str:
    """Generate Clieditorial (complete EAP in markdown)"""
    eap = get_eap()
    result = await eap.process_document(document, topic)
    return result.to_markdown()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN (for testing)
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    async def test_eap():
        print("=" * 70)
        print("📊 EAP LAYER TEST - Evresi → Analysi → Proposi")
        print("=" * 70)
        
        eap = EAPLayer()
        
        # Test document
        test_doc = """
        The European Union has proposed new regulations allowing private AI companies 
        to handle cross-border identity verification without mandatory disclosure of 
        their model architectures or training data. This framework would enable tech 
        giants to authenticate citizens across 27 member states while maintaining 
        proprietary control over their algorithms. Critics argue this creates 
        significant accountability gaps and potential sovereignty issues.
        
        The proposal lacks clear mechanisms for citizen redress, auditing requirements 
        are minimal, and there's no framework for model explainability. Financial 
        institutions and healthcare providers would be required to accept these 
        AI-driven identity verifications, creating systemic dependencies on 
        unregulated private infrastructure.
        """
        
        print("\n📄 Processing test document through EAP pipeline...")
        result = await eap.process_document(
            test_doc,
            topic="AI identity governance",
            source="policy_proposal"
        )
        
        print("\n" + "=" * 70)
        print("📋 EVRESI (Observation)")
        print("=" * 70)
        print(f"ID: {result.evresi.id}")
        print(f"Title: {result.evresi.title}")
        print(f"Facts: {len(result.evresi.facts)}")
        for fact in result.evresi.facts[:3]:
            print(f"  • {fact[:80]}...")
        
        print("\n" + "=" * 70)
        print("🔍 ANALYSI (Gap & Risk)")
        print("=" * 70)
        print(f"ID: {result.analysi.id}")
        print(f"Severity: {result.analysi.severity_level.upper()}")
        print(f"Gaps Found: {len(result.analysi.structural_gaps)}")
        for gap in result.analysi.structural_gaps[:3]:
            print(f"  • {gap['type'].upper()}: {gap['description'][:60]}...")
        
        print("\n" + "=" * 70)
        print("🔧 PROPOSI (Reconstruction)")
        print("=" * 70)
        print(f"ID: {result.proposi.id}")
        print(f"Paradigm: {result.proposi.paradigm_name}")
        print(f"Principles: {len(result.proposi.principles)}")
        for principle in result.proposi.principles[:3]:
            print(f"  • {principle[:70]}...")
        
        print("\n" + "=" * 70)
        print("📰 COMPLETE EAP DOCUMENT")
        print("=" * 70)
        print(f"Document ID: {result.id}")
        print(f"Title: {result.title}")
        print(f"Category: {result.category}")
        print(f"Tags: {', '.join(result.tags[:5])}")
        print(f"Publish Ready: {result.publish_ready}")
        
        print("\n📝 Executive Summary:")
        print(result.executive_summary[:300] + "...")
        
        # Save markdown
        print("\n" + "=" * 70)
        print("💾 Generating Markdown Output...")
        md = result.to_markdown()
        print(f"Generated {len(md)} characters of markdown")
        print("\n--- First 500 chars ---")
        print(md[:500])
        
        print("\n" + "=" * 70)
        print("📊 EAP Layer Stats:")
        stats = eap.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n✅ EAP Layer test complete!")
    
    asyncio.run(test_eap())

