"""
MIT License
Copyright (c) 2026 Nrupal Akolkar
"""

import asyncio
import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path
import hashlib


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class LogEntry:
    timestamp: datetime
    level: LogLevel
    message: str
    source: str = ""
    data: Dict = field(default_factory=dict)


@dataclass
class Execution:
    id: str
    goal: str
    status: ExecutionStatus
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    iterations: int = 0
    max_iterations: int = 10
    progress: float = 0.0
    logs: List[LogEntry] = field(default_factory=list)
    result: Optional[Dict] = None
    error: Optional[str] = None


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self._connections: Dict[str, asyncio.Queue] = {}
        self._subscribers: Dict[str, set] = {}

    def subscribe(self, client_id: str) -> asyncio.Queue:
        """Subscribe a client to updates."""
        queue = asyncio.Queue(maxsize=100)
        self._connections[client_id] = queue
        return queue

    def unsubscribe(self, client_id: str):
        """Unsubscribe a client."""
        if client_id in self._connections:
            del self._connections[client_id]

    async def broadcast(self, event: str, data: Dict):
        """Broadcast event to all connected clients."""
        message = json.dumps({
            "event": event,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        disconnected = []
        for client_id, queue in self._connections.items():
            try:
                await asyncio.wait_for(queue.put(message), timeout=1.0)
            except asyncio.TimeoutError:
                disconnected.append(client_id)
        for client_id in disconnected:
            self.unsubscribe(client_id)

    async def send_to(self, client_id: str, event: str, data: Dict):
        """Send event to specific client."""
        if client_id in self._connections:
            message = json.dumps({
                "event": event,
                "data": data,
                "timestamp": datetime.now().isoformat()
            })
            try:
                await asyncio.wait_for(
                    self._connections[client_id].put(message),
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                self.unsubscribe(client_id)

    def subscribe_execution(self, execution_id: str, client_id: str):
        """Subscribe client to specific execution updates."""
        if execution_id not in self._subscribers:
            self._subscribers[execution_id] = set()
        self._subscribers[execution_id].add(client_id)

    def unsubscribe_execution(self, execution_id: str, client_id: str):
        """Unsubscribe client from execution updates."""
        if execution_id in self._subscribers:
            self._subscribers[execution_id].discard(client_id)


class ExecutionManager:
    """Manages execution lifecycle and state."""

    def __init__(self, ws_manager: WebSocketManager):
        self.ws_manager = ws_manager
        self._executions: Dict[str, Execution] = {}
        self._handlers: Dict[str, Callable] = {}

    def create_execution(self, goal: str, max_iterations: int = 10) -> Execution:
        """Create a new execution."""
        exec_id = f"exec_{uuid.uuid4().hex[:12]}"
        now = datetime.now()
        execution = Execution(
            id=exec_id,
            goal=goal,
            status=ExecutionStatus.PENDING,
            created_at=now,
            updated_at=now,
            max_iterations=max_iterations
        )
        self._executions[exec_id] = execution
        return execution

    def get_execution(self, exec_id: str) -> Optional[Execution]:
        """Get execution by ID."""
        return self._executions.get(exec_id)

    def list_executions(self, status: Optional[ExecutionStatus] = None) -> List[Execution]:
        """List all executions, optionally filtered by status."""
        if status:
            return [e for e in self._executions.values() if e.status == status]
        return list(self._executions.values())

    async def start_execution(self, exec_id: str, handler: Callable):
        """Start execution with handler function."""
        execution = self._executions.get(exec_id)
        if not execution:
            return

        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.now()
        self._handlers[exec_id] = handler

        await self.ws_manager.broadcast("execution:started", {
            "execution_id": exec_id,
            "goal": execution.goal
        })

    async def update_progress(self, exec_id: str, iteration: int, logs: List[LogEntry]):
        """Update execution progress."""
        execution = self._executions.get(exec_id)
        if not execution:
            return

        execution.iterations = iteration
        execution.progress = (iteration / execution.max_iterations) * 100
        execution.updated_at = datetime.now()
        execution.logs.extend(logs)

        await self.ws_manager.broadcast("execution:progress", {
            "execution_id": exec_id,
            "iteration": iteration,
            "progress": execution.progress,
            "logs": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level.value,
                    "message": log.message,
                    "source": log.source
                }
                for log in logs[-10:]
            ]
        })

    async def complete_execution(self, exec_id: str, result: Dict):
        """Mark execution as completed."""
        execution = self._executions.get(exec_id)
        if not execution:
            return

        execution.status = ExecutionStatus.COMPLETED
        execution.completed_at = datetime.now()
        execution.updated_at = datetime.now()
        execution.result = result
        execution.progress = 100.0

        await self.ws_manager.broadcast("execution:completed", {
            "execution_id": exec_id,
            "result": result,
            "iterations": execution.iterations,
            "duration": (execution.completed_at - execution.started_at).total_seconds()
        })

    async def fail_execution(self, exec_id: str, error: str):
        """Mark execution as failed."""
        execution = self._executions.get(exec_id)
        if not execution:
            return

        execution.status = ExecutionStatus.FAILED
        execution.completed_at = datetime.now()
        execution.updated_at = datetime.now()
        execution.error = error

        await self.ws_manager.broadcast("execution:failed", {
            "execution_id": exec_id,
            "error": error,
            "iterations": execution.iterations
        })

    async def cancel_execution(self, exec_id: str):
        """Cancel a running execution."""
        execution = self._executions.get(exec_id)
        if not execution or execution.status != ExecutionStatus.RUNNING:
            return

        execution.status = ExecutionStatus.CANCELLED
        execution.completed_at = datetime.now()
        execution.updated_at = datetime.now()

        if exec_id in self._handlers:
            handler = self._handlers[exec_id]
            if hasattr(handler, 'cancel'):
                handler.cancel()
            del self._handlers[exec_id]

        await self.ws_manager.broadcast("execution:cancelled", {
            "execution_id": exec_id
        })

    async def stream_log(self, exec_id: str, log: LogEntry):
        """Stream a log entry to connected clients."""
        await self.ws_manager.broadcast("execution:log", {
            "execution_id": exec_id,
            "log": {
                "timestamp": log.timestamp.isoformat(),
                "level": log.level.value,
                "message": log.message,
                "source": log.source,
                "data": log.data
            }
        })


class DashboardAPI:
    """REST API for dashboard operations."""

    def __init__(self, exec_manager: ExecutionManager, ws_manager: WebSocketManager):
        self.exec_manager = exec_manager
        self.ws_manager = ws_manager

    def get_status(self) -> Dict:
        """Get dashboard status."""
        executions = self.exec_manager.list_executions()
        running = self.exec_manager.list_executions(ExecutionStatus.RUNNING)
        completed = self.exec_manager.list_executions(ExecutionStatus.COMPLETED)
        failed = self.exec_manager.list_executions(ExecutionStatus.FAILED)

        return {
            "status": "healthy",
            "version": "1.0.0",
            "uptime": "24h",
            "stats": {
                "total_executions": len(executions),
                "running": len(running),
                "completed": len(completed),
                "failed": len(failed)
            },
            "connections": len(self.ws_manager._connections)
        }

    def get_execution(self, exec_id: str) -> Optional[Dict]:
        """Get execution details."""
        execution = self.exec_manager.get_execution(exec_id)
        if not execution:
            return None

        return {
            "id": execution.id,
            "goal": execution.goal,
            "status": execution.status.value,
            "created_at": execution.created_at.isoformat(),
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "iterations": execution.iterations,
            "max_iterations": execution.max_iterations,
            "progress": execution.progress,
            "logs": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level.value,
                    "message": log.message,
                    "source": log.source
                }
                for log in execution.logs[-100:]
            ],
            "result": execution.result,
            "error": execution.error
        }

    def list_executions(self, status: Optional[str] = None) -> List[Dict]:
        """List executions."""
        status_enum = ExecutionStatus(status) if status else None
        executions = self.exec_manager.list_executions(status_enum)

        return [
            {
                "id": e.id,
                "goal": e.goal[:100] + "..." if len(e.goal) > 100 else e.goal,
                "status": e.status.value,
                "progress": e.progress,
                "iterations": e.iterations,
                "created_at": e.created_at.isoformat()
            }
            for e in sorted(executions, key=lambda x: x.created_at, reverse=True)
        ]

    def create_execution(self, goal: str, max_iterations: int = 10) -> Dict:
        """Create new execution."""
        execution = self.exec_manager.create_execution(goal, max_iterations)
        return {"execution_id": execution.id, "status": "pending"}

    async def cancel_execution(self, exec_id: str) -> Dict:
        """Cancel execution."""
        await self.exec_manager.cancel_execution(exec_id)
        return {"success": True}


