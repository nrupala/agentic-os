# agentic-OS: Progressive Development Plan v2.0

> **Based on 10 complete iterations through:**
> - All 47 engine files in D:\agentic-OS (truth, not labels)
> - All Rust code in D:\guardian-mesh (compiled but 18 critical gaps vs spec)
> - All 4,500+ lines of Guardian_Mesh_API spec (0 lines of implementation)
> - All 47 repos across the D:\ drive ecosystem (18 newly discovered)
> - AetherisPro master index (13 tier-1 + ~34 tier-2 repos)
> - All Linux Foundation standards (SPDX, DCO, OpenChain, etc. — zero compliance)
> - All user requirements across this conversation (30 gap items identified)
> - 190 failure mode dimensions across 19 components (only ~11 covered)
>
> **Core principle:** This is not a rewrite. This is an integration of an existing 47-repo ecosystem into a self-sustaining, never-dying OS.

---

> **Quick Reference**
>
> | Metric | Value |
> |--------|-------|
> | **Total Duration** | 68 weeks (~16 months) |
> | **Total Phases** | 8 (Phase -1 through Phase 6) |
> | **Peak Team Size** | 4 people |
> | **Total New Code** | ~27,500 lines |
> | **Existing Code to Integrate** | ~50,000+ lines across 13 repos |
> | **Ecosystem Scope** | 47 repos across D:\ drive |

---

## Table of Contents

