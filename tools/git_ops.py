"""
MIT License
Copyright (c) 2026 Nrupal Akolkar
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class GitStatus(Enum):
    CLEAN = "clean"
    MODIFIED = "modified"
    UNTRACKED = "untracked"
    STAGED = "staged"
    CONFLICT = "conflict"


class DiffType(Enum):
    ADDED = "added"
    DELETED = "deleted"
    MODIFIED = "modified"
    RENAMED = "renamed"


@dataclass
class GitUser:
    name: str
    email: str


@dataclass
class FileDiff:
    path: str
    diff_type: DiffType
    additions: int = 0
    deletions: int = 0
    hunks: List[str] = field(default_factory=list)


@dataclass
class Commit:
    hash: str
    short_hash: str
    message: str
    author: str
    author_email: str
    date: datetime
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0


@dataclass
class Branch:
    name: str
    is_current: bool
    is_remote: bool
    tracking_branch: Optional[str] = None


@dataclass
class RepoStatus:
    is_repo: bool
    branch: str
    ahead: int = 0
    behind: int = 0
    staged: List[str] = field(default_factory=list)
    modified: List[str] = field(default_factory=list)
    untracked: List[str] = field(default_factory=list)
    conflicted: List[str] = field(default_factory=list)


class GitProvider:
    """Git operations provider with full version control capabilities."""

    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.user: Optional[GitUser] = None
        self._detect_user()

    def _run_git(self, *args, capture_output: bool = True) -> Tuple[int, str, str]:
        """Execute git command and return result."""
        cmd = ['git'] + list(args)
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return -1, "", "Git command timed out"
        except FileNotFoundError:
            return -1, "", "Git not found. Is Git installed?"
        except Exception as e:
            return -1, "", str(e)

    def _detect_user(self):
        """Detect current git user."""
        _, stdout, _ = self._run_git('config', '--get', 'user.name')
        if stdout:
            _, email, _ = self._run_git('config', '--get', 'user.email')
            self.user = GitUser(name=stdout, email=email)
        else:
            self.user = GitUser(name="Nrupal", email="nrupala@users.noreply.github.com")

    def is_repo(self) -> bool:
        """Check if path is a git repository."""
        code, _, _ = self._run_git('rev-parse', '--git-dir')
        return code == 0

    def init(self, bare: bool = False) -> Dict:
        """Initialize a new git repository."""
        args = ['init']
        if bare:
            args.append('--bare')
        
        code, stdout, stderr = self._run_git(*args)
        
        if code == 0:
            return {
                "success": True,
                "message": f"Repository initialized at {self.repo_path}",
                "path": str(self.repo_path)
            }
        return {"success": False, "error": stderr}

    def clone(self, url: str, depth: Optional[int] = None, branch: Optional[str] = None) -> Dict:
        """Clone a remote repository."""
        args = ['clone']
        if depth:
            args.extend(['--depth', str(depth)])
        if branch:
            args.extend(['--branch', branch])
        args.append(url)
        args.append(str(self.repo_path))
        
        code, stdout, stderr = self._run_git(*args)
        
        if code == 0:
            return {
                "success": True,
                "message": f"Cloned from {url}",
                "path": str(self.repo_path)
            }
        return {"success": False, "error": stderr}

    def status(self) -> RepoStatus:
        """Get repository status."""
        if not self.is_repo():
            return RepoStatus(is_repo=False, branch="")
        
        code, stdout, _ = self._run_git('rev-parse', '--abbrev-ref', 'HEAD')
        branch = stdout if code == 0 else "unknown"
        
        code, stdout, _ = self._run_git('status', '--porcelain')
        lines = stdout.split('\n') if stdout else []
        
        staged, modified, untracked, conflicted = [], [], [], []
        
        for line in lines:
            if not line:
                continue
            status_code = line[:2]
            path = line[3:].strip('"')
            
            if 'U' in status_code or status_code == 'DD' or status_code == 'AA':
                conflicted.append(path)
            elif status_code[0] in 'MADRC':
                staged.append(path)
            if status_code[1] in 'MDRC':
                modified.append(path)
            if status_code == '??':
                untracked.append(path)
        
        code, stdout, _ = self._run_git('rev-list', '--left-right', '--count', '@{upstream}...HEAD')
        ahead, behind = 0, 0
        if code == 0 and stdout:
            parts = stdout.split()
            if len(parts) == 2:
                behind, ahead = int(parts[0]), int(parts[1])
        
        return RepoStatus(
            is_repo=True,
            branch=branch,
            ahead=ahead,
            behind=behind,
            staged=staged,
            modified=modified,
            untracked=untracked,
            conflicted=conflicted
        )

    def add(self, files: List[str] = None, all: bool = False) -> Dict:
        """Stage files for commit."""
        args = ['add']
        if all:
            args.append('-A')
        elif files:
            args.extend(files)
        else:
            return {"success": False, "error": "No files specified"}
        
        code, stdout, stderr = self._run_git(*args)
        
        if code == 0:
            return {
                "success": True,
                "message": f"Staged {len(files) if files else 'all'} file(s)",
                "staged": stdout.split('\n') if stdout else []
            }
        return {"success": False, "error": stderr}

    def commit(self, message: str, amend: bool = False, allow_empty: bool = False) -> Dict:
        """Create a new commit."""
        args = ['commit', '-m', message]
        if amend:
            args.insert(2, '--amend')
        if allow_empty:
            args.insert(2, '--allow-empty')
        
        code, stdout, stderr = self._run_git(*args)
        
        if code == 0:
            return {
                "success": True,
                "message": "Commit created",
                "commit": stdout.split('\n')[0] if stdout else ""
            }
        return {"success": False, "error": stderr}

    def log(self, max_count: int = 10, format: str = None, author: str = None) -> List[Commit]:
        """Get commit history."""
        args = ['log', f'--max-count={max_count}', '--format=%H|%h|%s|%an|%ae|%aI']
        if author:
            args.extend(['--author', author])
        
        code, stdout, _ = self._run_git(*args)
        
        commits = []
        if code == 0 and stdout:
            for line in stdout.split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 6:
                    commits.append(Commit(
                        hash=parts[0],
                        short_hash=parts[1],
                        message=parts[2],
                        author=parts[3],
                        author_email=parts[4],
                        date=datetime.fromisoformat(parts[5])
                    ))
        
        return commits

    def diff(self, target: str = None, cached: bool = False) -> List[FileDiff]:
        """Get diff for staged or unstaged changes."""
        args = ['diff', '--numstat']
        if cached:
            args.append('--cached')
        if target:
            args.append(target)
        
        code, stdout, _ = self._run_git(*args)
        
        diffs = []
        if code == 0 and stdout:
            for line in stdout.split('\n'):
                if not line:
                    continue
                parts = line.split('\t')
                if len(parts) >= 3:
                    path = parts[2]
                    additions = int(parts[0]) if parts[0] != '-' else 0
                    deletions = int(parts[1]) if parts[1] != '-' else 0
                    
                    diff_type = DiffType.MODIFIED
                    if additions > 0 and deletions == 0:
                        diff_type = DiffType.ADDED
                    elif additions == 0 and deletions > 0:
                        diff_type = DiffType.DELETED
                    
                    diffs.append(FileDiff(
                        path=path,
                        diff_type=diff_type,
                        additions=additions,
                        deletions=deletions
                    ))
        
        return diffs

    def branch(self, list: bool = False, create: str = None, delete: str = None,
               current: bool = False) -> Dict:
        """Branch operations."""
        if list:
            code, stdout, _ = self._run_git('branch', '-a')
            branches = []
            if code == 0 and stdout:
                for line in stdout.split('\n'):
                    if not line:
                        continue
                    is_current = line.startswith('*')
                    name = line[2:].strip()
                    is_remote = '/' in name and not name.startswith('*')
                    branches.append(Branch(
                        name=name,
                        is_current=is_current,
                        is_remote=is_remote
                    ))
            return {"success": True, "branches": branches}
        
        if create:
            code, _, stderr = self._run_git('branch', create)
            if code == 0:
                return {"success": True, "message": f"Branch '{create}' created"}
            return {"success": False, "error": stderr}
        
        if delete:
            code, _, stderr = self._run_git('branch', '-d', delete)
            if code == 0:
                return {"success": True, "message": f"Branch '{delete}' deleted"}
            return {"success": False, "error": stderr}
        
        if current:
            code, stdout, _ = self._run_git('rev-parse', '--abbrev-ref', 'HEAD')
            if code == 0:
                return {"success": True, "branch": stdout}
            return {"success": False, "error": "Not on any branch"}
        
        return {"success": False, "error": "No operation specified"}

    def checkout(self, ref: str, create_branch: str = None, force: bool = False) -> Dict:
        """Checkout a branch or commit."""
        args = ['checkout']
        if force:
            args.append('--force')
        if create_branch:
            args.extend(['-b', create_branch])
        args.append(ref)
        
        code, _, stderr = self._run_git(*args)
        
        if code == 0:
            branch_name = create_branch if create_branch else ref
            return {"success": True, "message": f"Switched to '{branch_name}'"}
        return {"success": False, "error": stderr}

    def merge(self, branch: str, no_ff: bool = False, abort: bool = False) -> Dict:
        """Merge a branch."""
        if abort:
            code, _, stderr = self._run_git('merge', '--abort')
            if code == 0:
                return {"success": True, "message": "Merge aborted"}
            return {"success": False, "error": stderr}
        
        args = ['merge']
        if no_ff:
            args.append('--no-ff')
        args.append(branch)
        
        code, stdout, stderr = self._run_git(*args)
        
        if code == 0:
            return {"success": True, "message": f"Merged '{branch}'"}
        return {"success": False, "error": stderr}

    def pull(self, rebase: bool = False,ff_only: bool = False) -> Dict:
        """Pull changes from remote."""
        args = ['pull']
        if rebase:
            args.append('--rebase')
        if ff_only:
            args.append('--ff-only')
        
        code, stdout, stderr = self._run_git(*args)
        
        if code == 0:
            return {"success": True, "message": "Pull successful", "output": stdout}
        return {"success": False, "error": stderr}

    def push(self, set_upstream: bool = False, force: bool = False,
             delete: bool = False, remote: str = 'origin', branch: str = None) -> Dict:
        """Push changes to remote."""
        args = ['push']
        if force:
            args.append('--force')
        if delete:
            args.append('--delete')
        if set_upstream:
            args.append('-u')
        if remote:
            args.append(remote)
        if branch:
            args.append(branch)
        
        code, stdout, stderr = self._run_git(*args)
        
        if code == 0:
            action = "Deleted" if delete else "Pushed"
            return {"success": True, "message": f"{action} to {remote}"}
        return {"success": False, "error": stderr}

    def stash(self, push: bool = False, pop: bool = False, list: bool = False,
              drop: bool = False, apply: bool = False, message: str = None) -> Dict:
        """Stash operations."""
        if list:
            code, stdout, _ = self._run_git('stash', 'list')
            if code == 0:
                stashes = []
                for line in stdout.split('\n'):
                    if line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            stashes.append({
                                "index": parts[0].strip(),
                                "message": parts[1].strip()
                            })
                return {"success": True, "stashes": stashes}
            return {"success": False, "error": "Failed to list stashes"}
        
        if push:
            args = ['stash']
            if message:
                args.extend(['push', '-m', message])
            else:
                args.append('push')
            code, stdout, stderr = self._run_git(*args)
            if code == 0:
                return {"success": True, "message": "Changes stashed"}
            return {"success": False, "error": stderr}
        
        if pop:
            code, _, stderr = self._run_git('stash', 'pop')
            if code == 0:
                return {"success": True, "message": "Stash applied"}
            return {"success": False, "error": stderr}
        
        if drop:
            code, _, stderr = self._run_git('stash', 'drop')
            if code == 0:
                return {"success": True, "message": "Stash dropped"}
            return {"success": False, "error": stderr}
        
        if apply:
            code, _, stderr = self._run_git('stash', 'apply')
            if code == 0:
                return {"success": True, "message": "Stash applied"}
            return {"success": False, "error": stderr}
        
        return {"success": False, "error": "No operation specified"}

    def reset(self, ref: str = None, mode: str = 'mixed', hard: bool = False) -> Dict:
        """Reset HEAD to a state."""
        args = ['reset']
        if hard:
            args.append('--hard')
        else:
            args.append(f'--{mode}')
        if ref:
            args.append(ref)
        
        code, _, stderr = self._run_git(*args)
        
        if code == 0:
            return {"success": True, "message": "Reset complete"}
        return {"success": False, "error": stderr}

    def revert(self, commit: str, no_commit: bool = False) -> Dict:
        """Revert a commit."""
        args = ['revert']
        if no_commit:
            args.append('--no-commit')
        args.append(commit)
        
        code, _, stderr = self._run_git(*args)
        
        if code == 0:
            return {"success": True, "message": f"Reverted {commit[:8]}"}
        return {"success": False, "error": stderr}

    def tag(self, name: str, annotation: str = None, message: str = None,
            delete: bool = False, list: bool = False) -> Dict:
        """Tag operations."""
        if list:
            code, stdout, _ = self._run_git('tag', '-l')
            if code == 0:
                return {"success": True, "tags": stdout.split('\n') if stdout else []}
            return {"success": False, "error": "Failed to list tags"}
        
        if delete:
            code, _, stderr = self._run_git('tag', '-d', name)
            if code == 0:
                return {"success": True, "message": f"Tag '{name}' deleted"}
            return {"success": False, "error": stderr}
        
        args = ['tag']
        if annotation:
            args.extend(['-a', name, '-m', annotation])
        elif message:
            args.extend(['-a', name, '-m', message])
        else:
            args.append(name)
        
        code, _, stderr = self._run_git(*args)
        
        if code == 0:
            return {"success": True, "message": f"Tag '{name}' created"}
        return {"success": False, "error": stderr}

    def remote(self, list: bool = False, add: str = None, remove: bool = False,
               update: bool = False) -> Dict:
        """Remote operations."""
        if list:
            code, stdout, _ = self._run_git('remote', '-v')
            if code == 0:
                remotes = []
                for line in stdout.split('\n') if stdout else []:
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            remotes.append({"name": parts[0], "url": parts[1]})
                return {"success": True, "remotes": remotes}
            return {"success": False, "error": "Failed to list remotes"}
        
        if add:
            code, _, stderr = self._run_git('remote', 'add', add)
            if code == 0:
                return {"success": True, "message": f"Remote '{add}' added"}
            return {"success": False, "error": stderr}
        
        if remove:
            code, _, stderr = self._run_git('remote', 'remove', remove)
            if code == 0:
                return {"success": True, "message": f"Remote '{remove}' removed"}
            return {"success": False, "error": stderr}
        
        if update:
            code, _, stderr = self._run_git('remote', 'update')
            if code == 0:
                return {"success": True, "message": "Remotes updated"}
            return {"success": False, "error": stderr}
        
        return {"success": False, "error": "No operation specified"}

    def fetch(self, all: bool = False, prune: bool = False, remote: str = None) -> Dict:
        """Fetch from remotes."""
        args = ['fetch']
        if all:
            args.append('--all')
        if prune:
            args.append('--prune')
        if remote:
            args.append(remote)
        
        code, stdout, stderr = self._run_git(*args)
        
        if code == 0:
            return {"success": True, "message": "Fetch complete", "output": stdout}
        return {"success": False, "error": stderr}

    def show(self, ref: str, format: str = None, stat: bool = False) -> Dict:
        """Show information about objects."""
        args = ['show']
        if stat:
            args.append('--stat')
        if format:
            args.append(f'--format={format}')
        args.append(ref)
        
        code, stdout, stderr = self._run_git(*args)
        
        if code == 0:
            return {"success": True, "output": stdout}
        return {"success": False, "error": stderr}

    def blame(self, file: str) -> Dict:
        """Show blame information for a file."""
        code, stdout, stderr = self._run_git('blame', file)
        
        if code == 0:
            return {"success": True, "output": stdout}
        return {"success": False, "error": stderr}

    def bisect(self, start: bool = False, good: str = None, bad: str = None,
               reset: bool = False) -> Dict:
        """Binary search for commits."""
        if reset:
            code, _, _ = self._run_git('bisect', 'reset')
            return {"success": True, "message": "Bisect reset"}
        
        if start:
            code, _, stderr = self._run_git('bisect', 'start')
            if code == 0:
                return {"success": True, "message": "Bisect started"}
            return {"success": False, "error": stderr}
        
        if good:
            code, _, stderr = self._run_git('bisect', 'good', good)
            if code == 0:
                return {"success": True, "message": f"Marked '{good}' as good"}
            return {"success": False, "error": stderr}
        
        if bad:
            code, _, stderr = self._run_git('bisect', 'bad', bad)
            if code == 0:
                return {"success": True, "message": f"Marked '{bad}' as bad"}
            return {"success": False, "error": stderr}
        
        return {"success": False, "error": "No operation specified"}

    def config(self, get: str = None, set: Tuple[str, str] = None,
               list: bool = False, global_config: bool = False) -> Dict:
        """Get or set git configuration."""
        args = ['config']
        if global_config:
            args.insert(1, '--global')
        
        if list:
            code, stdout, _ = self._run_git(*args)
            if code == 0:
                configs = {}
                for line in stdout.split('\n') if stdout else []:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        configs[key] = value
                return {"success": True, "config": configs}
            return {"success": False, "error": "Failed to list config"}
        
        if get:
            code, stdout, _ = self._run_git(*args, get)
            if code == 0:
                return {"success": True, "value": stdout}
            return {"success": False, "error": "Config not found"}
        
        if set:
            key, value = set
            code, _, stderr = self._run_git(*args, key, value)
            if code == 0:
                return {"success": True, "message": f"Set {key}={value}"}
            return {"success": False, "error": stderr}
        
        return {"success": False, "error": "No operation specified"}

    def clean(self, dry_run: bool = False, directories: bool = False,
              force: bool = False, exclude: List[str] = None) -> Dict:
        """Remove untracked files."""
        args = ['clean']
        if dry_run:
            args.append('--dry-run')
        if directories:
            args.append('-d')
        if force:
            args.append('-f')
        if exclude:
            for pattern in exclude:
                args.extend(['--exclude', pattern])
        
        code, stdout, stderr = self._run_git(*args)
        
        if code == 0:
            return {"success": True, "message": "Clean complete", "files": stdout.split('\n') if stdout else []}
        return {"success": False, "error": stderr}


def git_operations(repo_path: str = None) -> GitProvider:
    """Create a GitProvider instance."""
    return GitProvider(repo_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python git_ops.py <command> [args]")
        print("Commands: status, add, commit, push, pull, log, branch, diff, stash")
        sys.exit(1)

    git = GitProvider()

    if not git.is_repo():
        print("Error: Not a git repository")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "status":
        status = git.status()
        print(f"Branch: {status.branch}")
        print(f"Ahead: {status.ahead}, Behind: {status.behind}")
        print(f"Staged: {len(status.staged)}")
        print(f"Modified: {len(status.modified)}")
        print(f"Untracked: {len(status.untracked)}")
    elif cmd == "log":
        commits = git.log(max_count=10)
        for c in commits:
            print(f"{c.short_hash} {c.message} ({c.author})")
    elif cmd == "diff":
        diffs = git.diff()
        for d in diffs:
            print(f"{d.diff_type.value}: {d.path} (+{d.additions}/-{d.deletions})")
    elif cmd == "branch":
        result = git.branch(list=True)
        for b in result.get("branches", []):
            marker = "*" if b.is_current else " "
            print(f"{marker} {b.name}")
    else:
        print(f"Unknown command: {cmd}")
