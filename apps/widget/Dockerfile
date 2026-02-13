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
