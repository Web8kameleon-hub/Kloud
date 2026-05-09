"""
═══════════════════════════════════════════════════════════════════════════════
PIPELINE FRAMEWORK - Multi-step AI Pipelines
═══════════════════════════════════════════════════════════════════════════════

Pipelines janë sekuenca hapash për përpunim AI/ML.

Shembull:
  Step 1: Embeddings nga embedding_model
  Step 2: Vector search në knowledge_base
  Step 3: LLM (Ollama) për answer synthesis

Ruajtur si YAML:
  id: qa_rag_v1
  steps:
    - type: embed
      engine: local-embed-01
    - type: search
      index: kb_ai_ml
    - type: llm
      engine: ollama:deepthink

Author: Ledjan Ahmati / Kloud
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from datetime import datetime
import uuid
import asyncio
import json
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class StepType(Enum):
    """Llojet e hapave në pipeline"""
    LLM = "llm"                    # Language Model generation
    EMBED = "embed"                # Generate embeddings
    SEARCH = "search"              # Vector/keyword search
    CLASSIFY = "classify"          # Classification
    RERANK = "rerank"              # Rerank results
    TRANSFORM = "transform"        # Data transformation
    FILTER = "filter"              # Filter results
    MERGE = "merge"                # Merge multiple inputs
    BRANCH = "branch"              # Conditional branching
    TOOL = "tool"                  # External tool call
    CODE = "code"                  # Code execution


class PipelineStatus(Enum):
    """Statuset e pipeline-it"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ═══════════════════════════════════════════════════════════════════════════════
# STEP DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PipelineStep:
    """Hap i vetëm në pipeline"""
    id: str = field(default_factory=lambda: f"step_{uuid.uuid4().hex[:8]}")
    name: str = ""
    type: StepType = StepType.LLM
    
    # Engine/Resource
    engine: Optional[str] = None           # p.sh. "ollama:llama3.1"
    index: Optional[str] = None            # p.sh. "kb_ai_ml" për search
    tool: Optional[str] = None             # p.sh. "code_runner" për tool
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Input/Output mapping
    input_from: Optional[str] = None       # ID i hapit nga merr input
    input_key: str = "output"              # Çelësi i output-it të hapit të mëparshëm
    output_key: str = "output"             # Çelësi ku ruhet rezultati
    
    # Conditional
    condition: Optional[str] = None        # p.sh. "prev.confidence > 0.8"
    
    # Timeout
    timeout_seconds: float = 60.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "engine": self.engine,
            "index": self.index,
            "tool": self.tool,
            "config": self.config,
            "input_from": self.input_from,
            "timeout_seconds": self.timeout_seconds,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PipelineStep":
        return cls(
            id=data.get("id", f"step_{uuid.uuid4().hex[:8]}"),
            name=data.get("name", ""),
            type=StepType(data.get("type", "llm")),
            engine=data.get("engine"),
            index=data.get("index"),
            tool=data.get("tool"),
            config=data.get("config", {}),
            input_from=data.get("input_from"),
            input_key=data.get("input_key", "output"),
            output_key=data.get("output_key", "output"),
            condition=data.get("condition"),
            timeout_seconds=data.get("timeout_seconds", 60.0),
        )


