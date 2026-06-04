# agentic-OS Read-Only Reliability Tests

> TASK: Read-only reliability test of the agentic-OS pipeline.  
> DO NOT modify any config, file, service, model, or container. Report only.  
> **Context:** Local Python stack; FastAPI API :8080; Dashboard :8000; Flask :5000; Express :3001; OmegaDaemon :8765; MCP Server (stdio); observability (Loki :3100, Grafana :3000, Phoenix :6006, OTLP :4317). Source in `D:\agentic-OS`.

---

## 1) DISCOVER routes + auth

### 1a) FastAPI API Server (`api/server.py`)
```bash
grep -rn "\.route\(" api/server.py
grep -rn "@app\." api/server.py
grep -rn "@router\." api/server.py
```

### 1b) FastAPI Dashboard (`dashboard/app.py`)
```bash
grep -rn "\.route\(" dashboard/app.py
grep -rn "@app\." dashboard/app.py
```

### 1c) Flask Dashboard (`dashboard/web_dashboard.py`)
```bash
grep -rn "\.route\(" dashboard/web_dashboard.py
grep -rn "@app\." dashboard/web_dashboard.py
```

### 1d) Express.js Server (`dashboard/server.js`)
```bash
grep -rn "\.\(get\|post\|put\|delete\|use\)(" dashboard/server.js
```

### 1e) Engine-embedded Flask apps
```bash
grep -rn "\.route\(" engine/execution_engine.py engine/autocoder.py engine/meta_coder.py engine/self_correcting_memory.py
```

### 1f) Auth/RBAC
```bash
grep -rn "auth_basic\|\.htpasswd\|@login_required\|login_required\|require_auth\|authenticate" security/ api/ dashboard/
```

**List every discovered API endpoint with method + path + source file.**

---

## 2) API SERVER (direct, port 8080)

```bash
# Health
curl -s -m 10 http://localhost:8080/health
echo "---"

# API info
curl -s -m 10 http://localhost:8080/
echo "---"

# List executions
curl -s -m 10 http://localhost:8080/api/v1/executions
echo "---"

# Execute a goal (record latency + output)
time curl -s -m 60 -X POST http://localhost:8080/api/v1/execute \
  -H 'Content-Type: application/json' \
  -d '{"goal":"Reply with exactly: pong"}'
```

**Run 3 times, record latency + output each run.**

---

## 3) DASHBOARD ENDPOINTS

### 3a) FastAPI Dashboard (port 8000)
```bash
curl -s -m 10 http://localhost:8000/ | head -5
echo "---"
curl -s -m 10 http://localhost:8000/api/v1/status
echo "---"
curl -s -m 10 http://localhost:8000/api/v1/executions
echo "---"
```

### 3b) Flask Dashboard (port 5000)
```bash
curl -s -m 10 http://localhost:5000/ | head -5
echo "---"
curl -s -m 10 http://localhost:5000/api/state
echo "---"
curl -s -m 10 http://localhost:5000/api/workflows
echo "---"
curl -s -m 10 http://localhost:5000/api/deliverables
echo "---"
curl -s -m 10 http://localhost:5000/api/skills
echo "---"
curl -s -m 10 http://localhost:5000/api/repos
echo "---"
```

### 3c) Express.js Bridge (port 3001)
```bash
curl -s -m 10 http://localhost:3001/status
echo "---"
curl -s -m 10 http://localhost:3001/version
echo "---"
curl -s -m 10 http://localhost:3001/health
echo "---"
curl -s -m 10 http://localhost:3001/logs | head -20
echo "---"
```

---

## 4) OMEGA DAEMON (port 8765)

```bash
# Health / status
curl -s -m 10 http://localhost:8765/health
echo "---"
curl -s -m 10 http://localhost:8765/status
echo "---"

# Task queue status
curl -s -m 10 http://localhost:8765/tasks
echo "---"

# Metrics
curl -s -m 10 http://localhost:8765/metrics | head -30
echo "---"
```

---

## 5) MCP SERVER (stdio) — list tools

```bash
# If omega_mcp_server.py is running, list its 16 tools and test one
python -c "
import json, subprocess, sys
# Check if MCP process is detectable
result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], capture_output=True, text=True)
print(result.stdout[:500])
"
```

