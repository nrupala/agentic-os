# agentic-OS: Complete Architecture v3.1

> **Date:** 2026-06-03
> **Status:** Architecture — integrates all existing components
> **Core principle:** Nothing external. Every component built, verified, and signed by the OS itself.

---

## 1. The Four Existing Components

| # | Component | Path | Language | What It Is | Status |
|---|-----------|------|----------|-----------|--------|
| **C1** | **Linux Kernel** | Upstream (kernel.org) | C | Hardware abstraction. Process scheduler. Memory manager. Device drivers. TCP/IP stack. Filesystems. | Upstream — we use, not replace |
| **C2** | **Guardian Mesh** | `D:\guardian-mesh\` | Rust | 5-enclave guardian daemon. Protocol Firewall (18 rules). ML-DSA-65 crypto. Handshake Bus. Sealed Envelope IPC. | Partially built — core daemon compiles, enclave logic in progress |
| **C3** | **Guardian_Mesh_API** | `D:\Gurdian_Mesh_API\` | Spec + Protobuf | Architecture spec, formal spec, threat model (1,524 lines), gap analysis (995 lines), landscape analysis. | Complete spec — implementation drives from it |
| **C4** | **Omega Code** | `D:\agentic-OS\engine\` | Python | Builder, verifier, signer, improver. 47 engine modules, 7 security modules, 200+ tests. | Running — all tests pass |

---

## 2. Layer Diagram (Definitive)

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                                                                    │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │                        APPLICATIONS & AGENTS                                 │  │
│  │  User CLIs | Dashboards | WASM Agent Sandbox | Audio/Visio/Network LMs      │  │
│  │  Every agent is a WASM module built by Omega Code, signed by Omega Vault,   │  │
│  │  and loaded only after Guardian Mesh verifies its capability request.        │  │
│  └────────────────────────────────┬───────────────────────────────────────────┘  │
│                                   │                                               │
│                                   ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │                         OMEGA CODE (The Builder)                            │  │
│  │  Language: Python. Acts as the build/verify/improve daemon.                  │  │
│  │                                                                              │  │
│  │  ┌───────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │  │
│  │  │ FORGE     │ │ GAN       │ │ VAULT    │ │ AUDIT    │ │ SELF-EVAL    │   │  │
│  │  │ (generates│ │(discrimina│ │(signs,   │ │(hash-    │ │(verifies,    │   │  │
│  │  │  code)    │ │ tes code) │ │ encrypts) │ │ chain )  │ │  reports)    │   │  │
│  │  └─────┬─────┘ └─────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘   │  │
│  │        │             │            │            │              │            │  │
│  │  ┌─────┴─────────────┴────────────┴────────────┴──────────────┴───────┐   │  │
│  │  │  Every action is GATED by Guardian Mesh before it executes.         │   │  │
│  │  │  Forge generates → Mesh checks → Vault signs → SelfEval verifies   │   │  │
│  │  └────────────────────────────────────────────────────────────────────┘   │  │
│  └────────────────────────────────┬───────────────────────────────────────────┘  │
│                                   │                                               │
│                                   ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │                     GUARDIAN MESH (The Guardian)                            │  │
│  │  Language: Rust. Pure gRPC service. 5 enclaves, no god process.            │  │
│  │                                                                              │  │
│  │  Every request from Omega Code or any agent must pass through:              │  │
│  │                                                                              │  │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │  │
│  │  │SENTINEL   │   │GATEKEEPER│   │ WITNESS  │   │ ARBITER  │   │ VAULT    │ │  │
│  │  │(Observes) │──►│(Enforces)│──►│ (Audits) │──►│ (Decides)│──►│(Secrets) │ │  │
│  │  │           │   │          │   │          │   │          │   │          │ │  │
│  │  │anomaly    │   │policy    │   │ML-DSA-65 │   │conflict  │   │no-export │ │  │
│  │  │detection  │   │evaluation│   │chain     │   │resolution│   │key store │ │  │
│  │  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘ │  │
│  │        │              │              │              │              │        │  │
│  │        └──────────────┴──────────────┴──────────────┴──────────────┘        │  │
│  │                     No single component has full visibility                 │  │
│  │                                                                              │  │
│  │  ┌────────────────────────────────────────────────────────────────────┐    │  │
│  │  │  PROTOCOL FIREWALL (PF-01 to PF-18) — validates ALL incoming msgs   │    │  │
│  │  │  Envelope structure | CRC32C | ML-DSA sig | Timestamp | Nonce      │    │  │
│  │  │  Source auth | Handshake | Action type | Length | Path traversal   │    │  │
│  │  │  Blocklist | Rate limit | Deny list | Enclave health | Containment │    │  │
│  │  │  Audit trail → 18 rules, every message checked before any enclave   │    │  │
│  │  └────────────────────────────────────────────────────────────────────┘    │  │
│  │                                                                              │  │
│  │  ┌────────────────────────────────────────────────────────────────────┐    │  │
│  │  │  HANDSHAKE BUS — abstract unix sockets, HMAC + ML-KEM, dumb pipe    │    │  │
│  │  └────────────────────────────────────────────────────────────────────┘    │  │
│  └────────────────────────────────┬───────────────────────────────────────────┘  │
│                                   │                                               │
│                                   ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │                     GUARDIAN_MESH_API (The Contract)                        │  │
│  │  Location: D:\Gurdian_Mesh_API\                                              │  │
│  │  Defines:                                                                   │  │
│  │  - Wire-level envelope format (magic 0x474D5348, version 0x0200)            │  │
│  │  - 17 message types (EvaluateRequest → HealthResponse)                     │  │
│  │  - 7 routing rules (R1-R7: who can talk to whom)                          │  │
│  │  - 6 hardening rules (H1-H6: validate-before-parse, min subset, etc.)      │  │
│  │  - 6-stage graduated containment (Detect→Warn→Throttle→Isolate→Analyze→   │  │
│  │    Terminate)                                                               │  │
│  │  - 4 deployment security levels (SL-1 Standard → SL-4 Byzantine)          │  │
│  │  - Formal verification target: Gatekeeper in Lean 4                        │  │
│  │  - Threat model covering 30+ attack vectors (V-C1 to V-AI11)              │  │
│  │  - Global gap analysis against 40+ security vendors                        │  │
│  └────────────────────────────────┬───────────────────────────────────────────┘  │
│                                   │                                               │
│                                   ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │                      KNOWLEDGE GRAPH (The Control Plane)                    │  │
│  │  Built by: omega_hierarchical_memory (3-tier WAL protocol)                  │  │
│  │  Data: user preferences, habits, routines, patterns, skill levels           │  │
│  │  Feeds into:                                                                │  │
│  │  │ → Guardian Mesh Sentinel: "this behavior is normal for this user"        │  │
│  │  │ → Guardian Mesh Gatekeeper: "user has expert-level skills, relax cap"   │  │
│  │  │ → Omega Code MetaLearner: "user prefers strategy X for Y-type tasks"    │  │
│  │  │ → Scheduler: "user always compiles at 2pm, pre-warm resources"          │  │
│  └────────────────────────────────┬───────────────────────────────────────────┘  │
│                                   │                                               │
│                                   ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │                        LINUX KERNEL (The Foundation)                        │  │
│  │  We use, we do not replace:                                                 │  │
│  │  - Process scheduler (CFS) → we add guardian hooks via seccomp BPF         │  │
│  │  - Memory manager → we add guardian oversight via cgroups                  │  │
│  │  - Device drivers → we wrap with Guardian Mesh Evaluate() call             │  │
│  │  - TCP/IP stack → we guard via netfilter hooks                            │  │
│  │  - Filesystems (ext4, btrfs) → we guard via Landlock LSM                  │  │
│  │  - Namespaces + cgroups → we use for agent isolation                       │  │
│  │  - seccomp BPF → we use as the kernel-level guardian gate                  │  │
│  │  - TPM → we use for measured boot + key sealing                           │  │
│  │  - IOMMU → we use for device DMA isolation                                 │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                    │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. How Components Talk to Each Other

### 3.1 Protocol Stack

```
Omega Code (Python) ───gRPC (via Guardian_Mesh_API protobuf)───► Guardian Mesh (Rust)
                                    │
                           Protocol Firewall (18 rules)
                           Sentinel → Gatekeeper → Witness → Arbiter → Vault
                                    │
                           Sealed Envelope (ML-DSA-65 signed)
                           Handshake Bus (abstract unix socket)
                                    │
                           Linux Kernel (seccomp BPF enforcement)
