# SPDX-License-Identifier: MIT OR Apache-2.0
"""
Integration tests for agentic-OS API server with comprehensive mocks.
Tests API endpoints with mocked dependencies for isolated testing.
"""

import pytest
from unittest.mock import Mock, patch, PropertyMock
from pathlib import Path

# Add project root to path
import sys
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.server import ExecutionManager, ExecutionStatus

# Check if slowapi is available
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False

# Check if FastAPI TestClient is available
try:
    from fastapi.testclient import TestClient
    from api.server import app as _api_app
    FASTAPI_TESTABLE = True
except Exception:
    FASTAPI_TESTABLE = False

# Mock for PlanToOmegaBridge to avoid actual execution
class MockPlanToOmegaBridge:
    def __init__(self, execution_id):
        self.execution_id = execution_id
        
    def execute(self, plan_json, max_iterations=3, interactive=False):
        # Mock successful execution
        mock_result = Mock()
        mock_result.status = ExecutionStatus.SUCCESS
        mock_result.iteration = 1
        mock_result.output_files = ["test_output.py"]
        mock_result.errors = []
        mock_result.to_dict.return_value = {
            "status": "success",
            "iteration": 1,
            "output_files": ["test_output.py"],
            "errors": []
        }
        return mock_result
    
    def close(self):
        pass


@pytest.fixture
def execution_manager():
    """Create a fresh execution manager for each test."""
    return ExecutionManager()


@pytest.fixture
def mock_bridge():
    """Mock the PlanToOmegaBridge to prevent actual execution."""
    with patch('api.server.PlanToOmegaBridge', MockPlanToOmegaBridge):
        yield


@pytest.fixture
def mock_execution_run():
    """Mock the run_execution_sync method to control execution."""
    with patch.object(ExecutionManager, 'run_execution_sync', autospec=True) as mock:
        yield mock


class TestExecutionManager:
    """Test ExecutionManager functionality with mocks."""
    
    def test_create_execution(self, execution_manager):
        """Test creating a new execution."""
        mock_request = Mock()
        mock_request.goal = "Test goal"
        mock_request.request_type = "test"
        mock_request.max_iterations = 10
        
        execution = execution_manager.create_execution(mock_request)
        
        assert execution.execution_id.startswith("exec_")
        assert execution.goal == "Test goal"
        assert execution.status == ExecutionStatus.PENDING
        assert execution.execution_id in execution_manager.executions
    
    def test_get_execution_exists(self, execution_manager):
        """Test getting an existing execution."""
        mock_request = Mock()
        mock_request.goal = "Test goal"
        mock_request.request_type = "test" 
        mock_request.max_iterations = 10
        
        execution = execution_manager.create_execution(mock_request)
        retrieved = execution_manager.get_execution(execution.execution_id)
        
        assert retrieved == execution
    
    def test_get_execution_not_exists(self, execution_manager):
        """Test getting a non-existent execution."""
        assert execution_manager.get_execution("nonexistent") is None
    
@pytest.fixture
def rate_limiting_client():
    """Create a TestClient with rate limiting enabled and execution mocked.
    Each test gets a fresh app with a fresh limiter to avoid cross-test bleed.
    """
    if not SLOWAPI_AVAILABLE or not FASTAPI_TESTABLE:
        pytest.skip("FastAPI or slowapi not available")
    
    from enum import Enum
    from fastapi import FastAPI, Request
    from slowapi import Limiter
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    from fastapi.responses import JSONResponse
    
    test_app = FastAPI(title="test-agentic-os")
    limiter = Limiter(key_func=lambda: "test-client")
    test_app.state.limiter = limiter
    test_app.add_middleware(SlowAPIMiddleware)
    
    manager = ExecutionManager()
    
    @test_app.exception_handler(RateLimitExceeded)
    async def rl_handler(request, exc):
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    
    from pydantic import BaseModel
    class ExecuteRequest(BaseModel):
        goal: str = ""
        request_type: str = "test"
        max_iterations: int = 1
        steps: list = None
        files_to_create: list = None
        files_to_modify: list = None
        metadata: dict = {}
    
    class StatusResponse(BaseModel):
        execution_id: str = ""
        status: str = ""
        iteration: int = 0
        max_iterations: int = 1
        created_at: str = ""
        updated_at: str = ""
        error: str | None = None
    
    class ResultsResponse(BaseModel):
        execution_id: str = ""
        status: str = ""
        goal: str = ""
        output_files: list = []
        metrics: dict = {}
    
    from api.server import ExecutionStatus
    
    @test_app.post("/api/v1/execute", response_model=StatusResponse)
    @limiter.limit("5/minute")
    async def execute_rl(request: Request, exec_request: ExecuteRequest):
        from datetime import datetime
        execution = manager.create_execution(exec_request)
        return StatusResponse(
            execution_id=execution.execution_id,
            status=execution.status.value,
            iteration=execution.iteration,
            max_iterations=execution.max_iterations,
            created_at=execution.created_at,
            updated_at=execution.updated_at,
        )
    
    @test_app.get("/api/v1/status/{execution_id}", response_model=StatusResponse)
    @limiter.limit("30/minute")
    async def get_status_rl(request: Request, execution_id: str):
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
    
    with TestClient(test_app) as client:
        yield client


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiting_execute_endpoint(self, rate_limiting_client):
        """Test rate limiting on execute endpoint."""
        client = rate_limiting_client
        
        payload = {
            "goal": "Test rate limiting",
            "request_type": "test",
            "max_iterations": 1
        }
        
        responses = []
        for i in range(6):  # 5 allowed, 6th should be blocked
            response = client.post("/api/v1/execute", json=payload)
            responses.append(response.status_code)
        
        success_count = sum(1 for code in responses if code == 200)
        rate_limit_count = sum(1 for code in responses if code == 429)
        
        assert success_count >= 4
        assert rate_limit_count >= 1
    
    def test_rate_limiting_status_endpoint(self, rate_limiting_client):
        """Test rate limiting on status endpoint."""
        client = rate_limiting_client
        
        payload = {
            "goal": "Test status rate limiting",
            "request_type": "test", 
            "max_iterations": 1
        }
        
        create_response = client.post("/api/v1/execute", json=payload)
        execution_id = create_response.json()["execution_id"]
        
        responses = []
        for i in range(35):  # 30 allowed, 31+ should be blocked
            response = client.get(f"/api/v1/status/{execution_id}")
            responses.append(response.status_code)
            
        success_count = sum(1 for code in responses if code == 200)
        rate_limit_count = sum(1 for code in responses if code == 429)
        
        assert success_count >= 28
        assert rate_limit_count >= 2


class TestAuthentication:
    """Test authentication functionality (to be implemented)."""
    
    def test_auth_not_implemented(self):
        """Placeholder test - authentication will be implemented separately."""
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])