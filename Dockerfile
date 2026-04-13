FROM python:3.11-slim

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    git \
    bash \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g cline aider

RUN pip install --no-cache-dir \
    crawl4ai \
    ruff \
    phoenix

COPY --chown=root:root . .

RUN ln -s /usr/bin/nodejs /usr/bin/node 2>/dev/null || true

EXPOSE 3001

ENTRYPOINT ["bash", "-c"]
CMD ["source /etc/profile.d/*.sh 2>/dev/null || true; node dashboard/server.js"]
