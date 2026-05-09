# -*- coding: utf-8 -*-
"""
⚡ OLLAMA FAST ENGINE - Microservice Edition
============================================

LINJA OPTIKE - Zero overhead, zero fallback, zero kompleksitet.

NUK KA:
- Strategji komplekse
- Analiza keyword-esh  
- Fallback loops
- Modele 65GB
- Statistika/metadata të rënda

KA VETËM:
- 1 model (llama3.2:1b - 1.3GB)
- 1 thirrje HTTP
- 1 përgjigje

Koha e pritshme: 3-8 sekonda (jo 40-90!)

Author: Kloud Team
Version: 3.0.0 FAST
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Optional

import httpx

logger = logging.getLogger("ollama_fast")

# ═══════════════════════════════════════════════════════════════════════════════
# KONFIGURIM - MINIMAL
# ═══════════════════════════════════════════════════════════════════════════════

IS_DOCKER = os.path.exists("/.dockerenv") or os.environ.get("DOCKER_ENV") == "1"
# Container name in docker-compose.yml is "kloud-ollama"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "kloud-ollama" if IS_DOCKER else "localhost")
if OLLAMA_HOST.startswith("http://"):
    OLLAMA_HOST = OLLAMA_HOST.replace("http://", "").split(":")[0]

OLLAMA_URL = os.environ.get("OLLAMA_URL", f"http://{OLLAMA_HOST}:11434")

# TIMEOUT: Pa limit për streaming, 120s për chat normal
TIMEOUT = 120.0
STREAM_TIMEOUT = None  # Pa limit për streaming

# ═══════════════════════════════════════════════════════════════════════════════
# MODEL SELECTION - VETËM MODELE QË FLASIN MIRË
# ═══════════════════════════════════════════════════════════════════════════════
# HEQUR: phi3:mini, kloud-ocean:latest - flasin përçart në shqip
# MBAJTUR: llama3.1:8b - flet mirë të gjitha gjuhët

DEFAULT_MODEL = "llama3.1:8b"  # Model i vetëm i besueshëm
FALLBACK_MODELS = ["llama3.1:8b", "kloud-ocean:v2"]  # Vetëm modele të mëdha

# ALBANIAN DETECTION
ALBANIAN_MARKERS = [
    "ë", "ç", "përshëndetje", "mirëmëngjes", "faleminderit", "shqip",
    "unë", "jam", "jemi", "është", "çfarë", "pse", "kush", "ku", "kur",
    "mirëdita", "tungjatjeta", "ndihmë", "pyetje", "përgjigje",
]

# SYSTEM PROMPT - Import from Master Prompt
SYSTEM_PROMPT: str
try:
    import sys
    from pathlib import Path
    modules_path = Path(__file__).parent.parent / "modules"
    if modules_path.exists():
        sys.path.insert(0, str(modules_path))
        from curiosity_ocean.master_prompt import (
            CURIOSITY_OCEAN_COMPACT_PROMPT,  # type: ignore
        )
        SYSTEM_PROMPT = CURIOSITY_OCEAN_COMPACT_PROMPT
        logger.info("⚡ Master prompt loaded (compact)")
    else:
        raise ImportError("modules path does not exist")
except Exception as e:
    logger.warning(f"⚠️ Could not import master_prompt: {e}")
    # Fallback - minimal prompt
    SYSTEM_PROMPT = """You are Curiosity Ocean, the AI of Kloud Platform (kloud.cloud).
