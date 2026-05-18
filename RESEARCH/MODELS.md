# Paradise Stack v2.0 - LLM Model Catalog

> Reference: [eugeneyan/open-llms](https://github.com/eugeneyan/open-llms) - 12.7K Stars

---

## 🎯 Model Selection Guide

Paradise Stack v2.0 supports **multi-provider deployment** with the following model recommendations:

### By Task Type

| Task | Primary | Secondary | Local |
|------|---------|-----------|-------|
| **Code Generation** | Claude Opus | Code Llama | Mistral 7B |
| **Reasoning** | Claude Sonnet | Llama 3 70B | Mixtral 8x7B |
| **Fast Tasks** | Claude Haiku | Phi-3-mini | Gemma 2B |
| **Long Context** | Claude 200K | Phi-3-medium 128K | ChatGLM3 128K |
| **Embedding** | Claude Embeddings | e5-mistral | bge-large |
| **Vision** | Claude Vision | GPT-4V | LLaVA |

---

## 🤖 General Purpose LLMs (Commercial Use)

### Tier 1: Premium Performance

| Model | Provider | Params | Context | License | Use Case |
|-------|----------|--------|---------|---------|----------|
| Claude 3.5 Sonnet | Anthropic | - | 200K | Proprietary | Primary reasoning, code |
| Claude 3 Opus | Anthropic | - | 200K | Proprietary | Complex tasks |
| GPT-4 Turbo | OpenAI | - | 128K | Proprietary | General purpose |
| Gemini 1.5 Pro | Google | - | 1M | Proprietary | Long context |

### Tier 2: Open Source (Apache 2.0 / MIT)

| Model | Provider | Params | Context | License | Use Case |
|-------|----------|--------|---------|---------|----------|
| **Llama 3.1** | Meta | 8-70B | 128K | Custom | Primary OSS |
| **Mistral 7B** | Mistral | 7B | 32K | Apache 2.0 | Fast inference |
| **Mixtral 8x7B** | Mistral | 46.7B | 32K | Apache 2.0 | Balanced |
| **Qwen2.5** | Alibaba | 7-72B | 32K | Custom | Multilingual |
| **DeepSeek V2** | DeepSeek | 236B | 128K | Custom | Efficient MoE |
| **Phi-3** | Microsoft | 3.8-14B | 128K | MIT | Small, capable |
| **Gemma 2** | Google | 2-9B | 8K | Gemma Terms | Lightweight |
| **Yi-1.5** | 01.AI | 6-34B | 4K | Apache 2.0 | Bilingual |

### Tier 3: Specialized

| Model | Provider | Params | Context | License | Specialty |
|-------|----------|--------|---------|---------|-----------|
| **Snowflake Arctic** | Snowflake | 480B | 4K | Apache 2.0 | Enterprise SQL |
| **Jamba** | AI21 | 52B | 256K | Apache 2.0 | Long context |
| **RWKV 6** | BlinkDL | 1.6-7B | ∞ | Apache 2.0 | Infinite context (RNN) |
| **OLMo** | AI2 | 1-7B | 2K | Apache 2.0 | Fully open |

---

## 💻 Code-Specific LLMs

### Open Source (Commercial Use)

| Model | Provider | Params | Context | License | Benchmarks |
|-------|----------|--------|---------|---------|------------|
| **Code Llama** | Meta | 7-34B | 100K | Custom | HumanEval 62% |
| **DeepSeek Coder** | DeepSeek | 6.7-33B | 128K | Custom | HumanEval 70% |
| **StarCoder 2** | BigCode | 3-15B | 8K | OpenRAIL-M | HumanEval 45% |
| **Qwen2.5-Coder** | Alibaba | 7-32B | 128K | Custom | HumanEval 65% |
| **CodeGen2.5** | Salesforce | 7B | 2K | Apache 2.0 | HumanEval 40% |
| **WizardCoder** | WizardLM | 33B | 8K | OpenRAIL-M | HumanEval 57% |
| **Phi-3-mini-4k** | Microsoft | 3.8B | 4K | MIT | Mobile code |
| **Mistral-Coder** | Mistral | 7B | 32K | Apache 2.0 | Fast coding |

### Selection Guidelines

```python
# Code generation selection matrix
CODE_MODEL_SELECTION = {
    "simple_snippets": "phi-3-mini",      # Quick, small tasks
    "feature_development": "qwen2.5-coder", # Standard features
    "complex_algorithms": "deepseek-coder",  # Complex logic
    "full_stack": "code-llama-34b",         # Large context
    "local_fast": "starcoder-3b",           # Local inference
}
```

---

## 📊 Embedding Models

### Open Source (Commercial Use)

| Model | Provider | Dimensions | License | Use Case |
|-------|----------|------------|---------|----------|
| **e5-mistral** | Microsoft | 1024 | MIT | General text |
| **bge-large** | BAAI | 1024 | Apache 2.0 | Semantic search |
| **nomic-embed** | Nomic | 768 | Apache 2.0 | Local deployment |
| **GTE-large** | Alibaba | 1024 | Apache 2.0 | Chinese text |
| **Snowflake-Embed** | Snowflake | 768 | Apache 2.0 | SQL understanding |

### Selection Guidelines

```python
EMBEDDING_SELECTION = {
    "general": "BAAI/bge-large-en-v1.5",
    "code": "微调/code-embedder",
    "chinese": "BAAI/bge-large-zh",
    "multilingual": "intfloat/e5-mistral-7b-instruct",
    "local": "nomic-ai/nomic-embed-text-v1.5",
}
```

---

## 🔧 Provider Configuration

### API Providers

```python
PROVIDER_CONFIG = {
    "anthropic": {
        "models": ["claude-opus-4", "claude-sonnet-4", "claude-haiku-3"],
        "context": 200_000,
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    "openai": {
        "models": ["gpt-4-turbo", "gpt-4o", "gpt-4o-mini"],
        "context": 128_000,
        "api_key_env": "OPENAI_API_KEY",
    },
    "google": {
        "models": ["gemini-1.5-pro", "gemini-1.5-flash"],
        "context": 1_000_000,
        "api_key_env": "GOOGLE_API_KEY",
    },
}
```

### Local Providers

```python
LOCAL_PROVIDER_CONFIG = {
    "ollama": {
        "base_url": "http://localhost:11434",
        "models": {
            "reasoning": "llama3.1:70b",
            "coding": "codellama:34b",
            "fast": "mistral:7b",
            "embedding": "nomic-embed-text",
        },
    },
    "lm_studio": {
        "base_url": "http://localhost:1234/v1",
        "models": {...},
    },
}
```

---

## 📈 Performance Benchmarks

### HumanEval (Code)

| Model | Score | Notes |
|-------|-------|-------|
| Claude 3.5 Sonnet | 92% | Proprietary |
| DeepSeek Coder 33B | 70% | Open |
| Qwen2.5-Coder 32B | 65% | Open |
| Code Llama 34B | 62% | Open |
| StarCoder 2 15B | 45% | Open |
| Phi-3-mini | 40% | Mobile |

### MMLU (Reasoning)

| Model | Score | License |
|-------|-------|---------|
| Claude 3 Opus | 88% | Proprietary |
| Llama 3.1 70B | 82% | Custom |
| Mistral 7B | 64% | Apache 2.0 |
| Phi-3 14B | 78% | MIT |
| Gemma 2 9B | 68% | Gemma |

---

## 🚀 Deployment Recommendations

### For Individual Developers

```yaml
# Local-first setup
primary_model: mistral:7b-instruct      # Fast, capable
coding_model: qwen2.5-coder:7b        # Code-specific
embedding: nomic-embed-text           # Local embeddings
provider: ollama
```

### For Small Teams

```yaml
# Cloud + Local hybrid
primary_model: claude-sonnet-4         # Reasoning
coding_model: deepseek-coder-33b      # Code generation
fast_model: phi-3-mini                # Quick tasks
provider: anthropic + ollama
```

### For Enterprises

```yaml
# Full cloud deployment
primary_model: claude-opus-4           # Complex reasoning
coding_model: code-llama-34b          # Code (self-hosted)
context_model: gemini-1.5-pro         # Long documents
provider: anthropic + openai + google
```

---

## 📚 References

- [open-llms Repository](https://github.com/eugeneyan/open-llms)
- [HuggingFace Model Hub](https://huggingface.co/models)
- [LLM Leaderboard](https://chat.lmsys.org/?leaderboard)
- [Open LLM Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)

---

## 🔄 Model Updates

Models are evaluated quarterly for:
- Performance improvements
- New open-source releases
- License changes
- Benchmark updates

Last Updated: 2026-04-14
