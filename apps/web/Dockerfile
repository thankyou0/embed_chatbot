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
# Enable polling for file watching in Docker (required for Windows volume mounts)
ENV WATCHPACK_POLLING=true
ENV CHOKIDAR_USEPOLLING=true

EXPOSE 3000

# Check if node_modules exist in named volume, if not install them, then run dev server
CMD sh -c "if [ ! -d '/app/apps/web/node_modules/next' ]; then echo 'Installing dependencies in named volume (first run only)...' && cd /app && pnpm install --no-frozen-lockfile; fi && pnpm --filter @chatbot/web dev"

# ============================================
# Production Stage — Next.js standalone build
# ============================================
FROM development AS build

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /app/apps/web
RUN pnpm build

FROM node:18-alpine AS production

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Copy standalone output (includes server + minimal deps)
COPY --from=build /app/apps/web/.next/standalone ./
COPY --from=build /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=build /app/apps/web/public ./apps/web/public

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "apps/web/server.js"]
