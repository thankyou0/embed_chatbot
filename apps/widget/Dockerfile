# ---- Base Stage ----
FROM node:18-alpine AS base
WORKDIR /app
RUN apk add --no-cache libc6-compat
RUN corepack enable && corepack prepare pnpm@latest --activate

# ---- Dependencies Stage ----
FROM base AS deps
# Copy workspace config
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages ./packages
COPY apps/widget/package.json ./apps/widget/package.json

# Install dependencies
RUN pnpm install --frozen-lockfile

# ---- Builder Stage ----
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/packages ./packages
COPY . .

# Build args
ARG VITE_PUBLIC_API_URL
ENV VITE_PUBLIC_API_URL=${VITE_PUBLIC_API_URL}

# Build
RUN pnpm --filter @chatbot/widget build

# ---- Production Stage ----
FROM nginx:alpine AS production

# Copy built assets from builder stage
COPY --from=builder /app/apps/widget/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]

# ---- Development Stage ----
FROM base AS development
WORKDIR /app
RUN apk add --no-cache libc6-compat
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages ./packages
COPY apps/widget ./apps/widget
RUN pnpm install --no-frozen-lockfile
WORKDIR /app/apps/widget
ENV NODE_ENV=development
ENV CHOKIDAR_USEPOLLING=true
ENV VITE_HMR_POLLING=true
EXPOSE 3001
CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "3001"]
