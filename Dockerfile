# syntax=docker/dockerfile:1.4
# =============================================================================
# Paradise Stack - AI Agent Orchestration Platform
# Based on: MapCoder (ACL 2024), HyperAgent (arXiv 2024), SkillOrchestra (arXiv 2026)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Dependencies
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS deps

WORKDIR /deps

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Builder
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=deps /install /usr/local

COPY dashboard/package*.json ./
RUN npm ci --production && npm cache clean --force

# -----------------------------------------------------------------------------
# Stage 3: Runtime
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

LABEL maintainer="Paradise Stack"
LABEL description="AI Agent Orchestration Platform"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NODE_ENV=production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    curl \
    git \
    bash \
    && npm config set unsafe-perm true \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/nodejs /usr/bin/node

COPY --from=deps /install /usr/local
COPY --from=builder /build/node_modules ./node_modules
COPY . .

RUN adduser --disabled-password --gecos "" paradise && \
    addgroup paradise paradise && \
    chown -R paradise:paradise /app

USER paradise

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3001/status || exit 1

ENTRYPOINT ["bash", "-c"]
CMD ["source /etc/profile.d/*.sh 2>/dev/null || true; node dashboard/server.js"]
