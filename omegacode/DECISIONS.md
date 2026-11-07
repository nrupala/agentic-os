# Omegacode — Decisions

- 2026-11-06 ~20:05 CST (Nrupal, this chat): Omegacode builds in the RECOVERED
  `nrupala/agentic-os` repo (unarchived on his word — supersedes Wright's
  new-repo recommendation). Gemini works on it as brain; Wright executes.
- Token: fine-grained GitHub PAT created by Nrupal scoped to agentic-os,
  60-day validity (created 2026-11-06, expires ~2027-01-05). His reasoning:
  Gemini says she can deliver in two days, so 60 days is more than enough —
  no longer-lived token to be created. Token is vaulted via the
  custom.github-omegacode connector; the raw value never enters a chat or a
  Gemini prompt — Gemini's GitHub access runs through Wright's surrogate calls.
- Slice 1 (forge loop) built locally at ~/workspace/omegacode/ on 2026-11-06,
  to be pushed into agentic-os as the build's first slice.
