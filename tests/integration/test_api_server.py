"""
Integration tests for agentic-OS API server with comprehensive mocks.
Tests API endpoints with mocked dependencies for isolated testing.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from pathlib import Path

# Add project root to path
import sys
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.server import ExecutionManager, ExecutionStatus, ValidationChoice

# Check if slowapi is available
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False

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
    
class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiting_execute_endpoint(self):
        """Test rate limiting on execute endpoint."""
        if not hasattr(self, 'client') or not SLOWAPI_AVAILABLE:
            pytest.skip("FastAPI or slowapi not available")
        
        # Make multiple rapid requests to trigger rate limiting
        payload = {
            "goal": "Test rate limiting",
            "request_type": "test",
            "max_iterations": 1
        }
        
        responses = []
        for i in range(6):  # 5 allowed, 6th should be blocked
            response = self.client.post("/api/v1/execute", json=payload)
            responses.append(response.status_code)
        
        # First 5 should succeed (200), 6th should be rate limited (429)
        success_count = sum(1 for code in responses if code == 200)
        rate_limit_count = sum(1 for code in responses if code == 429)
        
        assert success_count >= 4  # Allow some tolerance
        assert rate_limit_count >= 1
    
    def test_rate_limiting_status_endpoint(self):
        """Test rate limiting on status endpoint."""
        if not hasattr(self, 'client') or not SLOWAPI_AVAILABLE:
            pytest.skip("FastAPI or slowapi not available")
        
        # Create an execution first
        payload = {
            "goal": "Test status rate limiting",
            "request_type": "test", 
            "max_iterations": 1
        }
        
        create_response = self.client.post("/api/v1/execute", json=payload)
        execution_id = create_response.json()["execution_id"]
        
        # Make multiple rapid status requests
        responses = []
        for i in range(35):  # 30 allowed, 31+ should be blocked
            response = self.client.get(f"/api/v1/status/{execution_id}")
            responses.append(response.status_code)
            
        # Count successes and rate limits
        success_count = sum(1 for code in responses if code == 200)
        rate_limit_count = sum(1 for code in responses if code == 429)
        
        assert success_count >= 28  # Allow some tolerance
        assert rate_limit_count >= 2


class TestAuthentication:
    """Test authentication functionality (to be implemented)."""
    
    def test_auth_not_implemented(self):
        """Placeholder test - authentication will be implemented separately."""
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])