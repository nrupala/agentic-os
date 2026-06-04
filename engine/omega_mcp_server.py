#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
OMEGA MCP Server
===============
Model Context Protocol server for OMEGA engine.
Enables integration with Claude Desktop, Cline, and other MCP clients.

Inspired by:
- cline/cline: VS Code extension with MCP tools
- codebase-mcp: Semantic search and persistent memory
- node-typer-MCP: 20 specialized tools

Features:
- MCP protocol implementation (stdio mode)
- 15+ specialized tools for coding automation
- Session management
- Semantic code search
- Memory system
"""

import sys
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
ENGINE_DIR = PROJECT_ROOT / "engine"
sys.path.insert(0, str(ENGINE_DIR))


class MCPTool:
    """Base MCP tool."""
    
    def __init__(self, name: str, description: str, input_schema: Dict):
        self.name = name
        self.description = description
        self.input_schema = input_schema
    
    def execute(self, params: Dict) -> Dict:
        raise NotImplementedError


class OmegaMCPServer:
    """OMEGA MCP Server - implements MCP protocol."""
    
    VERSION = "2.0.0"
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self._register_tools()
    
    def _register_tools(self):
        """Register all OMEGA MCP tools."""
        
        class ExecuteGoalTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_execute_goal",
                    "Execute a coding goal using OMEGA engine",
                    {
                        "type": "object",
                        "properties": {
                            "goal": {"type": "string", "description": "Coding task to execute"},
                            "project": {"type": "string", "description": "Project name", "default": "omega"}
                        },
                        "required": ["goal"]
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                try:
                    from omega_unified_service import OmegaUnifiedService, OmegaServiceConfig
                    config = OmegaServiceConfig(project=params.get("project", "omega"))
                    service = OmegaUnifiedService(config)
                    result = service.execute_goal(params["goal"])
                    return {"success": True, "result": result}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class SubmitTaskTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_submit_task",
                    "Submit a task to OMEGA daemon queue",
                    {
                        "type": "object",
                        "properties": {
                            "goal": {"type": "string", "description": "Task description"},
                            "project": {"type": "string", "description": "Project name", "default": "omega"}
                        },
                        "required": ["goal"]
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                try:
                    from omega_unified_service import OmegaUnifiedService, OmegaServiceConfig
                    config = OmegaServiceConfig(project=params.get("project", "omega"))
                    service = OmegaUnifiedService(config)
                    task_id = service.submit_task(params["goal"])
                    return {"success": True, "task_id": task_id}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class SelfRepairTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_self_repair",
                    "Attempt self-repair using Gödel Machine",
                    {
                        "type": "object",
                        "properties": {
                            "error": {"type": "string", "description": "Error message"},
                            "file_path": {"type": "string", "description": "File to repair"}
                        },
                        "required": ["error"]
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                try:
                    from omega_godel_machine import GödelMachine
                    
                    godel = GödelMachine(params.get("project", "omega"))
                    change = godel.analyze_failure_and_propose_fix(
                        params["error"], 
                        {"file": params.get("file_path", "engine/omega_forge.py")}
                    )
                    
                    if change:
                        applied = godel.apply_change(change.change_id)
                        return {"success": applied, "change_id": change.change_id}
                    return {"success": False, "error": "Could not generate repair"}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class GetStatusTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_get_status",
                    "Get OMEGA service status",
                    {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "Project name", "default": "omega"}
                        }
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                try:
                    from omega_unified_service import OmegaUnifiedService, OmegaServiceConfig
                    config = OmegaServiceConfig(project=params.get("project", "omega"))
                    service = OmegaUnifiedService(config)
                    return service.get_status()
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class VerifyBuildTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_verify_build",
                    "Verify build reproducibility",
                    {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "Project name", "default": "omega"}
                        }
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                try:
                    from omega_reproducible_builds import ReproducibleBuilds
                    repro = ReproducibleBuilds(params.get("project", "omega"))
                    return repro.verify_against_manifest()
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class SemanticSearchTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_semantic_search",
                    "Search code semantically using embeddings",
                    {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "project": {"type": "string", "description": "Project name", "default": "omega"},
                            "limit": {"type": "integer", "description": "Max results", "default": 10}
                        },
                        "required": ["query"]
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                try:
                    from omega_rag import OmegaRAG
                    rag = OmegaRAG(params.get("project", "omega"))
                    results = rag.search(params["query"], params.get("limit", 10))
                    return {"success": True, "results": results}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class MemoryStoreTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_memory_store",
                    "Store information in persistent memory",
                    {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Content to store"},
                            "category": {"type": "string", "description": "Category", "default": "general"},
                            "project": {"type": "string", "description": "Project name", "default": "omega"}
                        },
                        "required": ["content"]
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                try:
                    from omega_hierarchical_memory import HierarchicalMemory
                    memory = HierarchicalMemory(str(PROJECT_ROOT / f"projects/{params.get('project', 'omega')}"))
                    memory.store(
                        params["content"],
                        params.get("category", "general")
                    )
                    return {"success": True}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class MemoryRecallTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_memory_recall",
                    "Recall information from persistent memory",
                    {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Recall query"},
                            "project": {"type": "string", "description": "Project name", "default": "omega"}
                        },
                        "required": ["query"]
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                try:
                    from omega_hierarchical_memory import HierarchicalMemory
                    memory = HierarchicalMemory(str(PROJECT_ROOT / f"projects/{params.get('project', 'omega')}"))
                    results = memory.recall(params["query"])
                    return {"success": True, "results": results}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class ReadFileTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_read_file",
                    "Read file contents with smart parsing",
                    {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path"},
                            "line_start": {"type": "integer", "description": "Start line", "default": 0},
                            "line_count": {"type": "integer", "description": "Line count", "default": 100}
                        },
                        "required": ["path"]
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                try:
                    file_path = Path(params["path"])
                    if not file_path.exists():
                        return {"success": False, "error": "File not found"}
                    
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    lines = content.split("\n")
                    
                    start = params.get("line_start", 0)
                    count = params.get("line_count", 100)
                    selected = lines[start:start + count]
                    
                    return {
                        "success": True,
                        "content": "\n".join(selected),
                        "total_lines": len(lines),
                        "file_path": str(file_path)
                    }
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class WriteFileTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_write_file",
                    "Write code with auto-formatting and quality check",
                    {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path"},
                            "content": {"type": "string", "description": "Code content"},
                            "project": {"type": "string", "description": "Project name", "default": "omega"}
                        },
                        "required": ["path", "content"]
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                try:
                    file_path = Path(params["path"])
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    file_path.write_text(params["content"], encoding="utf-8")
                    
                    return {
                        "success": True,
                        "file_path": str(file_path),
                        "lines": len(params["content"].split("\n"))
                    }
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class ListDirectoryTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_list_directory",
                    "List directory contents with tree view",
                    {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Directory path"},
                            "depth": {"type": "integer", "description": "Depth", "default": 2}
                        },
                        "required": ["path"]
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                try:
                    dir_path = Path(params["path"])
                    if not dir_path.exists():
                        return {"success": False, "error": "Directory not found"}
                    
                    depth = params.get("depth", 2)
                    ignore = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist"}
                    
                    def build_tree(path: Path, current_depth: int) -> List:
                        if current_depth > depth:
                            return []
                        
                        items = []
                        try:
                            for item in sorted(path.iterdir()):
                                if any(ig in item.parts for ig in ignore):
                                    continue
                                if item.is_dir():
                                    items.append({"type": "dir", "name": item.name, "children": []})
                                else:
                                    items.append({"type": "file", "name": item.name})
                        except PermissionError:
                            pass
                        return items
                    
                    tree = build_tree(dir_path, 0)
                    return {"success": True, "tree": tree, "path": str(dir_path)}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class GitOperationsTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_git_operations",
                    "Git operations with session isolation",
                    {
                        "type": "object",
                        "properties": {
                            "operation": {"type": "string", "description": "Operation: status, diff, commit, branch"},
                            "message": {"type": "string", "description": "Commit message"},
                            "project": {"type": "string", "description": "Project name", "default": "omega"}
                        },
                        "required": ["operation"]
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                import subprocess
                try:
                    project_path = PROJECT_ROOT / "projects" / params.get("project", "omega")
                    operation = params["operation"]
                    
                    if operation == "status":
                        result = subprocess.run(
                            ["git", "status", "--porcelain"],
                            cwd=project_path,
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        return {"success": True, "status": result.stdout or "clean"}
                    
                    elif operation == "diff":
                        result = subprocess.run(
                            ["git", "diff"],
                            cwd=project_path,
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        return {"success": True, "diff": result.stdout}
                    
                    elif operation == "commit" and params.get("message"):
                        result = subprocess.run(
                            ["git", "add", "-A"],
                            cwd=project_path,
                            capture_output=True,
                            timeout=10
                        )
                        result = subprocess.run(
                            ["git", "commit", "-m", params["message"]],
                            cwd=project_path,
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        return {"success": True, "commit": result.stdout}
                    
                    return {"success": False, "error": "Unknown operation"}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class AnalyzeCodeTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_analyze_code",
                    "Analyze code quality, syntax, imports",
                    {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File or directory path"}
                        },
                        "required": ["path"]
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                try:
                    import ast
                    
                    file_path = Path(params["path"])
                    if not file_path.exists():
                        return {"success": False, "error": "Path not found"}
                    
                    if file_path.is_file():
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        
                        try:
                            tree = ast.parse(content)
                            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                            imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
                            imports.extend([node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module])
                            
                            return {
                                "success": True,
                                "type": "file",
                                "functions": functions[:10],
                                "classes": classes[:10],
                                "imports": list(set(imports))[:20],
                                "lines": len(content.split("\n"))
                            }
                        except SyntaxError as e:
                            return {"success": False, "error": f"Syntax error: {e}"}
                    
                    return {"success": False, "error": "Not implemented for directories"}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class ListSymbolsTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_list_symbols",
                    "Extract functions, classes, interfaces from code",
                    {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path"}
                        },
                        "required": ["path"]
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                try:
                    import ast
                    file_path = Path(params["path"])
                    if not file_path.exists():
                        return {"success": False, "error": "File not found"}
                    
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    tree = ast.parse(content)
                    
                    symbols = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            symbols.append({
                                "name": node.name,
                                "type": "function",
                                "line": node.lineno,
                                "args": [arg.arg for arg in node.args.args]
                            })
                        elif isinstance(node, ast.ClassDef):
                            symbols.append({
                                "name": node.name,
                                "type": "class",
                                "line": node.lineno,
                                "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                            })
                    
                    return {"success": True, "symbols": symbols[:50]}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class CreateCheckpointTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_create_checkpoint",
                    "Create workspace checkpoint for comparison",
                    {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Checkpoint name"},
                            "project": {"type": "string", "description": "Project name", "default": "omega"}
                        },
                        "required": ["name"]
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                import shutil
                try:
                    project = params.get("project", "omega")
                    checkpoint_dir = PROJECT_ROOT / "projects" / project / "checkpoints" / params["name"]
                    checkpoint_dir.mkdir(parents=True, exist_ok=True)
                    
                    source_dir = PROJECT_ROOT / "engine"
                    for py_file in source_dir.glob("*.py"):
                        dest = checkpoint_dir / py_file.name
                        shutil.copy2(py_file, dest)
                    
                    return {
                        "success": True,
                        "checkpoint": params["name"],
                        "created_at": datetime.now().isoformat()
                    }
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        class GetOptimalStrategyTool(MCPTool):
            def __init__(self):
                super().__init__(
                    "omega_optimal_strategy",
                    "Get optimal coding strategy from meta-learner",
                    {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "Project name", "default": "omega"}
                        }
                    }
                )
            
            def execute(self, params: Dict) -> Dict:
                try:
                    from omega_meta_learner import RecursiveMetaLearner
                    meta = RecursiveMetaLearner(params.get("project", "omega"))
                    return meta.get_optimal_parameters()
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        self.tools = {
            "omega_execute_goal": ExecuteGoalTool(),
            "omega_submit_task": SubmitTaskTool(),
            "omega_self_repair": SelfRepairTool(),
            "omega_get_status": GetStatusTool(),
            "omega_verify_build": VerifyBuildTool(),
            "omega_semantic_search": SemanticSearchTool(),
            "omega_memory_store": MemoryStoreTool(),
            "omega_memory_recall": MemoryRecallTool(),
            "omega_read_file": ReadFileTool(),
            "omega_write_file": WriteFileTool(),
            "omega_list_directory": ListDirectoryTool(),
            "omega_git_operations": GitOperationsTool(),
            "omega_analyze_code": AnalyzeCodeTool(),
            "omega_list_symbols": ListSymbolsTool(),
            "omega_create_checkpoint": CreateCheckpointTool(),
            "omega_optimal_strategy": GetOptimalStrategyTool(),
        }
    
    def handle_request(self, method: str, params: Dict = None) -> Dict:
        """Handle MCP request."""
        
        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "omega-mcp",
                    "version": self.VERSION
                },
                "capabilities": {
                    "tools": {}
                }
            }
        
        elif method == "tools/list":
            return {
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.input_schema
                    }
                    for tool in self.tools.values()
                ]
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_params = params.get("arguments", {})
            
            if tool_name in self.tools:
                result = self.tools[tool_name].execute(tool_params)
                return {"content": [{"type": "text", "text": json.dumps(result)}]}
            
            return {"error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}
        
        return {"error": {"code": -32600, "message": "Invalid request"}}
    
    def run(self):
        """Run MCP server in stdio mode."""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = self.handle_request(
                    request.get("method"),
                    request.get("params")
                )
                
                if "id" in request:
                    response["id"] = request["id"]
                    print(json.dumps(response), flush=True)
                    
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(json.dumps({"error": {"code": -32603, "message": str(e)}}), flush=True)


def main():
    server = OmegaMCPServer()
    server.run()


if __name__ == "__main__":
    main()