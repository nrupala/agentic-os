# 🏝️ Paradise Stack

> A fully independent, FOSS AI Software Engineering OS powered by multi-agent orchestration.

## ⚡ Quick Start (One Command)

```bash
# Linux/Mac
./test.sh

# Windows
test.bat

# Or manually:
docker-compose up -d
```

Then open **http://localhost:3001** in your browser.

That's it. No installation, no dependencies, nothing else needed.

---

## 🎯 What It Does

Enter a feature request (e.g., "generate a simple to-do list") and Paradise Stack:

1. **Architect** (Cline) - Creates implementation plan
2. **Knowledge** (Crawl4AI) - Retrieves relevant documentation
3. **Builder** (Aider) - Implements the code
4. **Guardian** (Ruff/ESLint) - Quality assurance

---

## 🔧 The Stack

| Agent | Tool | Purpose |
|-------|------|---------|
| Architect | [Cline CLI](https://github.com) | High-level planning |
| Builder | [Aider](https://aider.chat) | Git-native code implementation |
| Knowledge | [Crawl4AI](https://crawl4ai.com) | Documentation RAG |
| Guardian | [Ruff](https://ruff.rs) + [ESLint](https://eslint.org) | FOSS Quality Assurance |
| Senses | [Langfuse](https://langfuse.com) + [Phoenix](https://arize.com) | Observability |

---

## 🖥️ Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Paradise Dashboard** | http://localhost:3001 | Command Center |
| **Langfuse** | http://localhost:3000 | Tracing & Analytics |
| **Phoenix** | http://localhost:6006 | Agent Visualization |

---

## 📁 Project Structure

```
.
├── docker-compose.yml    # One-command startup
├── Dockerfile           # Container definition
├── dashboard/           # Web UI
│   ├── index.html       # Dashboard
│   ├── server.js        # Bridge server
│   └── workflow.js      # Agent orchestration
├── docs/
│   └── RESEARCH.md      # Research references
├── logs/                # Command logs
├── outputs/             # Generated artifacts
└── projects/            # Project files
```

---

## 🛠️ Development

### Local Setup (without Docker)

```powershell
# Install dependencies
pip install -r requirements.txt
cd dashboard && npm install && cd ..

# Start dashboard
node dashboard/server.js

# Start observability (in another terminal)
docker-compose up -d langfuse phoenix db
```

### Build Image

```bash
docker-compose build
```

### View Logs

```bash
docker-compose logs -f paradise
```

---

## 🔬 Research Basis

Paradise Stack is based on peer-reviewed research:

- **MapCoder** (ACL 2024) - Four-agent pipeline pattern
- **HyperAgent** (arXiv 2024) - Specialized agent roles
- **SkillOrchestra** (arXiv 2026) - Skill-aware orchestration
- **12-Factor Docker** - Container best practices

See [docs/RESEARCH.md](docs/RESEARCH.md) for full references.

---

## 📋 Version

Current: **1.1.0-dev**

### Versioning System

Paradise Stack uses [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH[-PRERELEASE]
1     .1     .0        -dev
```

| Component | Description |
|-----------|-------------|
| MAJOR | Breaking changes to core architecture |
| MINOR | New features, backwards-compatible |
| PATCH | Bug fixes, small improvements |
| PRERELEASE | Development markers (dev, alpha, beta) |

### Version Files

```bash
# Current version
cat VERSION

# Dependency versions
cat versions.json

# Full changelog
cat CHANGELOG.md
```

### API Version Endpoint

```bash
# Get version info
curl http://localhost:3001/version
```

Returns:
```json
{
  "platform": "1.1.0-dev",
  "node": "v20.x",
  "python": "3.11",
  "docker": "containerized",
  "dependencies": {
    "aider": "0.2.6",
    "crawl4ai": "0.8.6",
    "ruff": "0.15.10",
    "express": "4.x"
  }
}
```

### Version History

| Version | Date | Status |
|---------|------|--------|
| 1.1.0-dev | 2026-04-14 | Development |
| 1.0.0 | 2026-04-13 | Initial Release |

---

## 📜 License

MIT

---

*Paradise Stack - Version 1.1.0-dev | Based on MapCoder, HyperAgent, SkillOrchestra*
