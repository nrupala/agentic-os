#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
OMEGA Unified Shell Execution
============================
Centralized shell command execution that handles:
- OmegaShellTools.run()
- FeedbackLoop.run_linter()
- FeedbackLoop.run_tests()

This ensures CONSISTENT execution across the entire system.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
import shlex

@dataclass
class CommandResult:
    """Standard command result."""
    stdout: str
    stderr: str
    returncode: int
    success: bool
    
    def __post_init__(self):
        self.success = self.returncode == 0

class UnifiedShell:
    """
    Unified shell execution - single source of truth for command execution.
    All OMEGA components should use this class.
    """
    
    def __init__(self, root_path: str = None):
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.command_history: List[Dict] = []
        
        # Safe commands whitelist
        self.SAFE_COMMANDS = {
            "python", "python3", "pip", "pip3", "pytest", "ruff", "pyright",
            "git", "ls", "dir", "cat", "type", "echo", "mkdir", "rm", "del",
            "cd", "chdir", "pwd", "find", "grep", "rg", "head", "tail",
            "node", "npm", "npx", "cargo", "rustc", "go", "docker",
        }
        
        # Allowed file extensions
        self.ALLOWED_EXTENSIONS = {".py", ".js", ".ts", ".json", ".md", ".txt", ".yml", ".yaml"}
    
    def is_command_safe(self, cmd: str) -> bool:
        """Check if command is safe to execute."""
        if not cmd:
            return False
            
        # Get the base command
        parts = shlex.split(cmd)
        if not parts:
            return False
            
        base_cmd = parts[0].lower()
        
        # Allow safe commands
        if base_cmd in self.SAFE_COMMANDS:
            return True
            
        # Allow scripts in allowed directories
        for part in parts:
            path = Path(part)
            if path.exists() and path.suffix in self.ALLOWED_EXTENSIONS:
                return True
                
        return False
    
    def run(self, cmd: str, timeout: int = 30, cwd: str = None) -> CommandResult:
        """
        Execute a shell command.
        
        Args:
            cmd: Command string
            timeout: Timeout in seconds
            cwd: Working directory
            
        Returns:
            CommandResult with stdout, stderr, returncode
        """
        # Check safety
        if not self.is_command_safe(cmd):
            return CommandResult(
                stdout="",
                stderr=f"Command not allowed: {cmd}",
                returncode=1,
                success=False
            )
        
        # Execute
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd or str(self.root_path)
            )
            
            # Record history
            self.command_history.append({
                "cmd": cmd,
                "returncode": result.returncode,
                "timeout": timeout
            })
            
            return CommandResult(
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                success=result.returncode == 0
            )
            
        except subprocess.TimeoutExpired:
            return CommandResult(
                stdout="",
                stderr=f"Command timed out after {timeout}s",
                returncode=124,
                success=False
            )
        except Exception as e:
            return CommandResult(
                stdout="",
                stderr=str(e),
                returncode=1,
                success=False
            )
    
    def run_linter(self, file_path: str = ".", tool: str = "ruff") -> CommandResult:
        """
        Run linter on code.
        
        Args:
            file_path: Path to file or directory
            tool: Linter tool (ruff, pylint, flake8)
            
        Returns:
            CommandResult
        """
        if tool == "ruff":
            return self.run(f"ruff check {file_path}", timeout=30)
        elif tool == "pylint":
            return self.run(f"pylint {file_path}", timeout=60)
        elif tool == "flake8":
            return self.run(f"flake8 {file_path}", timeout=60)
        elif tool == "py_compile":
            return self.run(f"python -m py_compile {file_path}", timeout=30)
        else:
            return self.run(f"{tool} {file_path}", timeout=30)
    
    def run_tests(self, test_path: str = "tests/", markers: str = "") -> CommandResult:
        """
        Run test suite.
        
        Args:
            test_path: Path to tests
            markers: Pytest markers (unit, integration, etc.)
            
        Returns:
            CommandResult
        """
        cmd = "pytest"
        if markers:
            cmd += f" -m {markers}"
        cmd += f" {test_path}"
        
        return self.run(cmd, timeout=120)
    
    def run_typecheck(self, file_path: str = ".") -> CommandResult:
        """
        Run type checker.
        
        Args:
            file_path: Path to check
            
        Returns:
            CommandResult
        """
        # Try pyright first, then mypy
        result = self.run(f"pyright {file_path}", timeout=60)
        if result.returncode == 127:  # pyright not found
            result = self.run(f"mypy {file_path}", timeout=60)
        return result
    
    def verify_code(self, code: str) -> Dict[str, Any]:
        """
        Verify code by compiling.
        
        Args:
            code: Python code string
            
        Returns:
            Dict with verification results
        """
        import ast
        
        result = {
            "valid_syntax": False,
            "errors": [],
            "ast": None
        }
        
        try:
            ast.parse(code)
            result["valid_syntax"] = True
            result["ast"] = ast.dump(code)
        except SyntaxError as e:
            result["errors"].append(f"SyntaxError: {e}")
        except Exception as e:
            result["errors"].append(f"Error: {e}")
        
        return result
    
    def get_history(self) -> List[Dict]:
        """Get command history."""
        return self.command_history
    
    def clear_history(self):
        """Clear command history."""
        self.command_history = []


# Singleton instance for easy import
_shell_instance = None

def get_shell(root_path: str = None) -> UnifiedShell:
    """Get singleton shell instance."""
    global _shell_instance
    if _shell_instance is None:
        _shell_instance = UnifiedShell(root_path)
    return _shell_instance


if __name__ == "__main__":
    # Test the shell
    shell = UnifiedShell()
    
    print("=== UnifiedShell Test ===\n")
    
    # Test safe command
    result = shell.run("echo 'Hello OMEGA'")
    print(f"Echo: {result.stdout.strip()}")
    print(f"Safe: {result.success}")
    
    # Test linter
    result = shell.run_linter(".")
    print(f"\nLinter return code: {result.returncode}")
    
    # Test verify
    verify = shell.verify_code("def test(): return 42")
    print(f"\nVerify: {verify}")