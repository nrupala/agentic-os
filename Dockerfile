# syntax=docker/dockerfile:1.4
# =============================================================================
# Paradise Stack - AI Agent Orchestration Platform
# Version: 1.1.0-dev
# Based on: MapCoder (ACL 2024), HyperAgent (arXiv 2024), SkillOrchestra (arXiv 2026)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Dependencies (Python + Node packages)
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS deps

WORKDIR /deps

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    nodejs \
    npm \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages to /install
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Install cline globally for CLI access
RUN npm install -g cline && npm cache clean --force

# -----------------------------------------------------------------------------
# Stage 2: Runtime (Final container)
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

LABEL maintainer="Paradise Stack"
LABEL description="AI Agent Orchestration Platform"
LABEL version="1.1.0-dev"

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
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from deps
COPY --from=deps /install /usr/local

# Copy cline executable and global npm modules
COPY --from=deps /usr/local/bin/cline /usr/local/bin/cline
COPY --from=deps /usr/local/lib/node_modules /usr/local/lib/node_modules

# Copy dashboard dependencies
COPY dashboard/package*.json ./
RUN npm ci --production && npm cache clean --force

# Copy application code
COPY . .

# Create user and set permissions
RUN adduser --disabled-password --gecos "" paradise || true && \
    chown -R paradise:paradise /app

USER paradise

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3001/status || exit 1

ENTRYPOINT ["bash", "-c"]
CMD ["source /etc/profile.d/*.sh 2>/dev/null || true; node dashboard/server.js"]