```

### 3.2 The Five API Calls

The Guardian Mesh exposes exactly 3 gRPC endpoints (per the formal spec). The Omega Code calls all 3:

| Call | From | To | Purpose | When |
|------|------|----|---------|------|
| `Evaluate` | Omega Code / any agent | Guardian Mesh | "Can I perform this action?" | Before every operation |
| `VerifyProof` | Omega Code | Guardian Mesh | "Is this audit proof valid?" | During self-evaluation |
| `Health` | Omega Code | Guardian Mesh | "Are all enclaves alive?" | Every heartbeat interval |

Plus 2 internal calls (unix socket only, not exposed to agents):

| Call | From | To | Purpose |
|------|------|----|---------|
| `DeriveToken` | Any enclave | Vault | "Give me a one-time derived credential" |
| `AuditQuery` | Witness (external) | Witness | "Retrieve proof for past decision" |

### 3.3 Omega Code → Guardian Mesh (The Integration Contract)

When Omega Code wants to do anything (generate code, run tests, modify files), it MUST call Evaluate first:

```protobuf
// Omega Code asks Guardian Mesh: "May I generate code for module X?"
EvaluateRequest {
  action = ActionDescriptor {
    action_type = ACTION_CODE_EXECUTE
    context_hash = Blake3("generate kernel module for NVMe guardian")
    capability = <one-time token from Vault>
    nonce = <random 16 bytes>
    timestamp = <monotonic ms>
    risk_score = <Sentinel's assessment, 0 if first time>
  }
  nonce = <random 16 bytes>
  timestamp = <monotonic ms>
  sender_sig = <ML-DSA-65 signed>
}

