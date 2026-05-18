# agentic-OS Architecture (Text Diagram)

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           agentic-OS Core                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│    ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐    │
│    │    Memory    │     │  Cognitive   │     │    Security      │    │
│    │    System   │     │    Engine    │     │      Layer       │    │
│    │   (3-tier)  │     │  (Meta+GAN)  │     │  (Vault+RBAC)  │    │
│    └──────────────┘     └──────────────┘     └──────────────────┘    │
│                                                                         │
│    ┌──────────────────────────────────────────────────────────────┐    │
│    │              Recursive Forge Loop                            │    │
│    │                                                              │    │
│    │   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │    │
│    │   │RECOLLECT│ -> │  THINK  │ -> │GENERATE │ -> │ VERIFY  │ │    │
│    │   └─────────┘    └─────────┘    └─────────┘    └─────────┘ │    │
│    │       ▲                                                      │    │
│    │       │         ┌─────────┐    ┌─────────┐                  │    │
│    │       └──────── │ PERSIST │ <- │EVALUATE │                   │    │
│    │                 └─────────┘    └─────────┘                   │    │
│    └──────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## GAN Self-Correction Loop

```
    ┌─────────────┐
    │  Generator  │
    │  Creates    │
    │  Code       │
    └──────┬──────┘
           │
           v
    ┌─────────────┐
    │Discriminator│
    │  Evaluates  │
    │   Quality   │
    └──────┬──────┘
           │
    ┌──────┴──────┐
    │  Score >=   │
    │    0.7?     │
    └──────┬──────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
  [YES]        [NO]
     │           │
     ▼           ▼
  [PASS]    [REFINE]
               │
               ▼
          Back to
         Generator
```

## Memory Architecture

```
┌─────────────────────────────────────────┐
│  TIER 1: SHORT-TERM (SESSION-STATE.md) │
│  - Active working context                │
│  - Current iteration state               │
│  - WAL: Write before next tool call     │
└────────────────────┬────────────────────┘
                     │
                     v
┌─────────────────────────────────────────┐
│  TIER 2: MEDIUM-TERM (self-eval-logs/) │
│  - Daily episodic logs                  │
│  - 7-day retention                     │
│  - YYYY-MM-DD.md format                │
└────────────────────┬────────────────────┘
                     │
                     v
┌─────────────────────────────────────────┐
│  TIER 3: LONG-TERM (MEMORY.md)          │
│  - Distilled wisdom                     │
│  - Persists forever                    │
│  - RAG-indexed for retrieval           │
└─────────────────────────────────────────┘
```

## Recursive Loop Flow

```
┌────────────────────────────────────────────────────────┐
│                    RECURSIVE LOOP                        │
│                    (max 50 iterations)                   │
└────────────────────────────────────────────────────────┘
                         │
                         v
    ┌───────────────────────────────────────────────┐
    │ 1. RECOLLECT                                  │
    │    - Load state from SQLite                   │
    │    - Check pending tasks                      │
    └───────────────────────────────────────────────┘
                         │
                         v
    ┌───────────────────────────────────────────────┐
    │ 2. THINK                                      │
    │    - RAG retrieves relevant memories           │
    │    - Meta-cognition analyzes patterns          │
    │    - Generate disciplined prompt               │
    └───────────────────────────────────────────────┘
                         │
                         v
    ┌───────────────────────────────────────────────┐
    │ 3. GENERATE                                   │
    │    - GAN Generator creates code                │
    │    - Discriminator evaluates quality           │
    │    - Loop until passed or max iterations       │
    └───────────────────────────────────────────────┘
                         │
                         v
    ┌───────────────────────────────────────────────┐
    │ 4. VERIFY                                      │
    │    - Execute in Docker sandbox                │
    │    - Check for errors                         │
    └───────────────────────────────────────────────┘
                         │
                         v
              ┌──────────────────┐
              │     PASS?          │
              └────────┬───────────┘
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
           [YES]             [NO]
              │                 │
              ▼                 ▼
    ┌─────────────────┐  ┌─────────────────┐
    │ 5. PERSIST       │  │ Record failure   │
    │ - Save to SQLite │  │ Log error       │
    │ - Update memory  │  │ Return to top    │
    │ - Git commit     │  │ (next iter)     │
    └─────────────────┘  └─────────────────┘
              │
              v
    ┌─────────────────┐
    │ 6. EVALUATE      │
    │ - Self-assessment│
    │ - Distill lessons│
    │ - Send alerts    │
    └─────────────────┘
              │
              └──────────> BACK TO TOP
```

## Docker Stack

