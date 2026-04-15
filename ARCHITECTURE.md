# agentic-OS Architecture Diagrams

## System Overview

```mermaid
graph TB
    subgraph "agentic-OS Core"
        A[entrypoint.py]
        A --> B[AgenticOS Hub]
        B --> C[Recursive Forge Loop]
        B --> D[Memory System]
        B --> E[Cognitive Engine]
        B --> F[Security Layer]
    end
    
    subgraph "Recursive Forge Loop"
        C --> C1[1. RECOLLECT]
        C1 --> C2[2. THINK]
        C2 --> C3[3. GENERATE]
        C3 --> C4[4. VERIFY]
        C4 --> C5[5. PERSIST]
        C5 --> C6[6. EVALUATE]
        C6 --> C1
    end
    
    subgraph "Memory System (3-Tier)"
        D --> D1[SHORT: SESSION-STATE.md]
        D --> D2[MEDIUM: Daily Logs]
        D --> D3[LONG: MEMORY.md]
        D1 --> D4[WAL Protocol]
        D2 --> D4
        D3 --> D4
    end
    
    subgraph "Cognitive Engine"
        E --> E1[Meta-Cognition]
        E --> E2[RAG Retrieval]
        E --> E3[GAN Self-Correction]
        E1 --> E4[Failure Patterns]
        E2 --> E5[Semantic Index]
        E3 --> E6[Generator vs Discriminator]
    end
    
    subgraph "Security Layer"
        F --> F1[Vault AES-256-GCM]
        F --> F2[RBAC Access]
        F --> F3[Audit Trail]
        F --> F4[Email Alerts]
    end
    
    subgraph "Observability"
        G[Loki]
        H[Grafana Dashboard]
        I[Self-Evaluation Reports]
    end
    
    C6 --> G
    C6 --> H
    C6 --> I
```

## Recursive Loop Flow

```mermaid
flowchart LR
    subgraph Loop["Recursive Forge Loop"]
        direction TB
        A[RECOLLECT] --> B[THINK]
        B --> C[GENERATE]
        C --> D[VERIFY]
        D --> E{PASS?}
        E -->|Yes| F[PERSIST]
        E -->|No| G[Record Error]
        G --> A
        F --> H[EVALUATE]
        H --> A
    end
    
    A:Load state from SQLite
    A:Check memory context
    
    B:RAG retrieves memories
    B:Analyze patterns
    
    C:GAN generates code
    C:Discriminator scores
    
    D:Execute in Docker sandbox
    D:Check for errors
```

## GAN Self-Correction

```mermaid
flowchart TB
    Start([Goal]) --> Gen[Generator]
    
    Gen --> Code[Generate Code]
    Code --> Eval[Discriminator]
    Eval --> Score{Score >= 0.7?}
    
    Score -->|Yes| Pass[Passed]
    Score -->|No| Refine[Refine Code]
    Refine --> Code
    
    Eval --> Check1{Has Error Handling?}
    Eval --> Check2{Has Type Hints?}
    Eval --> Check3{Has Documentation?}
    Eval --> Check4{Code Length OK?}
    
    Check1 -->|No| Issues1[Add Error Handling]
    Check2 -->|No| Issues2[Add Type Hints]
    Check3 -->|No| Issues3[Add Documentation]
    Check4 -->|No| Issues4[Expand Code]
    
    Issues1 --> Refine
    Issues2 --> Refine
    Issues3 --> Refine
    Issues4 --> Refine
    
    Pass --> Success([Success])
```

## Memory Architecture

```mermaid
graph TB
    subgraph "Write Path (WAL)"
        W1[Tool Call] --> W2[Write to SHORT first]
        W2 --> W3[Append to MEDIUM]
        W3 --> W4[Distill to LONG]
    end
    
    subgraph "Read Path"
        R1[Query] --> R2[Search SHORT]
        R2 --> R3[Search MEDIUM]
        R3 --> R4[Search LONG]
        R4 --> R5[Rank & Return]
    end
    
    subgraph "Tiers"
        SHORT[SESSION-STATE.md<br/>Active context<br/>Wiped on session end]
        MEDIUM[self-eval-logs/<br/>YYYY-MM-DD.md<br/>7-day retention]
        LONG[MEMORY.md<br/>Distilled wisdom<br/>Forever]
    end
    
    W4 --> LONG
    R5 --> Results[Relevant Context]
```

