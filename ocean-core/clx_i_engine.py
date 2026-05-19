# -*- coding: utf-8 -*-
"""

 CLX.I MULTI-MODEL ENGINE - Enterprise Edition


Bashkon T GJITHA modelet CLX n nj sistem t vetm:

MODELET E DISPONUESHME:

 Model                    Size      Prdorimi

 kloud-ocean:v2        4.9 GB    [TARGET] DEFAULT - Pyetje t prgjithshme
 llama3.1:8b              4.9 GB    [SYNC] BACKUP - Fallback i sigurt
 gpt-oss:120b             65 GB     [BRAIN] DEEP - Analiza komplekse (microservice 8031)


STRATEGJIT:
1. AUTO - Zgjedh modelin sipas kompleksitetit t pyetjes
2. BALANCED - Prdor modele mesatare (v2, llama3.1) - DEFAULT
3. DEEP - Prdor modelin e madh (gpt-oss:120b) - via microservice 8031
4. FALLBACK - Provo modele n rradh nse njri dshton

HEQUR: phi3:mini, kloud-ocean:latest - nuk flasin shqip

Author: Kloud Team
Version: 2.0.1 Enterprise
"""

import asyncio
import httpx
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger("clx_i_engine")

#
# CONFIGURATION
#

IS_IN_DOCKER = os.path.exists("/.dockerenv") or os.environ.get("DOCKER_ENV") == "1"
# Use environment variable first, then container name for Docker, localhost for dev
# Container name in docker-compose.yml is "kloud-clx"
CLX_HOST = os.environ.get("CLX_HOST", os.environ.get("OLLAMA_HOST", "kloud-clx" if IS_IN_DOCKER else "localhost"))
# Clean up CLX_HOST if it contains http://
if CLX_HOST.startswith("http://"):
    CLX_HOST = CLX_HOST.replace("http://", "").split(":")[0]
CLX_BASE_URL = os.environ.get("CLX_URL", os.environ.get("OLLAMA_URL", f"http://{CLX_HOST}:11434"))
DEFAULT_TIMEOUT = 90.0  # Hetzner server needs more time for LLM


class ModelTier(Enum):
    """Niveli i modelit sipas madhsis dhe fuqis"""

    FAST = "fast"  # DISABLED - modelet e hequra
    BALANCED = "balanced"  # 4.9GB - kloud-ocean:v2, llama3.1:8b (DEFAULT)
    DEEP = "deep"  # 65GB - gpt-oss:120b (microservice 8031)


class Strategy(Enum):
    """Strategjia e zgjedhjes s modelit"""

    AUTO = "auto"  # Zgjedh automatikisht sipas pyetjes
    FAST = "fast"  # Gjithmon modele t shpejta
    BALANCED = "balanced"  # Gjithmon modele mesatare
    DEEP = "deep"  # Gjithmon modeli i madh
    FALLBACK = "fallback"  # Provo n rradh derisa njri funksionon


#
# MODEL REGISTRY - T gjitha modelet e disponueshme
#


@dataclass
class ClxModel:
    """Definicioni i nj modeli CLX"""

    name: str
    size_gb: float
    tier: ModelTier
    description: str
    context_length: int = 8192
    priority: int = 0  # 0 = highest priority in tier
    is_available: bool = True
    avg_response_ms: float = 0.0
    total_requests: int = 0
    failed_requests: int = 0


# T gjitha modelet e instaluara
# HEQUR: phi3:mini, kloud-ocean:latest, llama3.2:1b - nuk flasin shqip
AVAILABLE_MODELS: Dict[str, ClxModel] = {
    # ═══════════════════════════════════════════════════════════════════════════
    # TIER: BALANCED (4.9GB) - DEFAULT - Modelet e vetme që flasin mirë
    # ═══════════════════════════════════════════════════════════════════════════
    "llama3.1:8b": ClxModel(
        name="llama3.1:8b",
        size_gb=4.9,
        tier=ModelTier.BALANCED,
        description="Meta Llama 3.1 8B - Default model (~3-5s)",
        context_length=8192,
        priority=0,  # PRIMARY MODEL
    ),
    "kloud-ocean:v2": ClxModel(
        name="kloud-ocean:v2",
        size_gb=4.9,
        tier=ModelTier.BALANCED,
        description="Kloud Ocean v2 - Backup model (~3-5s)",
        context_length=8192,
        priority=1,
    ),
}

