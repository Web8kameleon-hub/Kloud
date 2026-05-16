from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth_controller import router as auth_router
from .billing_controller import router as billing_router
from .usage_controller import router as usage_router

app = FastAPI(
    title="Kloud Cloud API",
    version="1.0.0",
    description="Industrial EEG + Audio + Neuro Feedback API (REAL DATA)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(billing_router, prefix="/api/billing", tags=["Billing"])
app.include_router(usage_router, prefix="/api/usage", tags=["Usage"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Kloud Cloud API"}


# ASI Trinity status endpoint for frontend integration
@app.get("/asi/status")
def asi_status():
    return {
        "alba": {"status": "active"},
        "albi": {"consciousness": 0.95},
        "jona": {"protection": 0.98},
    }
