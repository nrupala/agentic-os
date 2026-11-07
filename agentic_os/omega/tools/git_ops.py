"""
agentic_os.omega.tools.git_ops
Atomic Git operations tool supporting branch isolation, staging,
and standard iteration-formatted commit messages: [ITERATION-n] [PASS|FAIL] <msg>.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, List, Optional, Set

from agentic_os.omega.core.sandbox import ExecutionResult, SandboxRunner
from agentic_os.omega.tools.base import BaseTool, ToolResult

logger = logging.getLogger("agentic_os.omega.tools.git_ops")


class GitOps(BaseTool):
    """
    Git lane synchronization and revision management tool.
    Enforces format standards on commits and executes through SandboxRunner.
    """

    ALLOWED_STATUSES: Set[str] = {"PASS", "FAIL", "INIT", "WARN"}

    def __init__(self, repo_root: Path, runner: Optional[SandboxRunner] = None) -> None:
        super().__init__(
            name="git_ops",
            description="Sandboxed Git revision and branch management for iteration commits.",
            version="1.0.0",
        )
        self.repo_root = repo_root.resolve()
        self.runner = runner or SandboxRunner(base_dir=self.repo_root)

    def _exec_git(self, args: List[str], timeout: float = 30.0) -> ExecutionResult:
        """Execute a git command within the repo boundary."""
        cmd = ["git"] + args
        return self.runner.run(cmd=cmd, cwd=self.repo_root, timeout=timeout)

    def get_current_branch(self) -> ToolResult:
        """Query the currently active branch name."""
        # symbolic-ref resolves unborn branches (fresh repo, no commits yet);
        # rev-parse --abbrev-ref HEAD cannot. Fall back for detached HEAD.
        res = self._exec_git(["symbolic-ref", "--short", "HEAD"])
        if not res.success:
            res = self._exec_git(["rev-parse", "--abbrev-ref", "HEAD"])
        if not res.success:
            return ToolResult.fail(f"Failed to get current branch: {res.stderr.strip()}", code="GIT_ERROR")
        return ToolResult.ok(data=res.stdout.strip())

    def checkout_branch(self, branch_name: str, create: bool = False) -> ToolResult:
        """Switch to an existing branch or create a new branch."""
        clean_name = branch_name.strip()
        if not clean_name:
            return ToolResult.fail("Branch name cannot be empty.")

        args = ["checkout"]
        if create:
            args.append("-B")
        args.append(clean_name)

        res = self._exec_git(args)
        if not res.success:
            return ToolResult.fail(f"Checkout failed: {res.stderr.strip()}", code="CHECKOUT_FAIL")
        return ToolResult.ok(data={"branch": clean_name, "created": create})

    def stage_files(self, paths: Optional[List[str]] = None) -> ToolResult:
        """Stage specified paths or all changes if not specified."""
        args = ["add"]
        if paths:
            args.extend(paths)
        else:
            args.append("-A")

        res = self._exec_git(args)
        if not res.success:
            return ToolResult.fail(f"Git add failed: {res.stderr.strip()}", code="STAGE_FAIL")
        return ToolResult.ok(staged=paths or "ALL")

    def commit_iteration(
        self,
        iteration: int,
        status: str,
        message: str,
        allow_empty: bool = False,
    ) -> ToolResult:
        """
        Produce a strictly formatted atomic iteration commit:
        `[ITERATION-{iteration}] [{status}] {message}`
        """
        normalized_status = status.upper().strip()
        if normalized_status not in self.ALLOWED_STATUSES:
            return ToolResult.fail(
                f"Invalid commit status '{status}'. Must be one of: {sorted(self.ALLOWED_STATUSES)}",
                code="INVALID_STATUS",
            )

        if iteration < 0:
            return ToolResult.fail("Iteration number must be a non-negative integer.", code="INVALID_ITERATION")

        formatted_msg = f"[ITERATION-{iteration}] [{normalized_status}] {message.strip()}"

        cmd = ["commit", "-m", formatted_msg]
        if allow_empty:
            cmd.append("--allow-empty")

        res = self._exec_git(cmd)
        if not res.success:
            # Check if reason was simply nothing to commit
            if "nothing to commit" in res.stdout or "nothing to commit" in res.stderr:
                return ToolResult.fail("Nothing to commit (working tree clean).", code="CLEAN_TREE")
            return ToolResult.fail(f"Commit failed: {res.stderr.strip()}", code="COMMIT_FAIL")

        head_res = self.get_head_commit()
        commit_hash = head_res.data if head_res.success else "UNKNOWN"

        return ToolResult.ok(
            data={
                "commit_hash": commit_hash,
                "message": formatted_msg,
                "iteration": iteration,
                "status": normalized_status,
            }
        )

    def get_status(self) -> ToolResult:
        """Check status of modified and untracked files in porcelain format."""
        res = self._exec_git(["status", "--porcelain"])
        if not res.success:
            return ToolResult.fail(f"Git status query failed: {res.stderr.strip()}")

        raw = res.stdout.strip()
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        return ToolResult.ok(data={"is_clean": len(lines) == 0, "changes": lines})

    def get_head_commit(self) -> ToolResult:
        """Get the full SHA-1 of the current HEAD commit."""
        res = self._exec_git(["rev-parse", "HEAD"])
        if not res.success:
            return ToolResult.fail(f"Failed to query HEAD: {res.stderr.strip()}")
        return ToolResult.ok(data=res.stdout.strip())

    def execute(self, action: str, **kwargs: Any) -> ToolResult:
        """BaseTool dispatch implementation."""
        if action == "status":
            return self.get_status()
        elif action == "current_branch":
            return self.get_current_branch()
        elif action == "checkout":
            return self.checkout_branch(
                branch_name=kwargs["branch_name"],
                create=kwargs.get("create", False),
            )
        elif action == "stage":
            return self.stage_files(paths=kwargs.get("paths"))
        elif action == "commit":
            return self.commit_iteration(
                iteration=kwargs["iteration"],
                status=kwargs["status"],
                message=kwargs["message"],
                allow_empty=kwargs.get("allow_empty", False),
            )
        return ToolResult.fail(f"Unsupported GitOps action: {action}")
