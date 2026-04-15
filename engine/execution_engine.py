"""
Paradise Stack - Execution Engine
Professional code generation matching opencode quality.
"""

import asyncio
import subprocess
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

LLAMA_CLI = None
for path in ["llama-cli", "C:/Users/HomeUser/.local/bin/llama-cli.exe"]:
    if Path(path).exists():
        LLAMA_CLI = path
        break

MODEL_PATH = None
for p in Path("C:/Users/HomeUser/.lmstudio/models").rglob("*.gguf"):
    if "qwen" in str(p).lower():
        MODEL_PATH = str(p)
        break

class ExecutionEngine:
    """
    Professional code generation - opencode-quality output.
    """
    
    def __init__(self):
        self.llm_available = bool(MODEL_PATH and LLAMA_CLI)
        print(f"    [Executor] LLM: {'Available' if self.llm_available else 'Not available'}")
        
    async def generate(self, task: str, language: str = "python") -> str:
        """Generate professional code."""
        
        print(f"    [Executor] Analyzing: {task[:60]}...")
        task_type = self._classify_task(task)
        print(f"    [Executor] Type: {task_type}")
        
        # Try LLM first
        if self.llm_available:
            print(f"    [Executor] LLM generation...")
            code = await self._generate_with_llm(task, language)
            if len(code) > 200:
                return code
        
        # Smart template generation
        print(f"    [Executor] Template generation...")
        return self._generate_template(task, task_type, language)
    
    async def _generate_with_llm(self, task: str, language: str) -> str:
        """Generate using local LLM."""
        prompt = self._build_prompt(task, language)
        
        prompt_file = OUTPUT_DIR / f"prompt_{int(time.time())}.txt"
        prompt_file.write_text(prompt)
        
        try:
            cmd = [LLAMA_CLI, "-m", MODEL_PATH, "-f", str(prompt_file),
                   "-t", "4", "-c", "4096", "--temp", "0.2", "-n", "2048", "--log-disable"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            prompt_file.unlink()
            
            if result.returncode == 0 and result.stdout:
                return self._extract_code(result.stdout)
        except Exception as e:
            print(f"    [Executor] LLM error: {e}")
            try:
                prompt_file.unlink()
            except:
                pass
        
        return ""
    
    def _build_prompt(self, task: str, language: str) -> str:
        return f'''Write complete, production-ready {language} code for:

{task}

Requirements:
- Complete runnable code with no placeholders
- Type hints (Python) or interfaces (JS/TS)
- Error handling with try/catch
- Input validation
- Proper logging
- Docstrings/comments

Output ONLY the code:
'''
    
    def _extract_code(self, output: str) -> str:
        lines = output.split('\n')
        code = []
        in_code = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code = not in_code
                continue
            if in_code:
                code.append(line)
            elif line.strip() and not any(x in line for x in ['Write', 'Requirements', 'Output']):
                if any(x in line for x in ['def ', 'class ', 'import ', 'const ', 'function', '<!DOCTYPE']):
                    in_code = True
                    code.append(line)
        
        return '\n'.join(code) if code else output[:3000]
    
    def _classify_task(self, task: str) -> str:
        task_lower = task.lower()
        
        patterns = [
            ("rest_api", ["rest", "api", "endpoint", "route", "crud"]),
            ("web_server", ["web server", "http server"]),
            ("auth", ["auth", "login", "password", "jwt", "token"]),
            ("cli", ["cli", "command", "tool"]),
            ("database", ["database", "db", "sql", "sqlite"]),
            ("web_page", ["html", "web page", "frontend"]),
            ("scraper", ["scrape", "crawl"]),
            ("test", ["test", "pytest"]),
            ("config", ["config", "settings"]),
            ("bot", ["bot", "telegram", "discord"]),
            ("worker", ["worker", "background", "queue"]),
            ("gateway", ["gateway", "proxy", "middleware"]),
        ]
        
        for type_name, keywords in patterns:
            if any(kw in task_lower for kw in keywords):
                return type_name
        
        return "general"
    
    def _generate_template(self, task: str, task_type: str, language: str) -> str:
        """Generate from professional templates."""
        
        templates = {
            "python": {
                "rest_api": '''"""Paradise Stack - REST API with CRUD
Task: {task}
"""
from flask import Flask, jsonify, request, abort
from functools import wraps
import logging
from typing import Dict, List, Optional, Any
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory database
class Database:
    def __init__(self):
        self._data: Dict[int, Dict] = {{}}
        self._next_id = 1
    
    def create(self, item: Dict) -> Dict:
        item["id"] = self._next_id
        self._data[self._next_id] = item
        self._next_id += 1
        return item
    
    def get(self, id: int) -> Optional[Dict]:
        return self._data.get(id)
    
    def get_all(self) -> List[Dict]:
        return list(self._data.values())
    
    def update(self, id: int, updates: Dict) -> Optional[Dict]:
        if id not in self._data:
            return None
        self._data[id].update(updates)
        return self._data[id]
    
    def delete(self, id: int) -> bool:
        if id in self._data:
            del self._data[id]
            return True
        return False

db = Database()

def handle_errors(func):
    """Decorator for error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {{func.__name__}}: {{e}}")
            logger.error(traceback.format_exc())
            return jsonify({{"error": str(e)}}), 500
    return wrapper

def validate_item(data: Dict) -> bool:
    """Validate item data."""
    if not isinstance(data, dict):
        return False
    if "name" not in data:
        return False
    if not isinstance(data["name"], str) or len(data["name"]) == 0:
        return False
    return True

# API Routes
@app.route("/api/health", methods=["GET"])
@handle_errors
def health():
    """Health check endpoint."""
    return jsonify({{"status": "healthy", "service": "paradise-api"}})

@app.route("/api/items", methods=["GET"])
@handle_errors
def list_items():
    """List all items."""
    items = db.get_all()
    return jsonify({{
        "items": items,
        "count": len(items),
        "status": "success"
    }})

@app.route("/api/items", methods=["POST"])
@handle_errors
def create_item():
    """Create a new item."""
    data = request.get_json()
    
    if not data:
        return jsonify({{"error": "Request body required"}}), 400
    
    if not validate_item(data):
        return jsonify({{"error": "Invalid item data. 'name' field required"}}), 400
    
    item = db.create({{
        "name": data["name"],
        "description": data.get("description", ""),
        "created_at": data.get("created_at", "now")
    }})
    
    logger.info(f"Created item: {{item['id']}}")
    return jsonify({{"item": item, "status": "created"}}), 201

@app.route("/api/items/<int:item_id>", methods=["GET"])
@handle_errors
def get_item(item_id: int):
    """Get a single item by ID."""
    item = db.get(item_id)
    
    if not item:
        return jsonify({{"error": f"Item {{item_id}} not found"}}), 404
    
    return jsonify({{"item": item, "status": "success"}})

@app.route("/api/items/<int:item_id>", methods=["PUT"])
@handle_errors
def update_item(item_id: int):
    """Update an existing item."""
    data = request.get_json()
    
    if not data:
        return jsonify({{"error": "Request body required"}}), 400
    
    item = db.update(item_id, data)
    
    if not item:
        return jsonify({{"error": f"Item {{item_id}} not found"}}), 404
    
    logger.info(f"Updated item: {{item_id}}")
    return jsonify({{"item": item, "status": "updated"}})

@app.route("/api/items/<int:item_id>", methods=["DELETE"])
@handle_errors
def delete_item(item_id: int):
    """Delete an item."""
    success = db.delete(item_id)
    
    if not success:
        return jsonify({{"error": f"Item {{item_id}} not found"}}), 404
    
    logger.info(f"Deleted item: {{item_id}}")
    return jsonify({{"message": f"Item {{item_id}} deleted", "status": "deleted"}})

@app.errorhandler(404)
def not_found(e):
    return jsonify({{"error": "Resource not found"}}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({{"error": "Internal server error"}}), 500

if __name__ == "__main__":
    print("Starting Paradise REST API")
    print("=" * 50)
    print("Endpoints:")
    print("  GET    /api/health")
    print("  GET    /api/items")
    print("  POST   /api/items")
    print("  GET    /api/items/<id>")
    print("  PUT    /api/items/<id>")
    print("  DELETE /api/items/<id>")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
''',

                "web_server": '''"""Paradise Stack - Web Server
Task: {task}
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 8000

class ParadiseHandler(SimpleHTTPRequestHandler):
    """HTTP request handler with JSON API support."""
    
    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path
        
        if path == "/":
            self.path = "/index.html"
            SimpleHTTPRequestHandler.do_GET(self)
            return
        
        if path == "/api/health":
            self.send_json({{"status": "healthy", "time": datetime.now().isoformat()}})
            return
        
        if path == "/api/items":
            self.send_json({{"items": [], "count": 0}})
            return
        
        self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            logger.info(f"POST {{self.path}}: {{data}}")
            
            response = {{"status": "success", "data": data, "id": 1}}
            self.send_json(response)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
    
    def send_json(self, data: dict, status: int = 200):
        """Send JSON response."""
        response = json.dumps(data)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        logger.info(f"[{{self.log_date_time_string()}}] {{format % args}}")

def main():
    """Start the web server."""
    server = HTTPServer(("0.0.0.0", PORT), ParadiseHandler)
    
    print("=" * 50)
    print("Paradise Web Server")
    print("=" * 50)
    print(f"URL: http://localhost:{{PORT}}")
    print(f"API: http://localhost:{{PORT}}/api/*")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nShutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()
''',

                "cli": '''"""Paradise Stack - CLI Tool
Task: {task}
"""
import sys
import argparse
import json
from pathlib import Path
from typing import Optional, List, Dict
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

class ParadiseCLI:
    """Main CLI application."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".paradise"
        self.config_file = self.config_dir / "config.json"
        self._init_config()
    
    def _init_config(self):
        """Initialize configuration."""
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self._save_config({{"version": "1.0.0", "initialized": True}})
    
    def _load_config(self) -> Dict:
        """Load configuration."""
        if self.config_file.exists():
            return json.loads(self.config_file.read_text())
        return {{}}
    
    def _save_config(self, config: Dict):
        """Save configuration."""
        self.config_file.write_text(json.dumps(config, indent=2))
    
    def cmd_init(self, args):
        """Initialize the project."""
        logger.info("Initializing Paradise CLI...")
        config = self._load_config()
        config["initialized"] = True
        config["initialized_at"] = str(Path.cwd())
        self._save_config(config)
        logger.info(f"Initialized at {{self.config_dir}}")
    
    def cmd_run(self, args):
        """Run a task."""
        name = args.name or "default"
        logger.info(f"Running task: {{name}}")
        # Add task execution logic here
    
    def cmd_status(self, args):
        """Show status."""
        config = self._load_config()
        logger.info(f"Paradise CLI v{{config.get('version', '?')}}")
        logger.info(f"Initialized: {{config.get('initialized', False)}}")
    
    def cmd_list(self, args):
        """List available commands."""
        logger.info("Available commands:")
        logger.info("  init    - Initialize project")
        logger.info("  run     - Run a task")
        logger.info("  status  - Show status")
        logger.info("  list    - List commands")

def main():
    """Entry point."""
    parser = argparse.ArgumentParser(description="Paradise CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # init
    init_parser = subparsers.add_parser("init", help="Initialize")
    
    # run
    run_parser = subparsers.add_parser("run", help="Run task")
    run_parser.add_argument("-n", "--name", help="Task name")
    
    # status
    subparsers.add_parser("status", help="Show status")
    
    # list
    subparsers.add_parser("list", help="List commands")
    
    args = parser.parse_args()
    cli = ParadiseCLI()
    
    commands = {{
        "init": cli.cmd_init,
        "run": cli.cmd_run,
        "status": cli.cmd_status,
        "list": cli.cmd_list,
    }}
    
    if args.command and args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
''',

                "database": '''"""Paradise Stack - Database Manager
Task: {task}
"""
import sqlite3
import logging
from contextlib import contextmanager
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path("paradise.db")

@contextmanager
def get_connection():
    """Get database connection with context manager."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {{e}}")
        raise
    finally:
        conn.close()

class DatabaseManager:
    """Manage database operations."""
    
    @staticmethod
    def init():
        """Initialize database schema."""
        with get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("Database initialized")
    
    @staticmethod
    def create(name: str, description: str = "") -> Dict:
        """Create a new item."""
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO items (name, description) VALUES (?, ?)",
                (name, description)
            )
            return {{"id": cursor.lastrowid, "name": name, "description": description}}
    
    @staticmethod
    def get(id: int) -> Optional[Dict]:
        """Get item by ID."""
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM items WHERE id = ?", (id,)).fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def get_all() -> List[Dict]:
        """Get all items."""
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM items ORDER BY created_at DESC")
            return [dict(row) for row in rows]
    
    @staticmethod
    def update(id: int, **kwargs) -> Optional[Dict]:
        """Update an item."""
        if not kwargs:
            return DatabaseManager.get(id)
        
        sets = ", ".join(f"{{k}} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [id]
        
        with get_connection() as conn:
            conn.execute(
                f"UPDATE items SET {{sets}}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                values
            )
            return DatabaseManager.get(id)
    
    @staticmethod
    def delete(id: int) -> bool:
        """Delete an item."""
        with get_connection() as conn:
            conn.execute("DELETE FROM items WHERE id = ?", (id,))
            return conn.total_changes > 0

if __name__ == "__main__":
    DatabaseManager.init()
    
    # Demo
    item = DatabaseManager.create("Test", "Description")
    logger.info(f"Created: {{item}}")
    logger.info(f"All: {{DatabaseManager.get_all()}}")
''',

                "web_page": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paradise Stack</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        :root {{
            --primary: #00d4ff;
            --bg: #0f0f23;
            --card-bg: #1a1a2e;
            --text: #e0e0e0;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        h1 {{
            color: var(--primary);
            margin-bottom: 1.5rem;
            font-size: 2rem;
        }}
        
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        button {{
            background: var(--primary);
            color: #000;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }}
        
        button:hover {{
            transform: translateY(-2px);
        }}
        
        input {{
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            padding: 0.75rem;
            border-radius: 6px;
            color: white;
            width: 100%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Paradise Stack</h1>
        
        <div class="card">
            <h2>Task: {task}</h2>
            <p>Generated by Paradise Stack</p>
        </div>
        
        <div class="card">
            <input type="text" id="input" placeholder="Enter something...">
            <button onclick="submit()">Submit</button>
        </div>
    </div>
    
    <script>
        function submit() {{
            const input = document.getElementById("input").value;
            alert("Paradise Stack: " + input);
        }}
    </script>
</body>
</html>
''',

                "auth": '''"""Paradise Stack - Authentication System
Task: {task}
"""
from flask import Flask, request, jsonify, g
import hashlib
import secrets
import json
import logging
from pathlib import Path
from typing import Optional, Dict
from functools import wraps
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
USERS_FILE = Path.home() / ".paradise" / "users.json"
USERS_FILE.parent.mkdir(exist_ok=True)

class AuthManager:
    """Manage authentication."""
    
    @staticmethod
    def _load_users() -> Dict:
        if USERS_FILE.exists():
            return json.loads(USERS_FILE.read_text())
        return {{}}
    
    @staticmethod
    def _save_users(users: Dict):
        USERS_FILE.write_text(json.dumps(users, indent=2))
    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify(password: str, hashed: str) -> bool:
        return AuthManager.hash_password(password) == hashed
    
    @staticmethod
    def register(username: str, password: str) -> Dict:
        users = AuthManager._load_users()
        
        if username in users:
            raise ValueError("User exists")
        
        users[username] = {{
            "password": AuthManager.hash_password(password),
            "created": datetime.now().isoformat()
        }}
        AuthManager._save_users(users)
        
        return {{"username": username, "status": "registered"}}
    
    @staticmethod
    def login(username: str, password: str) -> Optional[str]:
        users = AuthManager._load_users()
        
        if username not in users:
            return None
        
        if not AuthManager.verify(password, users[username]["password"]):
            return None
        
        token = secrets.token_urlsafe(32)
        users[username]["token"] = token
        AuthManager._save_users(users)
        
        return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({{"error": "Token required"}}), 401
        # Add token verification here
        return f(*args, **kwargs)
    return decorated

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({{"error": "username and password required"}}), 400
    
    try:
        result = AuthManager.register(data["username"], data["password"])
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({{"error": str(e)}}), 400

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({{"error": "username and password required"}}), 400
    
    token = AuthManager.login(data["username"], data["password"])
    
    if not token:
        return jsonify({{"error": "Invalid credentials"}}), 401
    
    return jsonify({{"token": token}})

@app.route("/api/protected")
@token_required
def protected():
    return jsonify({{"message": "Protected resource"}})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
''',

                "general": '''"""Paradise Stack Generated
Task: {task}
"""
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParadiseApp:
    """Main application class."""
    
    def __init__(self):
        logger.info("Initializing Paradise Stack")
        self.name = "Paradise Stack"
    
    def run(self):
        """Run the application."""
        logger.info(f"Running: {{self.name}}")
        logger.info(f"Task: {{task}}")
        print("=" * 50)
        print(f"{{self.name}}")
        print("=" * 50)
        
        # Add your implementation here
        result = self.process()
        print(f"Result: {{result}}")
        
        return 0
    
    def process(self):
        """Process the task."""
        return "Task completed successfully"

def main():
    app = ParadiseApp()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())
'''
            },
            "javascript": {
                "general": '''// Paradise Stack Generated
// Task: {task}

const ParadiseApp = {{
    name: "Paradise Stack",
    
    init() {{
        console.log("Initializing Paradise Stack");
    }},
    
    run() {{
        console.log("Running:", this.name);
        return "Success";
    }}
}};

ParadiseApp.init();
ParadiseApp.run();

export default ParadiseApp;
'''
            }
        }
        
        lang_templates = templates.get(language, templates["python"])
        return lang_templates.get(task_type, lang_templates["general"]).format(task=task)


async def execute(task: str, language: str = "python") -> str:
    """Execute code generation."""
    engine = ExecutionEngine()
    return await engine.generate(task, language)


if __name__ == "__main__":
    import sys
    import asyncio
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello World"
    code = asyncio.run(execute(task))
    print(code)
