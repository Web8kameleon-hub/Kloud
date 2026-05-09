"""
═══════════════════════════════════════════════════════════════════════════════
OLLAMA ENGINE - Local AI Integration for Ocean Core
═══════════════════════════════════════════════════════════════════════════════

Integron modele lokale LLM përmes Ollama.
100% Lokale, 100% Private, 0 Pagesa.

Modelet e mbështetura:
- llama3.1:8b (Meta, DEFAULT - flet mirë shqip)
- kloud-ocean:v2 (Kloud, backup)
"""

import asyncio
import httpx
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

logger = logging.getLogger("ollama_engine")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

import os

# Detect if running in Docker (environment variable or file check)
IS_IN_DOCKER = os.path.exists("/.dockerenv") or os.environ.get("DOCKER_ENV") == "1"

# Use host.docker.internal when in Docker to reach Ollama on host
OLLAMA_HOST = "host.docker.internal" if IS_IN_DOCKER else "localhost"
OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:11434"
DEFAULT_MODEL = "llama3.1:8b"  # UPDATED: phi3:mini hequr - nuk flet shqip
DEFAULT_TIMEOUT = 60.0  # seconds

# System prompt - imported from centralized module
try:
    import sys
    sys.path.insert(0, 'c:/Users/Admin/Desktop/Kloud-cloud/modules')
    from curiosity_ocean.curiosity_ocean_prompt import CURIOSITY_OCEAN_SYSTEM_PROMPT
    OCEAN_SYSTEM_PROMPT = CURIOSITY_OCEAN_SYSTEM_PROMPT
except ImportError:
    # Fallback if import fails
    OCEAN_SYSTEM_PROMPT = """You are Curiosity Ocean, the core conversational intelligence of Kloud Platform.
Respond in the same language as the user. Be clear, concise, and intelligent.
Do not fabricate citations or generate random topics. Answer only what is asked."""

# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class OllamaResponse:
    """Përgjigja nga Ollama"""
    content: str
    model: str
    done: bool
    total_duration_ns: int = 0
    load_duration_ns: int = 0
    prompt_eval_count: int = 0
    eval_count: int = 0
    eval_duration_ns: int = 0
    
    @property
    def total_duration_ms(self) -> float:
        return self.total_duration_ns / 1_000_000
    
    @property
    def tokens_per_second(self) -> float:
        if self.eval_duration_ns > 0:
            return (self.eval_count / self.eval_duration_ns) * 1_000_000_000
        return 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# OLLAMA ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class OllamaEngine:
    """
    Motor për komunikim me Ollama API.
    Përdor modele lokale LLM për gjenerim përgjigjes.
    """
    
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = OLLAMA_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        system_prompt: str = OCEAN_SYSTEM_PROMPT
    ):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.system_prompt = system_prompt
        self._client: Optional[httpx.AsyncClient] = None
        self._available = False
        self._checked = False
        
        logger.info(f"🦙 OllamaEngine initialized with model: {model}")
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-load HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout
            )
        return self._client
    
    async def is_available(self) -> bool:
        """Kontrollo nëse Ollama është i disponueshëm"""
        if self._checked:
            return self._available
            
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            self._available = response.status_code == 200
            self._checked = True
            
            if self._available:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                logger.info(f"✅ Ollama available with models: {models}")
            
            return self._available
        except Exception as e:
            logger.warning(f"⚠️ Ollama not available: {e}")
            self._available = False
            self._checked = True
            return False
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        context: Optional[List[int]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> OllamaResponse:
        """
        Gjenero përgjigje nga modeli.
        
        Args:
            prompt: Pyetja/teksti për të procesuar
            system: System prompt (opsional, përdor default nëse None)
            context: Konteksti nga biseda e mëparshme
            temperature: Kreativiteti (0.0-1.0)
            max_tokens: Numri maksimal i tokenëve
        
        Returns:
            OllamaResponse me përgjigjen
        """
        if not await self.is_available():
            return OllamaResponse(
                content="⚠️ Ollama nuk është aktiv. Sigurohu që Ollama po ekzekutohet.",
                model=self.model,
                done=True
            )
        
        try:
            client = await self._get_client()
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system or self.system_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }
            
            if context:
                payload["context"] = context
            
            response = await client.post("/api/generate", json=payload)
            
            if response.status_code != 200:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return OllamaResponse(
                    content=f"⚠️ Gabim nga Ollama: {response.status_code}",
                    model=self.model,
                    done=True
                )
            
            data = response.json()
            
            return OllamaResponse(
                content=data.get("response", ""),
                model=data.get("model", self.model),
                done=data.get("done", True),
                total_duration_ns=data.get("total_duration", 0),
                load_duration_ns=data.get("load_duration", 0),
                prompt_eval_count=data.get("prompt_eval_count", 0),
                eval_count=data.get("eval_count", 0),
                eval_duration_ns=data.get("eval_duration", 0)
            )
            
        except httpx.TimeoutException:
            logger.error("Ollama timeout")
            return OllamaResponse(
                content="⚠️ Ollama u vonua shumë. Provo një pyetje më të shkurtër.",
                model=self.model,
                done=True
            )
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return OllamaResponse(
                content=f"⚠️ Gabim: {str(e)}",
                model=self.model,
                done=True
            )
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> OllamaResponse:
        """
        Chat mode me histori bisede.
        
        Args:
            messages: Lista e mesazheve [{"role": "user/assistant", "content": "..."}]
            temperature: Kreativiteti
            max_tokens: Tokens maksimale
        
        Returns:
            OllamaResponse
        """
        if not await self.is_available():
            return OllamaResponse(
                content="⚠️ Ollama nuk është aktiv.",
                model=self.model,
                done=True
            )
        
        try:
            client = await self._get_client()
            
            # Shto system message në fillim
            full_messages = [
                {"role": "system", "content": self.system_prompt}
            ] + messages
            
            payload = {
                "model": self.model,
                "messages": full_messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }
            
            response = await client.post("/api/chat", json=payload)
            
            if response.status_code != 200:
                return OllamaResponse(
                    content=f"⚠️ Gabim: {response.status_code}",
                    model=self.model,
                    done=True
                )
            
            data = response.json()
            message = data.get("message", {})
            
            return OllamaResponse(
                content=message.get("content", ""),
                model=data.get("model", self.model),
                done=data.get("done", True),
                total_duration_ns=data.get("total_duration", 0),
                eval_count=data.get("eval_count", 0),
                eval_duration_ns=data.get("eval_duration", 0)
            )
            
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            return OllamaResponse(
                content=f"⚠️ Gabim: {str(e)}",
                model=self.model,
                done=True
            )
    
    async def list_models(self) -> List[str]:
        """Lista e modeleve të disponueshme"""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
            return []
        except:
            return []
    
    async def close(self):
        """Mbyll klientin"""
        if self._client:
            await self._client.aclose()
            self._client = None


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_ollama_engine: Optional[OllamaEngine] = None

def get_ollama_engine(model: str = DEFAULT_MODEL) -> OllamaEngine:
    """Merr singleton instance të OllamaEngine"""
    global _ollama_engine
    if _ollama_engine is None:
        _ollama_engine = OllamaEngine(model=model)
    return _ollama_engine


async def quick_ask(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Funksion i shpejtë për pyetje të thjeshta"""
    engine = get_ollama_engine(model)
    response = await engine.generate(prompt)
    return response.content


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    async def test():
        print("═" * 60)
        print("OLLAMA ENGINE TEST")
        print("═" * 60)
        
        engine = get_ollama_engine()
        
        # Check availability
        available = await engine.is_available()
        print(f"✅ Ollama available: {available}")
        
        if available:
            # List models
            models = await engine.list_models()
            print(f"📦 Models: {models}")
            
            # Test generation
            print("\n🧪 Testing generation...")
            response = await engine.generate("Sa është 25 + 17? Përgjigju shkurt.")
            print(f"📝 Response: {response.content}")
            print(f"⏱️ Time: {response.total_duration_ms:.0f}ms")
            print(f"🚀 Speed: {response.tokens_per_second:.1f} tokens/sec")
            
            # Test chat
            print("\n💬 Testing chat...")
            messages = [
                {"role": "user", "content": "Kush ishte Skënderbeu?"}
            ]
            chat_response = await engine.chat(messages)
            print(f"📝 Response: {chat_response.content[:200]}...")
        
        await engine.close()
        print("\n✅ Test complete!")
    
    asyncio.run(test())

