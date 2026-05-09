#!/usr/bin/env python3
"""
Personas Service Stub - All 4 AI personas in one container
KIDS_AI, STUDENT_AI, RESEARCH_AI, GENIUS_AI
"""
import sys
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9200

app = FastAPI(
    title="Kloud Personas Service",
    description="4 Cognitive AI Personas: KIDS_AI, STUDENT_AI, RESEARCH_AI, GENIUS_AI",
    version="1.0.0"
)

# Persona definitions
PERSONAS = {
    "KIDS_AI": {
        "name": "KIDS_AI",
        "target": "6-12 years old",
        "tone": "Friendly, fun, simple with emojis 🎨",
        "complexity": "very_simple",
        "example": "Imagine a rainbow 🌈 - that's how light works!",
        "model": "llama3.1:8b"  # phi3:mini removed - doesn't speak Albanian
    },
    "STUDENT_AI": {
        "name": "STUDENT_AI",
        "target": "13-22 years (high school to university)",
        "tone": "Educational, clear, with examples",
        "complexity": "moderate",
        "example": "Light is an electromagnetic wave with wavelength λ...",
        "model": "kloud-ocean:v2"
    },
    "RESEARCH_AI": {
        "name": "RESEARCH_AI",
        "target": "Researchers, PhDs, professionals",
        "tone": "Technical, precise, citations",
        "complexity": "advanced",
        "example": "According to Maxwell's equations (1865)...",
        "model": "llama3.1:8b"
    },
    "GENIUS_AI": {
        "name": "GENIUS_AI",
        "target": "NASA, CERN, cutting-edge research",
        "tone": "Mathematical, novel hypotheses, collaborative",
        "complexity": "genius",
        "example": "Given the Lagrangian L = ∫d⁴x √-g (R/16πG + ℒ_matter)...",
        "model": "gpt-oss:120b"
    }
}

class QueryRequest(BaseModel):
    query: str
    persona: str = "STUDENT_AI"
    context: Optional[str] = None

class PersonaResponse(BaseModel):
    persona: str
    response: str
    confidence: float
    model_used: str
    processing_time_ms: float

@app.get("/")
def root():
    return {
        "service": "Kloud Personas Service",
        "version": "1.0.0",
        "personas": list(PERSONAS.keys()),
        "status": "operational"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "personas",
        "port": PORT,
        "personas_active": 4,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/personas")
def list_personas():
    """List all available personas"""
    return {
        "personas": PERSONAS,
        "total": len(PERSONAS)
    }

@app.get("/persona/{name}")
def get_persona(name: str):
    """Get specific persona details"""
    if name not in PERSONAS:
        return {"error": f"Unknown persona: {name}", "available": list(PERSONAS.keys())}
    return PERSONAS[name]

@app.post("/query")
def query(request: QueryRequest):
    """Process query through specified persona"""
    if request.persona not in PERSONAS:
        request.persona = "STUDENT_AI"
    
    persona = PERSONAS[request.persona]
    
    # Simulate response based on persona
    if request.persona == "KIDS_AI":
        response = f"🌟 {persona['example']}"
    elif request.persona == "STUDENT_AI":
        response = f"📚 {persona['example']}"
    elif request.persona == "RESEARCH_AI":
        response = f"🔬 {persona['example']}"
    else:
        response = f"🧠 {persona['example']}"
    
    return PersonaResponse(
        persona=request.persona,
        response=response,
        confidence=0.92,
        model_used=persona["model"],
        processing_time_ms=150.0
    )

@app.get("/recommend")
def recommend_persona(complexity_score: float = 0.5):
    """Recommend persona based on complexity score"""
    if complexity_score < 0.20:
        return {"recommended": "KIDS_AI", "score": complexity_score}
    elif complexity_score < 0.45:
        return {"recommended": "STUDENT_AI", "score": complexity_score}
    elif complexity_score < 0.75:
        return {"recommended": "RESEARCH_AI", "score": complexity_score}
    else:
        return {"recommended": "GENIUS_AI", "score": complexity_score}

if __name__ == "__main__":
    print(f"👥 Starting Personas Service on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

