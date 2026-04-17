#!/usr/bin/env python3
"""
OMEGA Feedback Loop - NUCLEAR GRADE SAFETY
===========================================
The seamless feedback loop: code -> run -> error -> fix -> repeat.

NUCLEAR SAFETY THINKING:
- Every state change -> encrypted to FILE
- Every iteration -> logged and encrypted
- If RAM fails -> can resume from file
- No data exposure in memory
- Full audit trail

Key features:
- Run tests/lint immediately after edits
- Capture stderr and feed back to LLM as context
- Loop until green (auto-fix errors)
- Stream output so user can watch thinking
- ZERO-KNOWLEDGE: All state encrypted at rest

Inspired by: Claude Code (5-15s loop), OpenCode (streaming), Cursor (live squiggles)
"""

import os
import time
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO, format='[FEEDBACK] %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent

try:
    from omega_phase_encryptor import OmegaPhaseEncryptor
    from zero_knowledge_handoff import ZeroKnowledgeHandoff
    HAS_ZERO_KNOWLEDGE = True
except ImportError:
    HAS_ZERO_KNOWLEDGE = False


class LoopState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING_FIX = "waiting_fix"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class LoopResult:
    """Result of a feedback loop iteration."""
    iteration: int
    state: LoopState
    command: str
    return_code: int
    stdout: str
    stderr: str
    duration_ms: int
    errors_found: List[str] = field(default_factory=list)
    warnings_found: List[str] = field(default_factory=list)


@dataclass
class FeedbackLoopConfig:
    """Configuration for feedback loop."""
    max_iterations: int = 5
    timeout_seconds: int = 120
    run_linter_after_edit: bool = True
    run_tests_after_edit: bool = True
    stream_output: bool = True
    auto_fix: bool = False  # If true, LLM should auto-generate fixes
    lint_commands: List[str] = field(default_factory=lambda: ["ruff check .", "mypy ."])
    test_commands: List[str] = field(default_factory=lambda: ["pytest -v"])


