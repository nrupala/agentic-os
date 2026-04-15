# agentic-OS User Request Flow

## End-to-End Request Lifecycle

### 1. User Input Entry Points

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CLI:           python agentic-os.py --goal "Build a REST API"  │
│                                                                  │
│  API:           POST /execute { goal: "...", constraints: [...]}
│                                                                  │
│  Interactive:   python agentic-os.py --chat                    │
│                                                                  │
│  Webhook:       POST /webhook { trigger: "deploy", goal: "..." }│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Complete Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     USER SUBMITS REQUEST                                 │
│                     Goal: "Build a REST API"                            │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: REQUEST PARSING                                             │
│  • Parse goal, constraints, context                                    │
│  • Create request_id (UUID)                                            │
│  • Set iteration = 0                                                    │
│  • Load user preferences from memory                                     │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  PHASE 2: RECOLLECT                                                   │
│                                                                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │ Load from       │    │ Load from       │    │ Load from       │ │
│  │ SQLite          │    │ Memory          │    │ Git             │ │
│  │                 │    │                 │    │                 │ │
│  │ • forge_state  │    │ • SESSION.md    │    │ • Last commit   │ │
│  │ • failures     │    │ • MEMORY.md     │    │ • Branch state  │ │
│  │ • history      │    │ • Daily logs    │    │                 │ │
│  └────────┬────────┘    └────────┬────────┘    └─────────────────┘ │
│           └────────────────────────┼──────────────────────────────────┘│
│                                    │                                     │
└────────────────────────────────────┼─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  PHASE 3: THINK                                                        │
│                                                                          │
│  3.1 RAG Retrieval                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Query: "Build a REST API"                                       │   │
│  │  → Search MEMORY.md (TF-IDF)                                      │   │
│  │  → Search SESSION-STATE.md                                       │   │
│  │  → Return Top-K relevant memories                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  3.2 Meta-Cognition Analysis                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Query failures table (last 7 days)                              │   │
│  │  → Group by error_type                                           │   │
│  │  → If count >= 3: CAPABILITY GAP DETECTED                       │   │
│  │  → Derive constraints for each pattern                             │   │
│  │  Example: import_error → "Check imports before execution"         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  3.3 Build Disciplined Prompt                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  "You are NOT a chatbot. You are OMEGA..."                       │   │
│  │  + RAG retrieved context                                        │   │
│  │  + Derived constraints                                          │   │
│  │  + Previous failure patterns                                     │   │
│  │  + "No Quitting" mandate                                       │   │
│  │  = Strict JSON SPI with thought_process, rectified_code, tests    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  PHASE 4: GENERATE (GAN Self-Correction)                            │
│                                                                          │
│                              ┌──────────────┐                        │
│                              │   GENERATOR   │                        │
│                              │              │                        │
│                              │ Creates code │                        │
│                              │ based on     │                        │
│                              │ prompt       │                        │
│                              └──────┬───────┘                        │
│                                     │                                │
│                                     ▼                                │
│                              ┌──────────────┐                        │
│                              │ DISCRIMINATOR │                        │
│                              │              │                        │
│                              │ Evaluates:   │                        │
│                              │ • Error      │                        │
│                              │   handling   │                        │
│                              │ • Type hints │                        │
│                              │ • Docs       │                        │
│                              │ • Length     │                        │
│                              └──────┬───────┘                        │
│                                     │                                │
│                              Score >= 0.7?                           │
│                                     │                                │
│                    ┌────────────────┼────────────────┐             │
│                   [YES]              │            [NO]               │
│                    │                  │              │                │
│                    ▼                  │              ▼                │
│               PASSED                  │         REFINE               │
│                                     │              │                │
│                                     │              ▼                │
│                                     │    ┌──────────────┐           │
│                                     │    │ Fix issues  │           │
│                                     │    │ Loop back   │           │
│                                     │    └──────┬───────┘           │
│                                     │           └───────────────────┘ │
│                                     │                                 │
└─────────────────────────────────────┼─────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  PHASE 5: VERIFY (Sandbox)                                          │
│                                                                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐│
│  │ Docker Sandbox  │    │ Syntax Check   │    │ Unit Tests     ││
│  │                 │    │                 │    │                 ││
│  │ • Isolated     │    │ • Parse errors │    │ • Run pytest  ││
│  │ • Memory limit │    │ • Import check │    │ • Assertions  ││
│  │ • Network none │    │ • Type check   │    │ • Coverage    ││
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘│
│           └─────────────────────────┴─────────────────────────┘│
│                                    │                                   │
│                                    ▼                                   │
│                           ┌────────────────┐                          │
│                           │    RESULT       │                          │
│                           │                │                          │
│                           │ SUCCESS?       │                          │
│                           │ • Return 0     │                          │
│                           │ • No exceptions│                          │
│                           │ • Tests pass   │                          │
│                           └───────┬────────┘                          │
│                                   │                                  │
│                   ┌───────────────┴───────────────┐               │
│                  [YES]                            [NO]               │
│                   │                                │                │
└───────────────────┼────────────────────────────────┼────────────────┘
                    │                                │
                    ▼                                ▼
