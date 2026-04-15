"""
Paradise Stack - AutoCoder
LLM-powered autonomous code generation and modification.
"""

import asyncio
import subprocess
import json
import re
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

EXECUTOR = ThreadPoolExecutor(max_workers=4)

LLAMA_CLI = None
for path in ["llama-cli", "C:/Users/HomeUser/.local/bin/llama-cli.exe", 
             "C:/Users/HomeUser/.local/bin/llama-cli"]:
    if Path(path).exists():
        LLAMA_CLI = path
        break

def find_model() -> Optional[str]:
    search_paths = [
        Path("C:/Users/HomeUser/.lmstudio/models/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF/qwen2.5-coder-7b-instruct-q4_k_m.gguf"),
        Path("C:/Users/HomeUser/.lmstudio/models/bartowski/Qwen_Qwen3-Coder-Next-GGUF/Qwen_Qwen3-Coder-Next-imatrix.gguf"),
    ]
    for p in search_paths:
        if p.exists():
            return str(p)
    for p in Path("C:/Users/HomeUser/.lmstudio/models").rglob("*.gguf"):
        if "qwen" in str(p).lower():
            return str(p)
    return None

MODEL_PATH = find_model()

class LLMInterface:
    def __init__(self):
        self.model_path = MODEL_PATH
        self.llama_cli = LLAMA_CLI
        
    async def generate(self, prompt: str, max_tokens: int = 4096, temp: float = 0.3) -> str:
        if not self.model_path or not self.llama_cli:
            print("    [LLM] No model available, using templates")
            return ""
        
        prompt_file = OUTPUT_DIR / f"prompt_{int(time.time())}.txt"
        prompt_file.write_text(prompt)
        
        try:
            cmd = [
                self.llama_cli,
                "-m", self.model_path,
                "-f", str(prompt_file),
                "-t", "4",
                "-c", "4096",
                "--temp", str(temp),
                "-n", str(max_tokens),
                "--log-disable",
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            prompt_file.unlink()
            
            if result.returncode == 0 and result.stdout:
                return self._clean_output(result.stdout)
        except Exception as e:
            print(f"    [LLM] Error: {e}")
            try:
                prompt_file.unlink()
            except:
                pass
        
        return ""
    
    def _clean_output(self, output: str) -> str:
        lines = output.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code = not in_code
                continue
            if in_code:
                code_lines.append(line)
            elif any(c in line for c in ['def ', 'class ', 'import ', 'from ', 'async ', 'const ', 'let ', '<!DOCTYPE']):
                in_code = True
                code_lines.append(line)
        
        if code_lines:
            return '\n'.join(code_lines)
        return output[:5000]
    
    def is_available(self) -> bool:
        return bool(self.model_path and self.llama_cli)

class CodebaseReader:
    def __init__(self, root: Path):
        self.root = root
        
    def get_context(self, max_files: int = 50) -> Dict:
        files = []
        patterns = ["*.py", "*.js", "*.ts"]
        ignore = {".git", "node_modules", "__pycache__", ".venv", ".paradise"}
        
        for p in patterns:
            for f in self.root.rglob(p):
                if not any(ig in f.parts for ig in ignore):
                    files.append(str(f.relative_to(self.root)))
        
        return {
            "project_name": self.root.name,
            "files": files[:max_files],
            "has_flask": any("flask" in f.read_text(errors='ignore').lower() for f in self.root.rglob("*.py") if f.is_file()),
            "has_fastapi": any("fastapi" in f.read_text(errors='ignore').lower() for f in self.root.rglob("*.py") if f.is_file()),
        }

class AutoCoder:
    def __init__(self, root: Optional[Path] = None):
        self.root = root or PROJECT_ROOT
        self.reader = CodebaseReader(self.root)
        self.llm = LLMInterface()
        
    async def code(self, task: str, language: str = "python") -> Tuple[str, bool]:
        """Generate code for task."""
        start_time = time.time()
        task_lower = task.lower()
        
        context = self.reader.get_context()
        
        prompt = self._build_prompt(task, language, context)
        
        print(f"    [AutoCoder] LLM available: {self.llm.is_available()}")
        
        if self.llm.is_available():
            print(f"    [AutoCoder] Generating with LLM...")
            code = await self.llm.generate(prompt)
        else:
            code = ""
        
        if not code or len(code) < 100:
            print(f"    [AutoCoder] Using smart templates...")
            code = self._template_generate(task, language)
        
        generation_time = time.time() - start_time
        print(f"    [AutoCoder] Generated {len(code)} chars in {generation_time:.2f}s")
        
        return code, self.llm.is_available()
    
    def _build_prompt(self, task: str, language: str, context: Dict) -> str:
        framework_note = ""
        if context.get("has_fastapi"):
            framework_note = "Use FastAPI since the project already has FastAPI."
        elif context.get("has_flask"):
            framework_note = "Use Flask since the project already has Flask."
        
        prompt = f'''Write a complete, working {language} program.

Task: {task}
{framework_note}

Requirements:
- Complete, runnable code (no placeholders)
- Proper error handling
- Type hints for Python
- Docstrings
- Follow best practices

Output ONLY the code (no markdown, no explanations):
'''
        return prompt
    
    def _template_generate(self, task: str, language: str) -> str:
        """Generate comprehensive code using smart templates."""
        task_lower = task.lower()
        
        templates = {
            "python": {
                "rest_api": '''"""Paradise Stack Generated - REST API
Task: {task}
"""
from flask import Flask, jsonify, request
from functools import wraps
import time

app = Flask(__name__)

# In-memory data store
data_store = {{}}
next_id = 1

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{{func.__name__}} took {{time.time() - start:.3f}}s")
        return result
    return wrapper

@app.route("/")
@timer
def index():
    return jsonify({{
        "service": "Paradise REST API",
        "version": "1.0",
        "endpoints": ["/api/items", "/api/items/<id>"]
    }})

@app.route("/api/items", methods=["GET"])
@timer
def get_items():
    return jsonify({{"items": list(data_store.values()), "count": len(data_store)}})

@app.route("/api/items", methods=["POST"])
@timer
def create_item():
    global next_id
    item = request.get_json()
    if not item:
        return jsonify({{"error": "No data provided"}}), 400
    
    item["id"] = next_id
    next_id += 1
    data_store[item["id"]] = item
    return jsonify(item), 201

@app.route("/api/items/<int:item_id>", methods=["GET"])
@timer
def get_item(item_id):
    item = data_store.get(item_id)
    if not item:
        return jsonify({{"error": "Item not found"}}), 404
    return jsonify(item)

@app.route("/api/items/<int:item_id>", methods=["PUT"])
@timer
def update_item(item_id):
    if item_id not in data_store:
        return jsonify({{"error": "Item not found"}}), 404
    
    updates = request.get_json()
    data_store[item_id].update(updates)
    return jsonify(data_store[item_id])

@app.route("/api/items/<int:item_id>", methods=["DELETE"])
@timer
def delete_item(item_id):
    if item_id not in data_store:
        return jsonify({{"error": "Item not found"}}), 404
    
    del data_store[item_id]
    return jsonify({{"message": "Deleted"}}), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({{"error": "Not found"}}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({{"error": "Internal server error"}}), 500

if __name__ == "__main__":
    print("Starting Paradise REST API on http://localhost:5000")
    app.run(debug=True, port=5000)
''',

                "web_server": '''"""Paradise Stack Generated - Web Server
Task: {task}
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from pathlib import Path

PORT = 8000

class ParadiseHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        return super().do_GET()
    
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            print(f"Received: {{data}}")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({{"status": "ok", "received": data}}).encode())
        except Exception as e:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({{"error": str(e)}}).encode())

    def log_message(self, format, *args):
        print(f"[{{}}] {{}}".format(self.log_date_time_string(), format % args))

def main():
    server = HTTPServer(("0.0.0.0", PORT), ParadiseHandler)
    print(f"Paradise Web Server running on http://localhost:{{PORT}}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nShutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()
''',

                "cli": '''"""Paradise Stack Generated - CLI Tool
Task: {task}
"""
import sys
import argparse
import json
from pathlib import Path

def cmd_init(args):
    print("Initializing project...")
    Path(".paradise").mkdir(exist_ok=True)
    (Path(".paradise/config.json")).write_text(json.dumps({{"version": "1.0"}}))
    print("Done!")

def cmd_run(args):
    print(f"Running {{args.name}}...")

def cmd_list(args):
    print("Available commands:")
    print("  init  - Initialize project")
    print("  run   - Run a task")
    print("  list  - List tasks")

def main():
    parser = argparse.ArgumentParser(description="Paradise CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    p_init = subparsers.add_parser("init", help="Initialize")
    p_run = subparsers.add_parser("run", help="Run")
    p_run.add_argument("name", help="Task name")
    p_list = subparsers.add_parser("list", help="List")
    
    args = parser.parse_args()
    
    if args.command == "init":
        cmd_init(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
''',

                "database": '''"""Paradise Stack Generated - Database Operations
Task: {task}
"""
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Optional

DB_PATH = "paradise.db"

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Database initialized")

def create_item(name: str, description: str = "") -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO items (name, description) VALUES (?, ?)",
            (name, description)
        )
        return cursor.lastrowid

def get_item(item_id: int) -> Optional[Dict]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def list_items() -> List[Dict]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM items ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

def delete_item(item_id: int) -> bool:
    with get_connection() as conn:
        conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        return conn.total_changes > 0

if __name__ == "__main__":
    init_db()
    item_id = create_item("Test Item", "Description here")
    print(f"Created item {{item_id}}")
    print(list_items())
''',

                "web_page": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paradise Stack</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: system-ui, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 2rem; }}
        h1 {{ color: #00d4ff; margin-bottom: 1rem; }}
        .card {{ background: #16213e; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; }}
        button {{ background: #00d4ff; color: #000; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }}
        button:hover {{ opacity: 0.8; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Paradise Stack Generated</h1>
        <div class="card">
            <h2>Task: {task}</h2>
            <p>Generated by Paradise Stack</p>
        </div>
        <button onclick="alert(\'Paradise!\')">Click Me</button>
    </div>
</body>
</html>
''',

                "general": '''"""Paradise Stack Generated
Task: {task}
"""
import sys
from pathlib import Path

def main():
    print("Paradise Stack Output")
    print("=" * 40)
    print("Task: {task}")
    print("=" * 40)
    
    # Implementation here
    result = process_task()
    print(f"Result: {{result}}")
    
    return 0

def process_task():
    """Process the task."""
    return "Task completed successfully"

if __name__ == "__main__":
    sys.exit(main())
'''
            },
            "javascript": {
                "general": '''// Paradise Stack Generated
// Task: {task}
console.log("Paradise Stack Output");

async function main() {{
    console.log("Task: {task}");
    // Implementation here
}}

main().catch(console.error);
'''
            }
        }
        
        lang_templates = templates.get(language, templates["python"])
        
        if "rest" in task_lower or "api" in task_lower:
            template = lang_templates.get("rest_api", lang_templates["general"])
        elif "web" in task_lower and ("server" in task_lower or "serve" in task_lower):
            template = lang_templates.get("web_server", lang_templates["general"])
        elif "cli" in task_lower or "command" in task_lower:
            template = lang_templates.get("cli", lang_templates["general"])
        elif "db" in task_lower or "database" in task_lower or "sql" in task_lower:
            template = lang_templates.get("database", lang_templates["general"])
        elif "html" in task_lower or "page" in task_lower or "web" in task_lower:
            template = lang_templates.get("web_page", lang_templates["general"])
        else:
            template = lang_templates["general"]
        
        return template.format(task=task)


async def autocode(task: str, language: str = "python") -> str:
    coder = AutoCoder()
    code, _ = await coder.code(task, language)
    return code


if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello World"
    code = asyncio.run(autocode(task))
    print(code)
