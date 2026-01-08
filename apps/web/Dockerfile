# ============================================
# Next.js Web Dashboard Dockerfile
# Supports both local development and production
# ============================================

# ---- Base Stage ----
FROM node:18-alpine AS base

# Install dependencies only when needed
RUN apk add --no-cache libc6-compat

WORKDIR /app

# ---- Dependencies Stage ----
FROM base AS dependencies

# Copy package files
COPY apps/web/package.json ./
COPY pnpm-lock.yaml* ./

# Install pnpm and dependencies
RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm install --frozen-lockfile || pnpm install

# ---- Development Stage ----
FROM base AS development

WORKDIR /app

# Install pnpm for runtime dependency installation
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy package files for dependency installation
COPY apps/web/package.json ./
COPY pnpm-lock.yaml* ./

# Expose port
EXPOSE 3000

# Set environment
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1
# Enable polling for file watching on Windows/Docker
ENV WATCHPACK_POLLING=true
ENV CHOKIDAR_USEPOLLING=true

# Install dependencies and start dev server
# This ensures node_modules is available after volume mount
CMD ["sh", "-c", "pnpm install && pnpm dev"]

# ---- Builder Stage ----
FROM base AS builder

WORKDIR /app

# Copy dependencies
COPY --from=dependencies /app/node_modules ./node_modules

# Copy application code
COPY apps/web ./

# Set production environment for build
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Build the application
RUN corepack enable && npm run build

# ---- Production Stage ----
FROM base AS production

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Set ownership
RUN chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Run production server
CMD ["node", "server.js"]