**For each of the 16 MCP tools, verify:**
| Tool | Test |
|------|------|
| `omega_execute_goal` | Call with simple goal |
| `omega_submit_task` | Submit a test task |
| `omega_self_repair` | Trigger self-repair check |
| `omega_get_status` | Read service status |
| `omega_verify_build` | Check build state |
| `omega_semantic_search` | Search for symbol |
| `omega_memory_store` | Store test memory |
| `omega_memory_recall` | Recall stored memory |
| `omega_read_file` | Read known file |
| `omega_write_file` | Dry-run write |
| `omega_list_directory` | List directory |
| `omega_git_operations` | Check git status |
| `omega_analyze_code` | Analyze file |
| `omega_list_symbols` | List symbols |
| `omega_create_checkpoint` | Create checkpoint |
| `omega_optimal_strategy` | Get strategy |

---

## 6) CORE ENGINE — MEMORY / RAG / GAN

### 6a) Hierarchical Memory
```bash
# Store test memory (via direct import or API)
python -c "
from engine.omega_hierarchical_memory import HierarchicalMemory
m = HierarchicalMemory('.')
m.store('test-key', 'This is a read-only reliability test payload.', layer='session')
print('Stored OK')
recalled = m.recall('test-key')
print(f'Recalled: {recalled}')
"
```

### 6b) RAG Retrieval
```bash
python -c "
from engine.omega_rag import OmegaRAG
rag = OmegaRAG('.')
rag.ingest('test.txt', 'This is a test document for RAG reliability.')
results = rag.query('test document')
print(f'Results: {results}')
"
```

### 6c) GAN Self-Correction
```bash
python -c "
from engine.omega_gan import OmegaGAN
gan = OmegaGAN('.')
result = gan.generate('print(\"hello world\")', task_type='quick')
print(f'Generated: {result.get(\"code\", \"\")[:200]}')
print(f'Score: {result.get(\"score\", \"N/A\")}')
"
```

### 6d) Meta-Cognition
```bash
python -c "
from engine.omega_meta_logic import MetaCognition
mc = MetaCognition('.')
rules = mc.analyze_failures()
print(f'Failure rules: {rules}')
"
```

### 6e) Self-Evaluation
```bash
python -c "
from engine.omega_self_eval import SelfEvaluation
se = SelfEvaluation('.')
report = se.generate_report()
print(report[:500])
"
```

---

## 7) SECURITY LAYER

### 7a) Vault — encrypt/decrypt round-trip
```bash
python -c "
from security.omega_vault import OmegaVault
v = OmegaVault('.')
enc = v.encrypt('read-only test payload')
dec = v.decrypt(enc)
print(f'Round-trip OK: {dec == \"read-only test payload\"}')
print(f'Encrypted size: {len(enc)} bytes')
"
```

### 7b) RBAC — access control
```bash
python -c "
from security.omega_access import OmegaAccess
a = OmegaAccess('.')
print(f'Roles: {a.list_roles()}')
result = a.check_access('developer', 'read')
print(f'Access result: {result}')
"
```

### 7c) Audit Trail
```bash
python -c "
from security.omega_audit import OmegaAudit
au = OmegaAudit('.')
au.log('reliability_test', 'read-only test', 'test-user')
events = au.query(limit=5)
print(f'Last {len(events)} audit events:')
for e in events:
    print(f'  {e}')
"
```

### 7d) Key Rotation
```bash
python -c "
from security.omega_rotate import KeyRotation
kr = KeyRotation('.')
status = kr.get_rotation_status()
print(f'Rotation status: {status}')
"
```

---

## 8) OBSERVABILITY

### 8a) Health Monitor
```bash
python -c "
from observability.health import HealthMonitor
hm = HealthMonitor()
report = hm.check_all()
print(f'Services: {len(report.components)}')
print(f'Overall: {\"PASS\" if report.healthy else \"FAIL\"}')
for c in report.components:
    print(f'  {c.name}: {c.status.name}')
"
```

