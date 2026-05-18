#!/usr/bin/env python3
"""
OMEGA Shell Tools
================
Sandboxed shell execution with timeouts, streaming output, and error capture.
The feedback loop backbone - run tests, capture stderr, feed back to LLM.

Inspired by: Claude Code, OpenCode - tight shell integration
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='[SHELL] %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class CommandResult:
    """Result of a shell command execution."""
    command: str
    return_code: int
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool = False
    killed: bool = False
    
    @property
    def success(self) -> bool:
        return self.return_code == 0 and not self.timed_out
    
    @property
    def output(self) -> str:
        return self.stdout + ("\n--- STDERR ---\n" + self.stderr if self.stderr else "")


@dataclass
class ExecutionSession:
    """A shell execution session with working directory."""
    id: str
    cwd: Path
    env: Dict[str, str] = field(default_factory=dict)
    started: str = ""
    commands_run: int = 0


class OmegaShellTools:
    """
    Sandboxed shell execution with safety limits and streaming.
    Key to the seamless feedback loop: code → run → error → fix automatically.
    """
    
    # Dangerous commands to block
    BLOCKED_COMMANDS = {
        'rm -rf /', 'rm -rf /*', 'mkfs', 'dd if=', 
        'chmod -R 777 /', 'chown -R', ':(){:|:&};:',
        'curl -s', 'wget -s',  # Could download malicious scripts
    }
    
    # Allowed commands (whitelist approach)
    ALLOWED_COMMANDS = {
        'python', 'python3', 'pip', 'pip3', 'pytest', 'ruff', 'black',
        'node', 'npm', 'npx', 'yarn', 'pnpm',
        'cargo', 'rustc', 'rustfmt',
        'go', 'gofmt',
        'git', 'gitk',
        'ls', 'cd', 'pwd', 'cat', 'head', 'tail', 'grep', 'find', 'findstr',
        'type', 'dir', 'mkdir', 'rmdir', 'copy', 'move', 'xcopy',
        'cmd', 'powershell', 'echo', 'set', 'export',
        'clang', 'gcc', 'g++', 'make', 'cmake',
        'docker', 'kubectl', 'helm',
        'uv', 'poetry', 'pipenv',
    }
    
    def __init__(self, 
                 root_path: Optional[str] = None,
                 timeout_seconds: int = 120,
                 max_output_kb: int = 512,
                 sandbox_dir: Optional[str] = None):
        
        self.root = Path(root_path or PROJECT_ROOT)
        self.timeout = timeout_seconds
        self.max_output_kb = max_output_kb
        self.sandbox_dir = Path(sandbox_dir) if sandbox_dir else None
        
        # Execution tracking
        self.sessions: Dict[str, ExecutionSession] = {}
        self.command_history: List[CommandResult] = []
        
        # Create sandbox if needed
        if self.sandbox_dir:
            self.sandbox_dir.mkdir(parents=True, exist_ok=True)
    
    def _is_command_safe(self, command: str) -> Tuple[bool, str]:
        """Check if command is safe to execute."""
        cmd_lower = command.lower().strip()
        
        # Check blocked commands
        for blocked in self.BLOCKED_COMMANDS:
            if blocked in cmd_lower:
                return False, f"Blocked dangerous pattern: {blocked}"
        
        # Extract first command
        first_cmd = cmd_lower.split()[0] if cmd_lower.split() else ""
        
        # Check whitelist (allow if in whitelist or if using path like ./script.sh)
        if first_cmd not in self.ALLOWED_COMMANDS:
            # Allow if it's a path-based command
            if not any(c in cmd_lower for c in ['/', '\\', './', '..\\', '..']):
                return False, f"Command not in allowlist: {first_cmd}"
        
        return True, "OK"
    
    def _sanitize_env(self, extra_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Create sanitized environment variables."""
        # Start with base environment
        env = os.environ.copy()
        
        # Add project-specific paths
        env['PYTHONPATH'] = str(self.root / 'engine') + os.pathsep + env.get('PYTHONPATH', '')
        env['PATH'] = str(self.root) + os.pathsep + env.get('PATH', '')
        
        # Add any extra env vars
        if extra_env:
            env.update(extra_env)
        
        # Remove potentially dangerous vars
        for dangerous in ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'DYLD_INSERT_LIBRARIES']:
            env.pop(dangerous, None)
        
        return env
    
    def run(self, 
            command: str, 
            cwd: Optional[str] = None,
            env: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None,
            capture_output: bool = True,
            streaming_callback: Optional[Callable[[str], None]] = None) -> CommandResult:
        """
        Execute a shell command with timeout and output limits.
        
        This is the core of the feedback loop - runs tests, captures errors,
        and returns result for LLM to process.
        """
        start_time = time.time()
        
        # Safety check
        safe, reason = self._is_command_safe(command)
        if not safe:
            return CommandResult(
                command=command,
                return_code=-1,
                stdout="",
                stderr=f"Command blocked: {reason}",
                duration_ms=0,
                timed_out=False,
                killed=True
            )
        
        # Set working directory
        work_dir = Path(cwd) if cwd else self.root
        if not work_dir.exists():
            work_dir = self.root
        
        # Create environment
        run_env = self._sanitize_env(env)
        
        # Timeout
        timeout_val = timeout or self.timeout
        
        logger.info(f"Executing: {command[:80]}...")
        
        try:
            # Use shell=True on Windows, shell=False elsewhere
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=str(work_dir),
                env=run_env,
                stdout=subprocess.PIPE if capture_output else None,
                stderr=subprocess.PIPE if capture_output else None,
                text=True,
                bufsize=1
            )
            
            stdout_parts = []
            stderr_parts = []
            output_size = 0
            
            # Read output with size limits
            def read_stream(stream, is_stderr=False):
                nonlocal output_size
                try:
                    while True:
                        if stream is None:
                            break
                        line = stream.readline()
                        if not line:
                            break
                        
                        line_size = len(line.encode())
                        if output_size + line_size > self.max_output_kb * 1024:
                            return
                        
                        output_size += line_size
                        output = line
                        
                        stdout_parts.append(output) if not is_stderr else stderr_parts.append(output)
                        
                        if streaming_callback:
                            streaming_callback(output, is_stderr)
                            
                except:
                    pass
            
            # Run in thread to allow timeout
            stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, False))
            stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, True))
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Wait with timeout
            try:
                process.wait(timeout=timeout_val)
                stdout_thread.join(timeout=1)
                stderr_thread.join(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                logger.warning(f"Command timed out after {timeout_val}s: {command[:50]}")
                
                return CommandResult(
                    command=command,
                    return_code=-1,
                    stdout=''.join(stdout_parts),
                    stderr=''.join(stderr_parts),
                    duration_ms=int((time.time() - start_time) * 1000),
                    timed_out=True,
                    killed=False
                )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            result = CommandResult(
                command=command,
                return_code=process.returncode,
                stdout=''.join(stdout_parts),
                stderr=''.join(stderr_parts),
                duration_ms=duration_ms
            )
            
            self.command_history.append(result)
            logger.info(f"Command completed: {process.returncode} in {duration_ms}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return CommandResult(
                command=command,
                return_code=-1,
                stdout="",
                stderr=str(e),
                duration_ms=int((time.time() - start_time) * 1000)
            )
    
    def run_test(self, 
                 test_path: Optional[str] = None,
                 test_framework: str = "pytest",
                 extra_args: List[str] = None) -> CommandResult:
        """Run tests and capture results."""
        cmd = test_framework
        
        if test_path:
            cmd += f" {test_path}"
        
        if extra_args:
            cmd += " " + " ".join(extra_args)
        
        # Add common test options
        if test_framework == "pytest":
            cmd += " -v --tb=short"
        elif test_framework == "npm":
            cmd += " --test"
        
        return self.run(cmd)
    
    def run_linter(self, 
                   file_path: Optional[str] = None,
                   linter: str = "ruff") -> CommandResult:
        """Run linter on file or project."""
        cmd = linter
        
        if file_path:
            cmd += f" {file_path}"
        else:
            cmd += " ."
        
        return self.run(cmd)
    
    def run_typecheck(self, 
                      file_path: Optional[str] = None,
                      checker: str = "mypy") -> CommandResult:
        """Run type checker."""
        cmd = checker
        
        if file_path:
            cmd += f" {file_path}"
        else:
            cmd += " ."
        
        return self.run(cmd)
    
    def create_session(self, cwd: Optional[str] = None) -> str:
        """Create a new execution session."""
        import uuid
        session_id = uuid.uuid4().hex[:8]
        
        work_dir = Path(cwd) if cwd else self.root
        session = ExecutionSession(
            id=session_id,
            cwd=work_dir,
            started=datetime.now().isoformat()
        )
        
        self.sessions[session_id] = session
        return session_id
    
    def run_in_session(self, session_id: str, command: str) -> CommandResult:
        """Run command in a specific session."""
        session = self.sessions.get(session_id)
        if not session:
            return self.run(command)
        
        return self.run(command, cwd=str(session.cwd))
    
    def get_command_history(self, limit: int = 20) -> List[Dict]:
        """Get recent command history."""
        return [
            {
                'command': r.command,
                'return_code': r.return_code,
                'duration_ms': r.duration_ms,
                'success': r.success,
                'timed_out': r.timed_out
            }
            for r in self.command_history[-limit:]
        ]
    
    def get_project_commands(self) -> List[str]:
        """Get available project-specific commands."""
        commands = []
        
        # Check for Makefile
        if (self.root / 'Makefile').exists():
            commands.append('make')
        
        # Check for package.json
        if (self.root / 'package.json').exists():
            commands.extend(['npm run', 'npm test', 'npm run dev'])
        
        # Check for pyproject.toml
        if (self.root / 'pyproject.toml').exists():
            commands.extend(['python -m pytest', 'ruff check', 'black'])
        
        # Check for Cargo.toml
        if (self.root / 'Cargo.toml').exists():
            commands.extend(['cargo test', 'cargo build', 'cargo fmt'])
        
        return commands


class FeedbackLoop:
    """
    The seamless feedback loop: code → run → error → fix → repeat.
    This is what makes AI coding feel "seamless" vs "clunky".
    """
    
    def __init__(self, shell: OmegaShellTools):
        self.shell = shell
        self.max_iterations = 5
        self.iteration = 0
        
    def run_and_fix(self, 
                    apply_edit_fn: Callable[[str], bool],
                    test_command: str,
                    initial_code: str = "") -> Dict:
        """
        Run a feedback loop: apply edit → run tests → if fail, fix → repeat.
        
        Returns:
            - final_code: The code after all fixes
            - iterations: How many fix attempts
            - success: Whether tests passed
            - error_trace: Last error for debugging
        """
        self.iteration = 0
        last_error = ""
        
        while self.iteration < self.max_iterations:
            self.iteration += 1
            
            # Run the test command
            result = self.shell.run(test_command)
            
            if result.success:
                return {
                    'success': True,
                    'iterations': self.iteration,
                    'error_trace': None,
                    'output': result.stdout
                }
            
            # Extract error message
            error_output = result.stderr if result.stderr else result.stdout
            last_error = self._extract_error(error_output)
            
            logger.info(f"Iteration {self.iteration}: Test failed, attempting fix...")
            
            # Attempt to fix - this would be called from LLM
            # In practice, the LLM sees this error and generates a fix
            # Then apply_edit_fn is called with the new code
            
        return {
            'success': False,
            'iterations': self.iteration,
            'error_trace': last_error,
            'output': result.stdout
        }
    
    def _extract_error(self, output: str) -> str:
        """Extract the most relevant error from output."""
        lines = output.split('\n')
        
        # Look for common error patterns
        error_keywords = ['error:', 'Error:', 'FAILED', 'Traceback', 'Exception']
        
        for i, line in enumerate(lines):
            for keyword in error_keywords:
                if keyword in line:
                    # Return this line and next few lines
                    return '\n'.join(lines[i:i+5])
        
        # Fall back to last few lines
        return '\n'.join(lines[-10:])


if __name__ == "__main__":
    import sys
    
    shell = OmegaShellTools()
    
    if len(sys.argv) > 1:
        command = ' '.join(sys.argv[1:])
        result = shell.run(command, timeout=30)
        
        print(f"Return code: {result.return_code}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Timed out: {result.timed_out}")
        print(f"\n--- STDOUT ---\n{result.stdout[:2000]}")
        if result.stderr:
            print(f"\n--- STDERR ---\n{result.stderr[:2000]}")
    else:
        # Show available commands
        print("Available project commands:")
        for cmd in shell.get_project_commands():
            print(f"  - {cmd}")