"""
Paradise Stack - IntelliDaemon
VS Code IntelliSense-style background code intelligence daemon.

Features:
- Background code indexing (like VS Code's language server)
- Async non-blocking build/execute
- Intelligent code completion
- Symbol resolution
- Real-time diagnostics
- Component-aware code generation
"""

import asyncio
import json
import time
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

EXECUTOR = ThreadPoolExecutor(max_workers=4)

@dataclass
class Symbol:
    name: str
    kind: str  # function, class, variable, import
    file: str
    line: int
    col: int
    signature: str = ""
    doc: str = ""
    references: List[str] = field(default_factory=list)

@dataclass
class CodeFile:
    path: str
    content: str
    symbols: List[Symbol] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    diagnostics: List[Dict] = field(default_factory=list)
    hash: str = ""
    indexed_at: float = 0

class Indexer:
    """Background code indexer - scans and indexes codebase."""
    
    def __init__(self):
        self.index: Dict[str, Symbol] = {}
        self.files: Dict[str, CodeFile] = {}
        self.symbols_by_file: Dict[str, List[str]] = defaultdict(list)
        self.symbols_by_name: Dict[str, List[Symbol]] = defaultdict(list)
        self.import_graph: Dict[str, Set[str]] = defaultdict(set)
        self.indexing = False
        
    def scan_directory(self, root: Path, patterns: List[str] = None) -> List[Path]:
        """Scan directory for code files."""
        if patterns is None:
            patterns = ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.java", "*.go", "*.rs"]
        
        files = []
        ignore = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".paradise"}
        
        for pattern in patterns:
            files.extend(root.rglob(pattern))
        
        return [f for f in files if not any(ig in f.parts for ig in ignore)]
    
    async def index_file(self, filepath: Path) -> CodeFile:
        """Index a single file."""
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            file_hash = hashlib.md5(content.encode()).hexdigest()
            
            if filepath in self.files:
                if self.files[str(filepath)].hash == file_hash:
                    return self.files[str(filepath)]
            
            cf = CodeFile(
                path=str(filepath),
                content=content,
                hash=file_hash,
                indexed_at=time.time()
            )
            
            cf.symbols = await asyncio.get_event_loop().run_in_executor(
                EXECUTOR, self._extract_symbols, filepath, content
            )
            cf.imports = self._extract_imports(content, filepath.suffix)
            cf.diagnostics = await asyncio.get_event_loop().run_in_executor(
                EXECUTOR, self._lint_file, filepath, content
            )
            
            for sym in cf.symbols:
                self.index[sym.name] = sym
                self.symbols_by_file[filepath.name].append(sym.name)
                self.symbols_by_name[sym.name].append(sym)
            
            for imp in cf.imports:
                self.import_graph[str(filepath)].add(imp)
            
            self.files[str(filepath)] = cf
            return cf
            
        except Exception as e:
            return CodeFile(path=str(filepath), content="", hash="", indexed_at=time.time())
    
    def _extract_symbols(self, filepath: Path, content: str) -> List[Symbol]:
        """Extract symbols from file content."""
        symbols = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if filepath.suffix == '.py':
                if stripped.startswith('def '):
                    name = stripped.split('(')[0].replace('def ', '')
                    symbols.append(Symbol(
                        name=name, kind='function', file=str(filepath),
                        line=i+1, col=0, signature=stripped
                    ))
                elif stripped.startswith('class '):
                    name = stripped.split('(')[0].replace('class ', '')
                    symbols.append(Symbol(
                        name=name, kind='class', file=str(filepath),
                        line=i+1, col=0, signature=stripped
                    ))
                elif stripped.startswith('@'):
                    continue
                elif '=' in stripped and not stripped.startswith('#'):
                    var = stripped.split('=')[0].strip()
                    if var and ' ' not in var:
                        symbols.append(Symbol(
                            name=var, kind='variable', file=str(filepath),
                            line=i+1, col=0
                        ))
            
            elif filepath.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                if 'function ' in stripped or stripped.startswith('async '):
                    name = stripped.split('(')[0].split()[-1]
                    symbols.append(Symbol(
                        name=name, kind='function', file=str(filepath),
                        line=i+1, col=0, signature=stripped
                    ))
                elif 'class ' in stripped:
                    name = stripped.split('{')[0].replace('class ', '').strip()
                    symbols.append(Symbol(
                        name=name, kind='class', file=str(filepath),
                        line=i+1, col=0, signature=stripped
                    ))
                elif 'const ' in stripped or 'let ' in stripped or 'var ' in stripped:
                    name = stripped.split('=')[0].split()[-1]
                    if name and name not in ['{}', '[]']:
                        symbols.append(Symbol(
                            name=name, kind='variable', file=str(filepath),
                            line=i+1, col=0
                        ))
        
        return symbols
    
    def _extract_imports(self, content: str, ext: str) -> List[str]:
        """Extract imports from file."""
        imports = []
        
        for line in content.split('\n'):
            stripped = line.strip()
            if ext == '.py':
                if stripped.startswith('import ') or stripped.startswith('from '):
                    imports.append(stripped)
            elif stripped.startswith('import ') or stripped.startswith('require('):
                imports.append(stripped)
        
        return imports
    
    def _lint_file(self, filepath: Path, content: str) -> List[Dict]:
        """Quick lint check."""
        diagnostics = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if 'except:' in stripped and '# noqa' not in stripped:
                diagnostics.append({
                    "file": str(filepath),
                    "line": i+1,
                    "col": 0,
                    "severity": "warning",
                    "message": "Bare except clause"
                })
            
            if 'print(' in stripped and filepath.suffix == '.py' and 'logging' not in content[:1000]:
                if i > 5:
                    diagnostics.append({
                        "file": str(filepath),
                        "line": i+1,
                        "col": 0,
                        "severity": "info",
                        "message": "Consider using logging"
                    })
            
            if len(line) > 120:
                diagnostics.append({
                    "file": str(filepath),
                    "line": i+1,
                    "col": 0,
                    "severity": "info",
                    "message": "Line too long"
                })
        
        return diagnostics
    
    async def full_reindex(self, root: Path) -> Dict:
        """Reindex entire codebase."""
        self.indexing = True
        files = self.scan_directory(root)
        
        tasks = [self.index_file(f) for f in files]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self.indexing = False
        return {
            "files_indexed": len(self.files),
            "symbols_found": len(self.index),
            "diagnostics": sum(len(f.diagnostics) for f in self.files.values())
        }


