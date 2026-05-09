FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uvicorn fastapi redis httpx

COPY context_builder.py .
COPY fallbacks.py .
COPY knowledge_router.py .
COPY module_registry.py .
COPY reasoning_engine.py .
COPY __init__.py .

# Create main API entry point
RUN echo 'from fastapi import FastAPI\n\
from knowledge_router import route_query\n\
from reasoning_engine import reason\n\
from module_registry import list_modules\n\
\n\
app = FastAPI(title="Kloud AGI", version="1.0.0")\n\
\n\
@app.get("/health")\n\
def health(): return {"status": "healthy", "service": "agi"}\n\
\n\
@app.get("/modules")\n\
def modules(): return list_modules()\n\
\n\
@app.post("/reason")\n\
async def api_reason(query: str): return await reason(query)\n\
' > main.py

EXPOSE 8014

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8014"]

