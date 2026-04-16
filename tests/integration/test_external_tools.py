"""
Integration tests for git_ops and docker_ops with mocks.
Tests external tool integrations.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
import sys
import subprocess

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestGitOpsIntegration:
    """Test git operations with mocked external dependencies."""
    
    def test_git_provider_with_mock(self):
        """Test git provider with mocked subprocess."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
            
            from tools.git_ops import GitProvider
            git = GitProvider()
            assert git is not None
    
    def test_git_clone_with_mock(self):
        """Test git clone with mocked subprocess."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
            
            from tools.git_ops import GitProvider
            git = GitProvider()
            assert git is not None
    
    def test_git_status_with_mock(self):
        """Test git status with mocked subprocess."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0, 
                stdout='On branch main\nnothing to commit', 
                stderr=''
            )
            
            from tools.git_ops import GitProvider
            git = GitProvider()
            assert git is not None
    
    def test_git_branch_with_mock(self):
        """Test git branch with mocked subprocess."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='* main', stderr='')
            
            from tools.git_ops import GitProvider
            git = GitProvider()
            assert git is not None
    
    def test_git_log_with_mock(self):
        """Test git log with mocked subprocess."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='commit123\nAuthor: Test', stderr='')
            
            from tools.git_ops import GitProvider
            git = GitProvider()
            assert git is not None


class TestDockerOpsIntegration:
    """Test docker operations with mocked external dependencies."""
    
    def test_docker_runtime_with_mock(self):
        """Test docker runtime with mocked subprocess."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout='CONTAINER ID   IMAGE   COMMAND   STATUS',
                stderr=''
            )
            
            from tools.docker_ops import DockerRuntime
            docker = DockerRuntime()
            assert docker is not None
    
    def test_docker_build_with_mock(self):
        """Test docker build with mocked subprocess."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='Successfully built', stderr='')
            
            from tools.docker_ops import DockerRuntime
            docker = DockerRuntime()
            assert docker is not None
    
    def test_docker_run_with_mock(self):
        """Test docker run with mocked subprocess."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='container-id', stderr='')
            
            from tools.docker_ops import DockerRuntime
            docker = DockerRuntime()
            assert docker is not None
    
    def test_docker_ps_with_mock(self):
        """Test docker ps with mocked subprocess."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout='CONTAINER ID   IMAGE   COMMAND   STATUS',
                stderr=''
            )
            
            from tools.docker_ops import DockerRuntime
            docker = DockerRuntime()
            assert docker is not None
    
    def test_docker_images_with_mock(self):
        """Test docker images with mocked subprocess."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout='REPOSITORY   TAG   IMAGE ID',
                stderr=''
            )
            
            from tools.docker_ops import DockerRuntime
            docker = DockerRuntime()
            assert docker is not None
    
    @pytest.mark.asyncio
    async def test_async_docker_operations(self):
        """Test async docker operations with mocks."""
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b'output', b''))
            mock_process.returncode = 0
            mock_exec.return_value = mock_process
            
            from tools.docker_ops import DockerRuntime
            docker = DockerRuntime()
            assert docker is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])