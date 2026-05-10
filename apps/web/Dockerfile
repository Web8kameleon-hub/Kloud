FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install --legacy-peer-deps
RUN npm install --legacy-peer-deps tailwindcss@4 @tailwindcss/postcss @ducanh2912/next-pwa --save-dev

COPY . .

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# Production image
FROM node:20-alpine AS runner

# Install curl for healthcheck
RUN apk add --no-cache curl

WORKDIR /app

RUN addgroup -g 1001 -S nodejs
RUN adduser -S kloud -u 1001

COPY --from=builder --chown=kloud:nodejs /app/.next ./.next
COPY --from=builder --chown=kloud:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=kloud:nodejs /app/package*.json ./
COPY --from=builder --chown=kloud:nodejs /app/public ./public

USER kloud

EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:3000 || exit 1

CMD ["npm", "start"]

