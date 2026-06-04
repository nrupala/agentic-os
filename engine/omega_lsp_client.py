#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
OMEGA LSP Client
================
Language Server Protocol client for diagnostics, goto-def, hover.
Enables real-time error feedback as you type - like VS Code.

Inspired by: Cursor, OpenCode - live LSP diagnostics after each edit
"""

import os
import json
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO, format='[LSP] %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent


class DiagnosticSeverity(Enum):
    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4


@dataclass
class Position:
    """Text document position."""
    line: int
    character: int


@dataclass
class Range:
    """Text document range."""
    start: Position
    end: Position


@dataclass
class Diagnostic:
    """A diagnostic (error, warning, hint)."""
    range: Range
    severity: int
    message: str
    source: str = ""
    code: Optional[str] = None


@dataclass
class Location:
    """A location in a document."""
    uri: str
    range: Range


@dataclass
class LSPDocument:
    """A document open in LSP."""
    path: str
    version: int
    content: str
    language: str


class OmegaLSPClient:
    """
    LSP client for Python (Pyright) and TypeScript/JS (TS Server).
    Provides diagnostics, goto-def, hover, and code actions.
    """
    
    # Language server configurations
    LSP_CONFIGS = {
        'python': {
            'command': 'pyright',
            'args': ['--stdio'],
            'filetypes': ['python'],
            'rootPatterns': ['pyproject.toml', 'setup.py', 'requirements.txt', '.git']
        },
        'typescript': {
            'command': 'typescript-language-server',
            'args': ['--stdio'],
            'filetypes': ['typescript', 'javascript', 'typescriptreact', 'javascriptreact'],
            'rootPatterns': ['package.json', 'tsconfig.json', '.git']
        },
        'rust': {
            'command': 'rust-analyzer',
            'args': [],
            'filetypes': ['rust'],
            'rootPatterns': ['Cargo.toml', '.git']
        },
        'go': {
            'command': 'gopls',
            'args': [],
            'filetypes': ['go'],
            'rootPatterns': ['go.mod', '.git']
        }
    }
    
    def __init__(self, root_path: Optional[str] = None):
        self.root = Path(root_path) if root_path else PROJECT_ROOT
        
        # Document cache
        self.documents: Dict[str, LSPDocument] = {}
        
        # Language server processes
        self.servers: Dict[str, subprocess.Popen] = {}
        
        # Initialize for each language
        self._initialized = False
        self._capabilities: Dict[str, Dict] = {}
        
        # Request ID counter
        self._request_id = 0
        self._pending_requests: Dict[int, Any] = {}
        self._lock = threading.Lock()
    
    def _get_language(self, file_path: str) -> Optional[str]:
        """Get language from file extension."""
        ext = Path(file_path).suffix.lower()
        lang_map = {
            '.py': 'python',
            '.js': 'typescript',
            '.ts': 'typescript',
            '.jsx': 'typescript',
            '.tsx': 'typescript',
            '.rs': 'rust',
            '.go': 'go',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
        }
        return lang_map.get(ext)
    
    def _get_lang_server(self, language: str) -> Optional[Dict]:
        """Get language server config."""
        return self.LSP_CONFIGS.get(language)
    
    def _start_server(self, language: str) -> bool:
        """Start a language server."""
        config = self._get_lang_server(language)
        if not config:
            return False
        
        if language in self.servers:
            return True
        
        try:
            # Start the LSP server
            proc = subprocess.Popen(
                [config['command']] + config['args'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.root)
            )
            
            self.servers[language] = proc
            logger.info(f"Started LSP server for {language}")
            
            # Initialize the server
            self._initialize_server(language)
            
            return True
        except Exception as e:
            logger.warning(f"Failed to start {language} LSP server: {e}")
            return False
    
    def _initialize_server(self, language: str):
        """Initialize LSP server with workspace."""
        server = self.servers.get(language)
        if not server:
            return
        
        # Send initialize request
        init_params = {
            'processId': os.getpid(),
            'rootUri': self.root.as_uri(),
            'rootPath': str(self.root),
            'capabilities': {
                'textDocument': {
                    'synchronization': {
                        'willSave': True,
                        'didSave': True,
                        'willSaveWaitUntil': True
                    },
                    'hover': {'dynamicRegistration': True},
                    'definition': {'dynamicRegistration': True},
                    'references': {'dynamicRegistration': True},
                    'codeAction': {'dynamicRegistration': True},
                },
                'workspace': {
                    'applyEdit': True,
                    'workspaceFolders': True
                }
            },
            'workspaceFolders': [
                {'uri': self.root.as_uri(), 'name': 'workspace'}
            ]
        }
        
        self._send_request(language, 'initialize', init_params, callback=self._handle_init)
    
    def _handle_init(self, result):
        """Handle initialize response."""
        self._initialized = True
        self._capabilities = result.get('capabilities', {})
        logger.info("LSP servers initialized")
    
    def _send_request(self, language: str, method: str, params: Any, callback: Optional[Callable] = None) -> int:
        """Send an LSP request."""
        with self._lock:
            self._request_id += 1
            request_id = self._request_id
        
        if callback:
            self._pending_requests[request_id] = callback
        
        message = json.dumps({
            'jsonrpc': '2.0',
            'id': request_id,
            'method': method,
            'params': params
        })
        
        server = self.servers.get(language)
        if server and server.stdin:
            server.stdin.write(message + '\n')
            server.stdin.flush()
        
        return request_id
    
    def _send_notification(self, language: str, method: str, params: Any):
        """Send an LSP notification (no response)."""
        message = json.dumps({
            'jsonrpc': '2.0',
            'method': method,
            'params': params
        })
        
        server = self.servers.get(language)
        if server and server.stdin:
            server.stdin.write(message + '\n')
            server.stdin.flush()
    
    # ==================== Document Operations ====================
    
    def open_document(self, file_path: str, content: Optional[str] = None):
        """Open a document in the LSP server."""
        language = self._get_language(file_path)
        if not language:
            return
        
        # Start server if needed
        if language not in self.servers:
            if not self._start_server(language):
                logger.warning(f"Cannot start LSP server for {language}")
                return
        
        # Read content if not provided
        if content is None:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
            except:
                return
        
        # Store document
        self.documents[file_path] = LSPDocument(
            path=file_path,
            version=1,
            content=content,
            language=language
        )
        
        # Send didOpen notification
        self._send_notification(language, 'textDocument/didOpen', {
            'textDocument': {
                'uri': Path(file_path).as_uri(),
                'languageId': language,
                'version': 1,
                'text': content
            }
        })
    
    def close_document(self, file_path: str):
        """Close a document."""
        doc = self.documents.get(file_path)
        if not doc:
            return
        
        self._send_notification(doc.language, 'textDocument/didClose', {
            'textDocument': {'uri': Path(file_path).as_uri()}
        })
        
        del self.documents[file_path]
    
    def update_document(self, file_path: str, changes: List[Dict], version: int):
        """Update document content."""
        doc = self.documents.get(file_path)
        if not doc:
            return
        
        doc.version = version
        
        # Send didChange notification
        self._send_notification(doc.language, 'textDocument/didChange', {
            'textDocument': {
                'uri': Path(file_path).as_uri(),
                'version': version
            },
            'contentChanges': changes
        })
    
    # ==================== Diagnostics ====================
    
    def get_diagnostics(self, file_path: str) -> List[Diagnostic]:
        """Get diagnostics for a document."""
        doc = self.documents.get(file_path)
        if not doc:
            return []
        
        # Ensure document is open
        if file_path not in self.documents:
            self.open_document(file_path)
        
        # Request diagnostics
        # Note: In practice, LSP pushes diagnostics via 'textDocument/publishDiagnostics'
        # Here we simulate a synchronous request
        
        # For now, run the linter directly and parse output
        return self._run_linter_fallback(doc.language, file_path)
    
    def _run_linter_fallback(self, language: str, file_path: str) -> List[Diagnostic]:
        """Fallback: run linter directly instead of LSP."""
        diagnostics = []
        
        if language == 'python':
            try:
                result = subprocess.run(
                    ['python', '-m', 'py_compile', file_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    # Parse Python syntax errors
                    stderr = result.stderr
                    for line in stderr.split('\n'):
                        if 'SyntaxError' in line or 'IndentationError' in line:
                            # Extract line number
                            import re
                            match = re.search(r'line (\d+)', line)
                            line_num = int(match.group(1)) if match else 1
                            
                            diagnostics.append(Diagnostic(
                                range=Range(
                                    start=Position(line=line_num - 1, character=0),
                                    end=Position(line=line_num, character=0)
                                ),
                                severity=DiagnosticSeverity.ERROR.value,
                                message=line,
                                source='py_compile'
                            ))
            except:
                pass
        
        return diagnostics
    
    def get_all_diagnostics(self) -> Dict[str, List[Diagnostic]]:
        """Get diagnostics for all open documents."""
        all_diagnostics = {}
        
        for file_path in self.documents.keys():
            diagnostics = self.get_diagnostics(file_path)
            if diagnostics:
                all_diagnostics[file_path] = diagnostics
        
        return all_diagnostics
    
    # ==================== Go to Definition ====================
    
    def goto_definition(self, file_path: str, line: int, character: int) -> Optional[Location]:
        """Go to definition of symbol at position."""
        doc = self.documents.get(file_path)
        if not doc:
            return None
        
        # Request goto definition
        Path(file_path).as_uri()
        
        # For now, use simple regex-based finding
        # In production, use proper LSP definition request
        return self._find_definition_simple(file_path, line)
    
    def _find_definition_simple(self, file_path: str, target_line: int) -> Optional[Location]:
        """Simple definition finder based on name matching."""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Find function/class definitions
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Look for definitions
                if stripped.startswith('def ') or stripped.startswith('class '):
                    stripped.split()[1].split('(')[0].split(':')[0]
                    
                    # Return first definition
                    return Location(
                        uri=Path(file_path).as_uri(),
                        range=Range(
                            start=Position(line=i, character=0),
                            end=Position(line=i, character=len(line))
                        )
                    )
        except:
            pass
        
        return None
    
    # ==================== Hover ====================
    
    def get_hover(self, file_path: str, line: int, character: int) -> Optional[str]:
        """Get hover information for symbol at position."""
        doc = self.documents.get(file_path)
        if not doc:
            return None
        
        # Simple hover - find symbol at line and return its signature
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            if line < len(lines):
                line_content = lines[line].strip()
                
                # Look for function/class definition
                if 'def ' in line_content or 'class ' in line_content:
                    return line_content
                
                # Look for import
                if 'import ' in line_content or 'from ' in line_content:
                    return line_content
        
        except:
            pass
        
        return None
    
    # ==================== Code Actions ====================
    
    def get_code_actions(self, file_path: str, line: int, character: int) -> List[Dict]:
        """Get available code actions (quick fixes)."""
        # Simple code actions based on diagnostics
        diagnostics = self.get_diagnostics(file_path)
        
        actions = []
        for diag in diagnostics:
            if diag.range.start.line == line:
                # Generate fix action based on error type
                if 'undefined' in diag.message.lower():
                    actions.append({
                        'title': 'Import missing symbol',
                        'command': 'quickfix.import'
                    })
                elif 'unused' in diag.message.lower():
                    actions.append({
                        'title': 'Remove unused import',
                        'command': 'quickfix.remove_unused'
                    })
        
        return actions
    
    # ==================== Formatting ====================
    
    def format_document(self, file_path: str) -> bool:
        """Format document using LSP."""
        doc = self.documents.get(file_path)
        if not doc:
            return False
        
        # Request document formatting
        self._send_request(doc.language, 'textDocument/formatting', {
            'textDocument': {'uri': Path(file_path).as_uri()},
            'options': {
                'tabSize': 4,
                'insertSpaces': True
            }
        })
        
        return True
    
    # ==================== Utility ====================
    
    def restart_servers(self):
        """Restart all language servers."""
        for language, server in self.servers.items():
            try:
                server.terminate()
            except:
                pass
        
        self.servers.clear()
        self.documents.clear()
        self._initialized = False
        
        # Restart
        for language in self.LSP_CONFIGS.keys():
            self._start_server(language)
    
    def shutdown(self):
        """Shutdown all LSP servers."""
        for language, server in self.servers.items():
            try:
                self._send_notification(language, 'shutdown', None)
                server.terminate()
            except:
                pass
        
        self.servers.clear()


# Simple version without full LSP - uses basic tools
class SimpleLSPClient:
    """Simplified LSP client using basic command-line tools."""
    
    def __init__(self, root_path: Optional[str] = None):
        self.root = Path(root_path) if root_path else PROJECT_ROOT
    
    def lint_file(self, file_path: str) -> List[Dict]:
        """Lint a file using available tools."""
        ext = Path(file_path).suffix.lower()
        results = []
        
        if ext == '.py':
            # Try ruff
            try:
                result = subprocess.run(
                    ['ruff', 'check', file_path, '--output-format=json'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout:
                    try:
                        errors = json.loads(result.stdout)
                        for err in errors:
                            results.append({
                                'line': err.get('location', {}).get('row', 1),
                                'column': err.get('location', {}).get('column', 0),
                                'message': err.get('message', ''),
                                'severity': 'error' if err.get('code', '').startswith('E') else 'warning',
                                'source': 'ruff'
                            })
                    except:
                        pass
            except:
                pass
            
            # Try mypy
            try:
                result = subprocess.run(
                    ['mypy', file_path, '--no-error-summary', '--line-regex'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                for line in result.stdout.split('\n'):
                    if ': error:' in line or ': warning:' in line:
                        results.append({
                            'message': line,
                            'severity': 'error' if ': error:' in line else 'warning',
                            'source': 'mypy'
                        })
            except:
                pass
        
        return results
    
    def get_diagnostics(self, file_path: str) -> Dict:
        """Get diagnostics for a file."""
        return {
            'file': file_path,
            'diagnostics': self.lint_file(file_path),
            'timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    import sys
    
    client = SimpleLSPClient()
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(json.dumps(client.get_diagnostics(file_path), indent=2))
    else:
        print("Usage: python omega_lsp_client.py <file_path>")