// Guardian Mesh responds:
EvaluateResponse {
  verdict = { type: ALLOW | BLOCK | THROTTLE | ESCALATE }
  reason_hash = <Blake3 of reason string>
  gatekeeper_sig = <ML-DSA-65 signed>
}
```

If the verdict is BLOCK, Omega Code does NOT perform the action. Instead, it:
1. Records the block in the Knowledge Graph
2. Logs the block reason in omega_audit
3. If the pattern repeats, omega_meta_learner adjusts its strategy

If ALLOW, Omega Code proceeds. After completion:
1. Records the outcome in the Knowledge Graph
2. If failure, omega_error_classifier categorizes it
3. omega_godel_machine may propose a fix for next time

### 3.4 Knowledge Graph → Guardian Mesh (Preference Feedback)

The Knowledge Graph feeds into the Guardian Mesh at two points:

```
KG → Sentinel: "User John always does X at time Y. This is normal, not anomalous."
    → Gatekeeper: "User John has expert skill level. Reduce throttle on complex ops."
    → Arbiter: "User John has never been escalated. Allow with conditions."
```

This is the **adaptive guardian** pattern — the guardian doesn't just block, it learns the user's patterns and adjusts its strictness accordingly. But the Gatekeeper remains deterministic (no ML). The adjustment comes through **compiled policy profiles** that Omega Code generates based on KG analysis:

1. Omega Code analyzes KG weekly
2. Omega Code generates updated policy rules: "user is expert → allow CODE_EXECUTE with fewer restrictions"
3. Omega Code signs the new policy with omega_vault
4. Omega Code sends the policy update to Guardian Mesh via Evaluate
5. Guardian Mesh loads the new policy on next restart

---

## 4. Boot Chain (Startup Sequence)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          BOOT SEQUENCE                                        │
│                                                                               │
│  STEP 1: LINUX KERNEL BOOTS                                                   │
│  ├── BIOS/UEFI → bootloader → kernel init                                    │
│  ├── Kernel mounts rootfs                                                     │
│  └── Kernel starts init process                                              │
│                                                                               │
│  STEP 2: GUARDIAN MESH STARTS (init process)                                  │
│  ├── Guardian Mesh daemon starts as PID 1                                    │
│  ├── Protocol Firewall initializes (18 rules loaded from sealed policy store) │
│  ├── Vault enclave starts:                                                    │
│  │     - If TPM available: unseal master key                                 │
│  │     - If no TPM: prompt for passphrase → Argon2id KDF                     │
│  │     - Generate ML-DSA-65 keypair                                          │
│  │     - Ready to issue derived tokens                                       │
│  ├── Gatekeeper enclave starts:                                               │
│  │     - Load compiled policy decision tree (from sealed store)              │
│  │     - Policy is immutable at runtime — no dynamic loading                 │
│  ├── Sentinel enclave starts:                                                 │
│  │     - Load baseline behavioral model from KG snapshot                     │
│  │     - Begin observing system activity                                     │
│  ├── Witness enclave starts:                                                  │
│  │     - Load last audit chain hash from external anchor                     │
│  │     - Begin accepting AuditProof messages                                 │
│  ├── Arbiter enclave starts:                                                  │
│  │     - Load pluggable backend (default: RuleArbiter — deterministic)       │
│  │     - No action needed until escalation                                   │
│  ├── Handshake Bus initialized                                                │
│  │     - Abstract unix sockets created                                       │
│  │     - All 5 enclaves connected to bus                                     │
│  │     - Bus begins routing messages                                         │
│  └── gRPC server starts: Evaluate, VerifyProof, Health endpoints             │
│                                                                               │
│  STEP 3: OMEGA CODE STARTS                                                    │
│  ├── Omega Code process launched by Guardian Mesh (fork + exec)               │
│  ├── Before any operation, Omega Code calls Guardian Mesh Health()           │
│  ├── If Health returns OK, Omega Code proceeds                                │
│  ├── Omega Code loads Knowledge Graph from disk                               │
│  │     - Ephemeral tier: last session state                                  │
│  │     - Short-term tier: last 24h patterns                                  │
│  │     - Long-term tier: user preferences, skill levels, routines            │
│  ├── Omega Code calls Guardian Mesh Evaluate() to check startup permissions  │
│  └── READY                                                                   │
│                                                                               │
│  STEP 4: SYSTEM READY                                                         │
│  ├── Guardian Mesh: listening on gRPC, 5 enclaves running                     │
│  ├── Omega Code: loaded, ready to build/verify/improve                        │
│  ├── Knowledge Graph: loaded, feeding into Guardian Mesh through Omega Code   │
│  └── User can interact → every action goes through Guardian Mesh first        │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. What to Build Next (Priority Order)

### Phase 1: Guardian Mesh Completeness (weeks 1-8)

The Guardian Mesh daemon exists (`guardian-meshd`) but the 5 individual enclave modules (sentinel, gatekeeper, witness, arbiter, vault) need their logic implemented. The spec is complete in Guardian_Mesh_API.

| Task | File | What to Build |
|------|------|---------------|
| **Vault enclave** | `src/enclave/vault.rs` | Key generation, derived token issuance, signature verification, no-export policy. Spec: Formal Spec §1.3. |
| **Gatekeeper enclave** | `src/enclave/gatekeeper.rs` | Policy decision tree evaluation, deterministic rule matching. Spec: Formal Spec §1.3, Architecture §3.2. |
| **Sentinel enclave** | `src/enclave/sentinel.rs` | Anomaly detection, behavioral observation, risk scoring. Spec: Formal Spec §1.3. |
| **Witness enclave** | `src/enclave/witness.rs` | Blake3 hash chain, Merkle tree, external anchoring. Spec: Formal Spec §1.3. |
| **Arbiter enclave** | `src/enclave/arbiter.rs` | Conflict resolution, pluggable backend interface. Spec: Formal Spec §1.3. |
| **Handshake Bus** | `src/handshake_bus.rs` | (Exists) — verify against Formal Spec §1.1 (envelope format, routing tags, direction constraints R1-R7) |
| **Protocol Firewall** | `src/protocol_firewall.rs` | (Exists with 18 rules) — verify against Formal Spec §1.1 (CRC32C, ML-DSA, timestamp, nonce checks) |

### Phase 2: Omega Code → Guardian Mesh Integration (weeks 9-12)

| Task | What to Build |
|------|---------------|
| **gRPC client in Omega Code** | Python gRPC client that calls Guardian Mesh Evaluate/VerifyProof/Health |
| **Action gating in Forge** | Every `omega_forge` operation calls Evaluate first. If blocked, logs to KG + audit. |
| **Action gating in GAN** | Every `omega_gan` generate/critique calls Evaluate first. |
| **Action gating in Shell** | Every `omega_shell_tools` command execution calls Evaluate first. |
| **Action gating in Vault** | `omega_vault` encrypt/sign calls Evaluate first. |
| **KG → Guardian feedback loop** | Omega Code analyzes KG weekly, generates updated policy profiles, signs with vault, pushes to Guardian Mesh. |

### Phase 3: Self-Hosting Loop (weeks 13-16)

| Task | What to Build |
|------|---------------|
| **WASM agent sandbox** | Omega Code generates Rust WASM agent, Guardian Mesh gates every agent action |
| **Guardian Mesh self-build** | Omega Code generates new Guardian Mesh enclave code, compiles it, tests it, signs it, deploys it |
| **Container self-build** | Omega Code builds the deployment container using omega_forge |
| **Omega Code provenance** | Every omega_code version is signed by omega_vault, verified by Guardian Mesh Witness |

---

## 6. The Never-Dying Loop

```
         ┌────────────────────────────────────────────────────────────┐
         │                    THE INFINITE LOOP                         │
         │                                                              │
         │  1. User acts → Guardian Mesh evaluates → ALLOW or BLOCK     │
         │  2. If ALLOW: Omega Code performs the action                 │
         │  3. Omega Code records outcome in Knowledge Graph             │
         │  4. Omega Code checks: "did the action succeed?"              │
         │     ├── Yes → record success pattern                         │
         │     └── No → omega_error_classifier categorizes              │
         │              → omega_meta_learner adjusts strategy            │
         │              → omega_godel_machine proposes fix               │
         │  5. Guardian Mesh Sentinel detects anomalies                  │
         │  6. Guardian Mesh Gatekeeper enforces policy                  │
         │  7. Guardian Mesh Witness records everything in audit chain   │
         │  8. Omega Code self-evaluates weekly                         │
         │  9. Omega Code improves its own code                         │
         │     ├── omega_forge generates new version                    │
         │     ├── omega_gan scores the generated code                  │
         │     ├── omega_vault signs it                                 │
         │     └── omega_self_eval verifies it                          │
         │  10. GOTO 1 — the system never stops improving               │
         │                                                              │
         │  No external CI. No external signing. No external registry.  │
         │  No external dependency that, if removed, the OS dies.       │
         └──────────────────────────────────────────────────────────────┘
```
