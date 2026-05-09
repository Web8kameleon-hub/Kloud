FROM node:20-alpine

LABEL maintainer="Kloud Team"
LABEL description="Kitchen Worker - Newman Test Runner for Kloud"

# Install dependencies for newman
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont

# Set environment for puppeteer (if needed for future reporters)
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install --omit=dev

# Copy worker code
COPY worker.js ./

# Create directories for jobs and reports
RUN mkdir -p /app/kitchen-jobs /app/kitchen-reports /app/postman-collections

# Environment variables
ENV KITCHEN_JOBS_DIR=/app/kitchen-jobs \
    KITCHEN_REPORTS_DIR=/app/kitchen-reports \
    COLLECTIONS_DIR=/app/postman-collections \
    POLL_INTERVAL_MS=3000 \
    MAX_CONCURRENT_JOBS=2 \
    HEALTH_PORT=3100 \
    NODE_ENV=production

# Expose health check port
EXPOSE 3100

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:3100/health || exit 1

# Run as non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S kitchen -u 1001 && \
    chown -R kitchen:nodejs /app
USER kitchen

CMD ["node", "worker.js"]

