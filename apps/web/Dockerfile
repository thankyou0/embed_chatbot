# ============================================
# Next.js Web Dashboard Dockerfile
# Supports both local development and production
# ============================================

# ---- Base Stage ----
FROM node:18-alpine AS base

# Install dependencies only when needed
RUN apk add --no-cache libc6-compat wget

WORKDIR /app

# ---- Dependencies Stage ----
FROM base AS dependencies

# Copy root package.json and pnpm-workspace.yaml for monorepo
COPY package.json pnpm-workspace.yaml* ./

# Copy package files (handle optional packages)
COPY apps/web/package.json ./apps/web/package.json

# Install pnpm and dependencies
RUN corepack enable && corepack prepare pnpm@latest --activate
# Install without frozen lockfile for DigitalOcean compatibility
RUN pnpm install || (echo "pnpm install failed, trying npm install" && npm install)

# ---- Development Stage ----
FROM base AS development

WORKDIR /app

# Copy dependencies
COPY --from=dependencies /app/node_modules ./node_modules

# Copy application code
COPY apps/web ./

# Expose port
EXPOSE 3000

# Set environment
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

# Run development server
CMD ["npx", "next", "dev"]

# ---- Builder Stage ----
FROM base AS builder

WORKDIR /app

# Copy all dependencies and workspace files
COPY --from=dependencies /app/node_modules ./node_modules
COPY --from=dependencies /app/apps/web/node_modules ./apps/web/node_modules
COPY --from=dependencies /app/package.json ./package.json
COPY --from=dependencies /app/pnpm-workspace.yaml* ./pnpm-workspace.yaml

# Copy application code
COPY apps/web ./apps/web

# Set production environment for build
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Build the application
WORKDIR /app/apps/web
RUN corepack enable && (pnpm run build || npm run build)
WORKDIR /app

# ---- Production Stage ----
FROM base AS production

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/apps/web/public ./public
COPY --from=builder /app/apps/web/.next/standalone ./
COPY --from=builder /app/apps/web/.next/static ./.next/static

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
