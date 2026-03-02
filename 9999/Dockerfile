FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY output ./output

ENV PYTHONUNBUFFERED=1
ENV PORT=9999
EXPOSE 9999

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:9999/health || exit 1

CMD ["python", "app.py"]