┌──────────────────────────────┐    ┌──────────────────────────────────────┐
│  PHASE 6a: PERSIST          │    │  PHASE 6b: RECORD FAILURE           │
│                              │    │                                      │
│  1. Save to SQLite         │    │  1. Log to failures table           │
│  2. Update Memory (WAL)     │    │  2. Update state_snapshot.json       │
│  3. Git commit (atomic)     │    │  3. Increment attempt counter         │
│  4. Update snapshot         │    │  4. Return to RECOLLECT              │
│  5. Continue to VALIDATION  │    │     (increment iteration)            │
└──────────────────────────────┘    └──────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  PHASE 7: USER VALIDATION                                             │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      GENERATED OUTPUT                              │   │
│  │                                                                   │   │
│  │   # Generated REST API                                             │   │
│  │   @app.route('/api/users', methods=['GET', 'POST'])              │   │
│  │   def users():                                                     │   │
│  │       ...                                                          │   │
│  │                                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │   [ACCEPT]  │    │   [REFINE]   │    │     [REJECT]       │   │
│  │              │    │              │    │                      │   │
│  │ I approve   │    │ Make changes │    │ Abort everything    │   │
│  │ this output │    │ based on     │    │                      │   │
│  │              │    │ feedback    │    │                      │   │
│  └──────────────┘    └──────────────┘    └──────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
                    │
          ┌─────────┼─────────┐
          │         │         │
        [ACCEPT] [REFINE] [REJECT]
          │         │         │
          ▼         ▼         ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   END: SUCCESS  │  │  LOOP AGAIN     │  │   END: REJECTED  │
│                 │  │                 │  │                 │
│ 1. Record      │  │ 1. Add user    │  │ 1. Record       │
│    validation   │  │    feedback     │  │    rejection    │
│ 2. Final Git    │  │ 2. Back to    │  │ 2. Clean up    │
│    commit       │  │    THINK      │  │ 3. Stop loop   │
│ 3. Send alert   │  │ 3. New output │  │                 │
│ 4. Return       │  │ 4. VALIDATION │  │                 │
│    SUCCESS      │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## Validation & Termination

### USER VALIDATION OPTIONS

| Option | Action | Loop Behavior |
|--------|--------|---------------|
| **[ACCEPT]** | User approves output | **LOOP ENDS - SUCCESS** |
| **[REFINE]** | User requests changes | Loop continues with feedback |
| **[REJECT]** | User aborts | **LOOP ENDS - REJECTED** |

### WHEN DOES THE PROCESS END?

