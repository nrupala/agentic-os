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
├── dashboard/            # Web UI
│   ├── index.html       # Dashboard
│   ├── server.js        # Bridge server
│   └── workflow.js      # Agent orchestration
├── docs/
│   └── RESEARCH.md      # Research references
├── logs/                # Command logs
├── outputs/             # Generated artifacts
└── projects/           # Project files
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

Current: **1.0.0**

```bash
cat VERSION
```

---

## 📜 License

MIT
