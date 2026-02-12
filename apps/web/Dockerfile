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
# Enable polling for file watching on Windows/Docker
ENV WATCHPACK_POLLING=true
ENV CHOKIDAR_USEPOLLING=true

EXPOSE 3000

# Check if node_modules exist in named volume, if not install them, then run dev server
CMD sh -c "if [ ! -d '/app/apps/web/node_modules/next' ]; then echo 'Installing dependencies in named volume (first run only)...' && cd /app && pnpm install --no-frozen-lockfile; fi && pnpm --filter @chatbot/web dev"
