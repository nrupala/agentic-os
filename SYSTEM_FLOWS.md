# Agentic-OS System Flows

Complete flow diagrams showing request lifecycle, component interactions, and data paths.

---

## Table of Contents
1. [User Request Flow](#1-user-request-flow)
2. [Planning to Execution Bridge](#2-planning-to-execution-bridge)
3. [Recursive Loop Flow](#3-recursive-loop-flow)
4. [Cognitive Engine Flow](#4-cognitive-engine-flow)
5. [Memory & Knowledge Flow](#5-memory--knowledge-flow)
6. [Security & Access Flow](#6-security--access-flow)
7. [Observability Flow](#7-observability-flow)

---

## 1. User Request Flow

```mermaid
flowchart TD
    subgraph USER["USER INTERFACE LAYER"]
        CLI[CLI Input]
        API[API Request]
        CHAT[Chat Interface]
        WEB[Web Dashboard]
    end

    subgraph GATEWAY["GATEWAY / API"]
        AUTH[Authentication]
        PARSE[Request Parser]
        QUEUE[Task Queue]
    end

    subgraph PLANNING["PLANNING LAYER"]
        PLANNER[Paradise Planner]
        ANALYZER[Task Analyzer]
        MASTER_COG[Master Orchestrator]
        THINK[Meta-Cognition Think]
    end

    subgraph OMEGA["OMEGA EXECUTION LAYER"]
        BRIDGE[Plan→Omega Bridge]
        FORGE[Omega Forge]
        META[Meta-Cognition]
        GAN[GAN Self-Correction]
        RAG[RAG Retrieval]
    end

    subgraph MEMORY["MEMORY & KNOWLEDGE"]
        WORKING[Working Memory]
        EPISODIC[Episodes DB]
        SEMANTIC[Semantic KB]
        GRAPH[Knowledge Graph]
    end

    subgraph SECURITY["SECURITY LAYER"]
        VAULT[Secure Vault]
        RBAC[Access Control]
        AUDIT[Audit Trail]
    end

    subgraph OUTPUT["OUTPUT LAYER"]
        USER_VALIDATE[User Validation]
        ACCEPT[ACCEPT - Save]
        REFINE[REFINE - Iterate]
        REJECT[REJECT - Abort]
    end

    CLI --> AUTH
    API --> AUTH
    CHAT --> AUTH
    WEB --> AUTH
    
    AUTH --> PARSE
    PARSE --> QUEUE
    QUEUE --> PLANNER
    
    PLANNER --> ANALYZER
    ANALYZER --> MASTER_COG
    MASTER_COG --> THICK
    
    THINK --> BRIDGE
    BRIDGE --> FORGE
    
    FORGE --> META
    FORGE --> GAN
    FORGE --> RAG
    
    FORGE --> WORKING
    FORGE --> EPISODIC
    FORGE --> SEMANTIC
    
    FORGE --> VAULT
    FORGE --> RBAC
    FORGE --> AUDIT
    
    FORGE --> USER_VALIDATE
    USER_VALIDATE --> ACCEPT
    USER_VALIDATE --> REFINE
    USER_VALIDATE --> REJECT
    
    REFINE --> FORGE
    ACCEPT --> GRAPH
```

### Request Flow Description

| Step | Component | Description |
|------|-----------|-------------|
| 1 | User Input | User submits request via CLI/API/Chat |
| 2 | Authentication | Verify user identity and permissions |
| 3 | Request Parsing | Parse natural language into structured task |
| 4 | Task Queue | Queue task for async processing |
| 5 | Paradise Planner | Analyze codebase, detect patterns, generate plan |
| 6 | Master Orchestrator | Coordinate PDCA loops, orchestrate teams |
| 7 | Meta-Cognition | Think about the thinking, strategy selection |
| 8 | Plan→Omega Bridge | **CRITICAL: Convert plan to Omega execution context** |
| 9 | Omega Forge | Run recursive loop (RECOLLECT→RECTIFY→VERIFY→PERSIST) |
| 10 | User Validation | Present results for user acceptance |
| 11 | Finalize | Save to memory, graph, git |

---

## 2. Planning to Execution Bridge

```mermaid
flowchart LR
    subgraph PLANNING_SIDE["PLANNING SIDE"]
        P1[Paradise Planner]
        P2[Task Analyzer]
        P3[Master Orchestrator]
        P4[Generated Plan]
    end

    subgraph BRIDGE["THE BRIDGE"]
        direction TB
        B1[Parse Plan Phases]
        B2[Extract Constraints]
        B3[Map to Omega Context]
        B4[Create Execution State]
        B5[Wire Subsystems]
    end

    subgraph OMEGA_SIDE["OMEGA SIDE"]
        O1[OmegaForge]
        O2[Meta-Cognition]
        O3[GAN Generator]
        O4[RAG Retriever]
        O5[Hierarchical Memory]
    end

    P1 --> P2
    P2 --> P3
    P3 --> P4
    
    P4 --> B1
    B1 --> B2
    B2 --> B3
    B3 --> B4
    B4 --> B5
    
    B5 --> O1
    B5 --> O2
    B5 --> O3
    B5 --> O4
    B5 --> O5
```

### Bridge Data Contract

```mermaid
classDiagram
    class PlanContext {
        +str goal
        +str request_type
        +list steps
        +list files_to_create
        +list files_to_modify
        +dict constraints
        +list detected_patterns
    }
    
    class OmegaContext {
        +str goal
        +int max_iterations
        +list patterns
        +list constraints
        +str strategy
        +dict metadata
    }
    
    class StateSnapshot {
        +str iteration_id
        +str goal
        +str current_code
        +str last_error
        +str status
        +list decisions
    }
    
    PlanContext ..> OmegaContext : Bridge converts
    OmegaContext ..> StateSnapshot : Forge uses
```

### Bridge Handshake Protocol

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PLAN → OMEGA HANDSHAKE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PLANNING                          BRIDGE                      OMEGA  │
│  ───────                          ──────                      ─────  │
│                                                                      │
│  ┌─────────────┐                   ┌─────────────┐          ┌─────────────┐
│  │ Plan JSON   │                   │ Parse &     │          │ State       │
│  │ {           │ ───────────────► │ Transform   │ ───────► │ Snapshot    │
│  │   goal      │                   │ PlanContext │          │ {           │
│  │   steps     │                   │      ↓      │          │   iteration │
│  │   files     │                   │ OmegaContext│          │   goal      │
│  │   type      │                   │             │          │   code      │
│  │ }           │                   └─────────────┘          │   status   │
│  └─────────────┘                                             │ }          │
│                                                               └─────────────┘
│                                                                      │
│  ◄─── ACK with context_id ────►                            ◄─── Start ───►
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Recursive Loop Flow

```mermaid
flowchart TD
    START([Start]) --> RECOLLECT
    
    subgraph RECOLLECT["RECOLLECT Phase"]
        R1[Load from Working Memory]
        R2[Query Episodic DB]
        R3[Retrieve Semantic Knowledge]
        R4[Fetch from Knowledge Graph]
        R5[Combine Context]
    end
    
    RECOLLECT --> THINK
    
    subgraph THINK["THINK Phase"]
        T1[Meta-Cognition Analysis]
        T2[RAG Similarity Search]
        T3[Pattern Recognition]
        T4[Constraint Derivation]
        T5[Strategy Selection]
    end
    
    THINK --> GENERATE
    
    subgraph GENERATE["GENERATE Phase"]
        G1[GAN Generator Creates Code]
        G2[Discriminator Evaluates]
        G3{Score >= 0.7?}
        G4[Loop back to Generator]
    end
    
    GENERATE --> G3
    G3 -->|Yes| VERIFY
    G3 -->|No| G1
    
    THINK --> VERIFY
    
    subgraph VERIFY["VERIFY Phase"]
        V1[Docker Sandbox Check]
        V2[Unit Tests]
        V3[Security Scan]
        V4{Lint & Format}
        V5{All Checks Pass?}
    end
    
    VERIFY --> V5
    V5 -->|Yes| VALIDATE
    V5 -->|No| PERSIST_FAIL
    
    subgraph VALIDATE["USER VALIDATION"]
        V6[Present Results]
        V7[User Reviews Output]
        V8{ACCEPT?}
        V9{REFINE?}
        V10{REJECT?}
    end
    
    V5 --> V6
    V6 --> V7
    V7 --> V8
    
    subgraph PERSIST_FAIL["PERSIST (Failure Path)"]
        P1[Save Error State]
        P2[Record in Audit Trail]
        P3[Update Knowledge Graph]
    end
    
    V8 -->|Yes| ACCEPT
    V8 -->|No| V9
    V9 -->|Yes| REFINE_L
    V9 -->|No| REJECT
    
    ACCEPT[ACCEPT - Success] --> PERSIST_SUCCESS
    REJECT[REJECT - Abort] --> PERSIST_ABORT
    REFINE_L[REFINE - Iterate] --> RECOLLECT
    
    subgraph PERSIST_SUCCESS["PERSIST (Success Path)"]
        PS1[Save to Working Memory]
        PS2[Write to Episodes DB]
        PS3[Update Semantic KB]
        PS4[Commit to Git]
        PS5[Update Knowledge Graph]
        PS6[Send Notifications]
    end
    
    subgraph PERSIST_ABORT["PERSIST (Abort Path)"]
        PA1[Save Abort State]
        PA2[Log to Audit Trail]
        PA3[Notify User]
    end
    
    PERSIST_SUCCESS --> EVALUATE
    
    subgraph EVALUATE["EVALUATE Phase"]
        E1[Self-Evaluation Report]
        E2[Check Improvement Needed]
        E3{Lessons Learned?}
        E4[Update Patterns]
    end
    
    EVALUATE --> CHECK_DONE
    
    CHECK_DONE{Iteration < Max?}
    CHECK_DONE -->|Yes| RECOLLECT
    CHECK_DONE -->|No| MAX_IT
    
    MAX_IT[Max Iterations Reached] --> EXIT
    
    PERSIST_FAIL --> CHECK_DONE
    PERSIST_ABORT --> EXIT
    
    EXIT([Exit])
    
    ACCEPT --> EXIT
    REJECT --> EXIT
```

### Loop Termination Conditions

```mermaid
flowchart TD
    subgraph CONDITIONS["Termination Conditions"]
        C1["✓ ACCEPT - User approved output"]
        C2["✗ REJECT - User declined output"]
        C3["⏱ MAX_ITERATIONS - Hit iteration limit"]
        C4["😴 HIBERNATED - LLM unavailable"]
        C5["⏸ PAUSED - User timeout"]
        C6["🔒 SECURITY_BLOCKED - RBAC violation"]
        C7["💥 FATAL_ERROR - Unrecoverable error"]
    end
```

| Condition | Action | User Notification |
|-----------|--------|-------------------|
| ACCEPT | Save, commit, notify | "Goal achieved!" |
| REJECT | Abort, log reason | "Request cancelled" |
| MAX_ITERATIONS | Save state, pause | "Max attempts reached" |
| HIBERNATED | Save state, retry later | "LLM unavailable, retrying..." |
| PAUSED | Persist state | "Request paused" |
| SECURITY_BLOCKED | Block, audit | "Permission denied" |
| FATAL_ERROR | Rollback, alert | "Critical error occurred" |

---

## 4. Cognitive Engine Flow

```mermaid
flowchart TD
    subgraph INPUT["Cognitive Input"]
        USER_REQ[User Request]
        CONTEXT[Context Data]
        MEMORY[Memory State]
    end

    subgraph THINK["Meta-Cognition Think"]
        T1[Analyze Request Intent]
        T2[Assess Complexity]
        T3[Select Strategy]
        T4[Generate Prompt]
    end

    subgraph RETRIEVE["RAG Retrieval"]
        R1[Embed Query]
        R2[Vector Similarity Search]
        R3[Fetch Top-K Results]
        R4[Rerank Results]
        R5[Return Context]
    end

    subgraph GENERATE["GAN Self-Correction"]
        G1[Generator: Create Draft]
        G2[Discriminator: Evaluate]
        G3{Score >= Threshold?}
        G4[Record Pattern]
        G5[Return Refined Output]
    end

    subgraph LEARN["Continuous Learning"]
        L1[Success → Record Pattern]
        L2[Failure → Record Anti-Pattern]
        L3[Update Knowledge Graph]
        L4[Update RAG Index]
    end

    USER_REQ --> T1
    CONTEXT --> T1
    MEMORY --> T1
    
    T1 --> T2
    T2 --> T3
    T3 --> T4
    
    T4 --> R1
    R1 --> R2
    R2 --> R3
    R3 --> R4
    R4 --> R5
    
    T4 --> G1
    R5 --> G1
    
    G1 --> G2
    G2 --> G3
    
    G3 -->|Yes| G5
    G3 -->|No| G1
    
    G4 --> L1
    G2 --> L2
    
    L1 --> L3
    L2 --> L3
    L3 --> L4
    
    G5 --> OUTPUT[Final Output]
```

### GAN Self-Correction Loop

```mermaid
sequenceDiagram
    participant G as Generator
    participant D as Discriminator
    participant M as Memory
    participant KG as Knowledge Graph

    loop Until Score >= 0.7 or Max Iterations
        G->>G: Generate Code Draft
        G->>D: Submit Draft
        D->>D: Evaluate Against Criteria
        D->>D: Compute Quality Score
        
        alt Score >= 0.7
            D->>G: Accept Draft
            G->>M: Store Accepted Pattern
            G->>KG: Record Success
        else Score < 0.7
            D->>G: Reject with Feedback
            G->>G: Apply Corrections
            G->>KG: Record Attempt
        end
    end
```

---

## 5. Memory & Knowledge Flow

```mermaid
flowchart TD
    subgraph INGEST["Data Ingestion"]
        USER[User Input]
        CODE[Code Changes]
        RESULT[Execution Results]
        ERROR[Errors/Warnings]
    end

    subgraph TIERS["3-Tier Memory Architecture"]
        subgraph WORKING["Tier 1: Working Memory"]
            WM1[Current Session State]
            WM2[Active Context]
            WM3[Immediate Decisions]
        end
        
        subgraph EPISODIC["Tier 2: Episodic Memory"]
            EM1[Session Records]
            EM2[Task Histories]
            EM3[Decision Chains]
        end
        
        subgraph SEMANTIC["Tier 3: Semantic Memory"]
            SM1[Patterns Library]
            SM2[Code Snippets]
            SM3[Best Practices]
        end
    end

    subgraph GRAPH["Knowledge Graph"]
        KG1[Concepts]
        KG2[Relationships]
        KG3[Success Patterns]
        KG4[Failure Patterns]
    end

    subgraph WAL["WAL Protocol"]
        W1[Write-Ahead Log]
        W2[Checkpoint]
        W3[Recovery]
    end

    INGEST --> TIERS
    USER --> WM1
    CODE --> WM2
    RESULT --> WM3
    ERROR --> EM1
    
    WM1 --> EM1
    WM2 --> EM2
    WM3 --> EM3
    
    EM1 --> SM1
    EM2 --> SM2
    EM3 --> SM3
    
    SM1 --> KG1
    SM2 --> KG2
    SM3 --> KG3
    
    KG1 --> KG4
    
    TIERS --> WAL
    WAL --> GRAPH
```

### Knowledge Graph Entity Relationships

```mermaid
erDiagram
    CONCEPT ||--o{ PATTERN : learns_from
    CONCEPT ||--o{ CODE_SNIPPET : stored_as
    PATTERN ||--o{ TASK : used_in
    TASK ||--o{ DECISION : generates
    DECISION ||--|| SUCCESS : outcomes_in
    DECISION ||--|| FAILURE : outcomes_in
    CODE_SNIPPET ||--o{ SUCCESS : helps_achieve
    CODE_SNIPPET ||--o{ FAILURE : contributes_to
```

---

## 6. Security & Access Flow

```mermaid
flowchart TD
    subgraph REQUEST["Incoming Request"]
        REQ[User Request]
        AUTH[Auth Token]
        ROLE[User Role]
    end

    subgraph RBAC["RBAC Access Control"]
        R1[Check Permissions]
        R2{Role Allowed?}
        R3[Check Resource Access]
        R4{Resource Permitted?}
    end

    subgraph VAULT["Secure Vault"]
        V1[Encrypt Data]
        V2[Store Secrets]
        V3[Key Rotation]
        V4[AES-256-GCM]
    end

    subgraph AUDIT["Audit Trail"]
        A1[Log All Actions]
        A2[Track Changes]
        A3[Immutable Log]
        A4[Grafana Dashboard]
    end

    subgraph ALERT["Alert System"]
        AL1[Security Events]
        AL2[Email Notifications]
        AL3[Slack/Webhook]
    end

    REQ --> AUTH
    AUTH --> ROLE
    ROLE --> R1
    
    R1 --> R2
    R2 -->|Yes| R3
    R2 -->|No| DENY[DENY ACCESS]
    
    R3 --> R4
    R4 -->|Yes| PROCEED[Proceed]
    R4 -->|No| DENY
    
    PROCEED --> V1
    V1 --> V2
    V2 --> V4
    
    PROCEED --> A1
    A1 --> A2
    A2 --> A3
    A3 --> A4
    
    DENY --> AL1
    V1 --> AL1
    A1 --> AL1
    AL1 --> AL2
    AL1 --> AL3
```

---

## 7. Observability Flow

```mermaid
flowchart TD
    subgraph COLLECTION["Metrics Collection"]
        METRICS[Application Metrics]
        LOGS[Structured Logs]
        TRACES[Distributed Traces]
    end

    subgraph PROCESSING["Processing Layer"]
        PM[Prometheus Metrics]
        PL[Loki Log Aggregation]
        PT[Jaeger/Grafana Tempo]
    end

    subgraph STORAGE["Storage"]
        TS[Time-Series DB]
        LS[Log Database]
    end

    subgraph VISUALIZATION["Visualization"]
        GRAFANA[Grafana Dashboards]
        ALERTING[Alert Manager]
    end

    subgraph FEEDBACK["Feedback Loop"]
        FB[Performance Tuning]
        FB2[Error Detection]
        FB3[Capacity Planning]
    end

    COLLECTION --> PROCESSING
    METRICS --> PM
    LOGS --> PL
    TRACES --> PT
    
    PM --> TS
    PL --> LS
    PT --> TS
    
    TS --> GRAFANA
    LS --> GRAFANA
    
    GRAFANA --> ALERTING
    ALERTING --> FB
    FB --> COLLECTION
    
    FB2 --> FB
    FB3 --> FB
```

---

## Summary: Complete System Architecture

```mermaid
flowchart TB
    subgraph CLIENT["CLIENT LAYER"]
        CLI[CLI]
        API[REST API]
        UI[Web UI]
    end

    subgraph GATEWAY["API GATEWAY"]
        LB[Load Balancer]
        AUTH[Auth Service]
        RATE[Rate Limiter]
    end

    subgraph PLANNING["PARADISE PLANNING"]
        PLANNER[Paradise Planner]
        ANALYZER[Task Analyzer]
        MASTER[Master Orchestrator]
    end

    subgraph BRIDGE["PLAN→OMEGA BRIDGE"]
        PARSE[Plan Parser]
        TRANSFORM[Context Transformer]
        STATE[State Factory]
    end

    subgraph OMEGA["OMEGA-CODE EXECUTION"]
        FORGE[Omega Forge]
        META[Meta-Cognition]
        GAN[GAN Self-Correction]
        RAG[RAG Retrieval]
    end

    subgraph MEMORY["HIERARCHICAL MEMORY"]
        WORKING[Working Memory]
        EPISODIC[Episodic DB]
        SEMANTIC[Semantic KB]
        GRAPH[Knowledge Graph]
    end

    subgraph SECURITY["SECURITY"]
        VAULT[Secure Vault]
        RBAC[RBAC]
        AUDIT[Audit Trail]
    end

    subgraph OBS["OBSERVABILITY"]
        PROMETHEUS[Prometheus]
        LOKI[Loki]
        GRAFANA[Grafana]
    end

    CLIENT --> LB
    LB --> AUTH
    AUTH --> RATE
    RATE --> PLANNER
    
    PLANNER --> ANALYZER
    ANALYZER --> MASTER
    
    MASTER --> BRIDGE
    BRIDGE --> OMEGA
    
    OMEGA --> MEMORY
    OMEGA --> SECURITY
    
    MEMORY --> GRAPH
    GRAPH --> OBS
    
    SECURITY --> AUDIT
    AUDIT --> OBS
    
    OBS --> GRAFANA
```

---

## Next: Component Handshakes

See [COMPONENT_HANDSHAKES.md](COMPONENT_HANDSHAKES.md) for detailed protocol specifications.