class DashboardRenderer:
    """Renders dashboard HTML/JS/CSS."""

    @staticmethod
    def render_html() -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>agentic-OS Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --border: #30363d;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --accent: #58a6ff;
            --success: #3fb950;
            --warning: #d29922;
            --error: #f85149;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
        }
        
        .header {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--accent);
        }
        
        .stats {
            display: flex;
            gap: 2rem;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .stat-label {
            font-size: 0.75rem;
            color: var(--text-secondary);
            text-transform: uppercase;
        }
        
        .main {
            display: grid;
            grid-template-columns: 1fr 350px;
            height: calc(100vh - 70px);
        }
        
        .panel {
            background: var(--bg-secondary);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
        }
        
        .panel-header {
            padding: 1rem;
            border-bottom: 1px solid var(--border);
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .panel-content {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
        }
        
        .execution-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .execution-item {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.75rem;
            cursor: pointer;
            transition: border-color 0.2s;
        }
        
        .execution-item:hover {
            border-color: var(--accent);
        }
        
        .execution-item.active {
            border-color: var(--accent);
            background: rgba(88, 166, 255, 0.1);
        }
        
        .execution-goal {
            font-size: 0.875rem;
            margin-bottom: 0.5rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .execution-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            color: var(--text-secondary);
        }
        
        .status-badge {
            padding: 0.125rem 0.5rem;
            border-radius: 12px;
            font-size: 0.625rem;
            text-transform: uppercase;
            font-weight: 600;
        }
        
        .status-pending { background: var(--bg-tertiary); }
        .status-running { background: var(--accent); color: #fff; }
        .status-completed { background: var(--success); color: #fff; }
        .status-failed { background: var(--error); color: #fff; }
        
        .detail-panel {
            display: flex;
            flex-direction: column;
        }
        
        .terminal {
            flex: 1;
            background: #000;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.75rem;
            padding: 1rem;
            overflow-y: auto;
            white-space: pre-wrap;
            line-height: 1.5;
        }
        
        .log-entry {
            margin-bottom: 0.25rem;
        }
        
        .log-debug { color: var(--text-secondary); }
        .log-info { color: var(--text-primary); }
        .log-warning { color: var(--warning); }
        .log-error { color: var(--error); }
        .log-success { color: var(--success); }
        
        .progress-bar {
            height: 4px;
            background: var(--bg-tertiary);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 0.5rem;
        }
        
        .progress-fill {
            height: 100%;
            background: var(--accent);
            transition: width 0.3s ease;
        }
        
        .new-execution {
            padding: 1rem;
            border-bottom: 1px solid var(--border);
        }
        
        .new-execution textarea {
            width: 100%;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.75rem;
            color: var(--text-primary);
            font-family: inherit;
            resize: none;
            margin-bottom: 0.5rem;
        }
        
        .new-execution button {
            width: 100%;
            background: var(--accent);
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 0.75rem;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        
        .new-execution button:hover {
            opacity: 0.9;
        }
        
        .new-execution button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">agentic-OS Dashboard</div>
        <div class="stats">
            <div class="stat">
                <div class="stat-value" id="stat-total">0</div>
                <div class="stat-label">Total</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="stat-running">0</div>
                <div class="stat-label">Running</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="stat-completed">0</div>
                <div class="stat-label">Completed</div>
            </div>
        </div>
    </div>
    
    <div class="main">
        <div class="panel">
            <div class="panel-header">
                <span>Executions</span>
                <span id="execution-count">0</span>
            </div>
            <div class="new-execution">
                <textarea id="new-goal" rows="3" placeholder="Enter your goal..."></textarea>
                <button id="new-btn" onclick="createExecution()">Execute</button>
            </div>
            <div class="panel-content">
                <div class="execution-list" id="execution-list"></div>
            </div>
        </div>
        
        <div class="panel detail-panel">
            <div class="panel-header">
                <span id="detail-title">Select Execution</span>
                <div id="detail-status"></div>
            </div>
            <div class="progress-bar" id="progress-bar" style="display:none;">
                <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
            </div>
            <div class="terminal" id="terminal">
                <div class="log-info">Waiting for execution...</div>
            </div>
        </div>
    </div>
    
    <script>
        const API_BASE = '/api/v1';
        let executions = [];
        let selectedId = null;
        let ws = null;
        
        async function loadExecutions() {
            const res = await fetch(API_BASE + '/executions');
            const data = await res.json();
            executions = data.executions || [];
            renderExecutionList();
            updateStats();
        }
        
        function renderExecutionList() {
            const list = document.getElementById('execution-list');
            document.getElementById('execution-count').textContent = executions.length;
            list.innerHTML = executions.map(e => `
                <div class="execution-item ${e.id === selectedId ? 'active' : ''}" 
                     onclick="selectExecution('${e.id}')">
                    <div class="execution-goal">${escapeHtml(e.goal)}</div>
                    <div class="execution-meta">
                        <span class="status-badge status-${e.status}">${e.status}</span>
                        <span>${e.progress.toFixed(0)}%</span>
                    </div>
                </div>
            `).join('');
        }
        
        function updateStats() {
            document.getElementById('stat-total').textContent = executions.length;
            document.getElementById('stat-running').textContent = 
                executions.filter(e => e.status === 'running').length;
            document.getElementById('stat-completed').textContent = 
                executions.filter(e => e.status === 'completed').length;
        }
        
        async function selectExecution(id) {
            selectedId = id;
            renderExecutionList();
            
            const res = await fetch(API_BASE + '/executions/' + id);
            const data = await res.json();
            
            if (data.execution) {
                showExecutionDetail(data.execution);
            }
        }
        
        function showExecutionDetail(exec) {
            document.getElementById('detail-title').textContent = 'Execution ' + exec.id.slice(-8);
            document.getElementById('detail-status').innerHTML = 
                `<span class="status-badge status-${exec.status}">${exec.status}</span>`;
            
            document.getElementById('progress-bar').style.display = 'block';
            document.getElementById('progress-fill').style.width = exec.progress + '%';
            
            const terminal = document.getElementById('terminal');
            terminal.innerHTML = exec.logs.map(log => 
                `<div class="log-entry log-${log.level}">[${log.timestamp}] ${escapeHtml(log.message)}</div>`
            ).join('');
            terminal.scrollTop = terminal.scrollHeight;
        }
        
        async function createExecution() {
            const goal = document.getElementById('new-goal').value.trim();
            if (!goal) return;
            
            const btn = document.getElementById('new-btn');
            btn.disabled = true;
            btn.textContent = 'Starting...';
            
            try {
                const res = await fetch(API_BASE + '/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ goal, max_iterations: 10 })
                });
                const data = await res.json();
                
                await loadExecutions();
                selectExecution(data.execution_id);
                
                document.getElementById('new-goal').value = '';
            } finally {
                btn.disabled = false;
                btn.textContent = 'Execute';
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function connectWebSocket() {
            ws = new WebSocket('ws://' + location.host + '/ws');
            
            ws.onmessage = (event) => {
                const msg = JSON.parse(event.data);
                handleWebSocketMessage(msg);
            };
            
            ws.onclose = () => {
                setTimeout(connectWebSocket, 3000);
            };
        }
        
        function handleWebSocketMessage(msg) {
            switch (msg.event) {
                case 'execution:started':
                    loadExecutions();
                    break;
                case 'execution:progress':
                    if (msg.data.execution_id === selectedId) {
                        updateProgress(msg.data);
                    }
                    loadExecutions();
                    break;
                case 'execution:completed':
                    loadExecutions();
                    break;
                case 'execution:log':
                    if (msg.data.execution_id === selectedId) {
                        appendLog(msg.data.log);
                    }
                    break;
            }
        }
        
        function updateProgress(data) {
            document.getElementById('progress-fill').style.width = data.progress + '%';
            const terminal = document.getElementById('terminal');
            data.logs.forEach(log => appendLog(log));
        }
        
        function appendLog(log) {
            const terminal = document.getElementById('terminal');
            const div = document.createElement('div');
            div.className = 'log-entry log-' + log.level;
            div.textContent = '[' + log.timestamp.split('T')[1].slice(0, 12) + '] ' + log.message;
            terminal.appendChild(div);
            terminal.scrollTop = terminal.scrollHeight;
        }
        
        loadExecutions();
        connectWebSocket();
        setInterval(loadExecutions, 5000);
    </script>
</body>
</html>"""


def create_dashboard_app():
    """Create dashboard FastAPI app."""
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    from contextlib import asynccontextmanager
    
    ws_manager = WebSocketManager()
    exec_manager = ExecutionManager(ws_manager)
    api = DashboardAPI(exec_manager, ws_manager)
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
    
    app = FastAPI(title="agentic-OS Dashboard", lifespan=lifespan)
    
    @app.get("/", response_class=HTMLResponse)
    async def dashboard():
        return DashboardRenderer.render_html()
    
    @app.get("/api/v1/status")
    async def get_status():
        return api.get_status()
    
    @app.get("/api/v1/executions")
    async def list_executions(status: str = None):
        return {"executions": api.list_executions(status)}
    
    @app.get("/api/v1/executions/{exec_id}")
    async def get_execution(exec_id: str):
        execution = api.get_execution(exec_id)
        if not execution:
            return {"error": "Not found"}
        return {"execution": execution}
    
    @app.post("/api/v1/execute")
    async def create_execution(request: dict):
        goal = request.get("goal", "")
        max_iterations = request.get("max_iterations", 10)
        return api.create_execution(goal, max_iterations)
    
    @app.post("/api/v1/cancel/{exec_id}")
    async def cancel_execution(exec_id: str):
        return await api.cancel_execution(exec_id)
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        client_id = str(uuid.uuid4())
        queue = ws_manager.subscribe(client_id)
        
        try:
            while True:
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=30)
                    await websocket.send_text(message)
                except asyncio.TimeoutError:
                    await websocket.send_text(json.dumps({"event": "ping"}))
        except WebSocketDisconnect:
            ws_manager.unsubscribe(client_id)
    
    return app


if __name__ == "__main__":
    import uvicorn
    
    app = create_dashboard_app()
    print("Starting agentic-OS Dashboard on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