The recursive loop terminates when ANY of these conditions are met:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         TERMINATION CONDITIONS                            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. USER ACCEPTS                                                       │
│     ┌──────────────────────────────────────────────────────────────┐    │
│     │  User clicks [ACCEPT]                                        │    │
│     │  → Validation recorded in SQLite                              │    │
│     │  → Final Git commit (prod branch)                           │    │
│     │  → Success alert sent (if configured)                        │    │
│     │  → Clean up temporary files                                  │    │
│     │  → Return: { status: "success", code: "..." }              │    │
│     └──────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  2. USER REJECTS                                                      │
│     ┌──────────────────────────────────────────────────────────────┐    │
│     │  User clicks [REJECT]                                        │    │
│     │  → Rejection logged                                         │    │
│     │  → State cleaned up                                        │    │
│     │  → Return: { status: "rejected" }                          │    │
│     └──────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  3. MAX ITERATIONS REACHED                                            │
│     ┌──────────────────────────────────────────────────────────────┐    │
│     │  iteration >= MAX_ATTEMPTS (default: 50)                    │    │
│     │  → Recursion overload alert                                 │    │
│     │  → Best effort saved (partial code)                         │    │
│     │  → Return: { status: "max_iterations", code: "..." }      │    │
│     └──────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  4. LLM UNAVAILABLE (Hibernation)                                     │
│     ┌──────────────────────────────────────────────────────────────┐    │
│     │  MAX_RETRIES exhausted for LLM calls                       │    │
│     │  → State serialized to hibernate.json                       │    │
│     │  → Git commit with HIBERNATE status                       │    │
│     │  → Wait for LLM availability                              │    │
│     │  → Resume from saved state when LLM returns               │    │
│     │  → Return: { status: "hibernated", resumable: true }    │    │
│     └──────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  5. USER TIMEOUT                                                      │
│     ┌──────────────────────────────────────────────────────────────┐    │
│     │  No user response for 30 minutes                           │    │
│     │  → State preserved                                         │    │
│     │  → Resume token generated                                  │    │
│     │  → Return: { status: "paused", resumable: true }         │    │
│     └──────────────────────────────────────────────────────────────┘    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Decision Flow Summary

```
                    ┌─────────────────────┐
                    │  User Submits      │
                    │  Goal Request       │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  LOOP STARTS        │
                    │  (iteration = 1)    │
                    └──────────┬──────────┘
                               │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
        ┌───────────┐   ┌───────────┐   ┌───────────┐
        │ RECOLLECT │   │   THINK   │   │ GENERATE │
        │  state    │──▶│  RAG +    │──▶│  GAN     │
        │           │   │  Meta cog  │   │  self-corr│
        └───────────┘   └───────────┘   └─────┬─────┘
                                               │
                          ┌──────────────────┘
                          ▼
                    ┌───────────┐
                    │  VERIFY   │
                    │  sandbox  │
                    └─────┬─────┘
                          │
              ┌───────────┴───────────┐
              │                       │
           [PASS]                  [FAIL]
              │                       │
              ▼                       ▼
        ┌───────────┐         ┌───────────┐
        │  USER     │         │  Record   │
        │VALIDATION │         │  failure  │
        └─────┬─────┘         │  increment │
              │               │  iterate  │
        ┌─────┼─────┐         └─────┬─────┘
        │     │     │               │
    [ACCEPT][REFINE][REJECT]        │
        │     │     │         ┌────▼────┐
        │     │     │         │iter >= N?│
        ▼     ▼     ▼         └────┬────┘
     ┌────┐┌─────┐┌─────┐        │     │
     │END││LOOP ││ END │       [YES] [NO]
     │SUCC││AGAIN││REJEC│        │     │
     └────┘└─────┘└─────┘        ▼     ▼
                                   END  LOOP
                                   MAX  AGAIN
```

---

## Final Output Structure

When the process ends, the system returns:

```json
{
  "status": "success" | "rejected" | "max_iterations" | "hibernated",
  "request_id": "uuid-xxx",
  "goal": "Build a REST API",
  "iterations": 12,
  
  "code": "# Generated code here...",
  
  "validation": {
    "user_accepted": true,
    "validated_at": "2026-04-15T10:30:00Z"
  },
  
  "artifacts": [
    "projects/default/src/generated_api.py",
    "projects/default/src/tests.py",
    "projects/default/outputs/docs.md"
  ],
  
  "git": {
    "branch": "prod-2026-04-15_10-30-00",
    "commit": "abc123def"
  },
  
  "metrics": {
    "gan_score": 0.85,
    "verify_passed": true,
    "total_time_seconds": 45.2
  }
}
```

---

## Side Effects (Persisted Data)

After each iteration:
- **SQLite**: `forge_state`, `forge_history`, `failures` tables updated
- **Memory**: `SESSION-STATE.md` (WAL), `MEMORY.md` (distilled)
- **Git**: Atomic commit with branch strategy
- **Audit**: JSONL log entry appended

On successful completion:
- **Self-Evaluation Report**: Markdown report in `self-eval-logs/`
- **Success Alert**: Email sent (if SMTP configured)
- **Git**: Production branch created
