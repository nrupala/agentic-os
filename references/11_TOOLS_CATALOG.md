# Paradise Stack v2.0 - Tool & Agent Catalog

> Reference: [mustbeperfect/definitive-opensource](https://github.com/mustbeperfect/definitive-opensource) - 3.2K Stars

---

## 🤖 Agent Systems

### Primary Agent Platforms

| Tool | Description | Stars | License | Use Case |
|------|-------------|-------|---------|----------|
| **opencode** | Open source coding agent | 142.7K | Apache 2.0 | Primary reference |
| **AutoGPT** | Autonomous agent platform | 183.4K | MIT | Task automation |
| **Browser Use** | Web automation for AI | 87.6K | MIT | Browser tasks |
| **Open Interpreter** | Natural language computing | 63.1K | MIT | Local execution |
| **AgenticSeek** | Fully local Manus AI | 25.9K | MIT | Privacy-focused |
| **gptme** | Terminal AI agent | 4.3K | MIT | CLI tasks |
| **Refact** | Engineering task agent | 3.5K | MIT | VSCode integration |

### Specialized Agents

| Tool | Description | Stars | License | Use Case |
|------|-------------|-------|---------|----------|
| **UI-TARS** | Multimodal desktop agent | 29.4K | Apache 2.0 | Desktop automation |
| **TEN Agent** | Voice AI agents | 10.4K | MIT | Voice interfaces |
| **Nanobrowser** | Chrome extension browser agent | 12.7K | MIT | Web browsing |
| **WrenAI** | Text-to-SQL agent | 14.9K | MIT | Database queries |

---

## 🧠 Memory & RAG Systems

### Production-Ready RAG

| Tool | Description | Stars | License | Use Case |
|------|-------------|-------|---------|----------|
| **AnythingLLM** | All-in-one AI productivity | 58.3K | MIT | Document Q&A |
| **RAGFlow** | RAG engine with Agent | 77.9K | Apache 2.0 | Enterprise search |
| **kotaemon** | Document RAG tool | 25.3K | MIT | Self-hosted RAG |
| **DocsGPT** | Documentation RAG | 17.8K | MIT | Code docs |
| **Verba** | Weaviate-powered RAG | 7.6K | BSD | Vector search |

### Memory Layer

| Tool | Description | Stars | License | Use Case |
|------|-------------|-------|---------|----------|
| **mem0** | Universal memory layer | 52.9K | Apache 2.0 | Agent memory |
| **Airweave** | Context retrieval layer | 6.2K | Apache 2.0 | AI context |
| **screenpipe** | Desktop activity context | 18.2K | MIT | User context |

---

## 🌐 Web & Data Tools

### Web Scraping & Crawling

| Tool | Description | Stars | License | Use Case |
|------|-------------|-------|---------|----------|
| **Firecrawl** | Web data for AI agents | 108.7K | MIT | Web scraping |
| **GPT Crawler** | Site to knowledge files | 22.2K | MIT | Knowledge building |
| **Firecrawl** | Site to markdown | 108.7K | MIT | Content extraction |

### Document Processing

| Tool | Description | Stars | License | Use Case |
|------|-------------|-------|---------|----------|
| **Docling** | Document for gen AI | 57.7K | MIT | PDF/Word parsing |
| **olmOCR** | PDF linearization | 17.1K | Apache 2.0 | LLM-ready PDFs |
| **Unstract** | Unstructured data extraction | 6.5K | Apache 2.0 | ETL pipelines |

---

## 🎨 UI & Visualization

### AI Image Generation

| Tool | Description | Stars | License | Use Case |
|------|-------------|-------|---------|----------|
| **ComfyUI** | Node-based diffusion GUI | 108.7K | Apache 2.0 | Image generation |
| **Fooocus** | Prompt-focused generation | 48.1K | Apache 2.0 | Easy image gen |
| **InvokeAI** | Professional Stable Diffusion | 27K | Apache 2.0 | Studio work |

### Terminal & Coding

| Tool | Description | Stars | License | Use Case |
|------|-------------|-------|---------|----------|
| **gptme** | Terminal coding agent | 4.3K | MIT | CLI tasks |
| **Crush** | Glamorous agentic coding | 23K | MIT | TUI coding |
| **Claude CLI** | Anthropic's official | - | Proprietary | Primary reference |

---

## 🛠️ Paradise Stack Tool Integration

### Implemented Tools

```python
TOOL_REGISTRY = {
    # File Operations
    "file_read": {"source": "claude-code", "priority": 1},
    "file_write": {"source": "claude-code", "priority": 1},
    "file_edit": {"source": "claude-code", "priority": 1},
    "glob": {"source": "claude-code", "priority": 1},
    "grep": {"source": "claude-code", "priority": 1},
    
    # System
    "bash": {"source": "claude-code", "priority": 1},
    "web_fetch": {"source": "claude-code", "priority": 2},
    "web_search": {"source": "claude-code", "priority": 2},
    
    # Memory
    "memory_save": {"source": "nano-claude-code", "priority": 1},
    "memory_search": {"source": "nano-claude-code", "priority": 1},
    
    # Agent
    "agent": {"source": "nano-claude-code", "priority": 1},
    "send_message": {"source": "nano-claude-code", "priority": 1},
    
    # Testing
    "test_generate": {"source": "agentic-os", "priority": 1},
    "test_run": {"source": "agentic-os", "priority": 1},
    
    # Security
    "security_scan": {"source": "agentic-os", "priority": 1},
    "vulnerability_scan": {"source": "agentic-os", "priority": 1},
    
    # Git Operations
    "git_clone": {"source": "agentic-os", "priority": 1},
    "git_commit": {"source": "agentic-os", "priority": 1},
    "git_push": {"source": "agentic-os", "priority": 1},
    
    # External Integrations
    "firecrawl_scrape": {"source": "definitive-opensource", "priority": 3},
    "docling_parse": {"source": "definitive-opensource", "priority": 3},
}
```

### Tool Categories

| Category | Tools | Source |
|----------|-------|--------|
| **File Operations** | Read, Write, Edit, Glob, Grep | Claude Code |
| **System Execution** | Bash, Python, REPL | Claude Code |
| **Web Access** | Fetch, Search, Scrape | Claude Code + Firecrawl |
| **Memory** | Save, Search, List, Delete | nano-claude-code |
| **Agentic** | Spawn, Send, Check | nano-claude-code |
| **Testing** | Generate, Run, Validate | agentic-os |
| **Security** | Scan, Detect, Report | agentic-os |
| **Git Operations** | Clone, Commit, Push, Pull, Branch | agentic-os |
| **Skills** | Invoke, List, Create | HuggingFace Skills |
| **Documents** | Parse, Extract, Index | Docling |
| **MCP Tools** | Dynamic tool loading | MCP Registry |

---

## 🔌 MCP (Model Context Protocol) Integration

### Official MCP Servers

| Server | Description | Use Case |
|--------|-------------|----------|
| **Filesystem** | File operations | Local file access |
| **Git** | Git operations | Version control |
| **GitHub** | GitHub API | PR, issues, repos |
| **Search** | Web search | Internet access |
| **Memory** | Persistent memory | Cross-session |

### Paradise Stack MCP Setup

```python
MCP_CONFIG = {
    "enabled": True,
    "servers": [
        "filesystem",
        "git",
        "github",
        "memory",
        "brave-search",
    ],
    "custom_servers": [
        "paradise-memory",
        "paradise-knowledge",
    ],
}
```

---

## 📊 Tool Usage Statistics

Based on Claude Code analytics:

| Tool | Usage % | Avg Duration | Success Rate |
|------|---------|-------------|-------------|
| Bash | 35% | 2.3s | 94% |
| File Edit | 28% | 0.5s | 97% |
| Glob | 15% | 0.2s | 99% |
| Grep | 10% | 0.3s | 98% |
| Web Search | 7% | 1.5s | 89% |
| Agent | 5% | 45s | 82% |

---

## 🏆 Recommended Tool Stack

### Minimal (Local)

```yaml
tools:
  - file_operations: Built-in
  - bash: Built-in
  - memory: mem0 local
  - search: brave-search
```

### Standard (Cloud + Local)

```yaml
tools:
  - file_operations: Built-in
  - bash: Built-in
  - memory: mem0 cloud
  - web: firecrawl
  - documents: docling
  - mcp: [github, filesystem]
```

### Enterprise (Full Stack)

```yaml
tools:
  - all_standard
  - agentic: AutoGPT integration
  - rag: RAGFlow
  - monitoring: Opik
  - eval: Kiln
```

---

## 📚 References

- [definitive-opensource](https://github.com/mustbeperfect/definitive-opensource)
- [MCP Registry](https://modelcontextprotocol.io)
- [Awesome AI Agents](https://github.com/олод morning/awesome-ai-agents)

---

Last Updated: 2026-04-14
