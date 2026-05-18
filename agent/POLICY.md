# Paradise Stack - Agent Policy

## 1. Mandatory Process (PDCA)
Every task must follow this disciplined cycle:

### PLAN
1. Intent normalization - What does the user really want?
2. Constraint declaration - What are the limits?
3. Assumption listing - What must be true?
4. Architecture design - How will it be built?

### DO
5. Implementation - Execute the plan
6. Parallel carriers - Run multiple agents simultaneously where possible

### CHECK
7. Guardian verification - Lint, type check, security scan
8. Executor verification - Run tests, assertions, invariants
9. User verification - Confirm acceptance criteria met

### ACT
10. Fix issues - If CHECK fails, loop back to DO
11. Improve - Learn from outcomes, update knowledge graph
12. Document - Record decisions and rationale

**Skipping a step is a policy violation.**

## 2. Reasoning Requirements
Every decision must expose:
- **What I Know** - Verified facts from codebase
- **What I Assume** - Explicit assumptions stated clearly
- **What Can Go Wrong** - Edge cases and failure modes
- **How Failure is Mitigated** - Guards, fallbacks, recovery

## 3. Constraint Declaration
Every task must explicitly declare:
- **Timing**: Is there a deadline? Response time requirements?
- **Memory**: Resource constraints? Build size limits?
- **Determinism**: Must be reproducible? Idempotent?
- **Safety**: Is this safety-critical? What can go wrong?
- **Failure Behavior**: What happens on failure? Rollback?

If unknown, mark as `UNKNOWN_CONSTRAINT` and ask user.

## 4. Engineering Truth
Truth does not reside in generated code. Truth resides in:
- Tests (unit, integration, e2e)
- Assertions
- Invariants
- Contracts
- Verification artifacts

## 5. Safety Rules
- Default state must be safe-off
- All failures must be explicit and logged
- Silent failures are forbidden
- Undefined behavior is forbidden
- If uncertainty affects correctness or safety → STOP, FLAG, ASK

## 6. Cognitive Parallelism
Paradise Stack runs parallel PDCA loops:
- **Planner Loop** - Iterates on plan until optimal
- **Implementer Loop** - Iterates on code until clean
- **Guardian Loop** - Iterates on lint until clean
- **Executor Loop** - Iterates on tests until passing
- **Improver Loop** - Iterates on quality until max

All loops run simultaneously, coordinated by Orchestrator.

## 7. Style Rules
- Prefer explicit over clever
- Prefer boring over fragile
- Prefer deterministic over performant
- Prefer testable over optimized
- Prefer documented over assumed

## 8. Iteration Limits
- Default max iterations: 10
- Can exceed if user explicitly requests
- Each iteration must show progress
- Stuck detection after 3+ identical failures
- Escalate to human if truly stuck

## 9. Verification Triggers
Run verification after:
- Each implementation step
- Each file creation/modification
- Before declaring success
- On user request

## 10. Compliance
Any output violating this policy must be rejected and corrected.
