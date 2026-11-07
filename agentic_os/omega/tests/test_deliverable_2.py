# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
"""
agentic_os/omega/tests/test_deliverable_2.py
Harness test script to be executed by the vault test runner.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

from agentic_os.omega.core.sandbox import SandboxRunner
from agentic_os.omega.tools.base import BaseTool, ToolResult
from agentic_os.omega.tools.file_ops import GuardedFileOps
from agentic_os.omega.tools.git_ops import GitOps


def test_sandbox() -> None:
    runner = SandboxRunner()

    # 1. Successful execution
    res = runner.run(["python3", "-c", "import sys; sys.stdout.write('OUT_OK'); sys.exit(0)"])
    assert res.success is True
    assert res.stdout == "OUT_OK"
    assert res.exit_code == 0

    # 2. Timeout containment
    res_timeout = runner.run(["python3", "-c", "import time; time.sleep(10)"], timeout=0.5)
    assert res_timeout.timed_out is True
    assert res_timeout.exit_code == 124
    assert res_timeout.success is False

    # 3. Bad command
    res_bad = runner.run(["non_existent_binary_omega_xyz"])
    assert res_bad.success is False
    assert res_bad.exit_code == 127


def test_file_ops() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        ops = GuardedFileOps(workspace_root=root)

        # 1. Atomic write & read
        w_res = ops.write_text("sub/test.txt", "hello omega")
        assert w_res.success is True

        r_res = ops.read_text("sub/test.txt")
        assert r_res.success is True
        assert r_res.data == "hello omega"

        # 2. Directory traversal escape prevention
        escape_res = ops.write_text("../forbidden.txt", "payload")
        assert escape_res.success is False
        assert escape_res.metadata.get("code") == "TRAVERSAL_DETECTED"

        # 3. Listing
        l_res = ops.list_dir(".", recursive=True)
        assert l_res.success is True


def test_git_ops():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "checkout", "-B", "main"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test Runner"], cwd=repo_path, check=True)
        subprocess.run(["git", "config", "user.email", "test@runner.local"], cwd=repo_path, check=True)

        git = GitOps(repo_root=repo_path)

        # Branch resolution
        branch_res = git.get_current_branch()
        assert branch_res.success is True
        assert branch_res.data == "main"

        # Dirty status & staging
        (repo_path / "work.txt").write_text("iteration content\n")
        status_dirty = git.get_status()
        assert status_dirty.success is True
        assert status_dirty.data["is_clean"] is False

        stage_res = git.stage_files(["work.txt"])
        assert stage_res.success is True

        # Input guard validations
        bad_status = git.commit_iteration(1, "INVALID_STATUS_TAG", "msg")
        assert bad_status.success is False
        assert bad_status.metadata.get("code") == "INVALID_STATUS"

        bad_iter = git.commit_iteration(-1, "PASS", "msg")
        assert bad_iter.success is False
        assert bad_iter.metadata.get("code") == "INVALID_ITERATION"

        # Valid commit
        commit_res = git.commit_iteration(1, "PASS", "initial run")
        assert commit_res.success is True
        assert commit_res.data["iteration"] == 1
        assert commit_res.data["status"] == "PASS"
        assert commit_res.data["message"] == "[ITERATION-1] [PASS] initial run"
        commit_hash = commit_res.data["commit_hash"]
        assert isinstance(commit_hash, str) and len(commit_hash) > 0

        # HEAD commit check
        head_res = git.get_head_commit()
        assert head_res.success is True
        assert head_res.data == commit_hash

        # Git log message verification
        log_proc = subprocess.run(
            ["git", "log", "-1", "--format=%s"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        assert log_proc.stdout.strip() == "[ITERATION-1] [PASS] initial run"

        # Clean status post-commit
        status_clean = git.get_status()
        assert status_clean.success is True
        assert status_clean.data["is_clean"] is True

        # Checkout branch
        co_res = git.checkout_branch("feature/test", create=True)
        assert co_res.success is True
        assert co_res.data == {"branch": "feature/test", "created": True}
        assert git.get_current_branch().data == "feature/test"
