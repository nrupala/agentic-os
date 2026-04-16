#!/usr/bin/env python3
"""
agentic-OS API Server
====================
REST API + WebSocket streaming for agentic-OS

Provides:
- POST /api/v1/execute - Execute a goal
- GET /api/v1/status/{id} - Check execution status
- POST /api/v1/validate - Submit user validation
- GET /api/v1/results/{id} - Get results
- WS /ws/{id} - Real-time streaming

Usage:
    python api_server.py
    # Starts on http://localhost:8080
"""

import os
import sys
import json
import asyncio
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Try importing optional dependencies
try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Header
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("[WARNING] FastAPI not installed. Install with: pip install fastapi uvicorn requests")

# Rate limiting imports
try:
    from slowapi import Limiter, _get_remote_address
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False
    print("[WARNING] slowapi not installed. Install with: pip install slowapi")

# Authentication imports
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("[WARNING] PyJWT not installed. Install with: pip install pyjwt")

from engine.bridge import PlanToOmegaBridge

# ============================================================================
# Data Models
# ============================================================================

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    MAX_ITERATIONS = "max_iterations"
    REJECTED = "rejected"
    PAUSED = "paused"

class ValidationChoice(str, Enum):
    ACCEPT = "accept"
    REFINE = "refine"
    REJECT = "reject"

@dataclass
class Execution:
    execution_id: str
    goal: str
    request_type: str
    status: ExecutionStatus
    iteration: int
    max_iterations: int
    created_at: str
    updated_at: str
    result: Optional[Dict] = None
    error: Optional[str] = None
    output_files: list = None
    
    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "execution_id": self.execution_id,
            "goal": self.goal,
            "request_type": self.request_type,
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "iteration": self.iteration,
            "max_iterations": self.max_iterations,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "result": self.result,
            "error": self.error,
            "output_files": self.output_files,
        }

# ============================================================================
# Request/Response Models
# ============================================================================

class ExecuteRequest(BaseModel):
    goal: str = Field(..., description="The goal to execute", min_length=1)
    request_type: str = Field(default="feature_add", description="Request type: feature_add, bug_fix, refactor, api, frontend, database, auth, test, deploy, ml")
    steps: list = Field(default_factory=list, description="Implementation steps")
    files_to_create: list = Field(default_factory=list, description="Files to create")
    files_to_modify: list = Field(default_factory=list, description="Files to modify")
    max_iterations: int = Field(default=50, ge=1, le=200, description="Maximum iterations")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    auto_validate: bool = Field(default=False, description="Auto-accept successful outputs")

class ValidationRequest(BaseModel):
    choice: ValidationChoice = Field(..., description="User's choice: accept, refine, reject")
    feedback: Optional[str] = Field(default=None, description="Feedback for refine/reject")

class StatusResponse(BaseModel):
    execution_id: str
    status: str
    iteration: int
    max_iterations: int
    created_at: str
    updated_at: str
    error: Optional[str] = None

class ResultsResponse(BaseModel):
    execution_id: str
    status: str
    goal: str
    output_files: list
    metrics: dict

# ============================================================================
# Execution Manager
# ============================================================================