class CodeGenerator:
    """Context-aware code generator."""
    
    def __init__(self, indexer: Indexer):
        self.indexer = indexer
        self.cache: Dict[str, str] = {}
        
    def get_context(self, filepath: str = "") -> Dict:
        """Get relevant context for code generation."""
        context = {
            "files": list(self.indexer.files.keys()),
            "symbols": {},
            "recent_symbols": [],
            "diagnostics": []
        }
        
        for name, syms in list(self.indexer.symbols_by_name.items())[:50]:
            context["symbols"][name] = [
                {"file": s.file, "line": s.line, "kind": s.kind}
                for s in syms[:3]
            ]
        
        for cf in list(self.indexer.files.values())[-5:]:
            context["recent_symbols"].extend(cf.symbols[:2])
        
        for cf in self.indexer.files.values():
            context["diagnostics"].extend(cf.diagnostics)
        
        return context
    
    def generate_with_context(self, task: str, language: str, target_file: str = "") -> str:
        """Generate code with awareness of existing codebase."""
        context = self.get_context(target_file)
        
        related = []
        for sym_name, sym_info in context["symbols"].items():
            if any(kw in task.lower() for kw in sym_name.lower().split('_')):
                related.extend(sym_info)
        
        prompt_parts = [
            f"# Task: {task}",
            f"# Language: {language}",
            "",
            "# Related existing code:"
        ]
        
        for rel in related[:5]:
            for cf in self.indexer.files.values():
                if cf.path.endswith(rel["file"]):
                    prompt_parts.append(f"\n# From {rel['file']} line {rel['line']}:")
                    lines = cf.content.split('\n')
                    start = max(0, rel['line'] - 2)
                    end = min(len(lines), rel['line'] + 5)
                    prompt_parts.extend(lines[start:end])
                    break
        
        if context["diagnostics"]:
            prompt_parts.append("\n# Existing issues to avoid:")
            for diag in context["diagnostics"][:3]:
                prompt_parts.append(f"# - {diag['message']} in {diag['file']}")
        
        return '\n'.join(prompt_parts)