# Fallback order - VETËM MODELE QË FLASIN MIRË
# HEQUR: llama3.2:1b, phi3:mini, kloud-ocean:latest - flasin përçart
FALLBACK_ORDER = [
    "llama3.1:8b",  # 1st: I VETMI I BESUESHËM (4.9GB)
    "kloud-ocean:v2",  # 2nd: Backup (4.9GB)
]


#
# QUERY COMPLEXITY ANALYZER
#


class QueryComplexityAnalyzer:
    """Analizon kompleksitetin e pyetjes pr t zgjedhur modelin e duhur"""

    # Keywords q tregojn pyetje komplekse - EXTENDED for scientific domains
    DEEP_KEYWORDS = {
        # Analiza
        "analyze",
        "analyse",
        "analiz",
        "analizo",
        "explain in detail",
        "compare",
        "krahaso",
        "contrast",
        "research",
        "krko",
        # Reasoning
        "why",
        "pse",
        "reason",
        "arsye",
        "prove",
        "demonstrate",
        "logic",
        "logjik",
        "philosophy",
        "filozofi",
        # Technical
        "algorithm",
        "algoritm",
        "architecture",
        "arkitektur",
        "implement",
        "implemento",
        "design",
        "dizajno",
        "optimize",
        # Science
        "quantum",
        "kuantike",
        "neural",
        "neurale",
        "consciousness",
        "vetdije",
        "mathematics",
        "matematik",
        "physics",
        "fizik",
        # Business
        "strategy",
        "strategji",
        "business plan",
        "market analysis",
        #
        # EXTENDED: Fizik Teorike / Kozmologji
        #
        "entropy",
        "entropi",
        "thermodynamics",
        "termodinamik",
        "spacetime",
        "hapsir-koh",
        "relativity",
        "relativitet",
        "quantum field",
        "field theory",
        "string theory",
        "black hole",
        "singularity",
        "singularitet",
        "Schrdinger",
        "Heisenberg",
        "uncertainty",
        "pasiguri",
        "wave function",
        "superpozicion",
        "superposition",
        "entanglement",
        "cosmological",
        "kozmologjik",
        "dark matter",
        "dark energy",
        "Planck",
        "Hawking",
        "Einstein",
        "Feynman",
        #
        # EXTENDED: Neuroshkenc
        #
        "neural coding",
        "population vector",
        "population coding",
        "tuning curve",
        "synaptic plasticity",
        "attractor",
        "manifold",
        "spike train",
        "Poisson",
        "Hebbian",
        "cortical",
        "cortex",
        "prefrontal",
        "hippocampus",
        "amygdala",
        "cerebellum",
        "action potential",
        "membrane potential",
        "firing rate",
        "brain-computer interface",
        "BCI",
        "connectome",
        "neuroplasticity",
        "LTP",
        "LTD",
        "optogenetics",
        "fMRI",
        "EEG",
        "MEG",
        #
        # EXTENDED: Matematik e Avancuar
        #
        "Kolmogorov",
        "complexity theory",
        "information theory",
        "differential equation",
        "ekuacion diferencial",
        "topology",
        "topologji",
        "tensor",
        "eigenvalue",
        "eigenvektor",
        "Fourier",
        "Laplace",
        "stochastic",
        "stokastik",
        "probability",
        "probabilitet",
        "Hilbert",
        "Banach",
        "Lebesgue",
        "Riemann",
        "group theory",
        "category theory",
        "theorem",
        "teorem",
        "lemma",
        "corollary",
        "proof",
        "gradient",
        "derivat",
        "derivative",
        "integral",
        #
        # EXTENDED: Filozofi e Thell
        #
        "phenomenology",
        "fenomenologji",
        "ontology",
        "ontologji",
        "epistemology",
        "epistemologji",
        "metaphysics",
        "metafizik",
        "IIT",
        "Integrated Information Theory",
        "qualia",
        "panpsychism",
        "free will",
        "vullneti i lir",
        "determinism",
        "existentialism",
        "phenomenal",
        "noumenal",
        "Kant",
        "Hegel",
        "Husserl",
        "Heidegger",
        "Wittgenstein",
        "mind-body problem",
        "hard problem",
        "zombie argument",
        "emergence",
        "reduktionism",
        "dualism",
        "monism",
        #
        # EXTENDED: AI/ML Avancuar
        #
        "transformer",
        "attention mechanism",
        "self-attention",
        "gradient descent",
        "backpropagation",
        "optimization",
        "neural architecture",
        "deep learning",
        "machine learning",
        "reinforcement learning",
        "Q-learning",
        "policy gradient",
        "GAN",
        "VAE",
        "autoencoder",
        "diffusion model",
        "embedding",
        "latent space",
        "representation learning",
        "BERT",
        "GPT",
        "LLM",
        "foundation model",
        "fine-tuning",
        "transfer learning",
        "meta-learning",
        "AGI",
        "ASI",
        "superintelligence",
        "alignment problem",
    }

    # Keywords pr pyetje t shpejta
    FAST_KEYWORDS = {
        "hi",
        "hello",
        "prshndetje",
        "tungjatjeta",
        "thanks",
        "faleminderit",
        "bye",
        "mirupafshim",
        "yes",
        "no",
        "po",
        "jo",
        "ok",
        "okay",
        "what time",
        "sa sht ora",
        "date",
        "dat",
        "weather",
        "moti",
        "temperature",
        "temperatur",
    }

    @classmethod
    def analyze(cls, query: str) -> Tuple[ModelTier, float]:
        """
        Analizon pyetjen dhe kthen tier-in e rekomanduar.

        Returns:
            (ModelTier, confidence)
        """
        q_lower = query.lower().strip()
        word_count = len(q_lower.split())

        # 0) CRITICAL: Non-English detection - ALWAYS use BALANCED for multilingual
        # phi3:mini doesn't handle Albanian, Greek, German well
        non_english_patterns = [
            # Albanian
            "ë",
            "ç",
            "përshëndetje",
            "mirëmëngjes",
            "faleminderit",
            "flisni",
            "shqip",
            "unë",
            "jam",
            "jemi",
            "është",
            "çfarë",
            "pse",
            "kush",
            "ku",
            "si",
            # German
            "ü",
            "ö",
            "ä",
            "ß",
            "guten",
            "morgen",
            "tag",
            "abend",
            "danke",
            "bitte",
            "sprechen",
            "deutsch",
            "verstehen",
            "können",
            "möchten",
            # Greek
            "γεια",
            "καλημέρα",
            "ευχαριστώ",
            "παρακαλώ",
            "ελληνικά",
            "μιλάτε",
            "giea",
            "kalimera",
            "milate",
            "ellenika",
            "efharisto",
            # Italian
            "buongiorno",
            "ciao",
            "grazie",
            "prego",
            "parli",
            "italiano",
            # Russian (transliterated)
            "privet",
            "zdravstvuyte",
            "spasibo",
            "govorite",
            "russki",
            "pozhaluysta",
            # French
            "bonjour",
            "merci",
            "français",
            "parlez",
            # Spanish
            "hola",
            "buenos",
            "gracias",
            "habla",
            "español",
        ]

        is_non_english = any(p in q_lower for p in non_english_patterns)
        if is_non_english:
            return (ModelTier.BALANCED, 0.95)  # Force BALANCED for multilingual

        # ═══════════════════════════════════════════════════════════════════════
        # PRODUCTION FIX: ALWAYS use BALANCED - phi3:mini disabled
        # phi3:mini causes hallucination loops, never use FAST tier
        # ═══════════════════════════════════════════════════════════════════════

        # 1) Short queries -> BALANCED (NOT FAST anymore)
        if word_count <= 3:
            return (ModelTier.BALANCED, 0.95)  # Changed from FAST

        # 2) Check for deep keywords - now with better scoring
        deep_score = sum(1 for kw in cls.DEEP_KEYWORDS if kw in q_lower)

        # Only use DEEP tier if gpt-oss:120b is specifically requested
        # For AUTO strategy, prefer BALANCED which has reliable models
        # Pyetje normale me 3+ deep keywords = BALANCED (not DEEP anymore)
        if deep_score >= 3:
            return (ModelTier.BALANCED, 0.85)  # Use balanced for complex too

        # 3) Check for fast keywords - NOW RETURNS BALANCED instead of FAST
        fast_score = sum(1 for kw in cls.FAST_KEYWORDS if kw in q_lower)
        if fast_score >= 1:
            return (ModelTier.BALANCED, 0.85)  # Changed from FAST

        # 4) Medium length -> BALANCED
        if word_count <= 20:
            return (ModelTier.BALANCED, 0.80)

        # 5) Longer queries -> leaning DEEP
        if word_count > 30:
            return (ModelTier.DEEP, 0.70)

        # Default: BALANCED
        return (ModelTier.BALANCED, 0.75)