Created by Ledjan Ahmati. Respond in the user's language. Be concise, accurate, helpful.
Never invent facts. Admit if unsure: "Nuk e di" / "I don't know"."""


# ═══════════════════════════════════════════════════════════════════════════════
# RESPONSE - MINIMAL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FastResponse:
    """Përgjigje minimale"""
    content: str
    model: str
    duration_ms: float
    success: bool


# ═══════════════════════════════════════════════════════════════════════════════
# OLLAMA FAST ENGINE - LINJA OPTIKE
# ═══════════════════════════════════════════════════════════════════════════════

class OllamaFastEngine:
    """
    ⚡ OLLAMA FAST ENGINE
    
    Zero overhead. Zero fallback. Zero kompleksitet.
    Vetëm një thirrje direkte te Ollama.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.url = OLLAMA_URL
        self._client: Optional[httpx.AsyncClient] = None
        self._model_verified = False
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy client - krijohet vetëm një herë"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.url,
                timeout=httpx.Timeout(TIMEOUT, connect=5.0)
            )
        return self._client
    
    async def verify_model(self) -> bool:
        """Verifiko modelin - thirret vetëm 1 herë"""
        if self._model_verified:
            return True
        
        try:
            client = await self._get_client()
            resp = await client.get("/api/tags", timeout=5.0)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                
                # Provo modelet në renditje prioriteti
                for model in FALLBACK_MODELS:
                    if model in models:
                        self.model = model
                        self._model_verified = True
                        logger.info(f"⚡ Model {model} gati")
                        return True
                
                # Përdor çdo model të disponueshëm
                if models:
                    self.model = models[0]
                    self._model_verified = True
                    logger.info(f"⚡ Duke përdorur {self.model}")
                    return True
        except Exception as e:
            logger.error(f"❌ Ollama nuk u gjet: {e}")
        
        return False
    
    async def generate(self, prompt: str, system: str = None) -> FastResponse:
        """
        ⚡ GJENERO - Një thirrje, një përgjigje
        
        Args:
            prompt: Pyetja
            system: System prompt (opsional)
        
        Returns:
            FastResponse
        """
        import time
        start = time.perf_counter()
        
        # Verifiko modelin (vetëm herën e parë)
        if not self._model_verified:
            await self.verify_model()
        
        try:
            client = await self._get_client()
            
            # THIRRJE E VETME - pa fallback, pa retry
            resp = await client.post(
                "/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system or SYSTEM_PROMPT,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1024,  # Max tokens - mjaftueshëm
                    }
                }
            )
            
            elapsed_ms = (time.perf_counter() - start) * 1000
            
            if resp.status_code == 200:
                data = resp.json()
                return FastResponse(
                    content=data.get("response", ""),
                    model=self.model,
                    duration_ms=elapsed_ms,
                    success=True
                )
            
            logger.error(f"Ollama error: {resp.status_code}")
            return FastResponse(
                content=f"Gabim: Ollama ktheu {resp.status_code}",
                model=self.model,
                duration_ms=elapsed_ms,
                success=False
            )
            
        except httpx.TimeoutException:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return FastResponse(
                content="Timeout - Ollama nuk u përgjigj në kohë",
                model=self.model,
                duration_ms=elapsed_ms,
                success=False
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error(f"Generate error: {e}")
            return FastResponse(
                content=f"Gabim: {str(e)}",
                model=self.model,
                duration_ms=elapsed_ms,
                success=False
            )
    
    async def chat(self, message: str) -> FastResponse:
        """Alias për generate - për compatibility"""
        return await self.generate(message)
    
    async def generate_stream(self, prompt: str, system: str = None):
        """
        ⚡ STREAMING - Tokens one by one (SSE format)
        
        Args:
            prompt: Pyetja
            system: System prompt (opsional)
        
        Yields:
            Chunks of response as they arrive
        """
        # Verifiko modelin (vetëm herën e parë)
        if not self._model_verified:
            await self.verify_model()
        
        try:
            # Streaming client - pa timeout
            stream_client = httpx.AsyncClient(
                base_url=self.url,
                timeout=httpx.Timeout(STREAM_TIMEOUT, connect=10.0)
            )
            
            # STREAMING REQUEST
            async with stream_client.stream(
                "POST",
                "/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system or SYSTEM_PROMPT,
                    "stream": True,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 2048,
                    }
                }
            ) as resp:
                if resp.status_code == 200:
                    async for line in resp.aiter_lines():
                        if line:
                            try:
                                import json
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                            except:
                                pass
                else:
                    yield f"[Gabim: Ollama ktheu {resp.status_code}]"
            
            await stream_client.aclose()
                    
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"[Gabim: {str(e)}]"
    
    async def close(self):
        """Mbyll klientin"""
        if self._client:
            await self._client.aclose()
            self._client = None


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_engine: Optional[OllamaFastEngine] = None


def get_fast_engine() -> OllamaFastEngine:
    """Merr singleton"""
    global _engine
    if _engine is None:
        _engine = OllamaFastEngine()
    return _engine


async def fast_generate(prompt: str) -> str:
    """⚡ Funksion i shpejtë - një linjë"""
    engine = get_fast_engine()
    response = await engine.generate(prompt)
    return response.content


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    async def test():
        print("=" * 60)
        print("⚡ OLLAMA FAST ENGINE TEST")
        print("=" * 60)
        
        engine = get_fast_engine()
        
        tests = [
            "Përshëndetje!",
            "What is 2+2?",
            "Çfarë është Kloud?",
        ]
        
        for q in tests:
            print(f"\n📝 {q}")
            r = await engine.generate(q)
            print(f"⏱️  {r.duration_ms:.0f}ms | ✅ {r.success}")
            print(f"💬 {r.content[:150]}...")
        
        await engine.close()
        print("\n✅ Test complete!")
    
    asyncio.run(test())