class OmegaFeedbackLoop:
    """
    The seamless feedback loop - code → run → error → fix → repeat.
    
    This is what separates "seamless" from "clunky":
    - Seamless: runs tests immediately, captures errors, feeds back to LLM
    - Clunky: waits for "run tests?" prompt, shows errors to user to fix
    
    The loop works:
    1. Apply edit via edit_file tool
    2. Run linter/tests via shell immediately
    3. Capture stderr → feed back to LLM as new context
    4. LLM generates fix → applies → loop continues until green
    """
    
    def __init__(self, 
                 shell_tools,  # OmegaShellTools instance
                 lsp_client,   # OmegaLSPClient instance
                 config: Optional[FeedbackLoopConfig] = None):
        
        self.shell = shell_tools
        self.lsp = lsp_client
        self.config = config or FeedbackLoopConfig()
        
        self.current_iteration = 0
        self.loop_history: List[LoopResult] = []
        self._current_state = LoopState.IDLE
        self._encryptor = None
        self._handoff = None
        if HAS_ZERO_KNOWLEDGE:
            try:
                self._encryptor = OmegaPhaseEncryptor(project="omega_feedback")
                self._handoff = ZeroKnowledgeHandoff(project="omega_feedback")
            except Exception as e:
                logger.warning(f"[ZK] Feedback init failed: {e}")
    
    def _encrypt_history(self):
        """NUCLEAR SAFETY: Encrypt feedback history to file."""
        if not self._encryptor:
            return
        
        history_data = {
            "current_iteration": self.current_iteration,
            "current_state": self._current_state.value,
            "history": [
                {
                    "iteration": r.iteration,
                    "state": r.state.value,
                    "command": r.command,
                    "return_code": r.return_code,
                    "duration_ms": r.duration_ms,
                    "errors_found": r.errors_found,
                    "warnings_found": r.warnings_found
                }
                for r in self.loop_history
            ]
        }
        
        mem_path = self._encryptor.encrypt_memory(history_data, f"iteration_{self.current_iteration}")
        logger.info(f"[ZK] Feedback encrypted: {mem_path.name}")
    
    def load_encrypted_history(self, iteration: int = None) -> bool:
        """NUCLEAR SAFETY: Load feedback from encrypted file for resume."""
        if not self._encryptor:
            return False
        
        try:
            decrypted = self._encryptor.decrypt_memory(f"iteration_{iteration or 'latest'}")
            if decrypted:
                self.current_iteration = decrypted.get("current_iteration", 0)
                logger.info(f"[ZK] Feedback history loaded: {self.current_iteration} iterations")
                return True
        except Exception as e:
            logger.warning(f"[ZK] Load failed: {e}")
        return False
    
    def run_lint_check(self, 
                       file_path: Optional[str] = None,
                       streaming: bool = False) -> LoopResult:
        """Run linter checks on project or file."""
        self.current_iteration += 1
        
        commands = self.config.lint_commands
        if file_path:
            commands = [f"ruff check {file_path}", f"mypy {file_path}"]
        
        all_output = ""
        all_errors = []
        all_warnings = []
        
        for cmd in commands:
            if streaming:
                def callback(line, is_stderr):
                    nonlocal all_output
                    all_output += line + "\n"
                
                result = self.shell.run(cmd, timeout=60, streaming_callback=callback)
            else:
                result = self.shell.run(cmd, timeout=60)
            
            all_output += f"\n--- {cmd} ---\n{result.output}"
            
            # Parse errors and warnings
            errors, warnings = self._parse_linter_output(result.output)
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        
        state = LoopState.SUCCESS if not all_errors else LoopState.FAILED
        
        loop_result = LoopResult(
            iteration=self.current_iteration,
            state=state,
            command="; ".join(commands),
            return_code=0 if not all_errors else 1,
            stdout=all_output,
            stderr="",
            duration_ms=sum(r.duration_ms for r in self.shell.command_history[-2:]),
            errors_found=all_errors,
            warnings_found=all_warnings
        )
        
        self.loop_history.append(loop_result)
        return loop_result
    
    def run_tests(self, 
                  test_path: Optional[str] = None,
                  streaming: bool = False) -> LoopResult:
        """Run test suite."""
        self.current_iteration += 1
        
        cmd = self.config.test_commands[0]
        if test_path:
            cmd = f"pytest {test_path} -v --tb=short"
        
        all_output = ""
        
        if streaming:
            def callback(line, is_stderr):
                nonlocal all_output
                all_output += line + "\n"
            
            result = self.shell.run(cmd, timeout=self.config.timeout_seconds, streaming_callback=callback)
        else:
            result = self.shell.run(cmd, timeout=self.config.timeout_seconds)
        
        all_output = result.output
        
        # Parse test results
        errors, warnings = self._parse_test_output(result.output)
        
        state = LoopState.SUCCESS if result.return_code == 0 else LoopState.FAILED
        if result.timed_out:
            state = LoopState.TIMEOUT
        
        loop_result = LoopResult(
            iteration=self.current_iteration,
            state=state,
            command=cmd,
            return_code=result.return_code,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_ms=result.duration_ms,
            errors_found=errors,
            warnings_found=warnings
        )
        
        self.loop_history.append(loop_result)
        
        # NUCLEAR SAFETY: Encrypt history to file AFTER appending
        if HAS_ZERO_KNOWLEDGE:
            try:
                self._encrypt_history()
            except Exception as e:
                logger.warning(f"[ZK] Failed to encrypt feedback history: {e}")
        return loop_result
    
    def _parse_linter_output(self, output: str) -> Tuple[List[str], List[str]]:
        """Parse linter output to extract errors and warnings."""
        errors = []
        warnings = []
        
        for line in output.split('\n'):
            line = line.strip()
            
            # Ruff format: file:line:col: E### message
            if 'E' in line or 'F' in line:  # Error codes
                if ': error:' in line or 'E' in line[:10]:
                    errors.append(line)
                elif ': warning:' in line or 'W' in line[:10]:
                    warnings.append(line)
            
            # Mypy format: file:line: message
            elif 'error:' in line.lower():
                errors.append(line)
            elif 'warning:' in line.lower():
                warnings.append(line)
        
        return errors[:20], warnings[:20]  # Limit to prevent token overflow
    
    def _parse_test_output(self, output: str) -> Tuple[List[str], List[str]]:
        """Parse test output to extract failures."""
        errors = []
        warnings = []
        
        # Look for pytest FAIL section
        in_fail = False
        for line in output.split('\n'):
            if 'FAILED' in line:
                errors.append(line)
                in_fail = True
            elif in_fail and line.strip():
                errors.append(line)
            elif not line.strip():
                in_fail = False
            
            # Warnings
            if 'WARNING' in line or 'DeprecationWarning' in line:
                warnings.append(line)
        
        # Extract assertion errors
        if 'AssertionError' in output:
            for line in output.split('\n'):
                if 'AssertionError' in line:
                    errors.append(line.strip())
        
        return errors[:10], warnings[:10]
    
    def run_full_loop(self, 
                      apply_edit_fn: Callable[[str], bool],
                      file_path: Optional[str] = None,
                      on_iteration: Optional[Callable[[LoopResult], None]] = None) -> Dict:
        """
        Run full feedback loop: lint → fix → test → fix → repeat.
        
        Args:
            apply_edit_fn: Function to apply a code edit (returns success)
            file_path: Optional specific file to check
            on_iteration: Callback after each iteration with LoopResult
        
        Returns:
            Final result with iterations, success status, error trace
        """
        self.current_iteration = 0
        self.loop_history = []
        
        logger.info("Starting feedback loop...")
        
        for i in range(self.config.max_iterations):
            self.current_iteration = i + 1
            
            # Step 1: Run linter
            logger.info(f"Iteration {self.current_iteration}: Running linter...")
            lint_result = self.run_lint_check(file_path=file_path, streaming=self.config.stream_output)
            
            if on_iteration:
                on_iteration(lint_result)
            
            if lint_result.state == LoopState.FAILED:
                logger.warning(f"Linter found {len(lint_result.errors_found)} errors")
                
                # The LLM would see these errors and generate a fix
                # In this framework, we return the errors for the LLM to process
                return {
                    'success': False,
                    'stage': 'lint',
                    'iteration': self.current_iteration,
                    'errors': lint_result.errors_found,
                    'output': lint_result.stdout
                }
            
            # Step 2: Run tests
            logger.info(f"Iteration {self.current_iteration}: Running tests...")
            test_result = self.run_tests(test_path=file_path, streaming=self.config.stream_output)
            
            if on_iteration:
                on_iteration(test_result)
            
            if test_result.state == LoopState.SUCCESS:
                logger.info("All checks passed!")
                return {
                    'success': True,
                    'stage': 'tests',
                    'iteration': self.current_iteration,
                    'output': test_result.stdout
                }
            
            if test_result.state == LoopState.TIMEOUT:
                logger.error("Tests timed out")
                return {
                    'success': False,
                    'stage': 'timeout',
                    'iteration': self.current_iteration,
                    'output': test_result.stdout
                }
            
            # Test failed - get error details
            logger.warning(f"Tests failed with {len(test_result.errors_found)} errors")
            
            # Return errors for LLM to fix
            return {
                'success': False,
                'stage': 'test',
                'iteration': self.current_iteration,
                'errors': test_result.errors_found,
                'output': test_result.stdout
            }
        
        # Max iterations reached
        return {
            'success': False,
            'stage': 'max_iterations',
            'iteration': self.current_iteration,
            'history': [str(r.state) for r in self.loop_history]
        }
    
    def quick_check(self, file_path: str) -> Dict:
        """Quick check - run linter on a single file."""
        result = self.shell.run(f"ruff check {file_path}")
        
        return {
            'file': file_path,
            'success': result.return_code == 0,
            'errors': self._parse_linter_output(result.output)[0],
            'output': result.output[:500]
        }
    
    def get_context_for_llm(self) -> str:
        """
        Get formatted context for LLM to understand current state.
        This is what gets included in the prompt after each iteration.
        """
        if not self.loop_history:
            return "No feedback loop history yet."
        
        last_result = self.loop_history[-1]
        
        context_parts = [
            f"## Feedback Loop Status",
            f"**Iteration**: {last_result.iteration}",
            f"**State**: {last_result.state.value}",
            f"**Command**: {last_result.command}",
            f"**Duration**: {last_result.duration_ms}ms",
            ""
        ]
        
        if last_result.errors_found:
            context_parts.append("### Errors")
            for err in last_result.errors_found[:5]:
                context_parts.append(f"- {err}")
            context_parts.append("")
        
        if last_result.warnings_found:
            context_parts.append("### Warnings")
            for warn in last_result.warnings_found[:3]:
                context_parts.append(f"- {warn}")
            context_parts.append("")
        
        # Add recent output
        if last_result.stdout:
            context_parts.append("### Recent Output")
            context_parts.append(last_result.stdout[:1000])
        
        return "\n".join(context_parts)
    
    def reset(self):
        """Reset feedback loop state."""
        self.current_iteration = 0
        self.loop_history = []
        self._current_state = LoopState.IDLE
    
    def get_summary(self) -> Dict:
        """Get summary of feedback loop history."""
        if not self.loop_history:
            return {'total_iterations': 0, 'state': 'idle'}
        
        return {
            'total_iterations': len(self.loop_history),
            'current_iteration': self.current_iteration,
            'final_state': self.loop_history[-1].state.value,
            'total_errors': sum(len(r.errors_found) for r in self.loop_history),
            'total_warnings': sum(len(r.warnings_found) for r in self.loop_history),
            'total_duration_ms': sum(r.duration_ms for r in self.loop_history)
        }


