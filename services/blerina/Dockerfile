# ═══════════════════════════════════════════════════════════════════════════════
# DOCKERFILE - BLERINA Pillar Content Engine
# ═══════════════════════════════════════════════════════════════════════════════
#
# Generates high-quality pillar articles (3000-5000 words)
# with quality gate and LLM integration
# ═══════════════════════════════════════════════════════════════════════════════

FROM python:3.11-slim

LABEL maintainer="Kloud Cloud Team"
LABEL description="BLERINA - Pillar Content Engine v2.0"
LABEL version="2.0.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY services/blerina/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy main service
COPY services/blerina/main.py ./blerina_service.py

# Create output directory
RUN mkdir -p /app/generated_pillars

EXPOSE 8035

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8035/health || exit 1

CMD ["python", "blerina_service.py"]

