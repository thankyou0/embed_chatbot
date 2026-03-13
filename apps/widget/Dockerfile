FROM node:18-alpine AS development

WORKDIR /app

RUN apk add --no-cache libc6-compat
# Use npm to install pnpm globally — much faster than corepack in Docker.
RUN npm install -g pnpm@10.28.0 --no-fund --no-audit

# Copy workspace config
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages ./packages
COPY apps/widget ./apps/widget

# Reuse pnpm store cache across builds (same cache id as web — shared store).
RUN --mount=type=cache,id=pnpm-store,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

WORKDIR /app/apps/widget

ENV NODE_ENV=development
# Enable polling for file watching on Windows/Docker
ENV CHOKIDAR_USEPOLLING=true
ENV VITE_HMR_POLLING=true

EXPOSE 3001

CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "3001"]

# ============================================
# Production Stage — build + serve via nginx
# ============================================
FROM development AS build

ENV NODE_ENV=production

RUN pnpm build

FROM nginx:alpine AS production

# Copy nginx config
COPY apps/widget/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from build stage
COPY --from=build /app/apps/widget/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