class ExecutionManager:
    """Manages all active executions."""
    
    def __init__(self):
        self.executions: Dict[str, Execution] = {}
        self.websocket_connections: Dict[str, list] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self._lock = asyncio.Lock()
    
    def create_execution(self, request: ExecuteRequest) -> Execution:
        """Create a new execution."""
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        execution = Execution(
            execution_id=execution_id,
            goal=request.goal,
            request_type=request.request_type,
            status=ExecutionStatus.PENDING,
            iteration=0,
            max_iterations=request.max_iterations,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        
        self.executions[execution_id] = execution
        self.websocket_connections[execution_id] = []
        
        return execution
    
    def get_execution(self, execution_id: str) -> Optional[Execution]:
        """Get an execution by ID."""
        return self.executions.get(execution_id)
    
    async def update_status(self, execution_id: str, status: ExecutionStatus, **kwargs):
        """Update execution status."""
        async with self._lock:
            if execution_id in self.executions:
                exec = self.executions[execution_id]
                exec.status = status
                exec.updated_at = datetime.now().isoformat()
                for key, value in kwargs.items():
                    setattr(exec, key, value)
                
                # Broadcast to WebSocket clients
                await self.broadcast(execution_id, {
                    "type": "status_update",
                    "data": exec.to_dict()
                })
    
    async def broadcast(self, execution_id: str, message: dict):
        """Broadcast message to all WebSocket clients for an execution."""
        if execution_id in self.websocket_connections:
            dead_connections = []
            for ws in self.websocket_connections[execution_id]:
                try:
                    await ws.send_json(message)
                except:
                    dead_connections.append(ws)
            
            # Remove dead connections
            for ws in dead_connections:
                self.websocket_connections[execution_id].remove(ws)
    
    def run_execution_sync(self, execution_id: str, request: ExecuteRequest):
        """Run an execution synchronously (called from async context)."""
        execution = self.get_execution(execution_id)
        if not execution:
            return
        
        # Update status synchronously
        execution.status = ExecutionStatus.RUNNING
        execution.updated_at = datetime.now().isoformat()
        
        try:
            # Create plan JSON
            plan_json = {
                "goal": request.goal,
                "request_type": request.request_type,
                "steps": request.steps or ["analyze", "implement", "test"],
                "files_to_create": request.files_to_create,
                "files_to_modify": request.files_to_modify,
                "detected_patterns": [],
                "constraints": {},
                "metadata": {**request.metadata, "source": "api"}
            }
            
            # Run bridge.execute directly (it's sync)
            bridge = PlanToOmegaBridge(execution_id)
            result = bridge.execute(plan_json, max_iterations=min(3, request.max_iterations), interactive=False)
            bridge.close()
            
            # Update status
            execution.status = ExecutionStatus(result.status.value)
            execution.iteration = result.iteration
            execution.result = result.to_dict()
            execution.output_files = result.output_files
            execution.error = result.errors[-1] if result.errors else None
            execution.updated_at = datetime.now().isoformat()
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            execution.updated_at = datetime.now().isoformat()
    
    async def run_execution(self, execution_id: str, request: ExecuteRequest):
        """Run an execution asynchronously."""
        print(f"[API] Starting execution: {execution_id}")
        try:
            # Run sync code in thread pool to not block event loop
            loop = asyncio.get_event_loop()
            print(f"[API] Got loop: {loop}")
            print(f"[API] Running executor...")
            result = await loop.run_in_executor(None, lambda: self.run_execution_sync(execution_id, request))
            print(f"[API] Executor returned: {result}")
        except Exception as e:
            print(f"[API] Error: {e}")
            import traceback
            traceback.print_exc()
            await self.update_status(execution_id, ExecutionStatus.FAILED, error=str(e))
    
    def register_websocket(self, execution_id: str, ws: WebSocket):
        """Register a WebSocket connection."""
        if execution_id in self.websocket_connections:
            self.websocket_connections[execution_id].append(ws)
    
    def unregister_websocket(self, execution_id: str, ws: WebSocket):
        """Unregister a WebSocket connection."""
        if execution_id in self.websocket_connections and ws in self.websocket_connections[execution_id]:
            self.websocket_connections[execution_id].remove(ws)


# Global execution manager
manager = ExecutionManager()


# ============================================================================
# FastAPI Application (if available)
# ============================================================================

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="agentic-OS API",
        description="Unified Autonomous Coding Agent API",
        version="1.0.0"
    )
    
    # Add rate limiting middleware if available
    if SLOWAPI_AVAILABLE:
        from slowapi.util import get_remote_address
        limiter = Limiter(key_func=get_remote_address)
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, lambda request, exc: HTTPException(status_code=429, detail="Rate limit exceeded"))
        app.add_middleware(SlowAPIMiddleware)
    
    # API Key authentication dependency
    async def verify_api_key(x_api_key: Optional[str] = Header(None)):
        """Verify API key for authenticated endpoints."""
        if not JWT_AVAILABLE:
            return True  # Skip auth if JWT not available
        if not x_api_key:
            return True  # Allow unauthenticated for now
        return True
    
    @app.get("/")
    async def root():
        return {
            "name": "agentic-OS API",
            "version": "1.0.0",
            "docs": "/docs",
            "status": "operational"
        }
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "active_executions": len([e for e in manager.executions.values() if e.status == ExecutionStatus.RUNNING])
        }
    
    @app.post("/api/v1/execute", response_model=StatusResponse)
    async def execute(request: ExecuteRequest):
        """Execute a goal through the agentic-OS pipeline."""
        execution = manager.create_execution(request)
        
        # Start execution in background
        asyncio.create_task(manager.run_execution(execution.execution_id, request))
        
        return StatusResponse(
            execution_id=execution.execution_id,
            status=execution.status.value,
            iteration=execution.iteration,
            max_iterations=execution.max_iterations,
            created_at=execution.created_at,
            updated_at=execution.updated_at,
        )
    
    @app.get("/api/v1/status/{execution_id}", response_model=StatusResponse)
    async def get_status(execution_id: str):
        """Get the status of an execution."""
        execution = manager.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return StatusResponse(
            execution_id=execution.execution_id,
            status=execution.status.value if isinstance(execution.status, Enum) else execution.status,
            iteration=execution.iteration,
            max_iterations=execution.max_iterations,
            created_at=execution.created_at,
            updated_at=execution.updated_at,
            error=execution.error,
        )
    
    @app.get("/api/v1/results/{execution_id}", response_model=ResultsResponse)
    async def get_results(execution_id: str):
        """Get the results of an execution."""
        execution = manager.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        if execution.status not in [ExecutionStatus.SUCCESS, ExecutionStatus.FAILED, ExecutionStatus.MAX_ITERATIONS, ExecutionStatus.REJECTED]:
            raise HTTPException(status_code=202, detail="Execution still in progress")
        
        return ResultsResponse(
            execution_id=execution.execution_id,
            status=execution.status.value if isinstance(execution.status, Enum) else execution.status,
            goal=execution.goal,
            output_files=execution.output_files,
            metrics={
                "iteration": execution.iteration,
                "max_iterations": execution.max_iterations,
                "duration": "calculated",
            }
        )
    
    @app.post("/api/v1/validate/{execution_id}")
    async def validate(execution_id: str, request: ValidationRequest):
        """Submit user validation for an execution."""
        execution = manager.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Process validation
        if request.choice == ValidationChoice.ACCEPT:
            await manager.update_status(execution_id, ExecutionStatus.SUCCESS)
        elif request.choice == ValidationChoice.REJECT:
            await manager.update_status(execution_id, ExecutionStatus.REJECTED)
        else:
            # REFINE - would trigger another iteration
            await manager.update_status(execution_id, ExecutionStatus.RUNNING)
        
        return {
            "execution_id": execution_id,
            "choice": request.choice.value,
            "feedback": request.feedback,
            "updated_at": datetime.now().isoformat()
        }
    
    @app.get("/api/v1/executions")
    async def list_executions():
        """List all executions."""
        return {
            "executions": [
                e.to_dict() for e in list(manager.executions.values())[-50:]
            ],
            "total": len(manager.executions)
        }
    
    @app.websocket("/ws/{execution_id}")
    async def websocket_endpoint(websocket: WebSocket, execution_id: str):
        """WebSocket endpoint for real-time streaming."""
        await websocket.accept()
        manager.register_websocket(execution_id, websocket)
        
        # Send initial status
        execution = manager.get_execution(execution_id)
        if execution:
            await websocket.send_json({
                "type": "connected",
                "data": execution.to_dict()
            })
        
        try:
            while True:
                # Keep connection alive, receive any client messages
                data = await websocket.receive_text()
                
                # Handle ping/pong
                if data == "ping":
                    await websocket.send_text("pong")
                    
        except WebSocketDisconnect:
            manager.unregister_websocket(execution_id, websocket)


# ============================================================================
# Main Entry Point
# ============================================================================

def run_server(host: str = "0.0.0.0", port: int = 8080):
    """Run the API server."""
    if not FASTAPI_AVAILABLE:
        print("[ERROR] FastAPI is required. Install with: pip install fastapi uvicorn")
        return
    
    print(f"""
+=========================================================================+
|                      agentic-OS API SERVER                              |
+=========================================================================+

    Starting server at http://{host}:{port}
    
    Endpoints:
    - GET  /                    - API info
    - GET  /health              - Health check
    - POST /api/v1/execute      - Execute a goal
    - GET  /api/v1/status/{'{execution_id}'}  - Get status
    - GET  /api/v1/results/{'{execution_id}'}  - Get results
    - POST /api/v1/validate/{'{execution_id}'}  - Submit validation
    - GET  /api/v1/executions  - List executions
    - WS   /ws/{'{execution_id}'}  - Real-time streaming

+=========================================================================+
""")
    
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="agentic-OS API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    
    args = parser.parse_args()
    run_server(args.host, args.port)
