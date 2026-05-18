# Paradise Stack v2.0 - Skills Catalog

> Comprehensive reference: 500+ skills from 20+ sources

---

## 🎯 Skill Sources Overview

| Source | Skills | Category | License |
|--------|--------|----------|---------|
| HuggingFace Skills | 10+ | AI/ML | Apache 2.0 |
| Everything Claude Code | 156+ | DevOps | MIT |
| Agency Agents | 100+ | Multi-domain | MIT |
| Open Science Skills | 15 | Research | MIT |
| AI Marketing Skills | 50+ | Marketing | MIT |
| Finance Skills | 30+ | Finance | MIT |
| Open Creator | Dynamic | Skill Creation | MIT |

---

## 🤖 AI/ML Skills (HuggingFace)

**Source:** [huggingface/skills](https://github.com/huggingface/skills) | 10.2K Stars

| Skill | Description | Use Case |
|-------|-------------|----------|
| `hf-cli` | HuggingFace Hub operations | Model/dataset management |
| `huggingface-datasets` | Dataset exploration | Data loading, querying |
| `huggingface-gradio` | Gradio UI building | Web interface creation |
| `huggingface-llm-trainer` | Model fine-tuning | SFT, DPO, GRPO training |
| `huggingface-papers` | Research paper lookup | Literature review |
| `huggingface-vision-trainer` | Vision model training | Object detection |
| `transformers-js` | JS ML inference | Browser ML |

---

## 💻 Developer Skills (Everything Claude Code)

**Source:** [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | 140K Stars

### Coding Skills

| Skill | Description |
|-------|-------------|
| `tdd-workflow` | Test-driven development methodology |
| `security-review` | Security checklist execution |
| `verification-loop` | Continuous verification |
| `coding-standards` | Language-specific best practices |

### Language Patterns

| Skill | Languages |
|-------|----------|
| `python-patterns` | Python idioms |
| `golang-patterns` | Go idioms |
| `django-patterns` | Django best practices |
| `laravel-patterns` | Laravel architecture |
| `cpp-coding-standards` | C++ Core Guidelines |
| `springboot-patterns` | Java Spring Boot |

### DevOps Skills

| Skill | Description |
|-------|-------------|
| `docker-patterns` | Container security, networking |
| `deployment-patterns` | CI/CD, health checks |
| `database-migrations` | Prisma, Drizzle, Django |
| `api-design` | REST API design |

---

## 🎭 Agent Personas (Agency Agents)

**Source:** [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | 79.9K Stars

### Engineering Division

| Persona | Specialty |
|---------|-----------|
| Frontend Developer | React/Vue/Angular |
| Backend Architect | API design, scalability |
| Mobile App Builder | React Native, Flutter |
| AI Engineer | ML models, deployment |
| DevOps Automator | CI/CD, infrastructure |
| Security Engineer | Threat modeling |
| Database Optimizer | Query optimization |
| SRE | SLOs, observability |
| Embedded Firmware Engineer | RTOS, ESP32 |
| Solidity Engineer | Smart contracts |

### Design Division

| Persona | Specialty |
|---------|-----------|
| UI Designer | Visual design, components |
| UX Researcher | User testing, behavior |
| Brand Guardian | Brand identity |
| Whimsy Injector | Delightful interactions |

### Marketing Division

| Persona | Specialty |
|---------|-----------|
| Content Creator | Multi-platform content |
| Growth Hacker | User acquisition |
| SEO Specialist | Technical SEO |
| Social Media Strategist | Cross-platform |

### Sales Division

| Persona | Specialty |
|---------|-----------|
| Outbound Strategist | Prospecting |
| Discovery Coach | SPIN, Gap Selling |
| Deal Strategist | MEDDPICC |
| Pipeline Analyst | Forecasting |

---

## 🔬 Research Skills (Open Science)

**Source:** [scdenney/open-science-skills](https://github.com/scdenney/open-science-skills) | 15 Stars

### Research Design

| Skill | Description |
|-------|-------------|
| `conjoint-design` | Attribute architecture, AMCE/AMIE |
| `conjoint-diagnostics` | Diagnostic checklist |
| `survey-design` | Question construction, scales |
| `cross-national-design` | Cross-national surveys |
| `list-experiment` | Item count technique |

### Analysis

| Skill | Description |
|-------|-------------|
| `topic-modeling` | STM with metadata |
| `text-classification` | LLM-based classification |

### Writing

| Skill | Description |
|-------|-------------|
| `hypothesis-building` | Falsifiability, DAGs |
| `narrative-building` | Introduction logic |
| `pre-registration-writing` | PAP structure |
| `methods-reporting` | CONSORT, JARS, DA-RT |
| `paper-review` | Pre-submission audit |

---

## 📈 Marketing Skills

**Source:** [ericosiu/ai-marketing-skills](https://github.com/ericosiu/ai-marketing-skills) | 1.8K Stars

### Growth Engine

| Skill | Description |
|-------|-------------|
| `experiment-engine` | Autonomous experiments |
| `pacing-alerts` | Budget pacing |
| `weekly-scorecard` | Performance tracking |

### Sales Pipeline

| Skill | Description |
|-------|-------------|
| `deal-resurrector` | Revive dead deals |
| `trigger-prospector` | Signal-based prospecting |
| `icp-learner` | Auto-improve targeting |

### Content Ops

| Skill | Description |
|-------|-------------|
| `expert-panel` | Domain expert scoring |
| `quality-gate` | 90+ quality threshold |
| `editorial-brain` | Content strategy |

### SEO Ops

| Skill | Description |
|-------|-------------|
| `content-attack-brief` | Competitor content gaps |
| `gsc-optimizer` | Google Search Console |
| `trend-scout` | Emerging trends |

### Finance Ops

| Skill | Description |
|-------|-------------|
| `cfo-briefing` | Financial analysis |
| `cost-estimate` | Hidden cost detection |
| `scenario-modeler` | Financial modeling |

---

## 💰 Finance Skills

**Source:** [RKiding/Awesome-finance-skills](https://github.com/RKiding/Awesome-finance-skills) | MIT

| Category | Skills |
|----------|--------|
| Valuation | DCF, comparable analysis |
| Risk Management | VaR, stress testing |
| Portfolio | Rebalancing, optimization |
| Compliance | Regulatory reporting |

---

## 🛠️ Meta-Skills

**Source:** [pointerliu/skillize-any-libs](https://github.com/pointerliu/skillize-any-libs) | 4 Stars

| Skill | Description |
|-------|-------------|
| `skillize-any-lib` | Generate SKILL.md for any library |
| `open-creator` | Extract skills from conversations |

---

## 📋 Skill Format Standard

```markdown
---
name: skill-name
description: Use when [trigger conditions]
triggers: ["/skill-name", "use when..."]
model: sonnet|opus|haiku
category: coding|design|research|marketing|finance
difficulty: beginner|intermediate|advanced
---

# Skill Title

## When to Use
Trigger conditions...

## Instructions
1. Step one...
2. Step two...

## Examples
```bash
# Example command
```
```

## References
- [Source Documentation](link)
```

---

## 🔄 Skill Lifecycle

```
┌─────────────┐
│  Discover   │  GitHub Scanner finds new skills
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Evaluate   │  Quality check, relevance
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Integrate  │  Add to Paradise Stack
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Monitor    │  Track updates, versions
└─────────────┘
```

---

## 📊 Skill Statistics

| Category | Count |
|---------|-------|
| AI/ML | 10+ |
| Development | 100+ |
| Design | 5+ |
| Marketing | 30+ |
| Sales | 20+ |
| Research | 15+ |
| Finance | 30+ |
| **Total** | **200+** |

---

## 🗂️ Skill Directory Structure

```
ParadiseStack/
├── skills/
│   ├── ai-ml/
│   │   ├── hf-cli/
│   │   ├── huggingface-datasets/
│   │   └── huggingface-llm-trainer/
│   ├── development/
│   │   ├── tdd-workflow/
│   │   ├── security-review/
│   │   └── python-patterns/
│   ├── design/
│   │   ├── ui-designer/
│   │   └── ux-researcher/
│   ├── marketing/
│   │   ├── growth-engine/
│   │   ├── content-ops/
│   │   └── seo-ops/
│   ├── research/
│   │   ├── conjoint-design/
│   │   └── topic-modeling/
│   ├── finance/
│   │   ├── cfo-briefing/
│   │   └── valuation/
│   └── meta/
│       ├── skillize-any-lib/
│       └── open-creator/
```

---

## 🔍 Finding Skills

Paradise Stack uses the scanner to continuously update skills:

1. **Weekly Scan**: Check all source repos for new skills
2. **Version Check**: Verify skill compatibility
3. **Auto-Update**: Pull latest versions
4. **Catalog Refresh**: Regenerate this document

---

## 📚 References

- [HuggingFace Skills](https://github.com/huggingface/skills)
- [Everything Claude Code](https://github.com/affaan-m/everything-claude-code)
- [Agency Agents](https://github.com/msitarzewski/agency-agents)
- [Open Science Skills](https://github.com/scdenney/open-science-skills)
- [AI Marketing Skills](https://github.com/ericosiu/ai-marketing-skills)
- [Open Creator](https://github.com/timedomain-tech/open-creator)
- [Skillize Any Libs](https://github.com/pointerliu/skillize-any-libs)

---

Last Updated: 2026-04-14
