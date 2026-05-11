FROM oven/bun:1.1-alpine AS base
WORKDIR /app

# ── dev ──────────────────────────────────────────────────────────────────────
FROM base AS dev
RUN apk add --no-cache curl
COPY package.json ./
RUN bun install
EXPOSE 5173
CMD ["bun", "run", "dev"]

# ── builder ───────────────────────────────────────────────────────────────────
FROM base AS builder
COPY package.json bun.lockb* ./
RUN bun install --frozen-lockfile || bun install
COPY . .
RUN bun run build

# ── production ────────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