## Cognitive Engine

```mermaid
flowchart TB
    subgraph Input["Goal Input"]
        G[Goal]
    end
    
    subgraph MetaCog["Meta-Cognition"]
        M1[Analyze Failures]
        M2[Derive Constraints]
        M3[Generate Prompt]
        M1 --> M2 --> M3
    end
    
    subgraph RAG["RAG Retrieval"]
        R1[Query Index]
        R2[TF-IDF Scoring]
        R3[Top-K Results]
        R1 --> R2 --> R3
    end
    
    subgraph GAN["GAN Self-Correction"]
        G1[Generator]
        D1[Discriminator]
        G1 --> |Code| D1
        D1 --> |Score| G1
    end
    
    G --> MetaCog
    G --> RAG
    R3 --> Context
    Context --> G3[Combined Prompt]
    MetaCog --> G3
    G3 --> GAN
```

## Security Architecture

```mermaid
flowchart TB
    subgraph Access["RBAC Access Control"]
        A1[ADMIN<br/>Full Access]
        A2[DEVELOPER<br/>Build & Test]
        A3[AUDITOR<br/>Read Only]
    end
    
    subgraph Vault["AES-256-GCM Vault"]
        V1[Generate Key]
        V2[Encrypt Data]
        V3[Store Nonce + Ciphertext]
        V4[Decrypt]
        V1 --> V2 --> V3 --> V4
    end
    
    subgraph Audit["Audit Trail"]
        AT1[Log Event]
        AT2[JSONL Format]
        AT3[Tamper-Evident]
        AT4[Query & Report]
        AT1 --> AT2 --> AT3 --> AT4
    end
    
    subgraph Alerts["Email Alerts"]
        AL1[Recursion Overload]
        AL2[Unauthorized Access]
        AL3[Memory Pressure]
        AL1 & AL2 & AL3 --> AL4[SMTP Send]
    end
    
    User --> Access
    Access --> Vault
    Access --> Audit
    Audit --> Alerts
```

## Docker Stack

```mermaid
graph TB
    subgraph Docker["docker-compose.yml"]
        subgraph Agent["omega-agent"]
            AG1[verify_env.py]
            AG2[check_deps.py]
            AG3[entrypoint.py]
            AG1 --> AG2 --> AG3
        end
        
        subgraph Loki["loki"]
            L1[Log Aggregation]
            L2[3100:3100]
        end
        
        subgraph Grafana["grafana"]
            G1[OMEGA Dashboard]
            G2[Recursion Panel]
            G3[Security Panel]
            G4[Audit Trail]
            G1 --> G2
            G1 --> G3
            G1 --> G4
        end
    end
    
    subgraph Networks["omega-sandbox (internal)"]
        Agent --> Loki
        Agent --> Grafana
    end
    
    Loki --> Grafana
```

## State Persistence

```mermaid
flowchart TB
    subgraph State["State Management"]
        S1[SQLite DB]
        S2[state_snapshot.json]
        S3[Git Commits]
    end
    
    subgraph Snapshots["Snapshots"]
        SN1[recursion_depth]
        SN2[current_branch]
        SN3[llm_status]
        SN4[failure_patterns]
        SN5[pending_tasks]
        SN1 & SN2 & SN3 & SN4 & SN5 --> S2
    end
    
    subgraph Recovery["Warm Recovery"]
        R1[Load Snapshot]
        R2[Compute Hash]
        R3[Detect Drift]
        R4[Resume from Checkpoint]
        R1 --> R2 --> R3 --> R4
    end
    
    S1 --> Recovery
    S3 --> Recovery
```

