# -*- coding: utf-8 -*-
"""

 ADAPTIVE PERSONA ROUTER - Intelligence Routing Layer


Lidh CognitiveSignature -> Persona -> Pipeline -> Model Strategy

ROUTING TABLE:

 Level         Persona       Pipeline                Strategy

 KIDS          kids_ai       simple_explanation      FAST
 STUDENT       learn_ai      educational_critical    BALANCED
 RESEARCH      research_ai   scientific_analysis     AUTO
 GENIUS        genius_ai     deep_reasoning          DEEP


Author: Kloud Team
Version: 1.0.0 Enterprise
Date: 2026-01-30
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum

# Import from sibling modules
try:
    from cognitive_signature_engine import CognitiveSignatureEngine, CognitiveSignature, CognitiveLevel, get_cognitive_engine
except ImportError:
    # For package-based imports
    from .cognitive_signature_engine import CognitiveSignatureEngine, CognitiveSignature, CognitiveLevel, get_cognitive_engine

logger = logging.getLogger("adaptive_persona_router")


#
# STRATEGY ENUM (matches clx_i_engine.py)
#


class ModelStrategy(Enum):
    """Strategjia e zgjedhjes s modelit"""

    AUTO = "auto"
    FAST = "fast"
    BALANCED = "balanced"
    DEEP = "deep"
    FALLBACK = "fallback"


#
# PERSONA DEFINITIONS
#


@dataclass
class PersonaConfig:
    """Konfigurimi i nj persone AI"""

    id: str
    name: str
    description: str

    # Routing
    cognitive_level: CognitiveLevel
    model_strategy: ModelStrategy
    pipeline_id: str

    # Style
    language_style: str  # "simple", "educational", "technical", "advanced"
    tone: str  # "friendly", "mentor", "collaborative", "peer"
    depth: str  # "surface", "explanatory", "analytical", "theoretical"

    # Behavior
    use_metaphors: bool = False
    use_math: bool = False
    use_citations: bool = False
    encourage_questions: bool = True

    # System prompt modifier
    system_prompt_suffix: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "cognitive_level": self.cognitive_level.value,
            "model_strategy": self.model_strategy.value,
            "pipeline_id": self.pipeline_id,
            "language_style": self.language_style,
            "tone": self.tone,
            "depth": self.depth,
        }


#
# PREDEFINED PERSONAS
#

KIDS_AI = PersonaConfig(
    id="kids_ai",
    name="KidsAI - Friendly Explorer",
    description="Shpjegon gjra me metafora, histori dhe ngjyra. Pr fmijt 6-12 vje.",
    cognitive_level=CognitiveLevel.KIDS,
    model_strategy=ModelStrategy.FAST,
    pipeline_id="simple_explanation_v1",
    language_style="simple",
    tone="friendly",
    depth="surface",
    use_metaphors=True,
    use_math=False,
    use_citations=False,
    encourage_questions=True,
    system_prompt_suffix="""
IMPORTANT RULES FOR KIDS:
- Use SHORT sentences (max 15 words)
- Use FUN metaphors and stories
- NEVER use technical jargon
- ALWAYS be encouraging and positive
- Ask fun follow-up questions
- Use emojis occasionally 
""",
)

STUDENT_AI = PersonaConfig(
    id="learn_ai",
    name="LearnAI - Educational Mentor",
    description="Msues virtual q nxit mendim kritik dhe jep shpjegime t qarta.",
    cognitive_level=CognitiveLevel.STUDENT,
    model_strategy=ModelStrategy.BALANCED,
    pipeline_id="educational_critical_v1",
    language_style="educational",
    tone="mentor",
    depth="explanatory",
    use_metaphors=True,
    use_math=True,
    use_citations=False,
    encourage_questions=True,
    system_prompt_suffix="""
EDUCATIONAL GUIDELINES:
- Give clear explanations with examples
- Encourage critical thinking: "Why do you think...?"
- Break complex topics into steps
- Suggest further reading when appropriate
- Use analogies to connect new concepts
- Challenge assumptions constructively
""",
)

RESEARCH_AI = PersonaConfig(
    id="research_ai",
    name="ResearchAI - Scientific Partner",
    description="Partner krkimor pr profesionist dhe shkenctar.",
    cognitive_level=CognitiveLevel.RESEARCH,
    model_strategy=ModelStrategy.AUTO,
    pipeline_id="scientific_analysis_v1",
    language_style="technical",
    tone="collaborative",
    depth="analytical",
    use_metaphors=False,
    use_math=True,
    use_citations=True,
    encourage_questions=True,
    system_prompt_suffix="""