class BuildScheduler:
    """Non-blocking async build scheduler."""
    
    def __init__(self, indexer: Indexer, generator: CodeGenerator):
        self.indexer = indexer
        self.generator = generator
        self.builds: Dict[str, Dict] = {}
        self.build_queue: asyncio.Queue = asyncio.Queue()
        self.running_builds: Set[str] = set()
        
    async def schedule_build(self, task: str, language: str) -> str:
        """Schedule a build (non-blocking)."""
        build_id = f"build_{int(time.time() * 1000)}"
        
        self.builds[build_id] = {
            "id": build_id,
            "task": task,
            "language": language,
            "status": "queued",
            "progress": 0,
            "started_at": time.time(),
            "completed_at": None,
            "output": None,
            "error": None
        }
        
        await self.build_queue.put(build_id)
        asyncio.create_task(self._process_builds())
        
        return build_id
    
    async def _process_builds(self):
        """Process builds from queue."""
        while not self.build_queue.empty():
            if len(self.running_builds) >= 2:
                await asyncio.sleep(0.5)
                continue
            
            build_id = await self.build_queue.get()
            asyncio.create_task(self._run_build(build_id))
    
    async def _run_build(self, build_id: str):
        """Run a single build."""
        self.running_builds.add(build_id)
        build = self.builds[build_id]
        
        try:
            build["status"] = "indexing"
            build["progress"] = 10
            await self.indexer.full_reindex(PROJECT_ROOT)
            
            build["status"] = "generating"
            build["progress"] = 50
            
            context = self.generator.get_context()
            
            wf_id = f"wf_{int(time.time())}"
            output_dir = OUTPUT_DIR / wf_id
            output_dir.mkdir(exist_ok=True)
            
            code = self.generator.generate_with_context(build["task"], build["language"])
            
            ext = {".py": "py", ".js": "js", ".ts": "ts", ".html": "html"}.get(
                self._get_ext(build["language"]), "txt"
            )
            fname = f"main.{ext}"
            
            (output_dir / fname).write_text(code, encoding='utf-8')
            
            manifest = {
                "workflow_id": wf_id,
                "task": build["task"],
                "language": build["language"],
                "status": "completed",
                "context_aware": True,
                "files": [fname]
            }
            (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
            
            build["status"] = "completed"
            build["progress"] = 100
            build["completed_at"] = time.time()
            build["output"] = str(output_dir)
            
        except Exception as e:
            build["status"] = "failed"
            build["error"] = str(e)
        
        finally:
            self.running_builds.discard(build_id)
    
    def _get_ext(self, language: str) -> str:
        return {".py": "py", ".js": "js", ".ts": "ts", ".html": "html"}.get(language, "txt")
    
    def get_build_status(self, build_id: str) -> Optional[Dict]:
        """Get build status."""
        return self.builds.get(build_id)


class IntelliDaemon:
    """
    VS Code IntelliSense-style daemon.
    Runs in background, indexes code, provides completions.
    """
    
    def __init__(self):
        self.indexer = Indexer()
        self.generator = CodeGenerator(self.indexer)
        self.scheduler = BuildScheduler(self.indexer, self.generator)
        self.running = False
        self.started_at = time.time()
        
    async def start(self):
        """Start the daemon."""
        self.running = True
        print("IntelliDaemon: Starting...")
        
        await self.indexer.full_reindex(PROJECT_ROOT)
        
        print(f"IntelliDaemon: Indexed {len(self.indexer.files)} files")
        print(f"IntelliDaemon: Found {len(self.indexer.index)} symbols")
        print("IntelliDaemon: Ready")
    
    async def complete(self, prefix: str, file: str = "") -> List[Dict]:
        """Get code completions (IntelliSense-style)."""
        completions = []
        prefix_lower = prefix.lower()
        
        for name, syms in self.indexer.symbols_by_name.items():
            if name.lower().startswith(prefix_lower):
                for sym in syms[:1]:
                    completions.append({
                        "label": name,
                        "kind": sym.kind,
                        "detail": f"{sym.kind} in {Path(sym.file).name}",
                        "insertText": name
                    })
        
        return completions[:20]
    
    async def goto_definition(self, symbol: str, file: str = "") -> Optional[Dict]:
        """Go to symbol definition."""
        sym = self.indexer.index.get(symbol)
        if sym:
            return {"file": sym.file, "line": sym.line, "col": sym.col}
        return None
    
    async def find_references(self, symbol: str) -> List[Dict]:
        """Find all references to symbol."""
        refs = []
        for name, syms in self.indexer.symbols_by_name.items():
            if name == symbol:
                for sym in syms:
                    refs.append({"file": sym.file, "line": sym.line})
        return refs
    
    async def build(self, task: str, language: str = "python") -> str:
        """Start a non-blocking build."""
        return await self.scheduler.schedule_build(task, language)
    
    def get_status(self) -> Dict:
        """Get daemon status."""
        return {
            "running": self.running,
            "uptime": time.time() - self.started_at,
            "files_indexed": len(self.indexer.files),
            "symbols": len(self.indexer.index),
            "running_builds": len(self.scheduler.running_builds),
            "queued_builds": self.scheduler.build_queue.qsize()
        }


DAEMON = IntelliDaemon()

async def main():
    await DAEMON.start()
    
    print("\n--- Testing IntelliDaemon ---")
    
    print("\n[1] Completions for 'sym':")
    completions = await DAEMON.complete("sym")
    print(f"    Found: {len(completions)} completions")
    
    print("\n[2] Non-blocking build:")
    build_id = await DAEMON.build("Create a simple REST API endpoint", "python")
    print(f"    Build ID: {build_id}")
    
    for _ in range(10):
        status = DAEMON.scheduler.get_build_status(build_id)
        if status:
            print(f"    Status: {status['status']} ({status['progress']}%)")
            if status["status"] in ["completed", "failed"]:
                break
        await asyncio.sleep(0.5)
    
    print("\n[3] Daemon status:")
    print(json.dumps(DAEMON.get_status(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
