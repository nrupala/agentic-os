# Changelog

All notable changes to Paradise Stack will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1.0] - Production Ready

### Added
- Health check endpoint (`/health`) for production monitoring
- Security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
- Request/response logging middleware
- Command timeout handling with configurable `EXECUTION_TIMEOUT`
- Command length validation with configurable `MAX_COMMAND_LENGTH`
- Outputs directory with directory structure
- `.env.example` with all production variables
- `docs/DEPLOYMENT.md` production deployment guide
- Test suite additions: Container process, Outputs directory

### Changed
- Enhanced error handling in server.js
- CORS configuration via environment variables
- Test suite: Docker container test to Container process check
- Server now uses `HOST_PROJECT_ROOT` from environment
- Dockerfile multi-stage build optimization
- Global npm modules handling for cline
- Added `ripgrep` dependency for cline
- Updated requirements.txt to use `aider-chat` instead of `aider`

### Fixed
- Aider command path: `/home/paradise/.local/bin/aider`
- Crawl4AI command via Python module
- Cline missing dependency issue
- Test suite: Docker container test fails inside container (now uses process check)

## [1.0.0] - Initial Release

### Added
- Core dashboard with Express server on port 3001
- Workflow orchestration engine
- Agent pipeline: Cline (Architect) → Crawl4AI (Knowledge) → Aider (Builder) → Ruff (Guardian)
- Multi-stage Docker build
- Research-based architecture (MapCoder, HyperAgent, SkillOrchestra)
- Healthcheck monitoring
- Git and SSH volume mounts for GitHub operations

### Features
- One-command startup via docker-compose
- Terminal output streaming
- Command logging to `/logs/`
- Project workspace in `/projects/`
