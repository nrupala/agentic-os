# Omegacode — Spec distilled from the source

Source: Gemini Project conversation "Autonomous Software Engineering Capabilities"
(2026-04-28, published by Nrupal 2026-11-06, share g4bYhl5Q7x0X), read in full
by Wright 2026-11-06 via live browser. Nrupal's ruling in that chat, restated
2026-11-06: "This chat itself is what the Omega code is." LLM provider = Gemini.
GitHub = through Wright (standing grant; no PAT is ever pasted into a chat).

## What the source claims (Gemini's words, April 2026 — NOT verified capabilities)

An autonomous engineering unit (agentic-OS = Paradise Stack + OMEGA-CODE) for
production-ready, fully autonomous software development, "never-quit" model:
Recursive Forge generating parallel variations; self-correction via an error
ledger; state serialized to disk and resumed after crashes; a meta-cognition
engine deriving "Thinking Rules" from failure patterns; a Generator/Critic
(GAN-style) pair; 500+ skills; 40+ tools; multi-provider LLMs; hardened Docker
sandbox; 3-tier memory (semantic / episodic / working); AES-256-GCM, RBAC,
secret redaction; web dashboard, Loki logs, forensic audit trail.

Gemini promised delivery "in hours to a single day" if given GitHub + authority.
That promise was never redeemed — nothing was built from that chat. The old
`nrupala/agentic-os` code (archived 2026-10-06, ruled superseded, not a worker)
is template-heavy boilerplate that does not implement this loop.

## The buildable core (Wright's distillation — this is what we build)

1. **The Forge loop** — Thought → Action → Verify, iterating until the task's
   tests pass or a hard iteration cap is hit. Never-quit means *resume*, not
   *loop forever*: state is checkpointed to disk every iteration.
2. **Correction ledger** — every failure (traceback, failing test) is appended
   as a JSONL record and fed back as a hard constraint on the next attempt.
3. **Thinking Rules** — rules derived from ledger patterns, read aloud
   ("listen before acting") at the start of every run.
4. **Tools** — file read/write/edit, shell (allowlisted), git branch/commit
   with `[ITERATION-n] [PASS|FAIL]` tags. Executed by Wright's runtime;
   Gemini is the reasoning engine via the existing Gemini connector.
5. **Provenance** — every run leaves a forensic trail: plan, iterations,
   ledger, verdict, in `provenance/`.

Deferred until the core proves itself: Generator/Critic pair, 3-tier memory
beyond working+ledger, dashboard, Docker hardening, skill catalog. Each is a
later slice, added only when the loop earns it.

## Build order

- Slice 1 (2026-11-06, exists): forge loop skeleton with checkpoint/resume,
  correction ledger, thinking-rules reader, deterministic demo task, tests.
- Slice 2: Gemini brain wired into the loop (propose → Wright executes → verify).
  Contract per Gemini's Slice-1 review (2026-11-06, provenance/): every proposal
  is a JSON block {thought, action{type,target,content}, verification_plan} —
  no code without a thought and a verify plan, or the loop rejects it; a
  reflective summary after each PASS updates Thinking Rules; a ledger
  summarizer condenses the JSONL into a ruleset before it can bloat context
  (her named #1 risk: context poisoning).
- Slice 3: git branch/commit integration on a real target repo.
- Slice 4: first real product task end-to-end.

## Repo decision (Nrupal's call, pending)

New repo `nrupala/omegacode` (recommended — the archived agentic-os stays
archived as ruled) vs unarchiving agentic-os. No PAT is needed either way:
Wright holds GitHub under the standing grant and executes all repo operations.
