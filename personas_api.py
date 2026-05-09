"""Personas API - Kloud Cloud."""
import os

import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Kloud Personas Engine", version="1.0.0")

PERSONAS = [
    "Analyst", "Developer", "Manager", "Researcher", "Strategist",
    "Educator", "Innovator", "Consultant", "Architect", "Specialist",
    "Director", "Coordinator", "Advisor", "Expert", "Leader"
]


@app.get("/health")
def health():
    return {"status": "healthy", "service": "personas"}


@app.get("/")
def root():
    return {"message": "Personas Engine", "personas": len(PERSONAS)}


@app.get("/personas")
def list_personas():
    return {"personas": PERSONAS, "total": len(PERSONAS)}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8040))
    uvicorn.run(app, host="0.0.0.0", port=port)

