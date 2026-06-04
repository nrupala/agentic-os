#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
OMEGA Git Tools
==============
Git operations: diff, status, commit, branch - no hallucinated commands.
Real git integration for the seamless coding experience.

Inspired by: Claude Code, OpenCode - git-aware operations
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO, format='[GIT] %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent


class GitState(Enum):
    CLEAN = "clean"
    DIRTY = "dirty"
    MERGING = "merging"
    REBASING = "rebasing"


@dataclass
class GitDiff:
    """A git diff with statistics."""
    file_path: str
    status: str  # M, A, D, R
    additions: int
    deletions: int
    patch: str
    old_path: Optional[str] = None


@dataclass
class GitCommit:
    """A git commit."""
    hash: str
    short_hash: str
    author: str
    email: str
    date: str
    message: str
    files_changed: int = 0


@dataclass
class GitBranch:
    """A git branch."""
    name: str
    is_current: bool
    is_remote: bool
    last_commit: Optional[str] = None


@dataclass
class GitStatus:
    """Complete git status."""
    branch: str
    state: GitState
    staged: List[str] = field(default_factory=list)
    modified: List[str] = field(default_factory=list)
    untracked: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)


class OmegaGitTools:
    """
    Git operations with real command execution - no hallucination.
    Key component for git-aware context in LLM prompts.
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        self.repo = Path(repo_path) if repo_path else PROJECT_ROOT
        
        # Verify it's a git repo
        if not (self.repo / '.git').exists():
            # Try parent
            if (self.repo.parent / '.git').exists():
                self.repo = self.repo.parent
            else:
                logger.warning(f"Not a git repository: {self.repo}")
    
    def _run(self, *args, capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a git command."""
        cmd = ['git', '-C', str(self.repo)] + list(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Git command timed out"
        except Exception as e:
            return -1, "", str(e)
    
    def status(self) -> GitStatus:
        """Get current git status."""
        code, stdout, stderr = self._run('status', '--porcelain=v1')
        
        if code != 0:
            return GitStatus(branch="", state=GitState.CLEAN)
        
        staged = []
        modified = []
        untracked = []
        conflicts = []
        
        for line in stdout.strip().split('\n'):
            if not line:
                continue
            
            status_code = line[:2]
            file_path = line[3:]
            
            if status_code == '??':
                untracked.append(file_path)
            elif status_code == 'UU' or 'AA' in status_code or 'DD' in status_code:
                conflicts.append(file_path)
            elif status_code[0] in 'MADRC':  # Staged
                staged.append(file_path)
            elif status_code[1] in 'MADRC':  # Modified in worktree
                modified.append(file_path)
        
        # Get branch name
        _, branch_out, _ = self._run('branch', '--show-current')
        branch = branch_out.strip() or "HEAD detached"
        
        # Check for merge/rebase states
        state = GitState.CLEAN
        if (self.repo / '.git' / 'MERGE_HEAD').exists():
            state = GitState.MERGING
        elif (self.repo / '.git' / 'rebase-merge').exists() or (self.repo / '.git' / 'rebase-apply').exists():
            state = GitState.REBASING
        
        return GitStatus(
            branch=branch,
            state=state,
            staged=staged,
            modified=modified,
            untracked=untracked,
            conflicts=conflicts
        )
    
    def diff(self, 
             staged: bool = False,
             file_path: Optional[str] = None,
             context: int = 3) -> List[GitDiff]:
        """Get diff with statistics."""
        args = ['diff', f'-U{context}']
        
        if staged:
            args.append('--staged')
        
        if file_path:
            args.append('--')
            args.append(file_path)
        
        code, stdout, stderr = self._run(*args)
        
        if code != 0:
            return []
        
        diffs = []
        current_file = None
        current_status = 'M'
        
        for line in stdout.split('\n'):
            # New file diff
            if line.startswith('diff --git'):
                match = re.search(r'b/(.+)', line)
                if match:
                    current_file = match.group(1)
                    current_status = 'M'
            
            # File status from diff header
            elif line.startswith('new file mode'):
                current_status = 'A'
            elif line.startswith('deleted file mode'):
                current_status = 'D'
            elif line.startswith('rename from'):
                current_status = 'R'
                old = line.split('from ')[1].strip()
                current_file = old
            
            # Add/remove stats
            elif line.startswith('+') and not line.startswith('+++'):
                pass  # Addition
            elif line.startswith('-') and not line.startswith('---'):
                pass  # Deletion
            
            elif line.startswith('@@'):
                # This is the hunk header, capture the file context
                pass
            
            # End of file, save diff
            elif line == '' and current_file:
                if current_file and current_file not in [d.file_path for d in diffs]:
                    diffs.append(GitDiff(
                        file_path=current_file,
                        status=current_status,
                        additions=stdout.count('+' + current_file),
                        deletions=stdout.count('-' + current_file),
                        patch=stdout  # Simplified - would parse properly
                    ))
        
        # If no diffs parsed, create from stats
        if not diffs:
            for line in stdout.split('\n'):
                if line.startswith('diff --git'):
                    match = re.search(r'b/(.+)', line)
                    if match:
                        current_file = match.group(1)
                elif line.startswith('similarity index'):
                    # Handle rename
                    pass
        
        return diffs
    
    def diff_summary(self) -> Dict:
        """Get diff summary - files changed, additions, deletions."""
        code, stdout, _ = self._run('diff', '--stat')
        
        if code != 0:
            return {'files': 0, 'additions': 0, 'deletions': 0}
        
        stats = {'files': 0, 'additions': 0, 'deletions': 0}
        
        # Parse last line: "X files changed, Y insertions(+), Z deletions(-)"
        lines = stdout.strip().split('\n')
        if lines:
            last = lines[-1]
            file_match = re.search(r'(\d+) files? changed', last)
            add_match = re.search(r'(\d+) insertions?', last)
            del_match = re.search(r'(\d+) deletions?', last)
            
            if file_match:
                stats['files'] = int(file_match.group(1))
            if add_match:
                stats['additions'] = int(add_match.group(1))
            if del_match:
                stats['deletions'] = int(del_match.group(1))
        
        return stats
    
    def staged_summary(self) -> Dict:
        """Get staged changes summary."""
        code, stdout, _ = self._run('diff', '--staged', '--stat')
        
        if code != 0:
            return {'files': 0, 'additions': 0, 'deletions': 0}
        
        # Same parsing as diff_summary
        lines = stdout.strip().split('\n')
        stats = {'files': 0, 'additions': 0, 'deletions': 0}
        
        if lines:
            last = lines[-1]
            file_match = re.search(r'(\d+) files? changed', last)
            add_match = re.search(r'(\d+) insertions?', last)
            del_match = re.search(r'(\d+) deletions?', last)
            
            if file_match:
                stats['files'] = int(file_match.group(1))
            if add_match:
                stats['additions'] = int(add_match.group(1))
            if del_match:
                stats['deletions'] = int(del_match.group(1))
        
        return stats
    
    def branch_list(self, all: bool = True) -> List[GitBranch]:
        """List branches."""
        args = ['branch']
        if all:
            args.append('-a')
        
        code, stdout, _ = self._run(*args)
        
        if code != 0:
            return []
        
        branches = []
        
        for line in stdout.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            
            is_current = line.startswith('*')
            name = line.lstrip('* ').strip()
            
            is_remote = name.startswith('remotes/')
            if is_remote:
                name = name.replace('remotes/', '')
            
            branches.append(GitBranch(
                name=name,
                is_current=is_current,
                is_remote=is_remote
            ))
        
        return branches
    
    def current_branch(self) -> str:
        """Get current branch name."""
        code, stdout, _ = self._run('branch', '--show-current')
        return stdout.strip()
    
    def log(self, 
            n: int = 10, 
            file_path: Optional[str] = None,
            oneline: bool = True) -> List[GitCommit]:
        """Get commit history."""
        args = ['log', f'-n{n}', '--format=%H|%h|%an|%ae|%ai|%s']
        
        if oneline:
            args.append('--oneline')
        
        if file_path:
            args.append('--')
            args.append(file_path)
        
        code, stdout, _ = self._run(*args)
        
        if code != 0:
            return []
        
        commits = []
        
        for line in stdout.strip().split('\n'):
            if '|' not in line:
                continue
            
            parts = line.split('|')
            if len(parts) >= 6:
                commits.append(GitCommit(
                    hash=parts[0],
                    short_hash=parts[1],
                    author=parts[2],
                    email=parts[3],
                    date=parts[4],
                    message='|'.join(parts[5:])
                ))
        
        return commits
    
    def recent_diffs(self, n: int = 5) -> List[Dict]:
        """Get recent commits with their diffs."""
        commits = self.log(n=n, oneline=False)
        
        results = []
        for commit in commits:
            code, diff, _ = self._run('show', '--stat', commit.short_hash)
            
            results.append({
                'hash': commit.short_hash,
                'message': commit.message,
                'author': commit.author,
                'date': commit.date,
                'diff_summary': diff[:500] if diff else ""
            })
        
        return results
    
    def commit(self, message: str, all: bool = True) -> bool:
        """Create a commit."""
        args = ['commit', '-m', message]
        
        if all:
            args.append('-a')
        
        code, stdout, stderr = self._run(*args)
        
        if code == 0:
            logger.info(f"Committed: {message[:50]}")
            return True
        
        logger.error(f"Commit failed: {stderr}")
        return False
    
    def add(self, paths: List[str]) -> bool:
        """Stage files."""
        args = ['add'] + paths
        
        code, _, stderr = self._run(*args)
        
        return code == 0
    
    def checkout(self, branch: str, create: bool = False) -> bool:
        """Checkout a branch."""
        args = ['checkout']
        
        if create:
            args.append('-b')
        
        args.append(branch)
        
        code, _, stderr = self._run(*args)
        
        return code == 0
    
    def stash(self, message: Optional[str] = None, pop: bool = False) -> bool:
        """Stash changes."""
        args = ['stash']
        
        if message:
            args.extend(['-m', message])
        
        if pop:
            args.append('pop')
        
        code, _, _ = self._run(*args)
        
        return code == 0
    
    def get_file_history(self, file_path: str) -> List[GitCommit]:
        """Get commit history for a specific file."""
        return self.log(n=20, file_path=file_path, oneline=False)
    
    def who_changed(self, file_path: str) -> List[str]:
        """Get list of authors who changed a file."""
        code, stdout, _ = self._run('log', '--format=%an', '--', file_path)
        
        if code != 0:
            return []
        
        authors = []
        for author in stdout.strip().split('\n'):
            if author and author not in authors:
                authors.append(author)
        
        return authors
    
    def is_dirty(self) -> bool:
        """Check if repo has uncommitted changes."""
        status = self.status()
        return status.state != GitState.CLEAN or bool(status.staged or status.modified or status.untracked)
    
    def get_context(self) -> Dict:
        """Get comprehensive git context for LLM."""
        status = self.status()
        
        return {
            'branch': status.branch,
            'is_dirty': status.state != GitState.CLEAN,
            'staged_count': len(status.staged),
            'modified_count': len(status.modified),
            'untracked_count': len(status.untracked),
            'conflicts_count': len(status.conflicts),
            'recent_commits': [
                {'hash': c.short_hash, 'message': c.message}
                for c in self.log(n=5)
            ],
            'branches': [
                {'name': b.name, 'current': b.is_current}
                for b in self.branch_list()[:10]
            ]
        }


if __name__ == "__main__":
    import sys
    
    git = OmegaGitTools()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == 'status':
            status = git.status()
            print(f"Branch: {status.branch}")
            print(f"State: {status.state.value}")
            print(f"Staged: {len(status.staged)} files")
            print(f"Modified: {len(status.modified)} files")
            print(f"Untracked: {len(status.untracked)} files")
        
        elif cmd == 'branch':
            for b in git.branch_list():
                marker = "*" if b.is_current else " "
                print(f"{marker} {b.name}")
        
        elif cmd == 'log':
            for c in git.log(n=5):
                print(f"{c.short_hash} {c.message}")
        
        elif cmd == 'context':
            print(json.dumps(git.get_context(), indent=2))
    
    else:
        # Show current status
        status = git.status()
        print(f"Branch: {status.branch}")
        print(f"Dirty: {git.is_dirty()}")