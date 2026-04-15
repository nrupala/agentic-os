#!/usr/bin/env python3
"""
agentic-OS File Operations Tool
================================
Real file read/write/edit operations for agentic-OS

Provides:
- ReadFile: Read file contents
- WriteFile: Create/overwrite files  
- EditFile: Patch specific lines
- Glob: Pattern matching
- Grep: Search in files
- Bash: Execute shell commands
"""

import os
import sys
import re
import subprocess
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileOperationResult:
    """Result of a file operation."""
    success: bool
    operation: str
    path: str
    content: Optional[str] = None
    lines: Optional[int] = None
    error: Optional[str] = None
    backup_path: Optional[str] = None


class FileOperations:
    """
    File operations tool for agentic-OS.
    
    Usage:
        ops = FileOperations("/path/to/project")
        result = ops.read("src/main.py")
        result = ops.write("src/new.py", "print('hello')")
        result = ops.edit("src/main.py", "old line", "new line")
        result = ops.grep("src/", "function.*")
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.backup_dir = self.project_root / ".agentic-os" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.operation_log = []
    
    def _log_operation(self, operation: str, path: str, success: bool, error: str = None):
        """Log operation for audit trail."""
        self.operation_log.append({
            "operation": operation,
            "path": str(path),
            "success": success,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def read(self, path: str) -> FileOperationResult:
        """Read a file and return its contents."""
        try:
            file_path = self.project_root / path if not Path(path).is_absolute() else Path(path)
            
            if not file_path.exists():
                return FileOperationResult(
                    success=False,
                    operation="read",
                    path=str(path),
                    error=f"File not found: {path}"
                )
            
            content = file_path.read_text(encoding='utf-8')
            
            self._log_operation("read", str(path), True)
            
            return FileOperationResult(
                success=True,
                operation="read",
                path=str(path),
                content=content,
                lines=len(content.splitlines())
            )
            
        except Exception as e:
            self._log_operation("read", str(path), False, str(e))
            return FileOperationResult(
                success=False,
                operation="read",
                path=str(path),
                error=str(e)
            )
    
    def write(self, path: str, content: str, create_backup: bool = True) -> FileOperationResult:
        """Write content to a file, creating directories as needed."""
        try:
            file_path = self.project_root / path if not Path(path).is_absolute() else Path(path)
            
            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup if file exists
            backup_path = None
            if create_backup and file_path.exists():
                backup_path = self._create_backup(file_path)
            
            # Write file
            file_path.write_text(content, encoding='utf-8')
            
            self._log_operation("write", str(path), True)
            
            return FileOperationResult(
                success=True,
                operation="write",
                path=str(path),
                lines=len(content.splitlines()),
                backup_path=backup_path
            )
            
        except Exception as e:
            self._log_operation("write", str(path), False, str(e))
            return FileOperationResult(
                success=False,
                operation="write",
                path=str(path),
                error=str(e)
            )
    
    def edit(self, path: str, old_content: str, new_content: str) -> FileOperationResult:
        """
        Edit a file by replacing old_content with new_content.
        
        This does a simple string replacement - for more complex edits,
        use the line-based edit_line method.
        """
        try:
            # Read current content
            read_result = self.read(path)
            if not read_result.success:
                return read_result
            
            current_content = read_result.content
            
            # Check if old content exists
            if old_content not in current_content:
                return FileOperationResult(
                    success=False,
                    operation="edit",
                    path=str(path),
                    error=f"Content not found: {old_content[:100]}..."
                )
            
            # Create backup
            file_path = self.project_root / path if not Path(path).is_absolute() else Path(path)
            backup_path = self._create_backup(file_path)
            
            # Replace
            new_file_content = current_content.replace(old_content, new_content)
            
            # Write
            file_path.write_text(new_file_content, encoding='utf-8')
            
            self._log_operation("edit", str(path), True)
            
            return FileOperationResult(
                success=True,
                operation="edit",
                path=str(path),
                lines=len(new_file_content.splitlines()),
                backup_path=backup_path
            )
            
        except Exception as e:
            self._log_operation("edit", str(path), False, str(e))
            return FileOperationResult(
                success=False,
                operation="edit",
                path=str(path),
                error=str(e)
            )
    
    def edit_line(self, path: str, line_number: int, new_content: str) -> FileOperationResult:
        """Edit a specific line number in a file."""
        try:
            read_result = self.read(path)
            if not read_result.success:
                return read_result
            
            lines = read_result.content.splitlines(keepends=True)
            
            if line_number < 1 or line_number > len(lines):
                return FileOperationResult(
                    success=False,
                    operation="edit_line",
                    path=str(path),
                    error=f"Line {line_number} out of range (1-{len(lines)})"
                )
            
            # Create backup
            file_path = self.project_root / path if not Path(path).is_absolute() else Path(path)
            backup_path = self._create_backup(file_path)
            
            # Replace line (line_number is 1-indexed)
            lines[line_number - 1] = new_content + ('\n' if not new_content.endswith('\n') else '')
            
            # Write back
            file_path.write_text(''.join(lines), encoding='utf-8')
            
            self._log_operation("edit_line", str(path), True)
            
            return FileOperationResult(
                success=True,
                operation="edit_line",
                path=str(path),
                lines=len(lines),
                backup_path=backup_path
            )
            
        except Exception as e:
            self._log_operation("edit_line", str(path), False, str(e))
            return FileOperationResult(
                success=False,
                operation="edit_line",
                path=str(path),
                error=str(e)
            )
    
    def append(self, path: str, content: str) -> FileOperationResult:
        """Append content to a file."""
        try:
            file_path = self.project_root / path if not Path(path).is_absolute() else Path(path)
            
            # Create file if it doesn't exist
            if not file_path.exists():
                file_path.write_text('', encoding='utf-8')
            
            # Append
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            self._log_operation("append", str(path), True)
            
            return FileOperationResult(
                success=True,
                operation="append",
                path=str(path),
                lines=len(content.splitlines())
            )
            
        except Exception as e:
            self._log_operation("append", str(path), False, str(e))
            return FileOperationResult(
                success=False,
                operation="append",
                path=str(path),
                error=str(e)
            )
    
    def delete(self, path: str, create_backup: bool = True) -> FileOperationResult:
        """Delete a file (with backup)."""
        try:
            file_path = self.project_root / path if not Path(path).is_absolute() else Path(path)
            
            if not file_path.exists():
                return FileOperationResult(
                    success=False,
                    operation="delete",
                    path=str(path),
                    error=f"File not found: {path}"
                )
            
            # Create backup before delete
            backup_path = None
            if create_backup:
                backup_path = self._create_backup(file_path)
            
            # Delete
            file_path.unlink()
            
            self._log_operation("delete", str(path), True)
            
            return FileOperationResult(
                success=True,
                operation="delete",
                path=str(path),
                backup_path=backup_path
            )
            
        except Exception as e:
            self._log_operation("delete", str(path), False, str(e))
            return FileOperationResult(
                success=False,
                operation="delete",
                path=str(path),
                error=str(e)
            )
    
    def glob(self, pattern: str, path: str = None) -> FileOperationResult:
        """Find files matching a glob pattern."""
        try:
            search_path = self.project_root / path if path else self.project_root
            
            # Convert glob pattern
            if not pattern.startswith('**/'):
                pattern = '**/' + pattern
            
            matches = list(search_path.glob(pattern))
            
            # Filter out common ignore directories
            matches = [
                m for m in matches 
                if m.is_file() and not any(
                    ign in m.parts 
                    for ign in ['node_modules', '__pycache__', '.git', '.venv', 'venv', 'dist', 'build']
                )
            ]
            
            self._log_operation("glob", pattern, True)
            
            return FileOperationResult(
                success=True,
                operation="glob",
                path=pattern,
                content='\n'.join([str(m.relative_to(search_path)) for m in matches]),
                lines=len(matches)
            )
            
        except Exception as e:
            self._log_operation("glob", pattern, False, str(e))
            return FileOperationResult(
                success=False,
                operation="glob",
                path=pattern,
                error=str(e)
            )
    
    def grep(self, path: str, pattern: str, case_sensitive: bool = True) -> FileOperationResult:
        """Search for pattern in files."""
        try:
            search_path = self.project_root / path if not Path(path).is_absolute() else Path(path)
            
            if not search_path.exists():
                return FileOperationResult(
                    success=False,
                    operation="grep",
                    path=str(path),
                    error=f"Path not found: {path}"
                )
            
            results = []
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            if search_path.is_file():
                files_to_search = [search_path]
            else:
                files_to_search = [
                    f for f in search_path.rglob('*')
                    if f.is_file() and not any(
                        ign in f.parts 
                        for ign in ['node_modules', '__pycache__', '.git', '.venv']
                    )
                ]
            
            for file_path in files_to_search:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    for i, line in enumerate(content.splitlines(), 1):
                        if regex.search(line):
                            results.append(f"{file_path.relative_to(search_path)}:{i}:{line.rstrip()}")
                except:
                    pass
            
            self._log_operation("grep", f"{path}:{pattern}", True)
            
            return FileOperationResult(
                success=True,
                operation="grep",
                path=f"{path}:{pattern}",
                content='\n'.join(results),
                lines=len(results)
            )
            
        except Exception as e:
            self._log_operation("grep", f"{path}:{pattern}", False, str(e))
            return FileOperationResult(
                success=False,
                operation="grep",
                path=f"{path}:{pattern}",
                error=str(e)
            )
    
    def bash(self, command: str, cwd: str = None, timeout: int = 60) -> FileOperationResult:
        """Execute a bash command."""
        try:
            work_dir = self.project_root / cwd if cwd else self.project_root
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = result.stdout + result.stderr
            
            self._log_operation("bash", command, result.returncode == 0, 
                              error=output if result.returncode != 0 else None)
            
            return FileOperationResult(
                success=result.returncode == 0,
                operation="bash",
                path=command,
                content=output,
                error=None if result.returncode == 0 else f"Exit code: {result.returncode}"
            )
            
        except subprocess.TimeoutExpired:
            self._log_operation("bash", command, False, "Timeout")
            return FileOperationResult(
                success=False,
                operation="bash",
                path=command,
                error="Command timed out"
            )
        except Exception as e:
            self._log_operation("bash", command, False, str(e))
            return FileOperationResult(
                success=False,
                operation="bash",
                path=command,
                error=str(e)
            )
    
    def _create_backup(self, file_path: Path) -> str:
        """Create a backup of a file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        hash_suffix = hashlib.md5(str(file_path).encode()).hexdigest()[:6]
        backup_name = f"{file_path.name}.{timestamp}.{hash_suffix}.bak"
        backup_path = self.backup_dir / backup_name
        
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        backup_path.write_bytes(file_path.read_bytes())
        
        return str(backup_path.relative_to(self.project_root))
    
    def get_operation_log(self) -> List[Dict]:
        """Get the operation log."""
        return self.operation_log
    
    def rollback(self, backup_path: str) -> FileOperationResult:
        """Rollback from a backup."""
        try:
            backup_file = self.project_root / backup_path
            original_path = str(backup_path).rsplit('.', 3)[0]
            original_file = self.project_root / original_path
            
            if not backup_file.exists():
                return FileOperationResult(
                    success=False,
                    operation="rollback",
                    path=original_path,
                    error=f"Backup not found: {backup_path}"
                )
            
            # Restore from backup
            original_file.parent.mkdir(parents=True, exist_ok=True)
            original_file.write_bytes(backup_file.read_bytes())
            
            # Delete backup
            backup_file.unlink()
            
            self._log_operation("rollback", original_path, True)
            
            return FileOperationResult(
                success=True,
                operation="rollback",
                path=original_path
            )
            
        except Exception as e:
            self._log_operation("rollback", backup_path, False, str(e))
            return FileOperationResult(
                success=False,
                operation="rollback",
                path=backup_path,
                error=str(e)
            )


