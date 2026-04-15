# Paradise Stack v2.0 - Reference Sources & Architecture

> **"Do it once, do it right"** - Production-ready autonomous AI development organization

---

## 📚 Reference Sources

This document catalogs all external libraries, architectures, and systems that power Paradise Stack v2.0. Each source is credited with specific features extracted and integrated.

---

## 🏛️ Source 1: Claude Code Source Analysis

**Repository:** [chauncygu/collection-claude-code-source-code](https://github.com/chauncygu/collection-claude-code-source-code)  
**Stars:** 2.1K | **License:** Apache-2.0

### Extracted Architectures

| Feature | Implementation | Location |
|---------|---------------|----------|
| **40+ Tool System** | FileReadTool, FileEditTool, BashTool, GlobTool, GrepTool, WebFetchTool, WebSearchTool, AgentTool, MCPTool | `cognition/tools.py` |
| **87 Slash Commands** | /commit, /review, /session, /memory, /config, /skills, /help, /mcp | `commands/` directory |
| **7-Layer Memory Architecture** | Dual-scope (user + project), 4 memory types, AI search, staleness warnings | `cognition/memory.py` |
| **Auto-Compaction** | Reactive compression, micro-compression, trimmed compression, context collapsing | `cognition/compaction.py` |
| **Multi-Provider Support** | Anthropic, OpenAI, Gemini, Ollama, LM Studio, custom endpoints | `cognition/providers.py` |
| **Permission System** | default (ask), bypass (auto-allow), strict (auto-deny) | `cognition/permissions.py` |

### Code Patterns Extracted

```python
# Tool execution pattern
class StreamingToolExecutor:
    async def execute_tools(self, tools: List[Tool], context: Context):
        # Parallel tool execution with dependency tracking

# Context management pattern
async def autoCompact(messages: List[Message], max_tokens: int):
    # Automatic context compression strategies

# Multi-agent coordination
class CoordinatorAgent:
    async def route(self, task: Task) -> Agent:
        # Task routing to specialized sub-agents
```

### Reference Files
- `claude-code-source-code/src/query.ts` - Main agent loop (785KB)
- `claude-code-source-code/src/tools.ts` - Tool registration
- `claude-code-source-code/src/commands.ts` - Slash commands

---

## 🛠️ Source 2: Everything Claude Code

**Repository:** [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)  
**Stars:** 140K | **License:** MIT

### Extracted Features

| Feature | Implementation | Location |
|---------|---------------|----------|
| **38 Specialized Agents** | planner, architect, tdd-guide, code-reviewer, security-reviewer | `agents/` |
| **156+ Skills** | continuous-learning, tdd-workflow, security-review, verification-loop | `skills/` |
| **Hook System** | Pre/post execution hooks with runtime controls (ECC_HOOK_PROFILE) | `cognition/hooks.py` |
| **Continuous Learning** | Instinct-based patterns with confidence scoring | `cognition/self_improvement.py` |
| **Token Optimization** | Model selection, system prompt slimming, background process management | `cognition/optimizer.py` |
| **Memory Persistence** | Hooks that save/load context across sessions automatically | `cognition/memory.py` |
| **Verification Loops** | Checkpoint vs continuous evals, grader types, pass@k metrics | `cognition/verification.py` |

### Skill Format Specification

```markdown
---
name: skill-name
description: When to use this skill
triggers: ["/skill-name", "use skill when..."]
---

# Skill Title

## Guidance
Step-by-step instructions...

## Examples
Example usage patterns...
```

### Agent Format

```markdown
---
name: agent-name
type: planner|reviewer|builder|guardian
description: What this agent specializes in
model: sonnet|opus|haiku
---

# Agent Name

## Identity
Who this agent is...

## Core Mission
Primary objectives...

## Workflow
How they operate...
```

### Reference Files
- `agents/planner.md` - Feature implementation planning
- `agents/code-reviewer.md` - Quality and security review
- `skills/continuous-learning/SKILL.md` - Pattern extraction
- `hooks/pre:bash:*.js` - Pre-execution hooks

---

## 🎭 Source 3: Agency Agents

**Repository:** [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)  
**Stars:** 79.9K | **License:** MIT

### Extracted Personas (100+)

#### Engineering Division
| Persona | Specialty | Deliverables |
|---------|-----------|--------------|
| Frontend Developer | React/Vue/Angular, UI implementation | Components, layouts |
| Backend Architect | API design, database, scalability | Server systems |
| AI Engineer | ML models, deployment | Data pipelines |
| DevOps Automator | CI/CD, infrastructure | Deployment automation |
| Security Engineer | Threat modeling, secure review | Vulnerability assessments |
| Database Optimizer | Schema design, query optimization | Performance tuning |

#### Design Division
| Persona | Specialty |
|---------|-----------|
| UI Designer | Visual design, component libraries |
| UX Researcher | User testing, behavior analysis |
| Brand Guardian | Brand identity, consistency |

#### Marketing Division
| Persona | Specialty |
|---------|-----------|
| Content Creator | Multi-platform content |
| SEO Specialist | Technical SEO, link building |
| Growth Hacker | User acquisition, viral loops |

#### Sales Division
| Persona | Specialty |
|---------|-----------|
| Outbound Strategist | Signal-based prospecting |
| Deal Strategist | MEDDPICC qualification |

### Persona Format

```markdown
---
name: Persona Name
division: engineering|design|marketing|sales
specialty: Core expertise area
when_to_use: When to invoke this persona
success_metrics: How success is measured
---

# Persona Name

## Identity & Personality
Unique voice and communication style...

## Core Mission
Primary objectives and responsibilities...

## Technical Deliverables
Real code, processes, measurable outcomes...

## Success Metrics
How to measure effectiveness...
```

### Reference Files
- `engineering/engineering-frontend-developer.md`
- `engineering/engineering-backend-architect.md`
- `design/design-ui-designer.md`
- `marketing/marketing-content-creator.md`

---

## 📐 Source 4: System Design Resources

**Repository:** [ashishps1/awesome-system-design-resources](https://github.com/ashishps1/awesome-system-design-resources)  
**Stars:** 36.4K | **License:** GPL-3.0

### Extracted Patterns

#### Core Concepts
| Pattern | Application |
|---------|-------------|
| CAP Theorem | Consistency vs Availability tradeoffs |
| Consistent Hashing | Distributed load distribution |
| SPOF (Single Point of Failure) | Redundancy planning |
| Latency vs Throughput | Performance optimization |

#### Distributed Systems
| Pattern | Implementation |
|---------|----------------|
| Circuit Breaker | Fault tolerance, degradation |
| Heartbeats | Service health monitoring |
| Consensus Algorithms | Raft, Paxos coordination |
| Distributed Locking | Resource synchronization |

#### Caching Strategies
| Strategy | Use Case |
|----------|----------|
| Read-Through | Predictable read patterns |
| Write-Through | Immediate consistency |
| Cache Eviction | LRU, LFU, TTL |

#### Database Patterns
| Pattern | Implementation |
|---------|----------------|
| Sharding | Horizontal partitioning |
| Replication | Master-slave, multi-master |
| Indexing | B-tree, hash, composite |

### Pattern Documentation Format

```markdown
# Pattern Name

## What It Solves
Problem description...

## Implementation
Code examples...

## Trade-offs
Pros and cons...

## References
- [Distributed Systems Paper](link)
- [Related Pattern](#)
```

### Reference Files
- `diagrams/` - Architecture diagrams
- `implementations/` - Code implementations
- [AlgoMaster System Design](https://algomaster.io/learn/system-design)

---

## 🎨 Source 5: UI/UX Agent Prompts

**Repository:** [mustafakendiguzel/claude-code-ui-agents](https://github.com/mustafakendiguzel/claude-code-ui-agents)  
**Stars:** 495 | **License:** MIT

### Extracted Prompt Templates

| Template | Category | Purpose |
|----------|----------|---------|
| Design System Generator | UI Design | Design tokens, components |
| Universal UI/UX Methodology | UX Design | Adaptive design |
| React Component Architect | Components | TypeScript React |
| CSS Architecture Specialist | Web Dev | Scalable CSS |
| Micro-Interactions Expert | Animation | Performance animations |
| ARIA Implementation | Accessibility | WCAG compliance |

### Prompt Template Format

```markdown
---
name: prompt-name
description: Use this agent when you need [expertise area]
model: sonnet
category: ui-design|components|animation|accessibility
difficulty: beginner|intermediate|advanced
tags: [#ui, #design, #react]
---

# Prompt Title

**Category:** category-name  
**Difficulty:** Level  
**Tags:** tags

## Description
What this prompt does...

## Prompt
The actual prompt text...

## Example Usage
How to use...

## Sample Results
Expected outputs...
```

### Reference Files
- `prompts/ui-design/*.md`
- `prompts/components/*.md`
- `prompts/accessibility/*.md`

---

## 📦 Source 6: Definitive Open Source

**Repository:** [mustbeperfect/definitive-opensource](https://github.com/mustbeperfect/definitive-opensource)  
**Stars:** 3.2K | **License:** MIT

### Extracted Agent Tool Catalog

#### Agent Systems
| Tool | Description | Stars |
|------|-------------|-------|
| AgenticSeek | Fully local Manus AI | 25.9K |
| AutoGPT | Autonomous agent platform | 183.4K |
| Browser Use | Web automation for AI | 87.6K |
| Open Interpreter | Natural language interface | 63.1K |
| opencode | Open source coding agent | 142.7K |

#### RAG Systems
| Tool | Description | Stars |
|------|-------------|-------|
| AnythingLLM | All-in-one AI productivity | 58.3K |
| RAGFlow | RAG engine with Agent | 77.9K |
| kotaemon | Document RAG tool | 25.3K |

#### Tool Integration
| Tool | Description | Stars |
|------|-------------|-------|
| mem0 | Universal memory layer | 52.9K |
| Firecrawl | Web data for AI | 108.7K |
| Docling | Document processing | 57.7K |

### Reference Catalog Format

```markdown
# Tool Category

| Name | Description | Platform | Stars | License |
|------|-------------|----------|-------|---------|
| Tool | What it does | Cross/SelfHost | 10K | MIT |

## Quick Install
```bash
# Installation commands
```
```

---

## 🤖 Source 7: Open LLM Catalog

**Repository:** [eugeneyan/open-llms](https://github.com/eugeneyan/open-llms)  
**Stars:** 12.7K | **License:** Apache-2.0

### Extracted Models (Commercial Use)

#### General Purpose LLMs
| Model | Provider | Params | Context | License |
|-------|----------|--------|---------|---------|
| Llama 3 | Meta | 8-70B | 8K | Custom |
| Mistral 7B | Mistral | 7B | 16K | Apache 2.0 |
| Mixtral 8x7B | Mistral | 46.7B | 32K | Apache 2.0 |
| Qwen1.5 | Alibaba | 7-110B | 32K | Custom |
| Gemma | Google | 2-7B | 8K | Gemma Terms |
| DeepSeek | DeepSeek | 7-67B | 4K | Custom |
| Phi-3 | Microsoft | 3.8-14B | 128K | MIT |
| Phi-4 | Microsoft | 14B | 4K | MIT |

#### Code-Specific LLMs
| Model | Provider | Params | Context | License |
|-------|----------|--------|---------|---------|
| Code Llama | Meta | 7-34B | 4K | Custom |
| StarCoder | BigCode | 1.1-15B | 8K | OpenRAIL-M |
| WizardCoder | WizardLM | 15B | 8K | OpenRAIL-M |
| CodeGen2 | Salesforce | 1-16B | 2K | Apache 2.0 |

#### Embedding Models
| Model | Provider | Dimensions | License |
|-------|----------|------------|---------|
| e5-mistral | Microsoft | 1024 | MIT |
| bge-large | BAAI | 1024 | Apache 2.0 |
| nomic-embed | Nomic | 768 | Apache 2.0 |

### Model Selection Guidelines

```markdown
# Model Selection Matrix

| Task | Recommended | Alternative |
|------|-------------|-------------|
| Code Generation | Code Llama, StarCoder | DeepSeek-Coder |
| Reasoning | Llama 3 70B, Mixtral | Qwen 72B |
| Fast Tasks | Phi-3-mini, Gemma 2B | Mistral 7B |
| Long Context | Phi-3-medium 128K, Mixtral | ChatGLM3 128K |
| Local Deployment | Mistral 7B, Llama 3 8B | Qwen 7B |

## API Providers
- Anthropic (Claude)
- OpenAI (GPT-4)
- Google (Gemini)
- Together AI (Llama, Mistral)
- Groq (Fast inference)
- Ollama (Local)
```

---

## 🛠️ Source 8: Hugging Face Skills

**Repository:** [huggingface/skills](https://github.com/huggingface/skills)  
**Stars:** 10.2K | **License:** Apache-2.0

### Extracted Skills

| Skill | Description | Use Case |
|-------|-------------|----------|
| hf-cli | HuggingFace Hub operations | Model/dataset management |
| huggingface-datasets | Dataset exploration | Data loading, querying |
| huggingface-gradio | Gradio UI building | Web interface creation |
| huggingface-llm-trainer | Model fine-tuning | SFT, DPO, GRPO training |
| huggingface-papers | Research paper lookup | Literature review |
| huggingface-vision-trainer | Vision model training | Object detection, classification |
| transformers-js | JS ML inference | Browser/Node inference |

### Standard Skill Format

```markdown
---
name: skill-name
description: Execute [specific task] using [tool/method]
---

# Skill Title

## When to Use
Trigger conditions for activating this skill...

## Instructions
1. Step one...
2. Step two...

## Examples
```bash
# Example command
hf-cli download model
```
```

### Interoperability
- Claude Code plugin support
- Codex skills directory
- Gemini CLI extensions
- Cursor marketplace

---

## 🔗 Source 9: nano-claude-code

**Repository:** [SafeRL-Lab/nano-claude-code](https://github.com/SafeRL-Lab/nano-claude-code)  
**From:** collection-claude-code-source-code

### Extracted Features

| Feature | Implementation |
|---------|---------------|
| **Multi-provider** | 10+ providers (Anthropic, OpenAI, Gemini, Ollama) |
| **18 Built-in Tools** | Read, Write, Edit, Bash, Glob, Grep, Memory tools |
| **Git Worktree Isolation** | Parallel sub-agent execution |
| **Skill System** | Markdown-based reusable prompts |
| **Dual-scope Memory** | User + project level persistence |
| **Context Compression** | Auto-compact long conversations |

### Reference Implementation
```python
# nano_claude.py - Entry point
# agent.py - Agent loop with tool dispatch
# providers.py - Multi-provider adapters
# tools.py - Tool registration
# context.py - System prompt building
```

---

## 📊 Integration Map

### Component → Sources Mapping

```
Paradise Stack v2.0
├── cognition/
│   ├── knowledge_graph.py    ← collection-claude-code (7-layer memory)
│   ├── meta_cognition.py     ← everything-claude-code (continuous learning)
│   ├── self_improvement.py   ← everything-claude-code (instinct patterns)
│   ├── entities.py          ← definitive-opensource (tool catalog)
│   ├── verification.py      ← everything-claude-code (verification loops)
│   ├── engineering_teams.py ← agency-agents (persona structure)
│   ├── orchestrator.py      ← system-design (circuit breaker)
│   ├── master_orchestrator.py ← system-design (consensus)
│   ├── reactive_engine.py    ← collection-claude-code (tool execution)
│   ├── notebook.py          ← huggingface/skills (skill format)
│   ├── agent_pairing.py     ← agency-agents (handover protocols)
│   └── agent_personas.py    ← agency-agents (100+ personas)
│
├── agents/                   ← everything-claude-code (38 agents)
│
├── skills/                  ← huggingface/skills (skill format)
│
└── docs/
    ├── MODELS.md            ← open-llms (LLM catalog)
    ├── TOOLS.md            ← definitive-opensource (tool catalog)
    └── ARCHITECTURE.md      ← awesome-system-design (patterns)
```

---

## 📋 Feature Checklist

| Feature | Source | Status |
|---------|--------|--------|
| Multi-provider support | collection-claude-code | ✅ Implemented |
| 7-layer memory | collection-claude-code | ✅ Implemented |
| 100+ agent personas | agency-agents | ✅ Implemented |
| Skill system | huggingface/skills | ✅ Implemented |
| Hook system | everything-claude-code | ✅ Implemented |
| Continuous learning | everything-claude-code | ✅ Implemented |
| System design patterns | awesome-system-design | ✅ Implemented |
| Circuit breaker | awesome-system-design | ✅ Implemented |
| Context compaction | collection-claude-code | ✅ Implemented |
| Permission system | collection-claude-code | ✅ Implemented |
| LLM model catalog | open-llms | ✅ Implemented |
| Tool catalog | definitive-opensource | ✅ Implemented |
| Agent-type definitions | nano-claude-code | ✅ Implemented |
| Git worktree isolation | nano-claude-code | ✅ Implemented |

---

## 🏆 Summary Statistics

| Metric | Value |
|--------|-------|
| Total Reference Stars | 284K+ |
| Source Repositories | 8 |
| Extracted Features | 50+ |
| Agent Personas | 100+ |
| Skills | 156+ |
| LLM Models | 40+ |
| Tool Integrations | 20+ |
| System Patterns | 30+ |

---

## 📜 License Compliance

All referenced repositories maintain open-source licenses:
- Apache-2.0 (Claude Code, HuggingFace Skills)
- MIT (Agency Agents, UI Prompts, Everything Claude Code)
- GPL-3.0 (System Design Resources)

Proper attribution is maintained throughout Paradise Stack v2.0.

---

## 🔄 Continuous Updates

This document is updated when:
1. New features are extracted from references
2. Source repositories release significant updates
3. New patterns or architectures are identified

Last Updated: 2026-04-14
