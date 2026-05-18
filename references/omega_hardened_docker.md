# STAGE 1: The Builder (High-Risk/Heavyweight)
FROM python:3.12-slim AS builder

# Set build-time security settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install OS-level build dependencies for Numpy/Flask
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install pinned dependencies into a local directory
# This separates build-tools from the runtime environment
RUN pip install --no-cache-dir --prefix=/install \
    numpy==1.26.4 \
    flask==3.0.2 \
    gunicorn==21.2.0

# ---------------------------------------------------------

# STAGE 2: The Hardened Runtime (Omega-Code Production)
FROM python:3.12-slim

# Labels for metadata and traceability
LABEL maintainer="Omega-Code-Agent"
LABEL security.hardened="true"

# Production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/usr/local/lib/python3.12/site-packages

WORKDIR /app

# 1. Create a non-privileged user for execution
RUN addgroup --system omega && adduser --system --group omega

# 2. Copy ONLY the pre-compiled libraries from the builder
COPY --from=builder /install /usr/local

# 3. Copy application code with root ownership (read-only for user)
# This prevents the agent from modifying its own core logic at runtime
COPY --chown=root:root . .

# 4. Final Security Lockdown:
# Ensure temp directories are world-writable but scoped
RUN chmod 755 /app && \
    mkdir -p /tmp/omega && \
    chown omega:omega /tmp/omega

# Switch to non-root user for all subsequent operations
USER omega

# Informational port exposure for Flask
EXPOSE 5000

# Execute using Gunicorn for production-grade stability
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "2", "--timeout", "30"]

docker run -d \
  --name omega-proc \
  --read-only \
  --tmpfs /tmp/omega:rw,size=64m \
  --network none \
  --memory 512m \
  omega-hardened:latest
#!/bin/bash
# OMEGA-CODE Health Check: Verifies service responsiveness and memory pressure.

# Check if Flask is returning a 200 OK
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
MEM_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')

if [ "$STATUS_CODE" -eq 200 ] && [ $(echo "$MEM_USAGE < 90" | bc) -ne 0 ]; then
    echo "[OK] Service responsive. Memory: $MEM_USAGE%"
    exit 0
else
    echo "[CRITICAL] Status: $STATUS_CODE | Mem: $MEM_USAGE%"
    exit 1
fi