#
# RESPONSE DATA CLASS
#


@dataclass
class MultiModelResponse:
    """Prgjigja nga Multi-Model Engine"""

    content: str
    model_used: str
    tier: ModelTier
    strategy: Strategy
    done: bool
    total_duration_ms: float = 0.0
    tokens_per_second: float = 0.0
    fallback_attempts: int = 0
    query_complexity: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


#
# CLX.I MULTI-MODEL ENGINE
#


class ClxIEngine:
    """
     CLX.I MULTI-MODEL ENGINE

    Bashkon t gjitha modelet CLX n nj sistem enterprise t vetm.

    Prdorimi:
        engine = ClxIEngine()
        await engine.initialize()

        # Auto mode - zgjedh modelin sipas pyetjes
        response = await engine.generate("What is quantum physics?")

        # Specific strategy
        response = await engine.generate("Hi!", strategy=Strategy.FAST)
        response = await engine.generate("Analyze this complex problem...", strategy=Strategy.DEEP)
    """

    def __init__(
        self,
        base_url: str = CLX_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        default_strategy: Strategy = Strategy.FAST,  # CHANGED: Use FAST by default for speed
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_strategy = default_strategy
        self.models = AVAILABLE_MODELS.copy()

        self._client: Optional[httpx.AsyncClient] = None
        self._initialized = False
        self._available_models: List[str] = []

        # Stats
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "fallback_activations": 0,
            "requests_by_tier": {t.value: 0 for t in ModelTier},
            "requests_by_model": {},
        }

        # System prompt - with fallback if centralized Master Prompt unavailable
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load system prompt from centralized location or use fallback."""
        try:
            import sys
            import os

            # Try multiple possible paths for the master prompt
            possible_paths = [
                os.path.join(os.path.dirname(__file__), "..", "modules"),
                "c:/Users/Admin/Desktop/Kloud-cloud/modules",
                "/app/modules",  # Docker path
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    if path not in sys.path:
                        sys.path.insert(0, path)
                    try:
                        from curiosity_ocean.master_prompt import CURIOSITY_OCEAN_SYSTEM_PROMPT

                        return CURIOSITY_OCEAN_SYSTEM_PROMPT
                    except ImportError:
                        continue
        except Exception:
            pass

        # Fallback system prompt if import fails
        return """You are Curiosity Ocean, the AI of Kloud Platform (kloud.cloud).