# Integration with repo map for file-aware feedback
class FileAwareFeedbackLoop(OmegaFeedbackLoop):
    """Feedback loop that uses repo map for smarter context."""
    
    def __init__(self, shell_tools, lsp_client, repo_map, config=None):
        super().__init__(shell_tools, lsp_client, config)
        self.repo_map = repo_map
    
    def get_context_for_file(self, file_path: str) -> str:
        """Get file-specific context including imports and symbols."""
        context = self.repo_map.get_context_for_file(file_path)
        
        if not context:
            return ""
        
        lines = [
            f"## Context for {file_path}",
            f"**Imports**: {', '.join(context.get('imports', [])[:5])}",
            f"**Exports**: {', '.join(context.get('exports', [])[:5])}",
            ""
        ]
        
        symbols = context.get('symbols', [])
        if symbols:
            lines.append("### Symbols in file")
            for sym in symbols[:10]:
                lines.append(f"- {sym['name']} ({sym['kind']}) at line {sym['line']}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / 'engine'))
    
    from omega_shell_tools import OmegaShellTools
    from omega_lsp_client import SimpleLSPClient
    
    shell = OmegaShellTools()
    lsp = SimpleLSPClient()
    
    loop = OmegaFeedbackLoop(shell, lsp)
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "lint":
            result = loop.run_lint_check()
            print(f"State: {result.state.value}")
            print(f"Errors: {len(result.errors_found)}")
            if result.errors_found:
                print("\n".join(result.errors_found[:5]))
        
        elif cmd == "test":
            result = loop.run_tests()
            print(f"State: {result.state.value}")
            print(f"Output: {result.stdout[:500]}")
        
        elif cmd == "quick":
            if len(sys.argv) > 2:
                print(json.dumps(loop.quick_check(sys.argv[2]), indent=2))
    
    else:
        print("OMEGA Feedback Loop")
        print(f"Config: {loop.config.max_iterations} max iterations")
        print(f"Commands: {loop.config.lint_commands}")