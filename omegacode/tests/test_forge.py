import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import omega_forge as of


def test_loop_self_corrects(tmp_path, monkeypatch):
    monkeypatch.setattr(of, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(of, "LEDGER", tmp_path / "state" / "correction_ledger.jsonl")
    monkeypatch.setattr(of, "RULES", tmp_path / "state" / "thinking_rules.json")
    work = tmp_path / "work"
    work.mkdir()
    (work / "test_add.py").write_text(
        "from add import add\n\ndef test_add():\n    assert add(2, 3) == 5\n")
    state = of.forge("t1", of.demo_proposer,
                     [sys.executable, "-m", "pytest", "-q", "test_add.py"], work)
    assert state.status == "passed"
    assert state.iteration == 2  # first attempt failed, ledger-fed second passed
    constraints = of.ledger_constraints("t1")
    assert len(constraints) == 1 and "failed" in constraints[0]


def test_state_resumes(tmp_path, monkeypatch):
    monkeypatch.setattr(of, "STATE_DIR", tmp_path / "state")
    s = of.ForgeState(task="t2", iteration=3, status="running")
    s.checkpoint()
    r = of.ForgeState.resume("t2")
    assert r.iteration == 3
    done = of.ForgeState(task="t2", iteration=3, status="passed")
    done.checkpoint()
    assert of.ForgeState.resume("t2").iteration == 0  # finished runs don't resume
