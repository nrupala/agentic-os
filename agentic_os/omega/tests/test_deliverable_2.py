"""
agentic_os/omega/tests/test_deliverable_2.py
Harness test script to be executed by the vault test runner.
"""

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