- [0. The Honest Starting Point](#0-the-honest-starting-point)
  - [What Already Exists That We Don't Rebuild](#what-already-exists-that-we-dont-rebuild)
  - [What We Actually Need to Build](#what-we-actually-need-to-build)
- [1. Phase Restructuring](#1-phase-restructuring)
  - [Phase -1: Ecosystem Integration & Compliance Foundation (Weeks 1-4)](#phase--1-ecosystem-integration--compliance-foundation-weeks-1-4)
  - [Phase 0: Guardian Mesh Spec → Reality (Weeks 5-16)](#phase-0-guardian-mesh-spec--reality-weeks-5-16)
  - [Phase 1: Integration Bridge (Weeks 17-24)](#phase-1-integration-bridge-weeks-17-24)
  - [Phase 2: Boot Chain + Persistence (Weeks 25-32)](#phase-2-boot-chain--persistence-weeks-25-32)
  - [Phase 3: Self-Hosting Loop (Weeks 33-40)](#phase-3-self-hosting-loop-weeks-33-40)
  - [Phase 4: OS Fundamentals (Weeks 41-52)](#phase-4-os-fundamentals-weeks-41-52)
  - [Phase 5: Formal Verification (Weeks 53-60)](#phase-5-formal-verification-weeks-53-60)
  - [Phase 6: Multi-Node — SL-3/SL-4 (Weeks 61-68)](#phase-6-multi-node--sl-3sl-4-weeks-61-68)
- [2. The Failure Mode Matrix](#2-the-failure-mode-matrix)
- [3. Updated Timeline](#3-updated-timeline)
- [4. What Changed from v1.0](#4-what-changed-from-v10)
- [5. Resource Requirements](#5-resource-requirements)
- [6. The Self-Sustaining End State](#6-the-self-sustaining-end-state)
- [7. The Risks (Updated)](#7-the-risks-updated)
- [8. Success Criteria](#8-success-criteria)
- [9. Visual Timeline](#9-visual-timeline)

---

## 0. The Honest Starting Point

### What Already Exists That We Don't Rebuild

| Capability | Where It Exists | Language | Maturity | What We Do |
|-----------|----------------|----------|----------|------------|
| **WASM sandbox** | `D:\argent` | Rust | Implemented | **Integrate** — don't rebuild |
| **Formal verification (NL → Lean 4 → code)** | `D:\axiomcode` | Python | Implemented | **Integrate** — wrap as gRPC service |
| **Production gateway (running on OCI)** | `D:\Aetheris` | Rust | Running | **Use as deployment target** |
| **Search (55+ providers)** | `D:\nexus` | Python | Code-complete | **Integrate** — connect via gRPC |
| **Multi-agent workflow** | `D:\LocalForge` | TypeScript | Implemented | **Integrate** — bridge protocol |
| **ZK vault CLI** | `D:\argent` + `D:\zerok` | Rust+Go | Implemented | **Integrate** — vault backend |
| **Encrypted file vault** | `D:\argent` (ChaCha20) + Aetheris (ZFS) | Rust | Implemented | **Integrate** |
| **OPA policy bridge** | `D:\Aetheris\src\connector.rs` | Rust | Deployed | **Use as policy engine** |
| **Write-ahead log / audit** | `D:\Aetheris\src\wal.rs` | Rust | Tested | **Use as audit backend** |
| **Agent orchestration** | `D:\LLMVM` | Python | Implemented | **Integrate** |
| **Analytics** | `D:\pae` | Python | Implemented | **Integrate** |
| **Personal cloud** | `D:\Aetheris` (OCI) + `D:\Aetheris_Nexus` | Rust+TS | Running+Designed | **Use as deployment target** |
| **Guardian Mesh formal spec** | `D:\Gurdian_Mesh_API` | Docs | 4,500+ lines | **Implement from spec** |

**Total code we don't need to write: ~50,000+ lines** across 13 repos.

### What We Actually Need to Build

| Component | Why Build | Est. Size |
|-----------|-----------|-----------|
| **Guardian Mesh implementation** (matches existing spec) | 4,500 lines of spec, zero code | ~8,000 lines Rust |
| **Integration bridge** (connect Omega Code → all existing repos) | They don't talk to each other | ~3,000 lines Rust+Python |
| **Boot chain** (TPM, Secure Boot, measured boot, LOCKDOWN) | Doesn't exist anywhere | ~2,000 lines Rust+config |
| **OS fundamentals** (energy, memory, scheduling, lifecycle, diagnostics, vitals, error management, persistence) | Distributed across repos, no unified interface | ~10,000 lines |
| **Builder worker framework** (meta-learning loop) | Doesn't exist anywhere | ~3,000 lines Python |
| **Container self-build** | Doesn't exist anywhere | ~1,000 lines |
| **Ground-up compliance** (SPDX, DCO, LICENSE, CODE_OF_CONDUCT, etc.) | Zero compliance across all 47 repos | ~500 lines docs+CI |

**Total new code: ~27,500 lines.** Not 300,000. We don't rebuild what exists.

---

## 1. Phase Restructuring

### Phase -1: Ecosystem Integration & Compliance Foundation (Weeks 1-4)

**Goal:** Map the ecosystem, establish licenses and governance, stop duplicating work.

| # | Task | What | Existing Asset |
|---|------|------|----------------|
| -1.1 | Map all 47 repos to capabilities | Read every README, Cargo.toml, pyproject.toml | AetherisPro INTEGRATION_MAP.md |
| -1.2 | Establish single LICENSE (MIT OR Apache-2.0) across all repos | Add LICENSE file, SPDX headers to every file | None currently |
| -1.3 | Add CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md to every repo | Governance baseline | None currently |
| -1.4 | Add DCO check to every repo CI | Developer Certificate of Origin | None currently |
| -1.5 | Vendor Rust toolchain + Python interpreter | Download + pin exact versions + checksum | External dependency today |
| -1.6 | Vendor ALL Python dependencies (PyPI → local) | `pip download` everything, store in repo | External dependency today |
| -1.7 | Vendor ALL Rust dependencies (crates.io → local) | `cargo vendor`, store in repo | External dependency today |
| -1.8 | Verify: builds work with zero internet access | Air-gapped build test | Can't today |
| -1.9 | Define SLOs for "never-dying" | Uptime, RTO, RPO targets | Undefined |
| -1.10 | Write failure mode matrix (19 components × 10 dimensions) | 190 cells, fill for all components | Only 11/190 covered |

**Deliverable:** All 47 repos have LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, DCO. Builds work without internet. SLOs defined. Failure matrix complete.

---

### Phase 0: Guardian Mesh Spec → Reality (Weeks 5-16)

**Goal:** Guardian Mesh implementation matches its own formal spec. Fix the 18 critical gaps.

| # | Task | Existing Spec | Current Code |
|---|------|---------------|--------------|
| 0.1 | Implement envelope wire format | Byte-level spec (magic 0x474D5348, version, CRC-32C, routing) | Custom serialization |
| 0.2 | Split enclaves into separate processes | 5 enclaves, no shared state, seccomp-BPF per process | Single-process shared mutable context |
| 0.3 | Implement Vault per spec | Key derivation, ML-DSA-65, capability tokens, TPM binding | File-based audit logger only |
| 0.4 | Implement Witness chain | Blake3 hash chain, Merkle tree, sequence numbers, external anchoring | Signs single hash |
| 0.5 | Implement Gatekeeper per spec | GMPL decision tree, deterministic, no dynamic dispatch | HMAC check only |
| 0.6 | Implement Sentinel as pure observer | Cannot block, generates observation reports | Blocks on PF failure |
| 0.7 | Implement Arbiter as conflict resolver | Pluggable backend, escalation from Sentinel+Gatekeeper | Makes policy decisions (wrong role) |
| 0.8 | Implement all 18 PF rules | PF-01 to PF-18 fully specified | Only 4/18 implemented |
| 0.9 | Replace SHA-256 with Blake3 | Spec mandates Blake3 everywhere | SHA-256 everywhere |
| 0.10 | Fix HMAC timing side-channel | Constant-time comparison | Naive `==` |
| 0.11 | Add key persistence | Vault keys sealed to TPM, survive restart | Generated fresh every restart |
| 0.12 | Fix timestamp units to spec milliseconds | u64 Unix epoch milliseconds | Mixed ns/s/ms |
| 0.13 | Implement 6-stage graduated containment | Detect→Warn→Throttle→Isolate→Analyze→Terminate | Stages defined, never used |
| 0.14 | Add GMPL compiler | PEG grammar → compiled decision tree | `Vec<PolicyRule>` only |
| 0.15 | Implement Handshake Bus protocol | 8-state machine (S0-S7), boot ordering enforcement | Create session + HMAC only |

**Integration points with existing ecosystem:**
- Use **Argent's ChaCha20Poly1305** for Vault encryption (not rebuild)
- Use **Aetheris' OPA connector** for policy backend (not rebuild)
- Use **Aetheris' WAL** for audit trail (not rebuild)
- Use **Zerok** for portable vault CLI (not rebuild)

**Deliverable:** Guardian Mesh matches its formal spec. 5 enclaves as separate processes. All 18 PF rules. Blake3. Constant-time crypto. Key persistence.

---

### Phase 1: Integration Bridge (Weeks 17-24)

**Goal:** All 13 tier-1 repos talk to each other through Guardian Mesh.

| # | Task | Connects | Protocol |
|---|------|----------|----------|
| 1.1 | gRPC bridge: Omega Code → Guardian Mesh | All engine operations call Evaluate() before executing | gRPC protobuf |
| 1.2 | gRPC bridge: Argent → Guardian Mesh | Argent's WASM sandbox gated by Guardian Mesh | gRPC protobuf |
| 1.3 | gRPC bridge: AxiomCode → Guardian Mesh | Formal verification pipeline gated | gRPC protobuf |
| 1.4 | gRPC bridge: Aetheris → Guardian Mesh | Production gateway checks Guardian Mesh | gRPC protobuf |
| 1.5 | gRPC bridge: Nexus → Guardian Mesh | Search queries gated | gRPC protobuf |
| 1.6 | gRPC bridge: LocalForge → Guardian Mesh | Agent actions gated | gRPC protobuf |
| 1.7 | KG → Sentinel feedback bridge | Omega Code writes Sentinel observations to KG (relay, Sentinel never writes directly) | gRPC |
| 1.8 | KG → Gatekeeper policy update bridge | Omega Code analyzes KG weekly, signs new policy, pushes to Guardian Mesh | gRPC |
| 1.9 | Aetheris WAL → Witness audit chain bridge | Aetheris operational logs feed into Witness | gRPC |
| 1.10 | Zerok → Vault bridge | Zerok vault CLI uses Guardian Mesh Vault as backend | gRPC |

**Deliverable:** All 13 tier-1 repos connected through Guardian Mesh. Every action gated. KG → policy feedback loop live.

---

### Phase 2: Boot Chain + Persistence (Weeks 25-32)

**Goal:** System survives reboot. Chain of trust from TPM to application.

| # | Task | Why This Exists in Ecosystem |
|---|------|------------------------------|
| 2.1 | UEFI Secure Boot enrollment | Use Aetheris' deployment scripts (OCI already has this) |
| 2.2 | TPM PCR measurement (PCR 4-9) | TPM chip in every modern system |
| 2.3 | Vault key sealing to PCR values | Use Argent's TPM integration code |
| 2.4 | LOCKDOWN mode | Guardian Mesh spec already defines this |
| 2.5 | Recovery key procedure | Use Zerok's recovery key infrastructure |
| 2.6 | Remote attestation | Use Aetheris' attestation endpoint |
| 2.7 | Kernel hardening (seccomp, Landlock, cgroups, KASLR, KPTI) | Use Aetheris' OCI deployment config |
| 2.8 | WAL for Knowledge Graph (sled) | Use Aetheris' WAL pattern |
| 2.9 | Snapshot scheduling (daily KG, weekly Witness checkpoint) | New code |
| 2.10 | Backup/restore CLI | Use Zerok's backup infrastructure |

**Deliverable:** Measured boot. Keys survive reboot. LOCKDOWN mode. Remote attestation. Crash recovery.

---

### Phase 3: Self-Hosting Loop (Weeks 33-40)

**Goal:** OS builds, signs, and deploys its own components. The meta-learning loop.

| # | Task | What It Does |
|---|------|--------------|
| 3.1 | Omega Code builds Guardian Mesh | Forge generates new enclave code → GAN scores → Vault signs → SelfEval verifies → Guardian Mesh loads |
| 3.2 | Omega Code builds Omega Code | Same pipeline, recursive |
| 3.3 | Bootstrap: Rust toolchain from source | OS downloads Rust source, compiles rustc, compiles all Rust components |
| 3.4 | Bootstrap: Python from source | OS compiles Python from source, verifies against pinned hash |
| 3.5 | Container self-build pipeline | OS assembles OCI container, signs digest, deploys |
| 3.6 | Boot chain self-extension | OS generates new kernel module → signs → TPM measures → reseals keys |
| 3.7 | **Builder worker framework** | Spawns worker for missing capability → worker analyzes → learns → builds → records in KG |
| 3.8 | Skill registry | Each challenge → skill → solution recorded. Reused on repeat |
| 3.9 | GAN replacement: use AxiomCode | Current GAN is a template matcher. Replace with AxiomCode's real formal verification for code scoring |

**Critical integration:**
- Replace the fake GAN (template matcher) with **AxiomCode** (real formal verification)
- Replace the fake RAG (keyword grep) with **Nexus** (55+ provider search)
- Use **Argent** as the builder worker sandbox (WASM isolation)
- Use **LocalForge** as the multi-agent workflow runner

**Deliverable:** OS builds itself. Builder worker framework live. Fake GAN/RAG replaced with real implementations from ecosystem.

---

### Phase 4: OS Fundamentals (Weeks 41-52)

**Goal:** Production-grade across all 8 dimensions.

| # | Task | Estimated Impact |
|---|------|------------------|
| 4.1 | Health probes (liveness + readiness + startup + deep) | Vitals: 20% → 85% |
| 4.2 | Graceful shutdown (SIGTERM handler, drain, flush, seal) | Lifecycle: 10% → 80% |
| 4.3 | Structured logging (JSON, shipping, retention) | Diagnostics: 15% → 75% |
| 4.4 | Prometheus metrics (counters, histograms, gauges) | Diagnostics: 15% → 75% |
| 4.5 | Memory monitoring (RSS, OOM score, swap pressure, ZRAM) | Memory: 25% → 75% |
| 4.6 | CPU/power management (frequency, governor, ACPI states) | Energy: 35% → 70% |
| 4.7 | Priority scheduling (cgroups, nice, deadline scheduling) | Scheduling: 30% → 70% |
| 4.8 | Crash recovery (3-miss restart, exponential backoff, max 5) | Lifecycle: 10% → 80% |
| 4.9 | Error management (severity, trending, correlation, recovery procedures) | Error Mgmt: 60% → 85% |
| 4.10 | Persistence (WAL, snapshots, backup/restore, retention policies) | Persistence: 10% → 80% |

**Deliverable:** All 8 fundamentals at 70%+ production readiness.

---

### Phase 5: Formal Verification (Weeks 53-60)

**Goal:** Gatekeeper policy evaluator formally verified in Lean 4.

| # | Task | Note |
|---|------|------|
| 5.1 | Lean 4 environment setup | External tool, must be vendored |
| 5.2 | Extract Gatekeeper to Lean | ~200 lines for decision tree evaluator |
| 5.3 | Prove P1-P6 (termination, totality, determinism, priority, completeness, fail-secure) | Achievable — simpler than seL4 |
| 5.4 | Bisimulation proof (Rust matches Lean) | Hardest part, most projects fail here |
| 5.5 | GMPL compiler verification | Without this, evaluator proof is meaningless |

**Integration:** Use **AxiomCode** (existing NL → Lean 4 pipeline) for the proof generation. Don't write Lean proofs by hand — generate them from AxiomCode.

---

### Phase 6: Multi-Node — SL-3/SL-4 (Weeks 61-68)

**Goal:** Distributed Guardian Mesh with Byzantine fault tolerance.

| # | Task |
|---|------|
| 6.1 | Consensus protocol implementation (PBFT or HotStuff) |
| 6.2 | Multi-node message protocol |
| 6.3 | SL-3: 2-of-3 crash fault tolerance |
| 6.4 | SL-4: 3-of-4 Byzantine fault tolerance |
| 6.5 | Network partition handling + rejoin reconciliation |

**Deliverable:** Multi-node Guardian Mesh. SL-3 and SL-4 operational.

---

## 2. The Failure Mode Matrix (All 19 Components)

The complete 190-cell matrix replaces the old 11-row table. Only the 11 crash scenarios are shown for space — all other dimensions must be filled during Phase -1.

| Component | Crash | Hang | Compromise | Storage | Dependency | Corrupt | Resource | Recovery | In Plan? | Test? |
|-----------|-------|------|------------|---------|------------|---------|----------|----------|----------|-------|
| **Protocol Firewall** | Phase 0.8 | New | **CRITICAL** | RAM only | Vault | New | New | New | Phase 0.8 | New |
| **Sentinel** | DEGRADED | New | **CRITICAL** | LOW | KG | New | New | KG snap | Phase 0.6 | New |
| **Gatekeeper** | FAIL-TO-BLOCK | New | **CRITICAL** | LOW | Vault | New | VERY LOW | Sealed store | Phase 0.5, 5 | New |
| **Witness** | DEGRADED | New | **CRITICAL** | **ENOSPC** | Sequencer | Partial | New | Resume+gap | Phase 0.4 | New |
| **Arbiter** | DEGRADED | New | **CRITICAL** | LOW | Backend | New | LOW | Restart | Phase 0.7 | New |
| **Vault** | LOCKDOWN | New | **CRITICAL** | LOW | TPM | **CRITICAL** | LOW | Restart | Phase 0.3 | New |
| **Handshake Bus** | SYSTEM HALT | New | **CRITICAL** | RAM only | Vault | New | New | HW reset | Phase 0.15 | New |
| **Omega Code** | DEGRADED | New | **CATASTROPHIC** | **HIGH** | Guardian Mesh | New | **HIGH** | GM restart | Phase 1.1 | New |
| **KG** | DEGRADED | New | **CATASTROPHIC** | **HIGH** | Omega+Seq | **HIGH** | MEDIUM | Snapshot | Phase 2.8 | New |
| **Orchestrator** | FROZEN | New | **CRITICAL** | LOW | GM | **HIGH** | LOW | HW reset | Phase 0.2 | New |
| **Sequencer** | DEGRADED | New | **HIGH** | LOW | NTP | MEDIUM | LOW | Last seq | Phase 0.12 | New |
| **Boot Loader** | Fallback | New | LOCKDOWN | MEDIUM | TPM | LOCKDOWN | LOW | Recovery key | Phase 2.1-2.7 | New |
| **TPM** | Passphrase | New | **CRITICAL** | **HIGH** | SPI bus | **CRITICAL** | **LONG TERM** | Recovery key | Phase 2.3 | New |
| **Argent (ZKP vault)** | Phase 1.2 | New | New | New | GM | New | New | New | Phase 1.2 | New |
| **AxiomCode (formal proof)** | Phase 1.3 | New | New | New | GM | New | New | New | Phase 1.3 | New |
| **Aetheris (gateway)** | Phase 1.4 | New | New | New | GM | New | New | New | Phase 1.4 | New |
| **Nexus (search)** | Phase 1.5 | New | New | New | GM | New | New | New | Phase 1.5 | New |
| **LocalForge (agents)** | Phase 1.6 | New | New | New | GM | New | New | New | Phase 1.6 | New |
| **PAE (analytics)** | Phase 1.7 | New | New | New | GM | New | New | New | Phase 1.7 | New |

**Cells marked "New" must be filled during Phase -1 before any Phase 0 implementation begins.**

---

## 3. Updated Timeline

```
Week  0: PHASE -1: Ecosystem Integration & Compliance Foundation
           Map all 47 repos | Add LICENSE/CONTRIBUTING/SECURITY to all | Vendor ALL dependencies
           Define SLOs | Write 190-cell failure matrix | Air-gapped build test
Week  4: 
          PHASE 0: Guardian Mesh Spec → Reality
            Split enclaves | Implement Vault/Witness/Gatekeeper/Sentinel/Arbiter per spec
            All 18 PF rules | Blake3 | Constant-time crypto | Key persistence
Week 16:
          PHASE 1: Integration Bridge
            Connect Omega Code + Argent + AxiomCode + Aetheris + Nexus + LocalForge
            All through Guardian Mesh gRPC | KG → policy feedback loop
Week 24:
          PHASE 2: Boot Chain + Persistence
            TPM measured boot | Key sealing | LOCKDOWN | WAL | Snapshots | Backup
Week 32:
          PHASE 3: Self-Hosting Loop
            OS builds Guardian Mesh | OS builds Omega Code | Builder worker framework
            Replace fake GAN with AxiomCode | Replace fake RAG with Nexus
Week 40:
          PHASE 4: OS Fundamentals
            Health probes | Shutdown handler | Logging | Metrics | Memory/CPU/Energy
            Scheduling | Crash recovery | Error management | Persistence
Week 52:
          PHASE 5: Formal Verification
            Gatekeeper evaluator in Lean 4 | Use AxiomCode for proof generation
Week 60:
          PHASE 6: Multi-Node (SL-3/SL-4)
            Consensus | BFT | Partition handling
Week 68:
          → SYSTEM IS SELF-SUSTAINING
            All 47 repos integrated. No external dependencies. Self-building.
            Guardian Mesh formally verified. Multi-node BFT. Failure-resistant.
```

---

## 4. What Changed from v1.0

| Change | v1.0 | v2.0 | Why |
|--------|------|------|-----|
| **Phases** | 8 | 7 (+ Phase -1) | Added compliance/ecosystem mapping before building |
| **Self-hosting** | Phase 7 (week 65) | Phase 3 (week 32) | 33 weeks earlier. Core innovation shouldn't wait 18 months. |
| **Ecosystem integration** | None | Phases -1, 1, 3 | Don't rebuild 10+ existing capabilities |
| **Failure mode engineering** | None | Phase -1 (190-cell matrix) | Build failures into design from day 1 |
| **Compliance** | "OS meets its own bar" | Phase -1 (SPDX, DCO, LICENSE) | Need legal baseline before open source |
| **Energy management** | Phase 4 (week 40) | Phase 4 (week 41) | Same week, but now uses ACPI + cgroups + existing kernel infrastructure |
| **Total timeline** | 72 weeks | 68 weeks | Faster because we integrate rather than rebuild |
| **New code estimate** | ~200,000 lines | ~27,500 lines | 86% less code by using existing ecosystem |
| **"Nothing external"** | Aspirational | Phase -1 (vendor everything) | First action is to eliminate external dependencies |
| **GAN/RAG replacement** | None | Phase 3.9 | Replace aspirational labels with real implementations from ecosystem |

---

## 5. Resource Requirements

| Phase | Duration | Rust | Python | Docs/Compliance | Total |
|-------|----------|------|--------|-----------------|-------|
| -1: Ecosystem Integration | 4 weeks | 1 | 1 | 1 | 3 |
| 0: Guardian Mesh Implementation | 12 weeks | 3 | 0 | 0 | 3 |
| 1: Integration Bridge | 8 weeks | 2 | 2 | 0 | 4 |
| 2: Boot Chain + Persistence | 8 weeks | 2 | 0 | 0 | 2 |
| 3: Self-Hosting Loop | 8 weeks | 1 | 2 | 0 | 3 |
| 4: OS Fundamentals | 12 weeks | 2 | 1 | 0 | 3 |
| 5: Formal Verification | 8 weeks | 0 (Lean) | 1 (AxiomCode) | 1 (Proof) | 2 |
| 6: Multi-Node | 8 weeks | 2 | 0 | 0 | 2 |

**Peak team: 4 people. Total duration: 68 weeks (~16 months).**

---

## 6. The Self-Sustaining End State

```
After Phase 6, the system:

1. Boots from TPM-measured chain (UEFI → bootloader → kernel → Guardian Mesh → Omega Code)
2. Guardian Mesh (5 enclaves, multi-node BFT) gates EVERY action through 18 PF rules
3. Omega Code (the builder) has ALL dependencies vendored — builds WITHOUT internet
4. When OS encounters missing capability:
   → Meta-learning detects gap
   → Builder worker spawned in Argent WASM sandbox
   → Worker analyzes → learns → generates code via Forge
   → AxiomCode formally verifies the generated code
   → Guardian Mesh gates deployment
   → Vault signs the new component
   → KG records the skill for next time
5. If internet is down: OS continues operating AND improving
6. If GitHub disappears: OS still builds from vendored sources
7. If crates.io goes away: OS has all Rust crates locally
8. If PyPI vanishes: OS has all Python packages locally
9. If the machine reboots: TPM seals survive, Vault keys persist, Witness chain persists
10. If a component crashes: Orchestrator detects → restarts → state recovered from WAL
11. If disk fills: Witness chain rotated, KG snapshot compressed, oldest data archived
12. If battery is low: system enters power-save mode, suspends non-essential workers
13. NEVER DIES: because every failure mode is identified, documented, tested, and mitigated
```

---

## 7. The Risks (Updated)

| Risk | Old Likelihood | New Likelihood | Mitigation |
|------|---------------|----------------|------------|
| **Rebuilding existing capability** | High | **Eliminated** | Phase -1 maps all 47 repos. We integrate, not rebuild. |
| **Formal verification takes 3x longer** | High | Reduced | Use AxiomCode for proof generation. Don't write Lean proofs by hand. |
| **Multi-process enclave adds 5-15ms latency** | Medium | **Still present** | Move fast-path to L1 cache. Gatekeeper decision tree is <50KB. |
| **TPM unavailable** | High | **Still present** | Passphrase + Argon2id fallback. But TPM is in every modern system. |
| **Dependency management (vendor everything)** | Not addressed | **New risk** | Vendoring 20,000+ Rust crates + Python packages is ~10GB. Storage cost, not architecture blocker. |
| **Ecosystem integration conflicts** | Not addressed | **New risk** | 13 repos, 5 languages, different coding styles. Phase -1 must establish consistent interfaces. |

---

## 8. Success Criteria

What "done" looks like at the end of each phase:

| Phase | Success Criteria |
|-------|-----------------|
| **-1: Ecosystem Integration** | All 47 repos have LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, DCO. All builds pass in air-gapped environment. SLOs defined and documented. 190-cell failure matrix fully populated. |
| **0: Guardian Mesh** | Implementation matches formal spec byte-for-byte. 5 enclaves as separate processes with seccomp-BPF. All 18 PF rules pass. Blake3 replaces SHA-256 everywhere. Constant-time crypto. Vault keys persist across reboot. |
| **1: Integration Bridge** | All 13 tier-1 repos communicate through Guardian Mesh gRPC. Every action gated by a PF rule. KG → policy feedback loop produces at least one verified end-to-end policy update. |
| **2: Boot Chain** | System survives any number of reboots with keys intact. TPM measured boot operational. LOCKDOWN mode prevents unauthorized code. Remote attestation verifiable. Crash recovery restores from WAL. |
| **3: Self-Hosting** | OS builds Guardian Mesh from source without internet. OS builds Omega Code from source without internet. Builder worker framework produces at least one new capability. Fake GAN replaced with AxiomCode. Fake RAG replaced with Nexus. |
| **4: OS Fundamentals** | All 8 fundamentals scored at 70%+ production readiness. Health probes pass. Graceful shutdown works under load. Metrics dashboards show real data. Crash recovery handles 3 consecutive failures. |
| **5: Formal Verification** | Gatekeeper policy evaluator formally verified in Lean 4. P1-P6 properties proven. Bisimulation proof passes: Rust matches Lean. GMPL compiler verified. |
| **6: Multi-Node** | Distributed Guardian Mesh with 3+ nodes. SL-3 (2-of-3 crash tolerance) operational. SL-4 (3-of-4 BFT) operational. Partition handling tested: rejoin reconciliation successful. |

---

## 9. Visual Timeline

```
Week  0 ┤ Phase -1: Ecosystem Integration & Compliance Foundation (4 weeks)
        ├── Map 47 repos │ Add LICENSE/DCO/CoC │ Vendor all deps │ SLOs │ Failure matrix
Week  4 ┤████████████████
        │
        ├ Phase 0: Guardian Mesh Spec → Reality (12 weeks)
        │   Split enclaves │ Vault/Witness/Gatekeeper │ 18 PF rules │ Blake3 │ Key persistence
Week 16 ┤████████████████████████████████████████
        │
        ├ Phase 1: Integration Bridge (8 weeks)
        │   gRPC bridges: Omega Code │ Argent │ AxiomCode │ Aetheris │ Nexus │ LocalForge
Week 24 ┤████████████████████████████
        │
        ├ Phase 2: Boot Chain + Persistence (8 weeks)
        │   TPM measured boot │ Key sealing │ LOCKDOWN │ WAL │ Snapshots │ Backup
Week 32 ┤████████████████████████████
        │
        ├ Phase 3: Self-Hosting Loop (8 weeks)
        │   OS builds itself │ Builder worker │ Replace fake GAN/RAG with real tools
Week 40 ┤████████████████████████████
        │
        ├ Phase 4: OS Fundamentals (12 weeks)
        │   Health │ Shutdown │ Logging │ Metrics │ Memory │ CPU/Energy │ Scheduling │ Recovery
Week 52 ┤████████████████████████████████████████
        │
        ├ Phase 5: Formal Verification (8 weeks)
        │   Lean 4 │ Gatekeeper proof │ P1-P6 │ Bisimulation │ GMPL compiler verification
Week 60 ┤████████████████████████████
        │
        ├ Phase 6: Multi-Node SL-3/SL-4 (8 weeks)
        │   Consensus │ BFT │ Partition handling │ Rejoin reconciliation
Week 68 ┤████████████████████████████
        │
        └──► SYSTEM IS SELF-SUSTAINING
             47 repos integrated │ No external deps │ Formally verified │ Failure-resistant
```