```
┌─────────────────────────────────────────────────────────────┐
│              docker-compose.yml                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐                                           │
│  │omega-agent │                                           │
│  ├─────────────┤      ┌─────────┐      ┌─────────┐        │
│  │verify_env  │      │  loki   │      │ grafana │        │
│  │check_deps  │ ───> │         │ ───> │         │        │
│  │entrypoint  │      │ 3100    │      │  3000   │        │
│  └──────┬──────┘      └─────────┘      └─────────┘        │
│         │                                                        │
│  ┌──────┴──────────────────────────────────────────────┐     │
│  │              omega-sandbox (internal network)         │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layer                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │   Vault (AES)    │  │      RBAC        │              │
│  │  ┌────────────┐  │  │  ┌────────────┐  │              │
│  │  │ AES-256   │  │  │  │   ADMIN   │  │              │
│  │  │   GCM     │  │  │  │ DEVELOPER │  │              │
│  │  └────────────┘  │  │  │  AUDITOR  │  │              │
│  │                  │  │  └────────────┘  │              │
│  │  - Encrypt data  │  │  - Verify perms  │              │
│  │  - Store nonce │  │  - JIT access    │              │
│  │  - CSPRNG keys │  │  - Encrypted creds│              │
│  └──────────────────┘  └──────────────────┘              │
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │                   Audit Trail                     │     │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐           │     │
│  │  │  Login  │ │  Action │ │ Key Rot │           │     │
│  │  └────┬────┘ └────┬────┘ └────┬────┘           │     │
│  │       └───────────┴───────────┘                  │     │
│  │                     v                            │     │
│  │              JSONL Append-Only                   │     │
│  └──────────────────────────────────────────────────┘     │
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │                   Alerts                           │     │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐   │     │
│  │  │ Recursion  │ │Unauthorized │ │  Memory    │   │     │
│  │  │  Overload │ │   Access    │ │  Pressure  │   │     │
│  │  └────────────┘ └────────────┘ └────────────┘   │     │
│  └──────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Observability Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                 Observability Stack                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐    │
│  │   Logs     │ --> │    Loki    │ --> │  Grafana   │    │
│  │            │     │             │     │             │    │
│  │ - agent    │     │ - Aggregates│     │ - Dashboard │    │
│  │ - system   │     │ - Queries   │     │ - Panels   │    │
│  │ - audit    │     │ - Retention │     │ - Alerts   │    │
│  └─────────────┘     └─────────────┘     └──────┬──────┘    │
│                                                 │           │
│                                                 v           │
│                                        ┌─────────────┐    │
│                                        │   Panels    │    │
│                                        ├─────────────┤    │
│                                        │ Recursion   │    │
│                                        │ Efficiency  │    │
│                                        │ Security    │    │
│                                        │ Alerts      │    │
│                                        │ Audit Trail │    │
│                                        └─────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Meta-Cognition Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   Meta-Cognition Engine                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Failure Pattern Analysis                 │   │
│  │                                                      │   │
│  │   Query SQLite (last 7 days)                         │   │
│  │          │                                           │   │
│  │          v                                           │   │
│  │   Group by error_type                               │   │
│  │          │                                           │   │
│  │          v                                           │   │
│  │   Count occurrences                                 │   │
│  │          │                                           │   │
│  │          v                                           │   │
│  │   If count >= 3: CAPABILITY GAP DETECTED             │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                            v                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Constraint Derivation                   │   │
│  │                                                      │   │
│  │   import_error   -> Check imports first               │   │
│  │   timeout       -> Increase timeout values           │   │
│  │   permission    -> Check perms early                │   │
│  │   syntax_error  -> Validate syntax before run        │   │
│  │   memory        -> Monitor memory usage              │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                            v                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Disciplined Prompt Generation              │   │
│  │                                                      │   │
│  │   "You are NOT a chatbot. You are OMEGA..."        │   │
│  │   + Constraints from analysis                        │   │
│  │   + Previous failure patterns                        │   │
│  │   + "No Quitting" mandate                           │   │
│  │   = Strict JSON SPI output                           │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
agentic-OS/
│
├── agentic-os.py              # Unified entry point
├── quickstart.py             # Demo script
├── entrypoint.py             # Full loop
│
├── engine/
│   ├── omega_forge.py        # Core recursive engine
│   ├── omega_meta_logic.py   # Meta-cognition
│   ├── omega_gan.py          # GAN self-correction
│   ├── omega_rag.py          # RAG retrieval
│   ├── omega_hierarchical_memory.py  # 3-tier memory
│   ├── omega_self_eval.py    # Self-evaluation
│   ├── omega_vacuum.py       # Log cleanup
│   ├── omega_integrator.py    # Integration hub
│   └── omega_self_develop.py # Capability gaps
│
├── docker/
│   ├── Dockerfile.omega       # Hardened container
│   ├── docker-compose.yml    # Full stack
│   └── omega_engine.sh       # Never-quit loop
│
├── security/
│   ├── omega_vault.py       # AES-256-GCM
│   ├── omega_access.py       # RBAC
│   ├── omega_audit.py        # Audit trail
│   ├── omega_seed_gen.py     # Recovery seed
│   ├── omega_rotate.py      # Key rotation
│   └── omega_mail.py         # SMTP alerts
│
├── observability/
│   ├── loki-config.yaml      # Loki config
│   └── grafana/
│       ├── OMEGA-Master-Dashboard.json
│       └── provisioning/
│
└── system_scripts/
    ├── omega-guardian.service  # Systemd
    └── users.json             # RBAC users
```
