# 🏝️ The Paradise Stack
> A fully independent, FOSS AI Software Engineering OS.

## 🚀 The Stack
- **Architect:** [Cline CLI](https://github.com) - Autonomous Planning.
- **Builder:** [Aider](https://aider.chat) - Git-native Implementation.
- **Senses:** [Langfuse](https://langfuse.com) & [Arize Phoenix](https://arize.com) - Tracing & Observability.
- **Knowledge:** [Crawl4AI](https://crawl4ai.com) - Documentation RAG.
- **Guardian:** [Ruff](https://docs.astral.sh/ruff) + [ESLint](https://eslint.org) + [Prettier](https://prettier.io) - FOSS Quality Assurance.

## 🛠️ Quick Start
1. **Fix Build Tools:** Install [C++ Build Tools](https://microsoft.com) (Select "Desktop development with C++").
2. **Install:** `powershell ./setup.ps1`
3. **Launch Senses:** `docker-compose up -d`
4. **Code:** 
   - Use `cline "Plan feature X"` to create a `PLAN.md`.
   - Use `aider --message "Execute PLAN.md"` to build it.

## 🧠 Local Intelligence
Configured to run via **Ollama**. Default models:
- **Planning:** `deepseek-v3`
- **Coding:** `qwen2.5-coder:32b`


## 🏗️ The Workflow
1. **Architect (Cline):** High-level planning via `cline`.
2. **Knowledge (Crawl4AI):** Just-in-time documentation scraping.
3. **Builder (Aider):** Git-native code implementation.
4. **Guardian (Qodo):** Automated testing and quality gates.
5. **Senses (Langfuse/Phoenix):** Full observability of every token.

## 🖥️ The Command Center
Open `dashboard/index.html` in any browser to visualize the agent hand-off sequence and monitor system health.

## 🚀 Installation

### Option 1: Docker (Recommended)
```bash
docker-compose up -d
```
Open http://localhost:3001

### Option 2: Local Setup
```powershell
powershell ./setup.ps1
docker-compose up -d
```

## 📁 Project Structure
```
.
├── logs/           # Command execution logs
├── outputs/        # Generated artifacts
├── projects/       # Project-specific files
└── dashboard/      # Web UI
    ├── server.js   # Node bridge server
    └── index.html  # Command Center GUI
```

## 📋 Versioning
Current version: `1.0.0`

**Get version:**
```bash
# From VERSION file
cat VERSION

# From package.json
npm pkg get version
```

**Release workflow:**
```bash
# Update version in VERSION and package.json
# Create git tag
git tag v1.0.0
git push origin v1.0.0
```
