# # ============================================
# # Preact Widget Dockerfile
# # Optimized for development with hot reload
# # ============================================

# # ---- Base Stage ----
# FROM node:18-alpine AS base

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
# COPY apps/widget ./apps/widget
# COPY packages ./packages

# # Expose port
# EXPOSE 3001

# # Set environment variables
# ENV NODE_ENV=development
# ENV CI=true

# # Run development server with dependency check
# # If node_modules are missing (due to volume mount), install them first
# CMD sh -c "corepack enable && if [ ! -f '/app/.deps-installed' ]; then echo 'Installing dependencies (first run only)...' && pnpm install --frozen-lockfile --reporter=silent || pnpm install --reporter=silent && touch /app/.deps-installed; fi && pnpm --filter @chatbot/widget dev --host 0.0.0.0 --port 3001"

# # ---- Builder Stage ----
# FROM base AS builder

# WORKDIR /app

# # Copy dependencies
# COPY --from=dependencies /app/node_modules ./node_modules
# COPY --from=dependencies /app/apps/widget/node_modules ./apps/widget/node_modules
# COPY --from=dependencies /app/package.json ./package.json
# COPY --from=dependencies /app/pnpm-workspace.yaml* ./pnpm-workspace.yaml

# # Copy source code
# COPY apps/widget ./apps/widget
# COPY packages ./packages

# # Build the widget
# WORKDIR /app/apps/widget
# RUN pnpm run build

# # ---- Production Stage ----
# FROM nginx:alpine AS production

# # Copy built files to nginx
# COPY --from=builder /app/apps/widget/dist /usr/share/nginx/html

# # Copy nginx configuration
# COPY apps/widget/nginx.conf /etc/nginx/conf.d/default.conf

# # Expose port
# EXPOSE 80

# # Health check
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD wget --no-verbose --tries=1 --spider http://localhost:80 || exit 1

# # Run nginx
# CMD ["nginx", "-g", "daemon off;"]

FROM node:18-alpine AS development

WORKDIR /app

RUN apk add --no-cache libc6-compat
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy workspace config
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages ./packages
COPY apps/widget ./apps/widget

# Install deps ONCE
RUN pnpm install --no-frozen-lockfile

WORKDIR /app/apps/widget

ENV NODE_ENV=development

EXPOSE 3001

CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "3001"]