@dataclass
class StepResult:
    """Rezultati i një hapi"""
    step_id: str
    success: bool = True
    output: Any = None
    error: Optional[str] = None
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Pipeline:
    """
    PIPELINE - Sekuencë hapash për përpunim AI/ML
    """
    id: str = field(default_factory=lambda: f"pipe_{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    
    # Steps
    steps: List[PipelineStep] = field(default_factory=list)
    
    # Input/Output schema
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    
    # Default persona
    persona_id: Optional[str] = None
    
    # Metadata
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "persona_id": self.persona_id,
            "version": self.version,
            "tags": self.tags,
        }
    
    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), default_flow_style=False, allow_unicode=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pipeline":
        steps = [PipelineStep.from_dict(s) for s in data.get("steps", [])]
        return cls(
            id=data.get("id", f"pipe_{uuid.uuid4().hex[:12]}"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            steps=steps,
            persona_id=data.get("persona_id"),
            version=data.get("version", "1.0"),
            tags=data.get("tags", []),
        )
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> "Pipeline":
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PipelineExecution:
    """Ekzekutimi i një pipeline"""
    id: str = field(default_factory=lambda: f"exec_{uuid.uuid4().hex[:12]}")
    pipeline_id: str = ""
    status: PipelineStatus = PipelineStatus.PENDING
    
    # Input/Output
    input_data: Any = None
    output_data: Any = None
    
    # Step results
    step_results: Dict[str, StepResult] = field(default_factory=dict)
    current_step: Optional[str] = None
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Error
    error: Optional[str] = None
    
    @property
    def total_latency_ms(self) -> float:
        return sum(r.latency_ms for r in self.step_results.values())


class PipelineExecutor:
    """
    EXECUTOR - Ekzekuton pipelines
    """
    
    def __init__(self):
        self._engine_registry = None
        self._tool_registry = None
        self._executions: Dict[str, PipelineExecution] = {}
    
    def set_engine_registry(self, registry):
        """Vendos regjistrin e motorëve"""
        self._engine_registry = registry
    
    async def execute(
        self,
        pipeline: Pipeline,
        input_data: Any,
        context: Dict[str, Any] = None,
    ) -> PipelineExecution:
        """
        Ekzekuton pipeline
        """
        execution = PipelineExecution(
            pipeline_id=pipeline.id,
            input_data=input_data,
            status=PipelineStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        
        self._executions[execution.id] = execution
        context = context or {}
        
        # State dict për të ruajtur output-et e çdo hapi
        state = {
            "input": input_data,
            "context": context,
        }
        
        try:
            for step in pipeline.steps:
                execution.current_step = step.id
                
                # Check condition
                if step.condition:
                    if not self._evaluate_condition(step.condition, state):
                        logger.debug(f"Skipping step {step.id}: condition not met")
                        continue
                
                # Get input for this step
                step_input = self._get_step_input(step, state)
                
                # Execute step
                import time
                start = time.time()
                
                try:
                    result = await self._execute_step(step, step_input, state)
                    result.latency_ms = (time.time() - start) * 1000
                    
                    # Store result
                    state[step.id] = result.output
                    state[step.output_key] = result.output
                    execution.step_results[step.id] = result
                    
                except asyncio.TimeoutError:
                    result = StepResult(
                        step_id=step.id,
                        success=False,
                        error=f"Timeout after {step.timeout_seconds}s",
                    )
                    execution.step_results[step.id] = result
                    raise
                    
                except Exception as e:
                    result = StepResult(
                        step_id=step.id,
                        success=False,
                        error=str(e),
                    )
                    execution.step_results[step.id] = result
                    raise
            
            # Success
            execution.status = PipelineStatus.COMPLETED
            execution.output_data = state.get("output", state.get(pipeline.steps[-1].id))
            
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.error = str(e)
            logger.error(f"Pipeline execution failed: {e}")
        
        finally:
            execution.completed_at = datetime.utcnow()
            execution.current_step = None
        
        return execution
    
    async def _execute_step(
        self,
        step: PipelineStep,
        input_data: Any,
        state: Dict[str, Any],
    ) -> StepResult:
        """Ekzekuton një hap"""
        
        if step.type == StepType.LLM:
            return await self._execute_llm_step(step, input_data, state)
        elif step.type == StepType.EMBED:
            return await self._execute_embed_step(step, input_data, state)
        elif step.type == StepType.SEARCH:
            return await self._execute_search_step(step, input_data, state)
        elif step.type == StepType.TRANSFORM:
            return await self._execute_transform_step(step, input_data, state)
        elif step.type == StepType.TOOL:
            return await self._execute_tool_step(step, input_data, state)
        else:
            return StepResult(
                step_id=step.id,
                success=False,
                error=f"Unknown step type: {step.type}",
            )
    
    async def _execute_llm_step(
        self,
        step: PipelineStep,
        input_data: Any,
        state: Dict[str, Any],
    ) -> StepResult:
        """Ekzekuton LLM step"""
        from core.engines import EngineRequest, EngineMessage, EngineMode, get_registry
        
        # Build request
        messages = []
        if step.config.get("system_prompt"):
            messages.append(EngineMessage(role="system", content=step.config["system_prompt"]))
        
        # Format input
        if isinstance(input_data, str):
            messages.append(EngineMessage(role="user", content=input_data))
        elif isinstance(input_data, list):
            for msg in input_data:
                if isinstance(msg, dict):
                    messages.append(EngineMessage(role=msg.get("role", "user"), content=msg.get("content", "")))
        
        request = EngineRequest(
            engine_id=step.engine or "ollama:kloud-ocean:v2",
            mode=EngineMode.CHAT,
            messages=messages,
        )
        
        # Generate
        response = await get_registry().generate(request)
        
        return StepResult(
            step_id=step.id,
            success=response.success,
            output=response.text,
            error=response.error,
            metadata={
                "tokens": response.tokens.total_tokens,
                "engine": response.engine_id,
            },
        )
    
    async def _execute_embed_step(
        self,
        step: PipelineStep,
        input_data: Any,
        state: Dict[str, Any],
    ) -> StepResult:
        """Ekzekuton embedding step"""
        from core.engines import EngineRequest, EngineMode, get_registry
        
        request = EngineRequest(
            engine_id=step.engine or "ollama:nomic-embed-text",
            mode=EngineMode.EMBEDDING,
            input_text=str(input_data),
        )
        
        response = await get_registry().generate(request)
        
        return StepResult(
            step_id=step.id,
            success=response.success,
            output=response.embedding,
            error=response.error,
        )
    
    async def _execute_search_step(
        self,
        step: PipelineStep,
        input_data: Any,
        state: Dict[str, Any],
    ) -> StepResult:
        """Ekzekuton search step (placeholder)"""
        # TODO: Implement actual vector search
        return StepResult(
            step_id=step.id,
            success=True,
            output=[],  # Empty results for now
            metadata={"index": step.index},
        )
    
    async def _execute_transform_step(
        self,
        step: PipelineStep,
        input_data: Any,
        state: Dict[str, Any],
    ) -> StepResult:
        """Ekzekuton transform step"""
        transform_type = step.config.get("transform", "identity")
        
        if transform_type == "identity":
            output = input_data
        elif transform_type == "join":
            sep = step.config.get("separator", "\n")
            output = sep.join(str(x) for x in input_data) if isinstance(input_data, list) else str(input_data)
        elif transform_type == "extract":
            key = step.config.get("key")
            output = input_data.get(key) if isinstance(input_data, dict) else input_data
        else:
            output = input_data
        
        return StepResult(
            step_id=step.id,
            success=True,
            output=output,
        )
    
    async def _execute_tool_step(
        self,
        step: PipelineStep,
        input_data: Any,
        state: Dict[str, Any],
    ) -> StepResult:
        """Ekzekuton tool step (placeholder)"""
        # TODO: Implement tool execution
        return StepResult(
            step_id=step.id,
            success=True,
            output={"tool": step.tool, "result": "placeholder"},
        )
    
    def _get_step_input(self, step: PipelineStep, state: Dict[str, Any]) -> Any:
        """Merr input për hapin"""
        if step.input_from:
            return state.get(step.input_from, state.get("input"))
        return state.get("input")
    
    def _evaluate_condition(self, condition: str, state: Dict[str, Any]) -> bool:
        """Vlerëson kushtin (bazik)"""
        # Simple implementation
        try:
            return eval(condition, {"state": state, "prev": state})
        except:
            return True


# ═══════════════════════════════════════════════════════════════════════════════
# BUILT-IN PIPELINES
# ═══════════════════════════════════════════════════════════════════════════════

RAG_PIPELINE = Pipeline(
    id="rag_qa_v1",
    name="RAG Q&A Pipeline",
    description="Retrieval Augmented Generation for Q&A",
    steps=[
        PipelineStep(
            id="embed_query",
            name="Embed Query",
            type=StepType.EMBED,
            engine="ollama:nomic-embed-text",
        ),
        PipelineStep(
            id="search_kb",
            name="Search Knowledge Base",
            type=StepType.SEARCH,
            index="kb_ai_ml",
            input_from="embed_query",
        ),
        PipelineStep(
            id="format_context",
            name="Format Context",
            type=StepType.TRANSFORM,
            config={"transform": "join", "separator": "\n\n"},
            input_from="search_kb",
        ),
        PipelineStep(
            id="generate_answer",
            name="Generate Answer",
            type=StepType.LLM,
            engine="ollama:kloud-ocean:v2",
            config={
                "system_prompt": "Answer the question based on the provided context. Be concise and accurate."
            },
            input_from="format_context",
        ),
    ],
    tags=["rag", "qa", "knowledge-base"],
)

SIMPLE_CHAT_PIPELINE = Pipeline(
    id="simple_chat_v1",
    name="Simple Chat Pipeline",
    description="Basic chat with LLM",
    steps=[
        PipelineStep(
            id="generate",
            name="Generate Response",
            type=StepType.LLM,
            engine="ollama:kloud-ocean:v2",
        ),
    ],
    tags=["chat", "simple"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

class PipelineRegistry:
    """Regjistri i pipelines"""
    
    _instance: Optional["PipelineRegistry"] = None
    _pipelines: Dict[str, Pipeline]
    _executor: PipelineExecutor
    _initialized: bool
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._pipelines = {}
            cls._instance._executor = PipelineExecutor()
            cls._instance._initialized = False
        return cls._instance
    
    def initialize(self) -> None:
        if self._initialized:
            return
        
        # Register built-in pipelines
        self.register(RAG_PIPELINE)
        self.register(SIMPLE_CHAT_PIPELINE)
        
        self._initialized = True
        logger.info(f"✅ Pipeline Registry initialized with {len(self._pipelines)} pipelines")
    
    def register(self, pipeline: Pipeline) -> None:
        self._pipelines[pipeline.id] = pipeline
    
    def get(self, pipeline_id: str) -> Optional[Pipeline]:
        if not self._initialized:
            self.initialize()
        return self._pipelines.get(pipeline_id)
    
    def list_pipelines(self) -> List[Dict[str, Any]]:
        if not self._initialized:
            self.initialize()
        return [p.to_dict() for p in self._pipelines.values()]
    
    async def execute(
        self,
        pipeline_id: str,
        input_data: Any,
        context: Dict[str, Any] = None,
    ) -> PipelineExecution:
        pipeline = self.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        return await self._executor.execute(pipeline, input_data, context)


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL ACCESS
# ═══════════════════════════════════════════════════════════════════════════════

_registry = None


def get_pipeline_registry() -> PipelineRegistry:
    global _registry
    if _registry is None:
        _registry = PipelineRegistry()
        _registry.initialize()
    return _registry


def create_pipeline(data: Dict[str, Any]) -> Pipeline:
    return Pipeline.from_dict(data)


async def execute_pipeline(
    pipeline_id: str,
    input_data: Any,
    context: Dict[str, Any] = None,
) -> PipelineExecution:
    return await get_pipeline_registry().execute(pipeline_id, input_data, context)


def list_pipelines() -> List[Dict[str, Any]]:
    return get_pipeline_registry().list_pipelines()


__all__ = [
    "StepType",
    "PipelineStatus",
    "PipelineStep",
    "StepResult",
    "Pipeline",
    "PipelineExecution",
    "PipelineExecutor",
    "PipelineRegistry",
    "RAG_PIPELINE",
    "SIMPLE_CHAT_PIPELINE",
    "get_pipeline_registry",
    "create_pipeline",
    "execute_pipeline",
    "list_pipelines",
]

