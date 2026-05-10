FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uvicorn fastapi httpx redis

COPY api.py .
COPY discovery.py .
COPY explore.py .
COPY search.py .
COPY __init__.py .

ENV PORT=8019
EXPOSE 8019

CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8019}"]
