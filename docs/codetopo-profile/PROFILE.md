# Codetopo Profile — agentic-os (nrupala/agentic-os)

**What this is.** The agent-facing map of this repository, generated with
Codetopo 0.9.1 (local engine) — topology, trust boundaries, money
surface — with the graph snapshot beside it (`snapshot.json`,
`stats.json`) as the measured evidence.

- **Repo:** nrupala/agentic-os (private)
- **Commit profiled:** `405dab401b51b39025542e159d23f5faabea72df` (main)
- **Engine:** codetopo 0.9.1 · index run 2026-11-18
- **Graph:** 139 files walked · 4,641 nodes · 16,780 edges · audit chain valid
- **Nodes by kind:** function 304 · method 1,094 · class 291 · variable 293 · module 139 · file 139 · doc 37 · external 2,342 · package 2
- **Edges by kind:** calls 6,347 · reads 5,225 · contains 2,297 · defines 1,244 · imports 799 · writes 806 · inherits 62

## Coverage honesty

Extracted at symbol level: Python — the whole codebase (100 `.py`).
Markdown as Doc nodes (37). Not parsed: YAML workflows/config, the
Dockerfile, PowerShell (1 `.ps1`). Symbol coverage is complete for the
code present.

## Topology

"agentic-OS: Unified Autonomous Agent System" (README) — the Omegacode
build: an agent-driven code-generation and delivery environment.

- `agentic_os/omega/` — the core package (the graph's hub): the agent
  runtime, its tool layer (`tools/git_ops.py` and siblings — the tools
  an agent may wield), deliverable pipeline, and the test suites under
  `omega/tests/`.
- `tools/` — top-level operator tooling mirroring the package tools.
- `ARCHITECTURE.md`, `COMPONENT_HANDSHAKES.md`, `OMEGA_BUILD_PLAN.md`,
  `OMEGA_CODE_MANIFEST.md` — the design contract: read the handshakes
  doc before changing how components call each other.
- `ENVCONFIG.md` — the environment configuration contract; `Dockerfile`
  — the container build.

## Trust boundaries

- **This repo builds agents that act** — the trust boundary is the
  tool layer: what `tools/` exposes (git operations, file and process
  actions) is what an agent running this system can do. Changes to the
  tool layer are capability changes, reviewed as such.
- **Credentials:** the system runs against external services (its
  GitHub access is a fine-grained PAT scoped to this single repo,
  held in the vault and referenced by name only — never in this repo,
  never in this profile). Model/API keys likewise environment-held.
- **Handshake discipline:** `COMPONENT_HANDSHAKES.md` defines which
  component may ask what of another; the graph's 6,347 call edges are
  the measured version of that contract — a new cross-component call
  that contradicts the doc is a finding, not a feature.
- **Blast radius:** `agentic_os/omega/` core + the tool layer.

## Money surface

**No payment surface found.** Grep for stripe/paddle/checkout over the
Python tree hits only git-checkout wording in `git_ops.py` (a version-
control operation, not a payment). The system spends model/API credit
through its configured providers (keys by name, environment-held) —
that consumption is metered by the providers, not billed by this code.

## How an agent should approach

1. Read `ARCHITECTURE.md` + `COMPONENT_HANDSHAKES.md` first, then this
   profile; the manifest (`OMEGA_CODE_MANIFEST.md`) names what exists.
2. Treat any `tools/` change as a capability grant and say so in the PR.
3. Query the graph before touching the omega core.
4. Regenerate this profile at every release.

## Regeneration

`docs/codetopo-profile/refresh.sh` (in this pack) re-fetches the repo
at a named ref, re-runs the index, and rewrites `snapshot.json`,
`stats.json` and `verify.txt`.

## Standing-condition lines for this change

- Documentation at par: this pack is the documentation change, same PR;
  no behaviour changed.
- Release gate: NOT RUN for this profile PR · Guardian Mesh approval:
  NOT RUN. Merging is not "shipped"; the pack enters the gate queue in
  the Stage-1 evidence pack.
- OpenSSF Best Practices: project 16855 registered (checked
  2026-11-18); this additive docs change does not degrade any
  criterion.
