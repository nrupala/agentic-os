#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
OMEGA Seamless Service
======================
The unified seamless coding experience - Context + Tools + Feedback Loop.

This integrates all the trifecta components:
- Context: Repo map, semantic search, git-aware
- Tools: Shell, git, LSP, filesystem
- Feedback Loop: Run → error → fix → repeat

Inspired by: Claude Code, OpenCode, Cursor - the "seamless" experience
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[OMEGA] %(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
ENGINE_DIR = PROJECT_ROOT / "engine"
sys.path.insert(0, str(ENGINE_DIR))


@dataclass
class SeamlessConfig:
    """Configuration for seamless experience."""
    project: str = "omega"
    port: int = 8765
    auto_index: bool = True
    auto_lint: bool = True
    auto_test: bool = False
    max_context_tokens: int = 20000
    shell_timeout: int = 120
    max_iterations: int = 5


@dataclass
class SeamlessStatus:
    """Status of the seamless service."""
    status: str
    components: Dict[str, str]
    context_stats: Dict[str, int]
    last_operation: str
    uptime_seconds: int


class OmegaSeamlessService:
    """
    The seamless coding experience - all three pillars working together.
    
    Context:
    - RepoMap: AST-based file tree + symbols
    - SemanticSearch: Find code by meaning
    - GitTools: Know diffs, branches, history
    
    Tools:
    - ShellTools: Run tests, linters with timeouts
    - GitTools: Real git operations
    - LSPClient: Diagnostics, goto-def
    - FileTools: Read/write with path safety
    
    Feedback Loop:
    - Run lint after edit
    - Run tests after lint
    - Capture errors → feed back to LLM
    - Loop until green
    """
    
    VERSION = "3.0.0"
    
    def __init__(self, config: SeamlessConfig = None):
        self.config = config or SeamlessConfig()
        self.start_time = time.time()
        
        # Initialize all components
        self._init_components()
        
        logger.info(f"OMEGA Seamless Service v{self.VERSION} initialized")
    
    def _init_components(self):
        """Initialize all trifecta components."""
        
        # Context components
        logger.info("Initializing Context components...")
        try:
            from omega_repo_map import OmegaRepoMap
            self.repo_map = OmegaRepoMap(str(PROJECT_ROOT))
            self.repo_map.build_index()
            logger.info(f"  Repo map: {self.repo_map.index.stats}")
        except Exception as e:
            logger.warning(f"  Repo map failed: {e}")
            self.repo_map = None
        
        try:
            from omega_semantic_search import OmegaSemanticSearch
            self.semantic_search = OmegaSemanticSearch(str(PROJECT_ROOT))
            self.semantic_search.index_repository()
            logger.info(f"  Semantic search: {len(self.semantic_search.chunks)} chunks")
        except Exception as e:
            logger.warning(f"  Semantic search failed: {e}")
            self.semantic_search = None
        
        # Git context
        try:
            from omega_git_tools import OmegaGitTools
            self.git = OmegaGitTools(str(PROJECT_ROOT))
            git_context = self.git.get_context()
            logger.info(f"  Git: {git_context['branch']}, dirty={git_context['is_dirty']}")
        except Exception as e:
            logger.warning(f"  Git tools failed: {e}")
            self.git = None
        
        # Tool components
        logger.info("Initializing Tool components...")
        try:
            from omega_shell_tools import OmegaShellTools
            self.shell = OmegaShellTools(
                root_path=str(PROJECT_ROOT),
                timeout_seconds=self.config.shell_timeout
            )
            logger.info(f"  Shell: ready (timeout={self.config.shell_timeout}s)")
        except Exception as e:
            logger.warning(f"  Shell failed: {e}")
            self.shell = None
        
        try:
            from omega_lsp_client import SimpleLSPClient
            self.lsp = SimpleLSPClient(str(PROJECT_ROOT))
            logger.info("  LSP: ready")
        except Exception as e:
            logger.warning(f"  LSP failed: {e}")
            self.lsp = None
        
        # Infrastructure
        try:
            from omega_infrastructure import OmegaInfrastructure
            self.infra = OmegaInfrastructure(str(PROJECT_ROOT))
            disk_usage = self.infra.get_disk_usage()
            logger.info(f"  Infra: {disk_usage['cache_mb']}MB cached")
        except Exception as e:
            logger.warning(f"  Infra failed: {e}")
            self.infra = None
        
        # Feedback loop
        try:
            from omega_feedback_loop import OmegaFeedbackLoop, FeedbackLoopConfig
            loop_config = FeedbackLoopConfig(
                max_iterations=self.config.max_iterations,
                timeout_seconds=self.config.shell_timeout
            )
            self.feedback_loop = OmegaFeedbackLoop(self.shell, self.lsp, loop_config)
            logger.info(f"  Feedback loop: ready ({self.config.max_iterations} max iters)")
        except Exception as e:
            logger.warning(f"  Feedback loop failed: {e}")
            self.feedback_loop = None
    
    # ==================== CONTEXT API ====================
    
    def get_file_tree(self, max_depth: int = 3) -> Dict:
        """Get repository file tree."""
        if not self.repo_map:
            return {'error': 'Repo map not available'}
        return self.repo_map.get_file_tree(max_depth=max_depth)
    
    def get_file_context(self, file_path: str) -> Dict:
        """Get comprehensive context for a file."""
        if not self.repo_map:
            return {'error': 'Repo map not available'}
        return self.repo_map.get_context_for_file(file_path)
    
    def search_code(self, query: str, top_k: int = 10) -> List[Dict]:
        """Semantic search across codebase."""
        if not self.semantic_search:
            return [{'error': 'Semantic search not available'}]
        
        results = self.semantic_search.search(query, top_k=top_k)
        return [
            {
                'file': r.chunk.file_path,
                'line': r.chunk.start_line,
                'score': r.score,
                'preview': r.chunk.content[:200]
            }
            for r in results
        ]
    
    def get_git_context(self) -> Dict:
        """Get git-aware context for LLM."""
        if not self.git:
            return {'error': 'Git not available'}
        return self.git.get_context()
    
    def get_recent_diffs(self, n: int = 5) -> List[Dict]:
        """Get recent commits with diffs."""
        if not self.git:
            return []
        return self.git.recent_diffs(n=n)
    
    def get_relevant_context(self, query: str, max_tokens: int = 15000) -> str:
        """Get relevant code context for LLM based on query."""
        if not self.repo_map:
            return "Context not available"
        return self.repo_map.get_relevant_context(query, max_tokens)
    
    # ==================== TOOL API ====================
    
    def run_command(self, command: str, timeout: int = 60) -> Dict:
        """Execute a shell command safely."""
        if not self.shell:
            return {'success': False, 'error': 'Shell not available'}
        
        result = self.shell.run(command, timeout=timeout)
        return {
            'success': result.success,
            'return_code': result.return_code,
            'stdout': result.stdout[:5000],
            'stderr': result.stderr[:2000],
            'duration_ms': result.duration_ms,
            'timed_out': result.timed_out
        }
    
    def run_lint(self, file_path: str = None) -> Dict:
        """Run linter on project or file."""
        if not self.shell:
            return {'success': False, 'error': 'Shell not available'}
        
        cmd = "ruff check ."
        if file_path:
            cmd = f"ruff check {file_path}"
        
        result = self.shell.run(cmd, timeout=60)
        return {
            'success': result.return_code == 0,
            'output': result.output[:5000],
            'return_code': result.return_code
        }
    
    def run_tests(self, test_path: str = None) -> Dict:
        """Run test suite."""
        if not self.shell:
            return {'success': False, 'error': 'Shell not available'}
        
        cmd = "pytest -v --tb=short"
        if test_path:
            cmd = f"pytest {test_path} -v --tb=short"
        
        result = self.shell.run(cmd, timeout=self.config.shell_timeout)
        return {
            'success': result.return_code == 0,
            'output': result.output[:5000],
            'return_code': result.return_code,
            'duration_ms': result.duration_ms
        }
    
    def git_status(self) -> Dict:
        """Get git status."""
        if not self.git:
            return {'error': 'Git not available'}
        
        status = self.git.status()
        return {
            'branch': status.branch,
            'state': status.state.value,
            'staged': len(status.staged),
            'modified': len(status.modified),
            'untracked': len(status.untracked)
        }
    
    def git_diff(self, staged: bool = False) -> Dict:
        """Get git diff."""
        if not self.git:
            return {'error': 'Git not available'}
        
        diffs = self.git.diff(staged=staged)
        summary = self.git.diff_summary() if not staged else self.git.staged_summary()
        
        return {
            'summary': summary,
            'files': [d.file_path for d in diffs[:20]]
        }
    
    def git_commit(self, message: str) -> Dict:
        """Create a git commit."""
        if not self.git:
            return {'success': False, 'error': 'Git not available'}
        
        status = self.git.status()
        
        # Stage all changes
        if status.staged or status.modified or status.untracked:
            all_files = status.staged + status.modified + status.untracked
            self.git.add(all_files)
        
        success = self.git.commit(message)
        return {'success': success}
    
    def read_file(self, file_path: str, limit: int = 500) -> Dict:
        """Read a file safely."""
        try:
            full_path = PROJECT_ROOT / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:limit]
            
            return {
                'success': True,
                'content': ''.join(lines),
                'path': file_path,
                'lines': len(lines)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def write_file(self, file_path: str, content: str) -> Dict:
        """Write a file safely."""
        try:
            full_path = PROJECT_ROOT / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {'success': True, 'path': file_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_diagnostics(self, file_path: str) -> Dict:
        """Get LSP diagnostics for a file."""
        if not self.lsp:
            return {'error': 'LSP not available'}
        
        return self.lsp.get_diagnostics(file_path)
    
    # ==================== FEEDBACK LOOP API ====================
    
    def quick_check(self, file_path: str) -> Dict:
        """Quick check: lint a single file."""
        if not self.feedback_loop:
            return {'error': 'Feedback loop not available'}
        
        return self.feedback_loop.quick_check(file_path)
    
    def run_feedback_loop(self, file_path: str = None) -> Dict:
        """Run full feedback loop: lint → test → repeat."""
        if not self.feedback_loop:
            return {'error': 'Feedback loop not available'}
        
        result = self.feedback_loop.run_full_loop(
            apply_edit_fn=lambda x: True,  # Placeholder
            file_path=file_path
        )
        
        return result
    
    def get_feedback_context(self) -> str:
        """Get feedback loop context for LLM."""
        if not self.feedback_loop:
            return "Feedback loop not available"
        
        return self.feedback_loop.get_context_for_llm()
    
    # ==================== STATUS API ====================
    
    def get_status(self) -> SeamlessStatus:
        """Get overall service status."""
        components = {}
        
        if self.repo_map:
            components['repo_map'] = f"{self.repo_map.index.stats.get('total_files', 0)} files"
        if self.semantic_search:
            components['semantic_search'] = f"{len(self.semantic_search.chunks)} chunks"
        if self.git:
            components['git'] = "ready"
        if self.shell:
            components['shell'] = "ready"
        if self.lsp:
            components['lsp'] = "ready"
        if self.infra:
            components['infra'] = "ready"
        if self.feedback_loop:
            components['feedback_loop'] = "ready"
        
        context_stats = {}
        if self.repo_map:
            context_stats = self.repo_map.index.stats
        
        return SeamlessStatus(
            status="running" if components else "degraded",
            components=components,
            context_stats=context_stats,
            last_operation="initialized",
            uptime_seconds=int(time.time() - self.start_time)
        )
    
    def get_full_context(self, query: str = None) -> Dict:
        """
        Get full context for LLM - combines repo map, git, and semantic search.
        This is the key function that provides the "Context" in the trifecta.
        """
        context = {
            'version': self.VERSION,
            'project': self.config.project,
            'uptime_seconds': int(time.time() - self.start_time),
        }
        
        # File tree
        context['file_tree'] = self.get_file_tree(max_depth=2)
        
        # Git context
        if self.git:
            context['git'] = self.git.get_context()
        
        # Search results if query provided
        if query and self.semantic_search:
            context['search_results'] = self.search_code(query, top_k=5)
        
        # Recent diffs
        if self.git:
            context['recent_diffs'] = self.get_recent_diffs(n=3)
        
        # Shell history
        if self.shell:
            context['recent_commands'] = self.shell.get_command_history(limit=5)
        
        return context


# ==================== CLI ====================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="OMEGA Seamless Service")
    parser.add_argument("--project", default="omega", help="Project name")
    parser.add_argument("--port", type=int, default=8765, help="Port")
    parser.add_argument("--start", action="store_true", help="Start service")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--context", action="store_true", help="Show full context")
    parser.add_argument("--search", type=str, help="Search code")
    parser.add_argument("--lint", action="store_true", help="Run linter")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--git-status", action="store_true", help="Git status")
    parser.add_argument("--run", type=str, help="Run shell command")
    
    args = parser.parse_args()
    
    config = SeamlessConfig(project=args.project, port=args.port)
    service = OmegaSeamlessService(config)
    
    if args.status:
        status = service.get_status()
        print(f"\n=== OMEGA Seamless Service v{status.status} ===")
        print(f"Status: {status.status}")
        print(f"Uptime: {status.uptime_seconds}s")
        print("\nComponents:")
        for name, info in status.components.items():
            print(f"  - {name}: {info}")
        print("\nContext Stats:")
        for key, val in status.context_stats.items():
            print(f"  - {key}: {val}")
    
    elif args.context:
        print(json.dumps(service.get_full_context(), indent=2))
    
    elif args.search:
        results = service.search_code(args.search)
        print(json.dumps(results, indent=2))
    
    elif args.lint:
        result = service.run_lint()
        print(json.dumps(result, indent=2))
    
    elif args.test:
        result = service.run_tests()
        print(json.dumps(result, indent=2))
    
    elif args.git_status:
        result = service.git_status()
        print(json.dumps(result, indent=2))
    
    elif args.run:
        result = service.run_command(args.run)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"OMEGA Seamless Service v{service.VERSION}")
        print(f"Project: {args.project}")
        status = service.get_status()
        print(f"Status: {status.status}")
        print(f"Components: {len(status.components)}")


if __name__ == "__main__":
    main()