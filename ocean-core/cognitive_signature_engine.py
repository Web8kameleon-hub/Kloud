# -*- coding: utf-8 -*-
"""

[BRAIN] COGNITIVE SIGNATURE ENGINE - Adaptive Intelligence Layer


Vendos nivelin kognitiv t prdoruesit bazuar n:
- Kompleksitetin e pyetjes
- Terminologjin e prdorur
- Strukturn e arsyetimit
- Krkesn pr thellsi

FILOZOFIA:
"Nj njeri mund t mos ket arsim formal, por mund t jet gjeni.
 Sistemi duhet ta kuptoj kt automatikisht."

4 NIVELE:

 Level      Complexity   Karakteristikat                                    

 KIDS       < 0.20       Fjali t shkurtra, metafora, zero zhargon         
 STUDENT    0.20 - 0.45  Edukativ, kritik, orientues                        
 RESEARCH   0.45 - 0.75  Teknike, shkencore, analitike                      
 GENIUS     >= 0.75      Partneritet, matematik e thell, teori            


Author: Kloud Team
Version: 1.0.0 Enterprise
Date: 2026-01-30
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum

logger = logging.getLogger("cognitive_signature")


# 
# COGNITIVE LEVELS
# 

class CognitiveLevel(Enum):
    """Nivelet kognitive t prdoruesit"""
    KIDS = "kids"           # 6-12 vje ose pyetje shum t thjeshta
    STUDENT = "student"     # 13-25 vje ose pyetje edukative
    RESEARCH = "research"   # Profesionist/Shkenctar
    GENIUS = "genius"       # Nivel i lart pavarsisht moshs/arsimit


# 
# COGNITIVE SIGNATURE - Rezultati i analizs
# 

@dataclass
class CognitiveSignature:
    """Nnshkrimi kognitiv i prdoruesit"""
    level: CognitiveLevel
    complexity_score: float          # 0.0 - 1.0
    confidence: float                # Sa i sigurt sht klasifikimi
    
    # Detaje t analizs
    vocabulary_score: float = 0.0    # Niveli i fjalorit
    structure_score: float = 0.0     # Struktura e pyetjes
    depth_score: float = 0.0         # Krkesa pr thellsi
    domain_specificity: float = 0.0  # Sa specifike sht fusha
    
    # Metadata
    detected_domains: List[str] = field(default_factory=list)
    key_concepts: List[str] = field(default_factory=list)
    reasoning_indicators: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "complexity_score": round(self.complexity_score, 3),
            "confidence": round(self.confidence, 3),
            "vocabulary_score": round(self.vocabulary_score, 3),
            "structure_score": round(self.structure_score, 3),
            "depth_score": round(self.depth_score, 3),
            "domain_specificity": round(self.domain_specificity, 3),
            "detected_domains": self.detected_domains,
            "key_concepts": self.key_concepts[:5],  # Top 5
            "reasoning_indicators": self.reasoning_indicators[:3]
        }


# 
# DOMAIN KEYWORDS - Pr detektim t fushave t specializuara
# 

# Fizik Teorike / Kozmologji
PHYSICS_KEYWORDS = {
    "entropy", "entropi", "thermodynamics", "termodinamik",
    "spacetime", "hapsir-koh", "relativity", "relativitet",
    "quantum field", "field theory", "string theory", "teoria e telave",
    "black hole", "vrim e zez", "singularity", "singularitet",
    "Schrdinger", "Heisenberg", "uncertainty", "pasiguri",
    "wave function", "superpozicion", "superposition", "entanglement",
    "cosmological", "kozmologjik", "dark matter", "dark energy",
    "Planck", "Hawking", "Einstein", "Bohr", "Feynman"
}

# Neuroshkenc
NEUROSCIENCE_KEYWORDS = {
    "consciousness", "vetdije", "neural coding", "population vector",
    "tuning curve", "synaptic plasticity", "attractor", "manifold",
    "spike train", "Poisson", "Hebbian", "cortical", "cortex",
    "neuron", "axon", "dendrite", "synapse", "sinaps",
    "prefrontal", "hippocampus", "amygdala", "cerebellum",
    "action potential", "membrane potential", "firing rate",
    "neural network", "brain-computer interface", "BCI",
    "fMRI", "EEG", "MEG", "optogenetics", "connectome",
    "plasticity", "neuroplasticity", "LTP", "LTD"
}

# Matematik e Avancuar
MATH_KEYWORDS = {
    "Kolmogorov", "complexity theory", "information theory",
    "differential equation", "ekuacion diferencial",
    "topology", "topologji", "manifold", "tensor",
    "eigenvalue", "eigenvektor", "Fourier", "Laplace",
    "stochastic", "stokastik", "probability", "probabilitet",
    "integral", "derivat", "derivative", "gradient",
    "Hilbert", "Banach", "Lebesgue", "Riemann",
    "group theory", "teoria e grupeve", "category theory",
    "proof", "theorem", "teorem", "lemma", "corollary"
}

# Filozofi e Thell
PHILOSOPHY_KEYWORDS = {
    "phenomenology", "fenomenologji", "ontology", "ontologji",
    "epistemology", "epistemologji", "metaphysics", "metafizik",
    "IIT", "Integrated Information Theory", "qualia", "panpsychism",
    "consciousness", "free will", "vullneti i lir", "determinism",
    "existentialism", "ekzistencializm", "phenomenal", "noumenal",
    "Kant", "Hegel", "Husserl", "Heidegger", "Wittgenstein",
    "mind-body problem", "hard problem", "zombie argument",
    "emergence", "reduktionism", "dualism", "monism"
}

# AI/ML Avancuar
AI_ML_KEYWORDS = {
    "transformer", "attention mechanism", "self-attention",
    "gradient descent", "backpropagation", "optimization",
    "neural architecture", "deep learning", "machine learning",
    "reinforcement learning", "Q-learning", "policy gradient",
    "GAN", "VAE", "autoencoder", "diffusion model",
    "embedding", "latent space", "representation learning",
    "BERT", "GPT", "LLM", "foundation model",
    "fine-tuning", "transfer learning", "meta-learning",
    "AGI", "ASI", "superintelligence", "alignment problem"
}

# Pyetje t Thjeshta (Kids/Basic)
SIMPLE_KEYWORDS = {
    "far sht", "what is", "si funksionon", "how does",
    "pse", "why", "kur", "when", "ku", "where",
    "m thuaj", "tell me", "shpjego", "explain",
    "a mund", "can you", "dua t di", "I want to know",
    "ndihm", "help", "faleminderit", "thank you"
}


# 
# COGNITIVE SIGNATURE ENGINE
# 

class CognitiveSignatureEngine:
    """
    [BRAIN] COGNITIVE SIGNATURE ENGINE
    
    Analizon pyetjen dhe vendos nivelin kognitiv t prdoruesit.
    
    Filozofia:
    - Jo bazuar n mosh ose arsim
    - Bazuar n strukturn e mendimit
    - Bazuar n thellsin e pyetjes
    - Bazuar n terminologjin e prdorur
    
    Prdorimi:
        engine = CognitiveSignatureEngine()
        signature = engine.analyze("Explain IIT consciousness theory")
        print(signature.level)  # CognitiveLevel.GENIUS
    """
    
    # Thresholds pr nivelet
    THRESHOLDS = {
        "kids": 0.20,      # < 0.20 -> KIDS
        "student": 0.45,   # 0.20 - 0.45 -> STUDENT  
        "research": 0.75,  # 0.45 - 0.75 -> RESEARCH
        # >= 0.75 -> GENIUS
    }
    
    def __init__(self):
        """Inicializon motorin e nnshkrimit kognitiv"""
        # Kombino t gjitha domain keywords
        self.genius_keywords = (
            PHYSICS_KEYWORDS | 
            NEUROSCIENCE_KEYWORDS | 
            MATH_KEYWORDS | 
            PHILOSOPHY_KEYWORDS |
            AI_ML_KEYWORDS
        )
        
        self.simple_keywords = SIMPLE_KEYWORDS
        
        # Domain mapping
        self.domain_keywords = {
            "physics": PHYSICS_KEYWORDS,
            "neuroscience": NEUROSCIENCE_KEYWORDS,
            "mathematics": MATH_KEYWORDS,
            "philosophy": PHILOSOPHY_KEYWORDS,
            "ai_ml": AI_ML_KEYWORDS
        }
        
        # Reasoning indicators - tregojn mendim t thell
        self.reasoning_patterns = [
            r'\b(therefore|prandaj|thus|kshtu)\b',
            r'\b(implies|nnkupton|suggests|sugjeron)\b',
            r'\b(assuming|duke supozuar|given that|duke dhn)\b',
            r'\b(hypothesis|hipotez|theorem|teorem)\b',
            r'\b(if and only if|ather dhe vetm ather)\b',
            r'\b(let .* be|le .* jet)\b',
            r'\b(proof|demonstrim|demonstrate|tregoj)\b',
            r'\b(contradiction|kundrshtim|absurd)\b',
            r'\b(necessary|i domosdoshm|sufficient|i mjaftueshm)\b',
            r'\b(correlat|lidhet|relates to|cause|shkak)\b'
        ]
    
    def analyze(self, query: str) -> CognitiveSignature:
        """
        Analizon pyetjen dhe kthen nnshkrimin kognitiv.
        
        Args:
            query: Pyetja e prdoruesit
            
        Returns:
            CognitiveSignature me nivelin dhe detajet
        """
        q_lower = query.lower().strip()
        words = q_lower.split()
        word_count = len(words)
        
        # 1. Analizo fjalorin
        vocabulary_score = self._analyze_vocabulary(q_lower)
        
        # 2. Analizo strukturn
        structure_score = self._analyze_structure(query, word_count)
        
        # 3. Analizo krkesn pr thellsi
        depth_score = self._analyze_depth(q_lower)
        
        # 4. Analizo specifikn e fushs
        domain_specificity, detected_domains = self._analyze_domains(q_lower)
        
        # 5. Detekto indikatort e arsyetimit
        reasoning_indicators = self._detect_reasoning(query)
        
        # 6. Nxirr konceptet kryesore
        key_concepts = self._extract_concepts(q_lower)
        
        # 7. Llogarit kompleksitetin total
        complexity_score = self._calculate_complexity(
            vocabulary_score,
            structure_score,
            depth_score,
            domain_specificity,
            len(reasoning_indicators)
        )
        
        # 8. Vendos nivelin
        level = self._determine_level(complexity_score)
        
        # 9. Llogarit konfidencn
        confidence = self._calculate_confidence(
            complexity_score, 
            level,
            domain_specificity
        )
        
        return CognitiveSignature(
            level=level,
            complexity_score=complexity_score,
            confidence=confidence,
            vocabulary_score=vocabulary_score,
            structure_score=structure_score,
            depth_score=depth_score,
            domain_specificity=domain_specificity,
            detected_domains=detected_domains,
            key_concepts=key_concepts,
            reasoning_indicators=reasoning_indicators
        )
    
    def _analyze_vocabulary(self, query: str) -> float:
        """Analizon nivelin e fjalorit"""
        # Numro genius keywords
        genius_count = sum(1 for kw in self.genius_keywords if kw.lower() in query)
        
        # Numro simple keywords
        simple_count = sum(1 for kw in self.simple_keywords if kw.lower() in query)
        
        if genius_count >= 3:
            return 0.9
        elif genius_count >= 2:
            return 0.75
        elif genius_count >= 1:
            return 0.5
        elif simple_count >= 2:
            return 0.15
        else:
            return 0.3
    
    def _analyze_structure(self, query: str, word_count: int) -> float:
        """Analizon strukturn e pyetjes"""
        score = 0.3  # Baz
        
        # Pyetje t gjata jan zakonisht m komplekse
        if word_count > 50:
            score += 0.3
        elif word_count > 30:
            score += 0.2
        elif word_count > 15:
            score += 0.1
        elif word_count < 5:
            score -= 0.1
        
        # Ka nn-pyetje?
        if '?' in query and query.count('?') > 1:
            score += 0.1
        
        # Ka list ose numrim?
        if re.search(r'\b[1-9]\.\s|\b[a-z]\)\s|*|->|->', query):
            score += 0.15
        
        # Ka matematik inline?
        if re.search(r'[]|\\frac|\\int|\\sum', query):
            score += 0.25
        
        return min(1.0, max(0.0, score))
    
    def _analyze_depth(self, query: str) -> float:
        """Analizon krkesn pr thellsi"""
        depth_indicators = [
            (r'\b(detail|detaj|in depth|n thellsi)\b', 0.2),
            (r'\b(mechanism|mekanizm|underlying|themelor)\b', 0.25),
            (r'\b(mathematically|matematikisht|formally|formalisht)\b', 0.3),
            (r'\b(prove|demonstro|derive|nxirr)\b', 0.3),
            (r'\b(compare|krahaso|contrast|analyze|analizo)\b', 0.2),
            (r'\b(implications|implikime|consequences|pasoja)\b', 0.25),
            (r'\b(theoretical|teorik|empirical|empirik)\b', 0.2),
            (r'\b(model|modelim|simulate|simulo)\b', 0.2)
        ]
        
        score = 0.2
        for pattern, weight in depth_indicators:
            if re.search(pattern, query, re.IGNORECASE):
                score += weight
        
        return min(1.0, score)
    
    def _analyze_domains(self, query: str) -> Tuple[float, List[str]]:
        """Analizon specifikn e fushs"""
        detected = []
        max_score = 0.0
        
        for domain, keywords in self.domain_keywords.items():
            count = sum(1 for kw in keywords if kw.lower() in query)
            if count > 0:
                detected.append(domain)
                domain_score = min(1.0, count * 0.25)
                max_score = max(max_score, domain_score)
        
        return max_score, detected
    
    def _detect_reasoning(self, query: str) -> List[str]:
        """Detekton indikatort e arsyetimit logjik"""
        found = []
        for pattern in self.reasoning_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                found.extend(matches)
        return list(set(found))
    
    def _extract_concepts(self, query: str) -> List[str]:
        """Nxjerr konceptet kryesore"""
        concepts = []
        
        for keyword in self.genius_keywords:
            if keyword.lower() in query:
                concepts.append(keyword)
        
        return concepts[:10]  # Max 10 koncepte
    
    def _calculate_complexity(
        self,
        vocabulary: float,
        structure: float,
        depth: float,
        domain: float,
        reasoning_count: int
    ) -> float:
        """Llogarit kompleksitetin total"""
        # Peshat e komponentve
        weights = {
            "vocabulary": 0.30,
            "structure": 0.15,
            "depth": 0.25,
            "domain": 0.20,
            "reasoning": 0.10
        }
        
        # Normalizoi reasoning count
        reasoning_score = min(1.0, reasoning_count * 0.2)
        
        complexity = (
            vocabulary * weights["vocabulary"] +
            structure * weights["structure"] +
            depth * weights["depth"] +
            domain * weights["domain"] +
            reasoning_score * weights["reasoning"]
        )
        
        return min(1.0, max(0.0, complexity))
    
    def _determine_level(self, complexity: float) -> CognitiveLevel:
        """Vendos nivelin bazuar n kompleksitet"""
        if complexity < self.THRESHOLDS["kids"]:
            return CognitiveLevel.KIDS
        elif complexity < self.THRESHOLDS["student"]:
            return CognitiveLevel.STUDENT
        elif complexity < self.THRESHOLDS["research"]:
            return CognitiveLevel.RESEARCH
        else:
            return CognitiveLevel.GENIUS
    
    def _calculate_confidence(
        self, 
        complexity: float, 
        level: CognitiveLevel,
        domain_specificity: float
    ) -> float:
        """Llogarit sa i sigurt sht klasifikimi"""
        # Nse kompleksiteti sht pran thresholds, konfidenca ulet
        thresholds = list(self.THRESHOLDS.values())
        
        min_distance = min(abs(complexity - t) for t in thresholds)
        
        # Konfidenca baz
        confidence = 0.7
        
        # Nse larg nga thresholds, konfidenca rritet
        if min_distance > 0.15:
            confidence += 0.2
        elif min_distance > 0.08:
            confidence += 0.1
        
        # Domain specificity rrit konfidencn
        confidence += domain_specificity * 0.1
        
        return min(0.99, max(0.5, confidence))


# 
# FACTORY & SINGLETON
# 

_cognitive_engine: Optional[CognitiveSignatureEngine] = None

def get_cognitive_engine() -> CognitiveSignatureEngine:
    """Merr instancn singleton t motorit kognitiv"""
    global _cognitive_engine
    if _cognitive_engine is None:
        _cognitive_engine = CognitiveSignatureEngine()
    return _cognitive_engine


# 
# QUICK TEST
# 

if __name__ == "__main__":
    engine = get_cognitive_engine()
    
    test_queries = [
        # KIDS level
        ("far sht dielli?", CognitiveLevel.KIDS),
        ("What is a cat?", CognitiveLevel.KIDS),
        
        # STUDENT level  
        ("Si funksionon fotosinteza?", CognitiveLevel.STUDENT),
        ("Explain how gravity works", CognitiveLevel.STUDENT),
        
        # RESEARCH level
        ("Analyze the mechanism of synaptic plasticity in motor learning", CognitiveLevel.RESEARCH),
        ("Compare gradient descent optimization algorithms", CognitiveLevel.RESEARCH),
        
        # GENIUS level
        ("Explain IIT consciousness theory and its implications for panpsychism", CognitiveLevel.GENIUS),
        ("Derive the Kolmogorov complexity bounds for neural manifold dimensionality", CognitiveLevel.GENIUS),
        ("Analyze population vector decoding with Poisson spike variability", CognitiveLevel.GENIUS)
    ]
    
    print("=" * 70)
    print("[BRAIN] COGNITIVE SIGNATURE ENGINE - Test Suite")
    print("=" * 70)
    
    for query, expected in test_queries:
        signature = engine.analyze(query)
        status = "[OK]" if signature.level == expected else "[ERROR]"
        
        print(f"\n{status} Query: {query[:60]}...")
        print(f"   Level: {signature.level.value} (expected: {expected.value})")
        print(f"   Complexity: {signature.complexity_score:.3f}")
        print(f"   Confidence: {signature.confidence:.3f}")
        if signature.detected_domains:
            print(f"   Domains: {', '.join(signature.detected_domains)}")
        if signature.key_concepts:
            print(f"   Concepts: {', '.join(signature.key_concepts[:3])}")
    
    print("\n" + "=" * 70)
    print("Test complete!")

