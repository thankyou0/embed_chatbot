# # ============================================
# # Next.js Web Dashboard Dockerfile
# # Optimized for development with hot reload
# # ============================================

# # ---- Base Stage ----
# FROM node:18-alpine AS base

# # Install dependencies only when needed
# RUN apk add --no-cache libc6-compat wget

# # Install pnpm
# RUN corepack enable && corepack prepare pnpm@latest --activate

# WORKDIR /app

# # Set CI=true to avoid TTY issues
# ENV CI=true

# # ---- Dependencies Stage ----
# FROM base AS dependencies

# # Copy workspace configuration files
# COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml* ./

# # Copy all package.json files for workspace resolution
# COPY apps/web/package.json ./apps/web/package.json
# COPY apps/widget/package.json ./apps/widget/package.json
# COPY packages/shared/package.json ./packages/shared/package.json
# COPY packages/ui/package.json ./packages/ui/package.json

# # Install all dependencies
# RUN pnpm install --frozen-lockfile || pnpm install

# # ---- Development Stage ----
# FROM base AS development

# WORKDIR /app

# # Copy workspace files
# COPY --from=dependencies /app/package.json ./package.json
# COPY --from=dependencies /app/pnpm-lock.yaml* ./pnpm-lock.yaml*
# COPY --from=dependencies /app/pnpm-workspace.yaml* ./pnpm-workspace.yaml*

# # Copy all node_modules from dependencies stage
# COPY --from=dependencies /app/node_modules ./node_modules
# COPY --from=dependencies /app/apps/web/node_modules ./apps/web/node_modules
# COPY --from=dependencies /app/apps/widget/node_modules ./apps/widget/node_modules
# COPY --from=dependencies /app/packages/shared/node_modules ./packages/shared/node_modules
# COPY --from=dependencies /app/packages/ui/node_modules ./packages/ui/node_modules

# # Copy all package.json files
# COPY apps/web/package.json ./apps/web/package.json
# COPY apps/widget/package.json ./apps/widget/package.json
# COPY packages/shared/package.json ./packages/shared/package.json
# COPY packages/ui/package.json ./packages/ui/package.json

# # Copy application source (will be overridden by volume mount)
# COPY apps/web ./apps/web
# COPY packages ./packages

# # Expose port
# EXPOSE 3000

# # Set environment variables
# ENV NODE_ENV=development
# ENV NEXT_TELEMETRY_DISABLED=1
# ENV CI=true

# # Run development server with dependency check
# # If node_modules are missing (due to volume mount), install them first
# CMD sh -c "corepack enable && if [ ! -f '/app/.deps-installed' ]; then echo 'Installing dependencies (first run only)...' && pnpm install --frozen-lockfile --reporter=silent || pnpm install --reporter=silent && touch /app/.deps-installed; fi && pnpm --filter @chatbot/web dev"

# # ---- Builder Stage ----
# FROM base AS builder

# WORKDIR /app

# # Copy dependencies
# COPY --from=dependencies /app/node_modules ./node_modules
# COPY --from=dependencies /app/apps/web/node_modules ./apps/web/node_modules
# COPY --from=dependencies /app/package.json ./package.json
# COPY --from=dependencies /app/pnpm-workspace.yaml* ./pnpm-workspace.yaml

# # Copy source code
# COPY apps/web ./apps/web
# COPY packages ./packages

# # Set production environment
# ENV NODE_ENV=production
# ENV NEXT_TELEMETRY_DISABLED=1

# # Build the application
# WORKDIR /app/apps/web
# RUN pnpm run build

# # ---- Production Stage ----
# FROM base AS production

# WORKDIR /app

# # Create non-root user
# RUN addgroup --system --gid 1001 nodejs && \
#     adduser --system --uid 1001 nextjs

# # Copy built application
# COPY --from=builder /app/apps/web/public ./public
# COPY --from=builder /app/apps/web/.next/standalone ./
# COPY --from=builder /app/apps/web/.next/static ./.next/static

# # Set ownership
# RUN chown -R nextjs:nodejs /app

# # Switch to non-root user
# USER nextjs

# # Expose port
# EXPOSE 3000

# # Set production environment
# ENV NODE_ENV=production
# ENV NEXT_TELEMETRY_DISABLED=1
# ENV PORT=3000
# ENV HOSTNAME="0.0.0.0"

# # Health check
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# # Run production server
# CMD ["node", "server.js"]

FROM node:18-alpine AS development

WORKDIR /app

RUN apk add --no-cache libc6-compat
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy workspace config
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages ./packages
COPY apps/web ./apps/web

# Install deps ONCE
RUN pnpm install --no-frozen-lockfile

# Keep WORKDIR at root for workspace commands
WORKDIR /app

ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

EXPOSE 3000

# Check if node_modules exist in named volume, if not install them, then run dev server
CMD sh -c "if [ ! -d '/app/apps/web/node_modules/next' ]; then echo 'Installing dependencies in named volume (first run only)...' && cd /app && pnpm install --no-frozen-lockfile; fi && pnpm --filter @chatbot/web dev"
