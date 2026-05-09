"""
═══════════════════════════════════════════════════════════════════════════════
OLLAMA ADAPTER - Implementon kontratën e motorit për Ollama
═══════════════════════════════════════════════════════════════════════════════

Ky adapter map-on kontratën unike të Kloud në API-n e Ollama.
Mbështet: chat, completion, embedding.

Author: Ledjan Ahmati / Kloud
"""

import asyncio
import httpx
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

from .contract import (
    BaseEngineAdapter,
    EngineRequest,
    EngineResponse,
    EngineMessage,
    EngineMode,
    EngineType,
    TokenUsage,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

IS_IN_DOCKER = os.path.exists("/.dockerenv") or os.environ.get("DOCKER_ENV") == "1"
OLLAMA_HOST = "host.docker.internal" if IS_IN_DOCKER else "localhost"
OLLAMA_BASE_URL = os.environ.get("OLLAMA_URL", f"http://{OLLAMA_HOST}:11434")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "kloud-ocean:v2")
DEFAULT_TIMEOUT = 120.0


# ═══════════════════════════════════════════════════════════════════════════════
# OLLAMA ADAPTER
# ═══════════════════════════════════════════════════════════════════════════════

class OllamaAdapter(BaseEngineAdapter):
    """
    Adapter për Ollama - LLM lokal
    
    Përdorimi:
        adapter = OllamaAdapter("ollama:kloud-ocean:v2")
        await adapter.initialize()
        response = await adapter.generate(request)
    """
    
    def __init__(
        self,
        engine_id: str = "ollama:default",
        model: str = DEFAULT_MODEL,
        base_url: str = OLLAMA_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        config: Dict[str, Any] = None,
    ):
        super().__init__(engine_id, config)
        
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.engine_type = EngineType.LLM
        self.supported_modes = [EngineMode.CHAT, EngineMode.COMPLETION, EngineMode.EMBEDDING]
        
        self._client: Optional[httpx.AsyncClient] = None
        self._available_models: List[str] = []
        
        # System prompt
        self.default_system_prompt = """You are Ocean AI, the intelligent assistant for Kloud Cloud Platform.

CRITICAL RULES:
1. ALWAYS respond in the SAME LANGUAGE as the user's question
2. Keep responses concise and helpful
3. Be friendly and professional

About Kloud:
- Founder & CEO: Ledjan Ahmati
- Organization: WEB8euroweb GmbH
"""
    
    # ─────────────────────────────────────────────────────────────────────────
    # LIFECYCLE
    # ─────────────────────────────────────────────────────────────────────────
    
    async def initialize(self) -> bool:
        """Inicializon adapterin dhe kontrollon lidhjen me Ollama"""
        try:
            self._client = httpx.AsyncClient(timeout=self.timeout)
            
            # Test connection
            response = await self._client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                self._available_models = [m["name"] for m in data.get("models", [])]
                self._initialized = True
                logger.info(f"✅ Ollama connected: {len(self._available_models)} models available")
                return True
            else:
                logger.warning(f"Ollama connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Ollama initialization error: {e}")
            return False
    
    async def close(self):
        """Mbyll lidhjen"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    # ─────────────────────────────────────────────────────────────────────────
    # GENERATE - METODA KRYESORE
    # ─────────────────────────────────────────────────────────────────────────
    
    async def generate(self, request: EngineRequest) -> EngineResponse:
        """
        Gjeneron përgjigje nga Ollama
        
        Mbështet:
        - CHAT mode: messages → response
        - COMPLETION mode: prompt → response
        - EMBEDDING mode: input_text → vector
        """
        if not self._initialized:
            await self.initialize()
        
        if not self._client:
            return EngineResponse(
                text="",
                engine_id=self.engine_id,
                success=False,
                error="Ollama not connected",
            )
        
        # Route to appropriate method
        if request.mode == EngineMode.CHAT:
            return await self._generate_chat(request)
        elif request.mode == EngineMode.COMPLETION:
            return await self._generate_completion(request)
        elif request.mode == EngineMode.EMBEDDING:
            return await self._generate_embedding(request)
        else:
            return EngineResponse(
                text="",
                engine_id=self.engine_id,
                success=False,
                error=f"Unsupported mode: {request.mode}",
            )
    
    async def _generate_chat(self, request: EngineRequest) -> EngineResponse:
        """Chat mode - mesazhe → përgjigje"""
        
        # Build messages
        messages = []
        
        # Add system prompt if not present
        has_system = any(m.role == "system" for m in request.messages)
        if not has_system:
            messages.append({
                "role": "system",
                "content": self.default_system_prompt,
            })
        
        # Add user messages
        for msg in request.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content,
            })
        
        # Determine model
        model = self.model
        if ":" in request.engine_id:
            parts = request.engine_id.split(":", 1)
            if len(parts) > 1 and parts[1]:
                model = parts[1]
        
        # Build request
        ollama_request = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": request.params.temperature,
                "num_predict": request.params.max_tokens,
                "top_p": request.params.top_p,
                "top_k": request.params.top_k,
            }
        }
        
        if request.params.seed:
            ollama_request["options"]["seed"] = request.params.seed
        
        try:
            response = await self._client.post(
                f"{self.base_url}/api/chat",
                json=ollama_request,
            )
            
            if response.status_code != 200:
                return EngineResponse(
                    text="",
                    engine_id=self.engine_id,
                    success=False,
                    error=f"Ollama error: {response.status_code} - {response.text}",
                )
            
            data = response.json()
            
            return EngineResponse(
                text=data.get("message", {}).get("content", ""),
                engine_id=self.engine_id,
                model_name=model,
                tokens=TokenUsage(
                    input_tokens=data.get("prompt_eval_count", 0),
                    output_tokens=data.get("eval_count", 0),
                ),
                success=True,
                finish_reason="stop" if data.get("done") else "length",
                metadata={
                    "total_duration_ns": data.get("total_duration", 0),
                    "load_duration_ns": data.get("load_duration", 0),
                    "eval_duration_ns": data.get("eval_duration", 0),
                }
            )
            
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            return EngineResponse(
                text="",
                engine_id=self.engine_id,
                success=False,
                error=str(e),
            )
    
    async def _generate_completion(self, request: EngineRequest) -> EngineResponse:
        """Completion mode - prompt → përgjigje"""
        
        prompt = request.prompt or ""
        if not prompt and request.messages:
            # Convert messages to prompt
            prompt = "\n".join(m.content for m in request.messages)
        
        model = self.model
        if ":" in request.engine_id:
            parts = request.engine_id.split(":", 1)
            if len(parts) > 1 and parts[1]:
                model = parts[1]
        
        ollama_request = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": request.params.temperature,
                "num_predict": request.params.max_tokens,
            }
        }
        
        try:
            response = await self._client.post(
                f"{self.base_url}/api/generate",
                json=ollama_request,
            )
            
            if response.status_code != 200:
                return EngineResponse(
                    text="",
                    engine_id=self.engine_id,
                    success=False,
                    error=f"Ollama error: {response.status_code}",
                )
            
            data = response.json()
            
            return EngineResponse(
                text=data.get("response", ""),
                engine_id=self.engine_id,
                model_name=model,
                tokens=TokenUsage(
                    input_tokens=data.get("prompt_eval_count", 0),
                    output_tokens=data.get("eval_count", 0),
                ),
                success=True,
            )
            
        except Exception as e:
            logger.error(f"Ollama completion error: {e}")
            return EngineResponse(
                text="",
                engine_id=self.engine_id,
                success=False,
                error=str(e),
            )
    
    async def _generate_embedding(self, request: EngineRequest) -> EngineResponse:
        """Embedding mode - tekst → vektor"""
        
        text = request.input_text or request.prompt or ""
        if not text and request.messages:
            text = " ".join(m.content for m in request.messages)
        
        model = self.model
        
        ollama_request = {
            "model": model,
            "prompt": text,
        }
        
        try:
            response = await self._client.post(
                f"{self.base_url}/api/embeddings",
                json=ollama_request,
            )
            
            if response.status_code != 200:
                return EngineResponse(
                    text="",
                    engine_id=self.engine_id,
                    success=False,
                    error=f"Ollama embedding error: {response.status_code}",
                )
            
            data = response.json()
            
            return EngineResponse(
                text="",
                engine_id=self.engine_id,
                model_name=model,
                embedding=data.get("embedding", []),
                success=True,
            )
            
        except Exception as e:
            logger.error(f"Ollama embedding error: {e}")
            return EngineResponse(
                text="",
                engine_id=self.engine_id,
                success=False,
                error=str(e),
            )
    
    # ─────────────────────────────────────────────────────────────────────────
    # HEALTH & INFO
    # ─────────────────────────────────────────────────────────────────────────
    
    async def health_check(self) -> Dict[str, Any]:
        """Kontrollon statusin e Ollama"""
        try:
            if not self._client:
                self._client = httpx.AsyncClient(timeout=10)
            
            response = await self._client.get(f"{self.base_url}/api/tags")
            
            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                return {
                    "status": "healthy",
                    "engine_id": self.engine_id,
                    "base_url": self.base_url,
                    "models_available": len(models),
                    "models": models[:10],  # First 10
                    "default_model": self.model,
                }
            else:
                return {
                    "status": "unhealthy",
                    "engine_id": self.engine_id,
                    "error": f"HTTP {response.status_code}",
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "engine_id": self.engine_id,
                "error": str(e),
            }
    
    def get_available_models(self) -> List[str]:
        """Liston modelet e disponueshme"""
        return self._available_models


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY & HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def create_ollama_adapter(
    model: str = DEFAULT_MODEL,
    engine_id: str = None,
) -> OllamaAdapter:
    """Krijon Ollama adapter"""
    eid = engine_id or f"ollama:{model}"
    return OllamaAdapter(engine_id=eid, model=model)


async def test_ollama_connection() -> bool:
    """Teston lidhjen me Ollama"""
    adapter = OllamaAdapter()
    return await adapter.initialize()


__all__ = [
    "OllamaAdapter",
    "create_ollama_adapter",
    "test_ollama_connection",
    "OLLAMA_BASE_URL",
    "DEFAULT_MODEL",
]