### 8b) Circuit Breaker
```bash
python -c "
from observability.circuit_breaker import CircuitBreakerRegistry
cbr = CircuitBreakerRegistry()
print(f'Registered breakers: {cbr.list_breakers()}')
for name, breaker in cbr.list_breakers().items():
    print(f'  {name}: state={breaker.state.name}, failure_count={breaker.failure_count}')
"
```

### 8c) Metrics
```bash
# Check if Prometheus/OTLP metrics endpoint is live
curl -s -m 10 http://localhost:4317/ 2>&1 || echo "OTLP collector not reachable"
echo "---"
curl -s -m 10 http://localhost:6006/ 2>&1 | head -10 || echo "Phoenix not reachable"
echo "---"
curl -s -m 10 http://localhost:3100/ready 2>&1 || echo "Loki not reachable"
echo "---"
curl -s -m 10 http://localhost:3000/api/health 2>&1 || echo "Grafana not reachable"
```

---

## 9) PARALLEL EXECUTOR

```bash
python -c "
from engine.parallel_executor import ParallelExecutor
pe = ParallelExecutor(max_workers=4)
# Create a simple dependency graph
task_ids = []
for i in range(5):
    tid = pe.add_task(lambda x=i: x, name=f'task_{i}')
    task_ids.append(tid)
    if i > 0:
        pe.add_dependency(tid, task_ids[i-1])
results = pe.execute_all()
print(f'Tasks: {len(results)}')
for r in results:
    print(f'  {r.task.name}: status={r.status.name}, duration={r.duration_ms:.0f}ms')
"
```

---

## 10) FULL PIPELINE — run one simple goal

```bash
# Run a minimal goal through the Entrypoint (read-only mode — just spin up and verify init)
time python agentic-os.py --goal "print('hello world')" 2>&1 | tail -30

# Record:
# - Subsystem init success rate
# - Recursive Forge loop iterations
# - Code generation score
# - Total wall time
# - Any errors or failures
```

---

## 11) REPORT

### Table: Endpoint & Service Status

| # | Component | Endpoint | Port | Method | Latency | Pass/Fail | Note |
|---|-----------|----------|------|--------|---------|-----------|------|
| 1 | API Server | `/health` | 8080 | GET | | | |
| 2 | API Server | `/api/v1/executions` | 8080 | GET | | | |
| 3 | API Server | `/api/v1/execute` | 8080 | POST | | | |
| 4 | Dashboard | `/api/v1/status` | 8000 | GET | | | |
| 5 | Dashboard | `/api/state` | 5000 | GET | | | |
| 6 | Bridge | `/status` | 3001 | GET | | | |
| 7 | Bridge | `/health` | 3001 | GET | | | |
| 8 | Daemon | `/health` | 8765 | GET | | | |
| 9 | Daemon | `/tasks` | 8765 | GET | | | |
| 10 | Memory | `store/recall` | — | lib | | | |
| 11 | RAG | `ingest/query` | — | lib | | | |
| 12 | GAN | `generate` | — | lib | | | |
| 13 | Meta-Cognition | `analyze_failures` | — | lib | | | |
| 14 | Self-Eval | `generate_report` | — | lib | | | |
| 15 | Vault | `encrypt/decrypt` | — | lib | | | |
| 16 | RBAC | `check_access` | — | lib | | | |
| 17 | Audit | `log/query` | — | lib | | | |
| 18 | Health Monitor | `check_all` | — | lib | | | |
| 19 | Circuit Breaker | status | — | lib | | | |
| 20 | Parallel Executor | `execute_all` | — | lib | | | |
| 21 | Full Pipeline | `--goal` | — | CLI | | | |

### Summary Questions

- **Which LLM provider/model is configured?** (check `.env`, `PROJECT_NAME`, `LLM_PROVIDER`)
- **Is encryption enabled?** (`VAULT_ENABLED`, AES-256-GCM active?)
- **RBAC enforced?** (what roles exist, are endpoints protected?)
- **Any timeouts or errors?** (note every timeout/connection refusal/exception)
- **All subsystems initialized successfully?** (count vs expected)
- **Changes made?** Should be **NONE** — read-only. Verify with `git status` / `git diff`.
