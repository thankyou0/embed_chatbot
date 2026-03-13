FROM node:18-alpine AS development

WORKDIR /app

RUN apk add --no-cache libc6-compat
# Use npm to install pnpm globally — much faster than corepack in Docker
# (corepack verify/download can take 20+ min on slow network inside Alpine).
RUN npm install -g pnpm@10.28.0 --no-fund --no-audit

# Copy workspace config
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages ./packages
COPY apps/web ./apps/web

# Install deps with BuildKit cache mount so the pnpm store is reused across
# builds — this turns a cold 8-min install into ~30s on subsequent builds.
RUN --mount=type=cache,id=pnpm-store,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# Keep WORKDIR at root for workspace commands
WORKDIR /app

ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1
# Node heap sized for 8 GB systems (WSL2 gets ~4 GB, shared across containers)
ENV NODE_OPTIONS="--require /app/apps/web/suppress-watchpack.js --max-old-space-size=2560"
# Enable polling for file watching in Docker (required for Windows volume mounts)
ENV WATCHPACK_POLLING=true
ENV CHOKIDAR_USEPOLLING=true
ENV NEXT_TELEMETRY_DISABLED=1

EXPOSE 3000

# At runtime: if node_modules are missing (first-run on a fresh named volume)
# do a quick install, then start the dev server. --no-frozen-lockfile is
# intentional here because this is an emergency fallback, not a build step.
CMD sh -c "if [ ! -d '/app/apps/web/node_modules/next' ]; then echo 'node_modules not found — installing (first-run only)...' && cd /app && pnpm install --no-frozen-lockfile; fi && pnpm --filter @chatbot/web dev"

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
