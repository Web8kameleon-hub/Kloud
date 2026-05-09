# ============================================================================
# KLOUD BLOG AUTO-PUBLISHER
# Dockerfile for automatic GitHub Pages publishing
# Port: 8041
# ============================================================================

FROM python:3.11-slim

LABEL maintainer="Ledjan Ahmati <hello@ledjanahmatibusiness.com>"
LABEL description="Auto-publishes articles from Blerina & Dr. Albana to GitHub Pages"
LABEL service="blog_publisher"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create directories for pillars
RUN mkdir -p /app/blerina_pillars /app/medical_pillars

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PUBLISHER_PORT=8041
ENV POSTS_PER_DAY=4

# Expose port
EXPOSE 8041

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8041/health || exit 1

# Run the application
CMD ["python", "main.py"]

