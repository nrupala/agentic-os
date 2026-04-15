# Production Deployment Guide

> Paradise Stack v1.1.0 - Production Deployment

## Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+
- 4GB RAM minimum
- 20GB disk space

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/paradise-stack.git
cd paradise-stack

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Start the stack
docker-compose up -d

# Verify deployment
curl http://localhost:3001/health
```

## Configuration

### Required Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `3001` |
| `NODE_ENV` | Environment | `production` |
| `HOST_PROJECT_ROOT` | Project path | `/app` |

### Optional AI Settings

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for Aider |
| `OLLAMA_HOST` | Local Ollama endpoint |
| `OLLAMA_MODEL` | Ollama model name |

### Security Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `EXECUTION_TIMEOUT` | Max command time (ms) | `30000` |
| `MAX_COMMAND_LENGTH` | Max command size (chars) | `5000` |
| `ALLOWED_ORIGINS` | CORS origins | `*` |

## Production Checklist

- [ ] Set `NODE_ENV=production`
- [ ] Configure `ALLOWED_ORIGINS` with your domain
- [ ] Set secure `OPENAI_API_KEY`
- [ ] Configure `EXECUTION_TIMEOUT` for your workload
- [ ] Enable TLS/SSL via reverse proxy
- [ ] Set up monitoring with `/health` endpoint

## Reverse Proxy (Nginx)

```nginx
server {
    listen 443 ssl;
    server_name paradise.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Health Monitoring

```bash
# Basic health check
curl http://localhost:3001/health

# Expected response
{
  "status": "healthy",
  "uptime": 3600,
  "memory": { ... },
  "timestamp": "2026-04-14T..."
}

# Status endpoint
curl http://localhost:3001/status

# Version info
curl http://localhost:3001/version
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs paradise

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use

```bash
# Change port in .env
PORT=3002

# Or edit docker-compose.yml
ports:
  - "3002:3001"
```

### Commands timeout

```bash
# Increase timeout in .env
EXECUTION_TIMEOUT=60000
```

## Backup

```bash
# Backup logs and outputs
tar -czf backup.tar.gz logs/ outputs/ projects/

# Backup with timestamp
tar -czf "paradise-backup-$(date +%Y%m%d).tar.gz" logs/ outputs/ projects/
```

## Updating

```bash
# Pull latest
git pull

# Rebuild
docker-compose build
docker-compose up -d

# Run tests
docker exec paradise-bridge python3 /app/tests/test_suite.py
```

## License

MIT