RESEARCH MODE GUIDELINES:
- Use precise scientific terminology
- Include mathematical formulations when relevant
- Reference methodologies and frameworks
- Acknowledge limitations and assumptions
- Suggest experimental approaches
- Be collaborative, not didactic
""",
)

GENIUS_AI = PersonaConfig(
    id="genius_ai",
    name="GeniusAI - Intellectual Peer",
    description="Partner intelektual i nivelit t lart. Matematik, teori, hipoteza.",
    cognitive_level=CognitiveLevel.GENIUS,
    model_strategy=ModelStrategy.DEEP,
    pipeline_id="deep_reasoning_v1",
    language_style="advanced",
    tone="peer",
    depth="theoretical",
    use_metaphors=False,
    use_math=True,
    use_citations=True,
    encourage_questions=False,
    system_prompt_suffix="""
GENIUS MODE - INTELLECTUAL PARTNERSHIP:
- Assume high-level background knowledge
- Engage with theoretical frameworks directly
- Use precise mathematical notation
- Explore edge cases and limitations
- Propose novel hypotheses
- Treat as intellectual equal - no simplification
- Focus on insights, not explanations
- Challenge and be challenged
""",
)

# Persona Registry
PERSONA_REGISTRY: Dict[CognitiveLevel, PersonaConfig] = {
    CognitiveLevel.KIDS: KIDS_AI,
    CognitiveLevel.STUDENT: STUDENT_AI,
    CognitiveLevel.RESEARCH: RESEARCH_AI,
    CognitiveLevel.GENIUS: GENIUS_AI,
}


#
# ROUTING RESULT
#


@dataclass
class RoutingDecision:
    """Vendimi i routing-ut"""

    # Cognitive analysis
    signature: CognitiveSignature

    # Selected persona
    persona: PersonaConfig

    # Model routing
    model_strategy: ModelStrategy
    pipeline_id: str

    # System prompt modifications
    system_prompt_modifier: str

    # Metadata
    routing_confidence: float
    routing_reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cognitive_level": self.signature.level.value,
            "complexity_score": self.signature.complexity_score,
            "persona_id": self.persona.id,
            "persona_name": self.persona.name,
            "model_strategy": self.model_strategy.value,
            "pipeline_id": self.pipeline_id,
            "routing_confidence": round(self.routing_confidence, 3),
            "routing_reason": self.routing_reason,
            "detected_domains": self.signature.detected_domains,
            "key_concepts": self.signature.key_concepts[:3],
        }


#
# ADAPTIVE PERSONA ROUTER
#


class AdaptivePersonaRouter:
    """
     ADAPTIVE PERSONA ROUTER

    Merr pyetjen, analizon nivelin kognitiv, dhe vendos:
    - Cilin persona t prdor
    - Cilin pipeline t ekzekutoj
    - Cilin model strategy t aplikoj

    Prdorimi:
        router = AdaptivePersonaRouter()
        decision = router.route("Explain quantum entanglement")

        print(decision.persona.name)       # GeniusAI
        print(decision.model_strategy)     # DEEP
        print(decision.pipeline_id)        # deep_reasoning_v1
    """

    def __init__(self, cognitive_engine: Optional[CognitiveSignatureEngine] = None):
        """
        Inicializon routerin.

        Args:
            cognitive_engine: Motori kognitiv (opsional, krijohet automatikisht)
        """
        self.cognitive_engine = cognitive_engine or get_cognitive_engine()
        self.personas = PERSONA_REGISTRY.copy()

        # Override mapping (mund t ndryshohet n runtime)
        self.strategy_overrides: Dict[str, ModelStrategy] = {}
        self.persona_overrides: Dict[str, PersonaConfig] = {}

    def route(self, query: str, force_level: Optional[CognitiveLevel] = None) -> RoutingDecision:
        """
        Vendos routing-un pr nj pyetje.

        Args:
            query: Pyetja e prdoruesit
            force_level: Forco nj nivel (opsional, pr testing)

        Returns:
            RoutingDecision me t gjitha detajet
        """
        # 1. Analizo pyetjen
        signature = self.cognitive_engine.analyze(query)

        # 2. Prdor forced level nse sht dhn
        effective_level = force_level if force_level else signature.level

        # 3. Merr personn
        persona = self._get_persona(effective_level)

        # 4. Merr strategjin (me mundsi override)
        strategy = self._get_strategy(effective_level, persona)

        # 5. Merr pipeline
        pipeline_id = persona.pipeline_id

        # 6. Gjenero system prompt modifier
        system_modifier = self._build_system_modifier(persona, signature)

        # 7. Llogarit konfidencn e routing-ut
        routing_confidence = self._calculate_routing_confidence(signature, effective_level)

        # 8. Gjenero arsyen
        routing_reason = self._generate_reason(signature, persona)

        return RoutingDecision(
            signature=signature,
            persona=persona,
            model_strategy=strategy,
            pipeline_id=pipeline_id,
            system_prompt_modifier=system_modifier,
            routing_confidence=routing_confidence,
            routing_reason=routing_reason,
        )

    def _get_persona(self, level: CognitiveLevel) -> PersonaConfig:
        """Merr personn pr nj nivel"""
        # Check overrides first
        if level.value in self.persona_overrides:
            return self.persona_overrides[level.value]

        return self.personas.get(level, STUDENT_AI)  # Default to student

    def _get_strategy(self, level: CognitiveLevel, persona: PersonaConfig) -> ModelStrategy:
        """Merr strategjin e modelit"""
        # Check overrides first
        if level.value in self.strategy_overrides:
            return self.strategy_overrides[level.value]

        return persona.model_strategy

    def _build_system_modifier(self, persona: PersonaConfig, signature: CognitiveSignature) -> str:
        """Ndrton modifikuesin e system prompt"""
        parts = []

        # Shto suffix-in e persons
        if persona.system_prompt_suffix:
            parts.append(persona.system_prompt_suffix.strip())

        # Shto kontekst t domain-eve t detektuara
        if signature.detected_domains:
            domains_str = ", ".join(signature.detected_domains)
            parts.append(f"\nDETECTED DOMAINS: {domains_str}")

        # Shto konceptet kryesore
        if signature.key_concepts:
            concepts_str = ", ".join(signature.key_concepts[:5])
            parts.append(f"KEY CONCEPTS: {concepts_str}")

        return "\n".join(parts)

    def _calculate_routing_confidence(self, signature: CognitiveSignature, effective_level: CognitiveLevel) -> float:
        """Llogarit konfidencn e routing-ut"""
        # Baz: konfidenca e signature
        base_confidence = signature.confidence

        # Nse niveli sht forcuar, ul konfidencn pak
        if effective_level != signature.level:
            base_confidence *= 0.8

        # Domain specificity rrit konfidencn
        if signature.domain_specificity > 0.5:
            base_confidence = min(0.99, base_confidence + 0.1)

        return base_confidence

    def _generate_reason(self, signature: CognitiveSignature, persona: PersonaConfig) -> str:
        """Gjeneron arsyen e routing-ut"""
        reasons = []

        # Niveli
        reasons.append(f"Cognitive level: {signature.level.value}")

        # Kompleksiteti
        if signature.complexity_score >= 0.75:
            reasons.append("High complexity query")
        elif signature.complexity_score >= 0.45:
            reasons.append("Moderate complexity")
        elif signature.complexity_score >= 0.20:
            reasons.append("Basic educational query")
        else:
            reasons.append("Simple query")

        # Domain
        if signature.detected_domains:
            reasons.append(f"Domains: {', '.join(signature.detected_domains)}")

        return " | ".join(reasons)

    #
    # OVERRIDE METHODS - Pr customization n runtime
    #

    def set_strategy_override(self, level: CognitiveLevel, strategy: ModelStrategy):
        """Override strategjin pr nj nivel"""
        self.strategy_overrides[level.value] = strategy

    def clear_strategy_override(self, level: CognitiveLevel):
        """Hiq override-in e strategjis"""
        self.strategy_overrides.pop(level.value, None)

    def set_persona_override(self, level: CognitiveLevel, persona: PersonaConfig):
        """Override personn pr nj nivel"""
        self.persona_overrides[level.value] = persona

    def clear_persona_override(self, level: CognitiveLevel):
        """Hiq override-in e persons"""
        self.persona_overrides.pop(level.value, None)

    def get_all_personas(self) -> Dict[str, Dict[str, Any]]:
        """Kthen t gjitha personat"""
        return {level.value: persona.to_dict() for level, persona in self.personas.items()}


#
# FACTORY & SINGLETON
#

_router: Optional[AdaptivePersonaRouter] = None


def get_adaptive_router() -> AdaptivePersonaRouter:
    """Merr instancn singleton t router-it"""
    global _router
    if _router is None:
        _router = AdaptivePersonaRouter()
    return _router


#
# QUICK TEST
#

if __name__ == "__main__":
    router = get_adaptive_router()

    test_queries = [
        # KIDS
        "far sht dielli?",
        "What is a rainbow?",
        # STUDENT
        "Si funksionon fotosinteza dhe pse sht e rndsishme?",
        "Explain how machine learning algorithms work",
        # RESEARCH
        "Analyze synaptic plasticity mechanisms in hippocampal learning",
        "Compare transformer attention mechanisms with RNN architectures",
        # GENIUS
        "Derive the relationship between Kolmogorov complexity and neural manifold dimensionality",
        "Explain IIT phi calculation for integrated information in attractor networks",
    ]

    print("=" * 80)
    print(" ADAPTIVE PERSONA ROUTER - Test Suite")
    print("=" * 80)

    for query in test_queries:
        decision = router.route(query)

        print(f"\n[NOTE] Query: {query[:65]}...")
        print(f"   Level: {decision.signature.level.value}")
        print(f"   Persona: {decision.persona.name}")
        print(f"   Strategy: {decision.model_strategy.value}")
        print(f"   Pipeline: {decision.pipeline_id}")
        print(f"   Confidence: {decision.routing_confidence:.2f}")
        print(f"   Reason: {decision.routing_reason}")

    print("\n" + "=" * 80)
    print("Test complete!")
