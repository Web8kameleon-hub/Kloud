#!/usr/bin/env python3
"""
Adaptive Persona Router Stub - Docker container version
Routes queries to appropriate persona based on cognitive level
"""
import sys
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

app = FastAPI(
    title="Adaptive Persona Router",
    description="Routes queries to KIDS_AI, STUDENT_AI, RESEARCH_AI, or GENIUS_AI personas",
    version="1.0.0"
)

class CognitiveLevel(str, Enum):
    KIDS = "KIDS"
    STUDENT = "STUDENT"
    RESEARCH = "RESEARCH"
    GENIUS = "GENIUS"

class Strategy(str, Enum):
    FAST = "fast"
    BALANCED = "balanced"
    AUTO = "auto"
    DEEP = "deep"

class RouteRequest(BaseModel):
    query: str
    complexity_score: Optional[float] = None
    level: Optional[CognitiveLevel] = None

class PersonaInfo(BaseModel):
    name: str
    level: CognitiveLevel
    description: str
    tone: str
    strategy: Strategy

class RoutingDecision(BaseModel):
    persona: PersonaInfo
    pipeline: str
    model_preference: str
    strategy: Strategy
    confidence: float
    timestamp: str

# Persona configurations
PERSONAS = {
    CognitiveLevel.KIDS: PersonaInfo(
        name="KIDS_AI",
        level=CognitiveLevel.KIDS,
        description="Friendly AI for young learners",
        tone="Simple, fun, encouraging with emojis",
        strategy=Strategy.FAST
    ),
    CognitiveLevel.STUDENT: PersonaInfo(
        name="STUDENT_AI",
        level=CognitiveLevel.STUDENT,
        description="Educational AI for students",
        tone="Clear, structured, with examples",
        strategy=Strategy.BALANCED
    ),
    CognitiveLevel.RESEARCH: PersonaInfo(
        name="RESEARCH_AI",
        level=CognitiveLevel.RESEARCH,
        description="Professional AI for researchers",
        tone="Technical, precise, with references",
        strategy=Strategy.AUTO
    ),
    CognitiveLevel.GENIUS: PersonaInfo(
        name="GENIUS_AI",
        level=CognitiveLevel.GENIUS,
        description="Advanced AI for deep analysis",
        tone="Mathematical, novel hypotheses, collaborative",
        strategy=Strategy.DEEP
    )
}

# Model preferences - UPDATED: phi3:mini removed (doesn't speak Albanian)
MODEL_PREFERENCES = {
    CognitiveLevel.KIDS: "llama3.1:8b",
    CognitiveLevel.STUDENT: "kloud-ocean:v2",
    CognitiveLevel.RESEARCH: "llama3.1:8b",
    CognitiveLevel.GENIUS: "gpt-oss:120b"  # via microservice 8031
}

# Pipeline mappings
PIPELINES = {
    CognitiveLevel.KIDS: "simple_response_v1",
    CognitiveLevel.STUDENT: "educational_pipeline_v1",
    CognitiveLevel.RESEARCH: "research_pipeline_v1",
    CognitiveLevel.GENIUS: "deep_analysis_pipeline_v1"
}

def determine_level(complexity_score: float) -> CognitiveLevel:
    """Determine cognitive level from complexity score"""
    if complexity_score < 0.20:
        return CognitiveLevel.KIDS
    elif complexity_score < 0.45:
        return CognitiveLevel.STUDENT
    elif complexity_score < 0.75:
        return CognitiveLevel.RESEARCH
    else:
        return CognitiveLevel.GENIUS

def route_query(request: RouteRequest) -> RoutingDecision:
    """Route a query to appropriate persona"""
    # Determine level
    if request.level:
        level = request.level
    elif request.complexity_score is not None:
        level = determine_level(request.complexity_score)
    else:
        # Default analysis based on query length
        word_count = len(request.query.split())
        complexity = min(1.0, word_count * 0.02)
        level = determine_level(complexity)
    
    persona = PERSONAS[level]
    
    return RoutingDecision(
        persona=persona,
        pipeline=PIPELINES[level],
        model_preference=MODEL_PREFERENCES[level],
        strategy=persona.strategy,
        confidence=0.90,
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/")
def root():
    return {
        "service": "Adaptive Persona Router",
        "version": "1.0.0",
        "personas": [p.name for p in PERSONAS.values()],
        "status": "operational"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "adaptive-router",
        "personas_available": 4,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/route", response_model=RoutingDecision)
def route(request: RouteRequest):
    """Route a query to the appropriate persona"""
    return route_query(request)

@app.get("/personas")
def get_personas():
    """Get all available personas"""
    return {
        "personas": [
            {
                "name": p.name,
                "level": p.level.value,
                "description": p.description,
                "tone": p.tone,
                "strategy": p.strategy.value,
                "model": MODEL_PREFERENCES[p.level],
                "pipeline": PIPELINES[p.level]
            }
            for p in PERSONAS.values()
        ]
    }

@app.get("/strategy/{level}")
def get_strategy(level: CognitiveLevel):
    """Get strategy for a specific cognitive level"""
    persona = PERSONAS[level]
    return {
        "level": level.value,
        "persona": persona.name,
        "strategy": persona.strategy.value,
        "model": MODEL_PREFERENCES[level],
        "pipeline": PIPELINES[level]
    }

if __name__ == "__main__":
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8011
    print(f"🎯 Starting Adaptive Persona Router on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

