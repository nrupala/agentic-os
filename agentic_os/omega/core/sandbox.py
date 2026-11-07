"""
agentic_os.omega.core.sandbox
Isolated subprocess runner with strict telemetry, timeout containment,
and fail-closed execution guarantees for Omega Forge iterations.
"""

from __future__ import annotations

import logging
import os
import shlex
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

logger = logging.getLogger("agentic_os.omega.core.sandbox")


@dataclass(frozen=True)
class ExecutionResult:
    """Immutable result of a sandboxed command execution."""

    cmd: List[str]
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    timed_out: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.exit_code == 0 and not self.timed_out and self.error is None


class SandboxRunner:
    """
    Guarded subprocess runner.
    Executes commands in controlled working directories with sanitized environments,
    hard timeout boundaries, and fail-closed failure classification.
    """

    # Baseline environment variables safe for tool/compiler execution
    SAFE_ENV_PASSTHROUGH: Set[str] = {
        "PATH",
        "VIRTUAL_ENV",
        "PYTHONPATH",
        "LANG",
        "LC_ALL",
        "HOME",
        "USER",
        "TMPDIR",
    }

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        default_timeout_sec: float = 30.0,
        allowed_env_vars: Optional[Set[str]] = None,
        extra_env: Optional[Dict[str, str]] = None,
    ) -> None:
        self.base_dir = (base_dir or Path.cwd()).resolve()
        self.default_timeout_sec = max(0.5, default_timeout_sec)
        self.allowed_env_vars = allowed_env_vars or self.SAFE_ENV_PASSTHROUGH
        self.extra_env = extra_env or {}

        if not self.base_dir.exists():
            self.base_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_env(self, custom_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Produce an isolated environment map preventing leakage of parent process state."""
        sanitized: Dict[str, str] = {}
        for var in self.allowed_env_vars:
            val = os.environ.get(var)
            if val is not None:
                sanitized[var] = val

        # Layer configured defaults and call-specific overrides
        sanitized.update(self.extra_env)
        if custom_env:
            sanitized.update(custom_env)

        return sanitized

    def _resolve_cwd(self, cwd: Optional[Path]) -> Path:
        """Resolve and verify working directory to avoid directory escapes."""
        target = (cwd or self.base_dir).resolve()
        try:
            target.relative_to(self.base_dir)
        except ValueError:
            logger.warning(
                "Execution working directory %s outside base %s; rejecting to base.",
                target,
                self.base_dir,
            )
            return self.base_dir
        return target

    def run(
        self,
        cmd: Sequence[str],
        timeout: Optional[float] = None,
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> ExecutionResult:
        """
        Execute a command within sandbox bounds.
        Fails closed on timeouts, operating system errors, and unauthorized escapes.
        """
        cmd_list = list(cmd)
        if not cmd_list:
            return ExecutionResult(
                cmd=cmd_list,
                exit_code=-1,
                stdout="",
                stderr="Execution rejected: empty command sequence.",
                duration_ms=0.0,
                timed_out=False,
                error="EMPTY_COMMAND",
            )

        resolved_cwd = self._resolve_cwd(cwd)
        effective_timeout = timeout if timeout is not None else self.default_timeout_sec
        effective_env = self._sanitize_env(env)

        t_start = time.perf_counter()
        try:
            process = subprocess.Popen(
                cmd_list,
                cwd=str(resolved_cwd),
                env=effective_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                close_fds=True,
            )
            stdout, stderr = process.communicate(timeout=effective_timeout)
            duration_ms = (time.perf_counter() - t_start) * 1000.0

            return ExecutionResult(
                cmd=cmd_list,
                exit_code=process.returncode,
                stdout=stdout or "",
                stderr=stderr or "",
                duration_ms=duration_ms,
                timed_out=False,
                error=None if process.returncode == 0 else f"PROCESS_EXIT_{process.returncode}",
                metadata={"cwd": str(resolved_cwd)},
            )

        except subprocess.TimeoutExpired:
            duration_ms = (time.perf_counter() - t_start) * 1000.0
            process.kill()
            stdout, stderr = process.communicate()
            logger.error(
                "Command '%s' timed out after %.2fs",
                shlex.join(cmd_list),
                effective_timeout,
            )
            return ExecutionResult(
                cmd=cmd_list,
                exit_code=124,  # Standard UNIX timeout exit code
                stdout=stdout or "",
                stderr=f"Timeout expired: Command exceeded {effective_timeout:.2f}s.\n" + (stderr or ""),
                duration_ms=duration_ms,
                timed_out=True,
                error="COMMAND_TIMEOUT",
                metadata={"cwd": str(resolved_cwd), "timeout_limit": effective_timeout},
            )

        except (FileNotFoundError, PermissionError, OSError) as os_err:
            duration_ms = (time.perf_counter() - t_start) * 1000.0
            logger.error("Sandbox execution OS error on '%s': %s", cmd_list[0], os_err)
            return ExecutionResult(
                cmd=cmd_list,
                exit_code=127,
                stdout="",
                stderr=str(os_err),
                duration_ms=duration_ms,
                timed_out=False,
                error=f"OS_EXECUTION_FAILURE: {type(os_err).__name__}",
                metadata={"cwd": str(resolved_cwd)},
            )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    runner = SandboxRunner()
    res = runner.run(["python3", "-c", "import sys; print('SANDBOX_RUNNER_OK'); sys.exit(0)"])
    assert res.success, f"Self-test failed: {res.stderr}"
    print(f"Self-test verified: {res.stdout.strip()} ({res.duration_ms:.2f}ms)")
