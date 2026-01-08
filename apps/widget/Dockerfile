# ============================================
# Preact Widget Dockerfile
# Supports both local development and production
# ============================================

# ---- Base Stage ----
FROM node:18-alpine AS base

RUN apk add --no-cache libc6-compat wget

WORKDIR /app

# ---- Dependencies Stage ----
FROM base AS dependencies

# Copy root package.json and pnpm-workspace.yaml for monorepo
COPY package.json pnpm-workspace.yaml* ./

# Copy package files
COPY apps/widget/package.json ./apps/widget/package.json

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
COPY apps/widget ./

# Expose port
EXPOSE 3001

# Set environment
ENV NODE_ENV=development

# Run development server
CMD ["npx", "vite", "--host", "0.0.0.0", "--port", "3001"]

# ---- Builder Stage ----
FROM base AS builder

WORKDIR /app

# Copy all dependencies and workspace files
COPY --from=dependencies /app/node_modules ./node_modules
COPY --from=dependencies /app/apps/widget/node_modules ./apps/widget/node_modules
COPY --from=dependencies /app/package.json ./package.json
COPY --from=dependencies /app/pnpm-workspace.yaml* ./pnpm-workspace.yaml

# Copy application code
COPY apps/widget ./apps/widget

# Build the widget
WORKDIR /app/apps/widget
RUN corepack enable && (pnpm run build || npm run build)
WORKDIR /app

# ---- Production Stage ----
FROM nginx:alpine AS production

# Copy built files to nginx
COPY --from=builder /app/apps/widget/dist /usr/share/nginx/html

# Copy nginx configuration
COPY apps/widget/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80 || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