## User Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant AgenticOS
    participant Memory
    participant GAN
    participant Sandbox
    
    User->>CLI: python agentic-os.py --goal "Build API"
    CLI->>AgenticOS: Initialize
    AgenticOS->>Memory: Load Context
    Memory-->>AgenticOS: Context Loaded
    
    loop Recursive Loop (max 50)
        AgenticOS->>Memory: Retrieve Relevant
        Memory-->>AgenticOS: Memories
        AgenticOS->>GAN: Generate Code
        GAN-->>AgenticOS: Code + Score
        AgenticOS->>Sandbox: Verify
        Sandbox-->>AgenticOS: Result
        
        alt Success
            AgenticOS->>Memory: Remember Success
            AgenticOS-->>User: Done!
        else Failure
            AgenticOS->>Memory: Log Failure
            AgenticOS->>AgenticOS: Recurse
        end
    end
```

## Observability Flow

```mermaid
flowchart LR
    subgraph Collect["Log Collection"]
        L1[omega-agent logs]
        L2[System logs]
        L3[Audit logs]
    end
    
    subgraph Store["Storage"]
        LG[Loki]
        ES[Elasticsearch]
    end
    
    subgraph Query["Query & Analysis"]
        Q1[LogQL Queries]
        Q2[KQL Queries]
    end
    
    subgraph Visualize["Visualization"]
        V1[Grafana Dashboards]
        V2[Panels]
    end
    
    subgraph Alert["Alerting"]
        A1[Grafana Alerts]
        A2[SMTP Alerts]
    end
    
    L1 & L2 & L3 --> LG
    LG --> Q1
    Q1 --> V1
    V1 --> V2
    V1 --> A1
    A1 --> A2
```

## Meta-Cognition Pattern Analysis

```mermaid
flowchart TB
    subgraph Analysis["Failure Analysis"]
        F1[Query Failures]
        F2[Group by Type]
        F3[Count Occurrences]
        F4[Detect Patterns]
        F1 --> F2 --> F3 --> F4
    end
    
    subgraph Types["Error Types"]
        T1[import_error]
        T2[timeout]
        T3[permission]
        T4[syntax_error]
        T5[memory]
    end
    
    subgraph Derivation["Constraint Derivation"]
        D1[For import_error<br/>=> Check imports first]
        D2[For timeout<br/>=> Increase timeout]
        D3[For permission<br/>=> Check perms early]
        T1 --> D1
        T2 --> D2
        T3 --> D3
    end
    
    F4 --> Types
    Types --> Derivation
    Derivation --> Prompt[Disciplined Prompt]
```

## Complete System Data Flow

```mermaid
flowchart TB
    subgraph Input
        Goal[Goal / Task]
        Env[Environment Variables]
    end
    
    subgraph Processing
        Think[THINK<br/>RAG + Meta]
        Generate[GENERATE<br/>GAN]
        Verify[VERIFY<br/>Sandbox]
    end
    
    subgraph Storage
        SQLite[(SQLite<br/>forge_state)]
        Files[Filesystem<br/>Memory + Logs]
        Git[(Git<br/>Version Control)]
    end
    
    subgraph Output
        Code[Generated Code]
        Reports[Self-Eval Reports]
        Metrics[Grafana Metrics]
    end
    
    Input --> Think
    Think --> Generate
    Generate --> Verify
    
    Verify -->|Success| Code
    Code --> Reports
    Code --> Git
    
    Think --> SQLite
    Verify --> SQLite
    Verify --> Files
    
    Reports --> Metrics
    
    subgraph Loops
        Verify -->|Fail| Think
    end
```

## Self-Development Loop

```mermaid
flowchart TB
    subgraph Detect["Gap Detection"]
        G1[Query Failures]
        G2[Count >= 3]
        G3[Same Category?]
        G1 --> G2 --> G3
    end
    
    subgraph Resolve["Auto-Resolution"]
        R1{Error Type?}
        R2[Install Dependency]
        R3[Update Config]
        R4[Preload Module]
        G3 --> R1
        R1 -->|import_error| R2
        R1 -->|config_error| R3
        R1 -->|import_delay| R4
    end
    
    subgraph Update["System Update"]
        U1[Update check_deps.py]
        U2[Update MEMORY.md]
        U3[Log Resolution]
        R2 & R3 & R4 --> U1
        U1 --> U2 --> U3
    end
    
    subgraph Shadow["Shadow Agent"]
        S1[Background Loop]
        S2[Sleep 5 min]
        S3[Check Gaps]
        S1 --> S2 --> S3 --> S1
        S3 --> Detect
    end
```
