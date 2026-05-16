from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import bioscience, clinical, concept, graph, search, telemetry

app = FastAPI(title="kloud Knowledge Fabric API")

# CORS middleware for browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://kloud.com",
        "https://www.kloud.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(telemetry.router)
app.include_router(clinical.router)
app.include_router(bioscience.router)
app.include_router(concept.router)
app.include_router(graph.router)