# ============================================================================
# CLI for Testing
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="agentic-OS File Operations")
    parser.add_argument("operation", choices=["read", "write", "edit", "glob", "grep", "bash", "ls"])
    parser.add_argument("path", help="File path or glob pattern")
    parser.add_argument("--content", help="Content for write/edit operations")
    parser.add_argument("--old", help="Old content for edit")
    parser.add_argument("--new", help="New content for edit")
    parser.add_argument("--project", default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    ops = FileOperations(args.project)
    
    if args.operation == "read":
        result = ops.read(args.path)
    elif args.operation == "write":
        result = ops.write(args.path, args.content or "")
    elif args.operation == "edit":
        result = ops.edit(args.path, args.old or "", args.new or "")
    elif args.operation == "glob":
        result = ops.glob(args.path)
    elif args.operation == "grep":
        result = ops.grep(args.path, args.content or "")
    elif args.operation == "bash":
        result = ops.bash(args.path)
    elif args.operation == "ls":
        result = ops.bash(f"ls -la {args.path}")
    else:
        print(f"Unknown operation: {args.operation}")
        return
    
    print(f"Success: {result.success}")
    print(f"Operation: {result.operation}")
    print(f"Path: {result.path}")
    if result.content:
        print(f"\n--- Content ---")
        print(result.content[:1000] + "..." if len(result.content) > 1000 else result.content)
    if result.error:
        print(f"\n--- Error ---")
        print(result.error)
    if result.backup_path:
        print(f"\nBackup: {result.backup_path}")


if __name__ == "__main__":
    main()
