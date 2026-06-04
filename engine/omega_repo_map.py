#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
OMEGA Repo Map
=============
AST-based code indexing and repository mapping.
Builds symbol index of entire repo, feeds file tree + signatures to LLM.

Inspired by: Cursor, OpenCode, Aider - tree-sitter based repo mapping
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='[REPO_MAP] %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class Symbol:
    """Represents a code symbol (function, class, variable)."""
    name: str
    kind: str  # function, class, method, variable, constant
    file_path: str
    line: int
    signature: str = ""
    docstring: str = ""
    children: List[str] = field(default_factory=list)


@dataclass
class FileNode:
    """Represents a file in the repository tree."""
    path: str
    name: str
    extension: str
    size: int
    mtime: float
    symbols: List[Symbol] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    hash: str = ""


@dataclass
class RepoIndex:
    """Complete repository index."""
    root: str
    files: Dict[str, FileNode] = field(default_factory=dict)
    symbols: Dict[str, List[Symbol]] = field(default_factory=dict)
    imports_graph: Dict[str, Set[str]] = field(default_factory=dict)
    last_updated: str = ""
    stats: Dict[str, int] = field(default_factory=dict)


class OmegaRepoMap:
    """AST-based repository mapping using tree-sitter."""
    
    EXTENSION_LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.rs': 'rust',
        '.go': 'go',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'c-sharp',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
    }
    
    IGNORE_PATTERNS = {
        '.git', '.svn', '.hg', '__pycache__', 'node_modules',
        '.venv', 'venv', '.env', 'env', 'dist', 'build',
        '.pytest_cache', '.mypy_cache', '.ruff_cache',
        '*.pyc', '*.pyo', '*.so', '*.dylib', '.DS_Store',
        '*.log', '*.tmp', '*.swp', '*.swo', '~*',
    }
    
    def __init__(self, root_path: Optional[str] = None):
        self.root = Path(root_path or PROJECT_ROOT)
        self.index = RepoIndex(root=str(self.root))
        self._symbol_cache: Dict[str, Symbol] = {}
        
    def is_ignored(self, path: Path) -> bool:
        """Check if path matches ignore patterns."""
        name = path.name
        for pattern in self.IGNORE_PATTERNS:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern or pattern in str(path):
                return True
        return False
    
    def scan_files(self) -> List[Path]:
        """Scan repository for source files."""
        files = []
        for root, dirs, filenames in os.walk(self.root):
            # Filter ignored directories in-place
            dirs[:] = [d for d in dirs if not self.is_ignored(Path(root) / d)]
            
            for fname in filenames:
                path = Path(root) / fname
                if self.is_ignored(path):
                    continue
                ext = path.suffix.lower()
                if ext in self.EXTENSION_LANGUAGE_MAP:
                    files.append(path)
        return files
    
    def compute_file_hash(self, path: Path) -> str:
        """Compute SHA256 hash of file contents."""
        try:
            with open(path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        except Exception:
            return ""
    
    def parse_python_symbols(self, path: Path) -> List[Symbol]:
        """Parse Python file for symbols using basic AST-like parsing."""
        symbols = []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            in_class = None
            indent_stack = []
            
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Class definition
                if stripped.startswith('class ') and ':' in stripped:
                    match = stripped[6:].split('(')[0].strip()
                    if match:
                        symbols.append(Symbol(
                            name=match,
                            kind='class',
                            file_path=str(path),
                            line=i,
                            signature=stripped
                        ))
                        in_class = match
                        indent_stack.append(len(line) - len(line.lstrip()))
                
                # Function/method definition
                elif stripped.startswith('def ') and '(' in stripped:
                    func_name = stripped[4:].split('(')[0].strip()
                    if not func_name.startswith('_') or '__init__' in func_name:
                        sig = stripped[4:]
                        # Extract parameter names for signature
                        try:
                            params = sig.split('(')[1].split(')')[0]
                            params_list = [p.strip().split('=')[0] for p in params.split(',') if p.strip()]
                            sig = f"def {func_name}({', '.join(params_list[:5])}"
                            if len(params_list) > 5:
                                sig += ", ..."
                            sig += ")"
                        except:
                            sig = f"def {func_name}(...)"
                        
                        symbols.append(Symbol(
                            name=func_name,
                            kind='class' if in_class else 'function',
                            file_path=str(path),
                            line=i,
                            signature=sig
                        ))
                
                # Reset class context on dedent
                elif in_class and line and not line[0].isspace():
                    in_class = None
                    indent_stack = []
                    
        except Exception as e:
            logger.warning(f"Failed to parse {path}: {e}")
        
        return symbols
    
    def parse_imports(self, path: Path) -> List[str]:
        """Extract imports from a file."""
        imports = []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for line in content.split('\n'):
                stripped = line.strip()
                if stripped.startswith('import '):
                    imports.append(stripped[7:].strip())
                elif stripped.startswith('from '):
                    if ' import ' in stripped:
                        mod = stripped[5:].split(' import ')[0]
                        imports.append(mod)
        except:
            pass
        return imports
    
    def build_index(self, force: bool = False) -> RepoIndex:
        """Build complete repository index."""
        logger.info(f"Building index for {self.root}")
        
        files = self.scan_files()
        logger.info(f"Found {len(files)} source files")
        
        for path in files:
            try:
                stat = path.stat()
                file_hash = self.compute_file_hash(path)
                
                symbols = self.parse_python_symbols(path) if path.suffix == '.py' else []
                imports = self.parse_imports(path)
                
                # Get exports (top-level functions/classes)
                exports = [s.name for s in symbols if s.kind in ('function', 'class')]
                
                node = FileNode(
                    path=str(path),
                    name=path.name,
                    extension=path.suffix,
                    size=stat.st_size,
                    mtime=stat.st_mtime,
                    symbols=symbols,
                    imports=imports,
                    exports=exports,
                    hash=file_hash
                )
                
                self.index.files[str(path)] = node
                
                # Index symbols
                for sym in symbols:
                    if sym.name not in self.index.symbols:
                        self.index.symbols[sym.name] = []
                    self.index.symbols[sym.name].append(sym)
                
                # Build imports graph
                self.index.imports_graph[str(path)] = set(imports)
                
            except Exception as e:
                logger.warning(f"Failed to index {path}: {e}")
        
        self.index.last_updated = datetime.now().isoformat()
        self.index.stats = {
            'total_files': len(self.index.files),
            'total_symbols': len(self.index.symbols),
            'total_imports': sum(len(v) for v in self.index.imports_graph.values())
        }
        
        logger.info(f"Index built: {self.index.stats}")
        return self.index
    
    def get_file_tree(self, max_depth: int = 4) -> Dict:
        """Get file tree structure for LLM context."""
        tree = {'name': self.root.name, 'type': 'directory', 'children': {}}
        
        def add_to_tree(node: Dict, parts: List[str], depth: int):
            if depth >= max_depth:
                return
            if not parts:
                return
            
            name = parts[0]
            if len(parts) == 1:
                node['children'][name] = {'type': 'file'}
            else:
                if name not in node['children']:
                    node['children'][name] = {'type': 'directory', 'children': {}}
                add_to_tree(node['children'][name], parts[1:], depth + 1)
        
        for path in sorted(self.index.files.keys()):
            rel_path = Path(path).relative_to(self.root)
            add_to_tree(tree, list(rel_path.parts), 0)
        
        return tree
    
    def get_file_order(self) -> List[str]:
        """
        Get files in dependency order (DAG topological sort).
        Files that are imported by others come last (dependencies first).
        
        This is used by the PLANNER step to hand off to OMEGA STACK.
        """
        if not self.index or not self.index.files:
            return []
        
        # Build adjacency: what each file imports
        imported_by = {}  # file -> files that import it
        
        for file_path, imports in self.index.imports_graph.items():
            for imp in imports:
                if imp not in imported_by:
                    imported_by[imp] = []
                imported_by[imp].append(file_path)
        
        # Topological sort: files with most dependents first (leaf nodes last)
        file_order = []
        remaining = set(self.index.files.keys())
        
        while remaining:
            # Find files with no unprocessed imports
            ready = []
            for f in remaining:
                # Check if all files it imports are already processed
                imports = self.index.imports_graph.get(f, set())
                unprocessed_imports = imports & remaining
                if not unprocessed_imports:
                    ready.append(f)
            
            if not ready:
                # Circular dependency - just take one
                ready = [list(remaining)[0]]
            
            # Sort by dependency count (most dependent first)
            ready.sort(key=lambda f: len(imported_by.get(f, [])), reverse=True)
            file_order.extend(ready)
            remaining -= set(ready)
        
        return file_order
    
    def get_file_symbols(self, file_path: str) -> List[Symbol]:
        """Get all symbols in a file."""
        node = self.index.files.get(file_path)
        return node.symbols if node else []
    
    def find_symbol(self, name: str) -> List[Symbol]:
        """Find symbol by name across all files."""
        return self.index.symbols.get(name, [])
    
    def get_imports_chain(self, file_path: str) -> List[str]:
        """Get all files this file imports."""
        return list(self.index.imports_graph.get(file_path, set()))
    
    def get_callers(self, symbol_name: str) -> List[str]:
        """Find files that call a given symbol."""
        callers = []
        target_files = {s.file_path for s in self.index.symbols.get(symbol_name, [])}
        
        for path, imports in self.index.imports_graph.items():
            # Simple heuristic - check if any target file is referenced
            for tf in target_files:
                tf_name = Path(tf).stem
                if tf_name in str(imports):
                    callers.append(path)
                    break
        
        return callers
    
    def get_context_for_file(self, file_path: str, include_symbols: bool = True) -> Dict:
        """Get comprehensive context for a file - tree-sitter style."""
        node = self.index.files.get(file_path)
        if not node:
            return {}
        
        context = {
            'file': file_path,
            'size': node.size,
            'imports': node.imports,
            'exports': node.exports,
        }
        
        if include_symbols:
            context['symbols'] = [
                {'name': s.name, 'kind': s.kind, 'line': s.line, 'signature': s.signature}
                for s in node.symbols
            ]
        
        # Get import chain
        context['imports_from'] = self.get_imports_chain(file_path)
        
        return context
    
    def get_relevant_context(self, query: str, max_tokens: int = 15000) -> str:
        """Get relevant code context for LLM based on query."""
        # Find relevant symbols
        query_terms = query.lower().split()
        relevant_files = set()
        relevant_symbols = []
        
        # Score files by relevance
        for name, symbols in self.index.symbols.items():
            if any(term in name.lower() for term in query_terms):
                relevant_symbols.extend(symbols)
                for s in symbols:
                    relevant_files.add(s.file_path)
        
        # Build context
        context_parts = []
        total_len = 0
        
        # Add file tree summary
        context_parts.append("# Repository Structure")
        tree = self.get_file_tree(max_depth=2)
        context_parts.append(self._format_tree(tree))
        context_parts.append("")
        
        # Add relevant file contexts
        for path in sorted(relevant_files)[:10]:
            fc = self.get_context_for_file(path)
            text = self._format_file_context(fc)
            if total_len + len(text) < max_tokens:
                context_parts.append(text)
                total_len += len(text)
        
        return "\n".join(context_parts[:20])
    
    def _format_tree(self, tree: Dict, prefix: str = "") -> str:
        """Format tree as string."""
        lines = []
        children = tree.get('children', {})
        for i, (name, node) in enumerate(sorted(children.items())):
            is_last = i == len(children) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{name}")
            if node.get('type') == 'directory':
                ext = "    " if is_last else "│   "
                lines.extend(self._format_tree(node, prefix + ext).split('\n')[1:])
        return '\n'.join(lines)
    
    def _format_file_context(self, fc: Dict) -> str:
        """Format file context for LLM."""
        lines = [f"# {fc.get('file', 'unknown')}", ""]
        
        if fc.get('imports'):
            lines.append("## Imports")
            for imp in fc['imports'][:10]:
                lines.append(f"  - {imp}")
            lines.append("")
        
        if fc.get('symbols'):
            lines.append("## Symbols")
            for sym in fc['symbols'][:15]:
                kind_emoji = {'class': ' 🅾', 'function': 'ƒ', 'method': '⦿'}.get(sym['kind'], '·')
                lines.append(f"  {kind_emoji} {sym['name']}: {sym.get('signature', '')}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def to_dict(self) -> Dict:
        """Export index as dictionary."""
        return {
            'root': self.index.root,
            'stats': self.index.stats,
            'last_updated': self.index.last_updated,
            'files': {
                k: {
                    'path': v.path,
                    'name': v.name,
                    'extension': v.extension,
                    'size': v.size,
                    'symbols_count': len(v.symbols),
                    'imports_count': len(v.imports),
                    'exports': v.exports[:10],
                    'hash': v.hash,
                }
                for k, v in list(self.index.files.items())[:100]
            },
            'top_symbols': list(self.index.symbols.keys())[:50]
        }


if __name__ == "__main__":
    import sys
    
    repo_map = OmegaRepoMap()
    repo_map.build_index()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--tree':
            print(repo_map.get_file_tree())
        elif sys.argv[1] == '--symbols':
            for name, syms in list(repo_map.index.symbols.items())[:20]:
                print(f"{name}: {len(syms)} occurrences")
        elif sys.argv[1] == '--context':
            if len(sys.argv) > 2:
                print(repo_map.get_context_for_file(sys.argv[2]))
        elif sys.argv[1] == '--relevant':
            if len(sys.argv) > 2:
                print(repo_map.get_relevant_context(sys.argv[2]))
        else:
            print(json.dumps(repo_map.to_dict(), indent=2))
    else:
        print(json.dumps(repo_map.to_dict(), indent=2))