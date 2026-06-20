# ── Stage 1: Build ────────────────────────────────────────────────────────────
# Use Debian-based Node for build stage because npm in node:20-alpine
# intermittently fails with "Exit handler never called!" in this environment.
FROM node:20-bookworm-slim AS build

WORKDIR /app

# VITE_API_URL is baked into the JS bundle at build time.
# Override at build time:  docker build --build-arg VITE_API_URL=/api .
# Default /api works with ingress path routing to service-a.
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

COPY package*.json ./
# --include=dev ensures devDependencies (vite, eslint, etc.) are always installed
RUN npm ci --include=dev

COPY . .
RUN npm run build

# ── Stage 2: Serve with Nginx ─────────────────────────────────────────────────
FROM nginx:stable-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
