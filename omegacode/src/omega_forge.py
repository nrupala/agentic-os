"""Omegacode Slice 1 — the Forge loop.

Thought -> Action -> Verify, with:
- state checkpointed to disk every iteration (crash = resume, not restart)
- a correction ledger: every failure is appended as JSONL and fed back
  as a hard constraint on the next attempt
- Thinking Rules derived from ledger patterns, read before acting

Stdlib only. The proposer is pluggable: Slice 1 ships a deterministic demo
proposer; Slice 2 wires Gemini in as the brain behind the same interface.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
LEDGER = ROOT / "state" / "correction_ledger.jsonl"
RULES = ROOT / "state" / "thinking_rules.json"


# ---------- state ----------
@dataclass
class ForgeState:
    task: str
    iteration: int = 0
    status: str = "running"  # running | passed | capped
    history: list = field(default_factory=list)

    def checkpoint(self) -> Path:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        p = STATE_DIR / "forge_state.json"
        p.write_text(json.dumps(self.__dict__, indent=2))
        return p

    @classmethod
    def resume(cls, task: str) -> "ForgeState":
        p = STATE_DIR / "forge_state.json"
        if p.exists():
            data = json.loads(p.read_text())
            if data.get("task") == task and data.get("status") == "running":
                return cls(**data)
        return cls(task=task)


# ---------- correction ledger ----------
def ledger_append(task: str, iteration: int, error: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    rec = {"ts": time.time(), "task": task, "iteration": iteration,
           "error": error[:2000]}
    with LEDGER.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def ledger_constraints(task: str) -> list[str]:
    if not LEDGER.exists():
        return []
    out = []
    for line in LEDGER.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec["task"] == task:
            out.append(f"Iteration {rec['iteration']} failed: {rec['error'][:200]}")
    return out


# ---------- thinking rules ----------
def derive_rules() -> list[str]:
    """Derive Thinking Rules from failure patterns across the whole ledger."""
    if not LEDGER.exists():
        return []
    counts: dict[str, int] = {}
    for line in LEDGER.read_text().splitlines():
        if not line.strip():
            continue
        err = json.loads(line)["error"]
        sig = re.sub(r"\d+", "N", err.strip().splitlines()[-1] if err.strip() else err)
        counts[sig] = counts.get(sig, 0) + 1
    rules = [f"AVOID (seen {n}x): {sig}" for sig, n in counts.items() if n >= 2]
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    RULES.write_text(json.dumps(rules, indent=2))
    return rules


# ---------- verify ----------
def verify(cmd: list[str], cwd: Path) -> tuple[bool, str]:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
    return r.returncode == 0, (r.stdout + r.stderr)


# ---------- the loop ----------
def forge(task: str, proposer, verify_cmd: list[str], workdir: Path,
          max_iterations: int = 5) -> ForgeState:
    """proposer(task, iteration, constraints) -> writes files into workdir."""
    rules = derive_rules()
    if rules:
        print("Thinking Rules (listen before acting):")
        for r in rules:
            print(f"  - {r}")
    state = ForgeState.resume(task)
    while state.iteration < max_iterations:
        state.iteration += 1
        constraints = ledger_constraints(task)
        proposer(task, state.iteration, constraints, workdir)
        ok, output = verify(verify_cmd, workdir)
        tag = "PASS" if ok else "FAIL"
        state.history.append({"iteration": state.iteration, "tag": tag})
        print(f"[ITERATION-{state.iteration}] [{tag}] task={task}")
        if ok:
            state.status = "passed"
            state.checkpoint()
            return state
        ledger_append(task, state.iteration, output)
        state.checkpoint()  # checkpoint AFTER ledger write: resume never loses a failure
    state.status = "capped"
    state.checkpoint()
    return state


# ---------- Slice 1 demo proposer (deterministic, no LLM) ----------
def demo_proposer(task: str, iteration: int, constraints: list[str], workdir: Path) -> None:
    """Writes add.py. Attempt 1 carries a real bug; once the ledger shows the
    failure, later attempts write the corrected version — the self-correction
    path, exercised honestly without an LLM in Slice 1."""
    target = workdir / "add.py"
    if iteration == 1 and not constraints:
        target.write_text("def add(a, b):\n    return a - b  # bug, on purpose for slice-1 proof\n")
    else:
        target.write_text("def add(a, b):\n    return a + b\n")


if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "demo-add"
    workdir = ROOT / "outputs" / "demo"
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "test_add.py").write_text(
        "from add import add\n\ndef test_add():\n    assert add(2, 3) == 5\n    assert add(-1, 1) == 0\n")
    state = forge(task, demo_proposer, [sys.executable, "-m", "pytest", "-q", "test_add.py"],
                  workdir)
    print(f"FINAL: status={state.status} iterations={state.iteration}")
    sys.exit(0 if state.status == "passed" else 1)