Created by Ledjan Ahmati. Respond in the user's language. Be concise, accurate, helpful.
Never invent facts. Admit if unsure: "Nuk e di" / "I don't know"."""

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-load HTTP client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=httpx.Timeout(self.timeout, connect=10.0))
        return self._client

    async def initialize(self) -> bool:
        """Inicializon engine dhe kontrollon modelet e disponueshme"""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")

            if response.status_code == 200:
                data = response.json()
                self._available_models = [m["name"] for m in data.get("models", [])]

                # Update availability
                for model_name, model in self.models.items():
                    model.is_available = model_name in self._available_models

                self._initialized = True
                logger.info(f" ClxIEngine initialized with {len(self._available_models)} models")
                logger.info(f"   [PKG] Available: {self._available_models}")
                return True

            return False
        except Exception as e:
            logger.error(f"Failed to initialize ClxIEngine: {e}")
            return False

    def _select_model(self, query: str, strategy: Strategy) -> Tuple[str, ModelTier]:
        """Zgjedh modelin - VETËM llama3.1:8b (modelet e vogla flasin përçart)"""

        # FORCE: llama3.1:8b - I VETMI QË FLET MIRË!
        if "llama3.1:8b" in self._available_models:
            return "llama3.1:8b", ModelTier.BALANCED

        # Backup: kloud-ocean:v2 (4.9GB)
        if "kloud-ocean:v2" in self._available_models:
            return "kloud-ocean:v2", ModelTier.BALANCED

        # Last resort: first available
        if self._available_models:
            return self._available_models[0], ModelTier.BALANCED

        return "llama3.1:8b", ModelTier.BALANCED

    async def generate(
        self,
        prompt: str,
        strategy: Strategy = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        force_model: Optional[str] = None,
    ) -> MultiModelResponse:
        """
        Gjenero prgjigje duke prdorur multi-model strategy.

        Args:
            prompt: Pyetja
            strategy: Strategjia (AUTO, FAST, BALANCED, DEEP, FALLBACK)
            system: System prompt custom (opsional)
            temperature: Kreativiteti (0.0-1.0)
            max_tokens: Tokens maksimale
            force_model: Forco nj model specifik (anashkalon strategjin)

        Returns:
            MultiModelResponse me prgjigjen dhe metadata
        """
        strategy = strategy or self.default_strategy

        if not self._initialized:
            await self.initialize()

        self.stats["total_requests"] += 1

        # Determine model
        if force_model and force_model in self.models:
            model_name = force_model
            tier = self.models[force_model].tier
        else:
            model_name, tier = self._select_model(prompt, strategy)

        # Query complexity for metadata
        _, complexity = QueryComplexityAnalyzer.analyze(prompt)

        # Try with fallback
        fallback_attempts = 0
        models_to_try = [model_name] if strategy != Strategy.FALLBACK else FALLBACK_ORDER

        for try_model in models_to_try:
            if try_model not in self._available_models:
                continue

            try:
                response = await self._call_clx(
                    model=try_model, prompt=prompt, system=system or self.system_prompt, temperature=temperature, max_tokens=max_tokens
                )

                if response and response.get("response"):
                    # Success!
                    self.stats["successful_requests"] += 1
                    self.stats["requests_by_tier"][tier.value] += 1
                    self.stats["requests_by_model"][try_model] = self.stats["requests_by_model"].get(try_model, 0) + 1

                    total_duration_ms = response.get("total_duration", 0) / 1_000_000
                    eval_count = response.get("eval_count", 0)
                    eval_duration = response.get("eval_duration", 1)
                    tokens_per_second = (eval_count / eval_duration) * 1_000_000_000 if eval_duration else 0

                    # Update model stats
                    model_obj = self.models.get(try_model)
                    if model_obj:
                        model_obj.total_requests += 1
                        # Running average
                        model_obj.avg_response_ms = (
                            model_obj.avg_response_ms * (model_obj.total_requests - 1) + total_duration_ms
                        ) / model_obj.total_requests

                    return MultiModelResponse(
                        content=response["response"],
                        model_used=try_model,
                        tier=self.models.get(try_model, AVAILABLE_MODELS.get(model_name)).tier,
                        strategy=strategy,
                        done=response.get("done", True),
                        total_duration_ms=total_duration_ms,
                        tokens_per_second=tokens_per_second,
                        fallback_attempts=fallback_attempts,
                        query_complexity=complexity,
                        metadata={
                            "prompt_eval_count": response.get("prompt_eval_count", 0),
                            "eval_count": eval_count,
                        },
                    )

            except Exception as e:
                logger.warning(f"Model {try_model} failed: {e}")
                fallback_attempts += 1
                self.stats["fallback_activations"] += 1

                if try_model in self.models:
                    self.models[try_model].failed_requests += 1

        # All models failed
        self.stats["failed_requests"] += 1
        return MultiModelResponse(
            content="",
            model_used="none",
            tier=ModelTier.BALANCED,
            strategy=strategy,
            done=False,
            fallback_attempts=fallback_attempts,
            query_complexity=complexity,
            metadata={
                "error": "all_models_failed",
                "message": "No available model returned a valid response",
            },
        )

    async def _call_clx(self, model: str, prompt: str, system: str, temperature: float, max_tokens: int) -> Optional[Dict[str, Any]]:
        """Thirr CLX API"""
        client = await self._get_client()

        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        response = await client.post("/api/generate", json=payload)

        if response.status_code == 200:
            return response.json()

        logger.error(f"CLX returned {response.status_code}: {response.text[:200]}")
        return None

    async def chat(
        self, messages: List[Dict[str, str]], strategy: Strategy = None, temperature: float = 0.7, max_tokens: int = 2048
    ) -> MultiModelResponse:
        """Chat mode me histori bisede"""
        strategy = strategy or self.default_strategy

        if not self._initialized:
            await self.initialize()

        # Get last user message for complexity analysis
        last_user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        model_name, tier = self._select_model(last_user_msg, strategy)

        try:
            client = await self._get_client()

            full_messages = [{"role": "system", "content": self.system_prompt}] + messages

            payload = {
                "model": model_name,
                "messages": full_messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }

            response = await client.post("/api/chat", json=payload)

            if response.status_code == 200:
                data = response.json()
                message = data.get("message", {})

                return MultiModelResponse(
                    content=message.get("content", ""),
                    model_used=model_name,
                    tier=tier,
                    strategy=strategy,
                    done=data.get("done", True),
                    total_duration_ms=data.get("total_duration", 0) / 1_000_000,
                    query_complexity=0.0,
                )

        except Exception as e:
            logger.error(f"Chat error: {e}")

        return MultiModelResponse(content="[WARN] Chat dshtoi.", model_used="none", tier=ModelTier.BALANCED, strategy=strategy, done=True)

    def get_stats(self) -> Dict[str, Any]:
        """Merr statistikat e engine"""
        return {
            **self.stats,
            "available_models": self._available_models,
            "model_performance": {
                name: {
                    "avg_response_ms": m.avg_response_ms,
                    "total_requests": m.total_requests,
                    "failed_requests": m.failed_requests,
                    "success_rate": ((m.total_requests - m.failed_requests) / m.total_requests * 100 if m.total_requests > 0 else 100),
                }
                for name, m in self.models.items()
                if m.is_available
            },
        }

    async def close(self):
        """Mbyll klientin"""
        if self._client:
            await self._client.aclose()
            self._client = None


#
# SINGLETON INSTANCE
#

_multi_engine: Optional[ClxIEngine] = None


def get_clx_i_engine() -> ClxIEngine:
    """Get singleton instance"""
    global _multi_engine
    if _multi_engine is None:
        _multi_engine = ClxIEngine()
    return _multi_engine


async def quick_generate(prompt: str, strategy: Strategy = Strategy.AUTO) -> str:
    """Funksion i shpejt pr pyetje"""
    engine = get_clx_i_engine()
    response = await engine.generate(prompt, strategy=strategy)
    return response.content


#
# TEST
#

if __name__ == "__main__":

    async def test():
        print("" * 70)
        print(" CLX.I MULTI-MODEL ENGINE TEST")
        print("" * 70)

        engine = get_clx_i_engine()
        initialized = await engine.initialize()

        if not initialized:
            print("[ERROR] Failed to initialize - is CLX running?")
            return

        print(f"\n[OK] Initialized with {len(engine._available_models)} models:")
        for name in engine._available_models:
            model = engine.models.get(name)
            if model:
                print(f"   * {name} ({model.size_gb}GB) - {model.tier.value}")

        # Test queries
        test_cases = [
            ("Hi!", Strategy.AUTO, "Should use FAST"),
            ("What is 2+2?", Strategy.AUTO, "Should use FAST/BALANCED"),
            ("Explain quantum entanglement in detail", Strategy.AUTO, "Should use DEEP"),
            ("far sht Kloud?", Strategy.BALANCED, "Albanian - BALANCED"),
        ]

        print("\n" + "" * 70)
        print(" TESTING STRATEGIES")
        print("" * 70)

        for query, strategy, expected in test_cases:
            print(f"\n[NOTE] Query: {query[:50]}...")
            print(f"   Strategy: {strategy.value} ({expected})")

            response = await engine.generate(query, strategy=strategy, max_tokens=100)

            print(f"   Model: {response.model_used} ({response.tier.value})")
            print(f"   Time: {response.total_duration_ms:.0f}ms")
            print(f"   Speed: {response.tokens_per_second:.1f} tok/s")
            print(f"   Response: {response.content[:100]}...")

        # Stats
        print("\n" + "" * 70)
        print("[DATA] STATS")
        print("" * 70)
        stats = engine.get_stats()
        print(f"   Total requests: {stats['total_requests']}")
        print(f"   Successful: {stats['successful_requests']}")
        print(f"   By tier: {stats['requests_by_tier']}")

        await engine.close()
        print("\n[OK] Test complete!")

    asyncio.run(test())
