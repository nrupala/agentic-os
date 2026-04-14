# Changelog

All notable changes to Paradise Stack will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1.0] - Development

### Added
- Version endpoint (`/version`) in dashboard server
- Dependency version tracking in status
- CHANGELOG.md for version history
- Semantic versioning support

### Changed
- Dockerfile multi-stage build optimization
- Global npm modules handling for cline

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
