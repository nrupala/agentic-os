"""
MIT License
Copyright (c) 2026 Nrupal Akolkar
"""

import asyncio
import json
import uuid
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ContainerStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    RESTARTING = "restarting"
    EXITED = "exited"
    DEAD = "dead"
    UNKNOWN = "unknown"


class ImageStatus(Enum):
    PENDING = "pending"
    BUILDING = "building"
    PULLING = "pulling"
    READY = "ready"
    FAILED = "failed"


@dataclass
class Container:
    id: str
    name: str
    image: str
    status: ContainerStatus
    created: datetime
    ports: Dict[str, str] = field(default_factory=dict)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0


@dataclass
class Image:
    id: str
    tags: List[str]
    size: int
    created: datetime


@dataclass
class BuildResult:
    success: bool
    image_id: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    error: Optional[str] = None
    duration: float = 0.0


@dataclass
class ExecutionResult:
    exit_code: int
    stdout: str
    stderr: str
    duration: float


class DockerRuntime:
    """Docker runtime for containerized execution."""

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.containers: Dict[str, Container] = {}
        self.images: Dict[str, Image] = {}
        self._connected = False

    async def check_docker(self) -> bool:
        """Check if Docker is available."""
        proc = await asyncio.create_subprocess_exec(
            'docker', 'version', '--format', '{{.Server.Version}}',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        self._connected = proc.returncode == 0
        return self._connected

    async def pull_image(self, image: str, tag: str = "latest") -> Dict:
        """Pull a Docker image."""
        full_image = f"{image}:{tag}"
        
        try:
            proc = await asyncio.create_subprocess_exec(
                'docker', 'pull', full_image,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                return {
                    "success": True,
                    "message": f"Pulled {full_image}",
                    "image": full_image
                }
            return {
                "success": False,
                "error": stderr.decode() if stderr else "Pull failed"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def build_image(
        self,
        dockerfile: str,
        tag: str,
        build_args: Dict[str, str] = None,
        no_cache: bool = False
    ) -> BuildResult:
        """Build a Docker image from Dockerfile."""
        start_time = datetime.now()
        logs = []
        
        dockerfile_path = Path(dockerfile)
        if not dockerfile_path.is_absolute():
            dockerfile_path = self.project_path / dockerfile_path
        
        context_path = dockerfile_path.parent
        
        cmd = ['docker', 'build', '-t', tag]
        
        if no_cache:
            cmd.append('--no-cache')
        
        if build_args:
            for key, value in build_args.items():
                cmd.extend(['--build-arg', f'{key}={value}'])
        
        cmd.extend(['-f', str(dockerfile_path), str(context_path)])
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            image_id = None
            async for line in proc.stdout:
                decoded = line.decode('utf-8', errors='replace').strip()
                logs.append(decoded)
                
                if 'Successfully tagged' in decoded:
                    image_id = tag
                elif 'Successfully built' in decoded:
                    parts = decoded.split()
                    if 'built' in parts:
                        idx = parts.index('built')
                        if idx + 1 < len(parts):
                            image_id = parts[idx + 1]
            
            await proc.wait()
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return BuildResult(
                success=proc.returncode == 0,
                image_id=image_id,
                logs=logs,
                duration=duration
            )
        except Exception as e:
            return BuildResult(
                success=False,
                logs=logs,
                error=str(e),
                duration=(datetime.now() - start_time).total_seconds()
            )

    async def run_container(
        self,
        image: str,
        name: str = None,
        command: List[str] = None,
        ports: Dict[str, str] = None,
        volumes: Dict[str, str] = None,
        environment: Dict[str, str] = None,
        detach: bool = True,
        remove: bool = True
    ) -> Dict:
        """Run a Docker container."""
        if name is None:
            name = f"agentic-{uuid.uuid4().hex[:8]}"
        
        cmd = ['docker', 'run']
        
        if detach:
            cmd.append('-d')
        
        if remove:
            cmd.append('--rm')
        
        cmd.extend(['--name', name])
        
        if ports:
            for host_port, container_port in ports.items():
                cmd.extend(['-p', f'{host_port}:{container_port}'])
        
        if volumes:
            for host_path, container_path in volumes.items():
                cmd.extend(['-v', f'{host_path}:{container_path}'])
        
        if environment:
            for key, value in environment.items():
                cmd.extend(['-e', f'{key}={value}'])
        
        cmd.append(image)
        
        if command:
            cmd.extend(command)
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0 or detach:
                container_id = stdout.decode().strip()[:12]
                
                await asyncio.sleep(0.5)
                inspect = await self.inspect_container(container_id)
                
                self.containers[container_id] = Container(
                    id=container_id,
                    name=name,
                    image=image,
                    status=ContainerStatus.RUNNING,
                    created=datetime.now(),
                    ports=ports or {}
                )
                
                return {
                    "success": True,
                    "container_id": container_id,
                    "name": name,
                    "status": "running"
                }
            
            return {
                "success": False,
                "error": stderr.decode() if stderr else "Run failed"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def exec_container(
        self,
        container: str,
        command: List[str],
        detach: bool = False
    ) -> ExecutionResult:
        """Execute a command in a running container."""
        start_time = datetime.now()
        
        cmd = ['docker', 'exec']
        
        if detach:
            cmd.append('-d')
        
        cmd.append(container)
        cmd.extend(command)
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return ExecutionResult(
                exit_code=proc.returncode,
                stdout=stdout.decode('utf-8', errors='replace'),
                stderr=stderr.decode('utf-8', errors='replace'),
                duration=duration
            )
        except Exception as e:
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration=0.0
            )

    async def stop_container(self, container: str, timeout: int = 10) -> Dict:
        """Stop a running container."""
        try:
            proc = await asyncio.create_subprocess_exec(
                'docker', 'stop', '-t', str(timeout), container,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                if container in self.containers:
                    self.containers[container].status = ContainerStatus.EXITED
                return {"success": True, "message": f"Stopped {container}"}
            
            return {"success": False, "error": stderr.decode() if stderr else "Stop failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def remove_container(self, container: str, force: bool = False) -> Dict:
        """Remove a container."""
        try:
            cmd = ['docker', 'rm']
            if force:
                cmd.append('-f')
            cmd.append(container)
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                if container in self.containers:
                    del self.containers[container]
                return {"success": True, "message": f"Removed {container}"}
            
            return {"success": False, "error": stderr.decode() if stderr else "Remove failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def inspect_container(self, container: str) -> Optional[Dict]:
        """Get container details."""
        try:
            proc = await asyncio.create_subprocess_exec(
                'docker', 'inspect', container,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                data = json.loads(stdout.decode('utf-8'))
                if data:
                    return data[0]
            return None
        except Exception:
            return None

    async def list_containers(self, all: bool = False) -> List[Dict]:
        """List containers."""
        try:
            cmd = ['docker', 'ps', '--format', '{{.ID}}|{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}']
            if all:
                cmd.append('-a')
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            containers = []
            for line in stdout.decode().strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 4:
                    status = ContainerStatus.RUNNING
                    status_str = parts[3].lower()
                    if 'exited' in status_str:
                        status = ContainerStatus.EXITED
                    elif 'paused' in status_str:
                        status = ContainerStatus.PAUSED
                    
                    containers.append({
                        "id": parts[0],
                        "name": parts[1],
                        "image": parts[2],
                        "status": status.value,
                        "ports": parts[4] if len(parts) > 4 else ""
                    })
            
            return containers
        except Exception:
            return []

    async def list_images(self) -> List[Dict]:
        """List Docker images."""
        try:
            proc = await asyncio.create_subprocess_exec(
                'docker', 'images', '--format', '{{.ID}}|{{.Repository}}|{{.Tag}}|{{.Size}}',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            images = []
            for line in stdout.decode().strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 3:
                    images.append({
                        "id": parts[0],
                        "repository": parts[1],
                        "tag": parts[2],
                        "size": parts[3] if len(parts) > 3 else ""
                    })
            
            return images
        except Exception:
            return []

    async def get_logs(self, container: str, tail: int = 100) -> str:
        """Get container logs."""
        try:
            proc = await asyncio.create_subprocess_exec(
                'docker', 'logs', '--tail', str(tail), container,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            stdout, _ = await proc.communicate()
            return stdout.decode('utf-8', errors='replace')
        except Exception as e:
            return str(e)

    async def get_stats(self, container: str) -> Dict:
        """Get container resource stats."""
        try:
            proc = await asyncio.create_subprocess_exec(
                'docker', 'stats', '--no-stream', '--format',
                '{{.CPUPerc}}|{{.MemPerc}}|{{.MemUsage}}', container,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0 and stdout:
                parts = stdout.decode().strip().split('|')
                if len(parts) >= 2:
                    cpu = float(parts[0].rstrip('%'))
                    mem = float(parts[1].rstrip('%'))
                    
                    if container in self.containers:
                        self.containers[container].cpu_percent = cpu
                        self.containers[container].memory_percent = mem
                    
                    return {
                        "cpu_percent": cpu,
                        "memory_percent": mem,
                        "memory_usage": parts[2] if len(parts) > 2 else ""
                    }
            return {"cpu_percent": 0, "memory_percent": 0}
        except Exception:
            return {"cpu_percent": 0, "memory_percent": 0}

    async def prune_containers(self) -> Dict:
        """Remove stopped containers."""
        try:
            proc = await asyncio.create_subprocess_exec(
                'docker', 'container', 'prune', '-f',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            return {
                "success": True,
                "output": stdout.decode().strip()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def prune_images(self) -> Dict:
        """Remove unused images."""
        try:
            proc = await asyncio.create_subprocess_exec(
                'docker', 'image', 'prune', '-f',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            return {
                "success": True,
                "output": stdout.decode().strip()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_network(self, name: str, driver: str = "bridge") -> Dict:
        """Create a Docker network."""
        try:
            proc = await asyncio.create_subprocess_exec(
                'docker', 'network', 'create', '--driver', driver, name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                return {"success": True, "network_id": stdout.decode().strip()}
            return {"success": False, "error": stderr.decode().strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}


class SandboxExecutor:
    """Execute code in isolated Docker sandbox."""

    def __init__(self, runtime: DockerRuntime):
        self.runtime = runtime

    async def execute_python(
        self,
        code: str,
        timeout: int = 60,
        packages: List[str] = None
    ) -> ExecutionResult:
        """Execute Python code in sandbox."""
        import base64
        
        encoded_code = base64.b64encode(code.encode()).decode()
        
        setup_commands = []
        if packages:
            for pkg in packages:
                setup_commands.append(f"pip install {pkg}")
            setup_commands.append("pip install --quiet")
        
        full_code = "\n".join(setup_commands + [code])
        
        environment = {
            "PYTHONUNBUFFERED": "1"
        }
        
        result = await self.runtime.run_container(
            image="python:3.11-slim",
            command=[
                'sh', '-c',
                f'echo {encoded_code} | base64 -d > /tmp/script.py && python /tmp/script.py'
            ],
            environment=environment,
            volumes={
                str(self.runtime.project_path): "/workspace"
            },
            detach=False,
            remove=True
        )
        
        if result.get("success"):
            container_id = result["container_id"]
            await asyncio.sleep(0.5)
            
            output = await self.runtime.get_logs(container_id)
            await self.runtime.stop_container(container_id)
            
            return ExecutionResult(
                exit_code=0,
                stdout=output,
                stderr="",
                duration=0.0
            )
        
        return ExecutionResult(
            exit_code=-1,
            stdout="",
            stderr=result.get("error", "Execution failed"),
            duration=0.0
        )

    async def execute_bash(
        self,
        script: str,
        timeout: int = 60
    ) -> ExecutionResult:
        """Execute bash script in sandbox."""
        import base64
        
        encoded_script = base64.b64encode(script.encode()).decode()
        
        result = await self.runtime.run_container(
            image="bash:latest",
            command=[
                'sh', '-c',
                f'echo {encoded_script} | base64 -d > /tmp/script.sh && bash /tmp/script.sh'
            ],
            volumes={
                str(self.runtime.project_path): "/workspace"
            },
            detach=False,
            remove=True
        )
        
        if result.get("success"):
            container_id = result["container_id"]
            await asyncio.sleep(0.5)
            
            output = await self.runtime.get_logs(container_id)
            await self.runtime.stop_container(container_id)
            
            return ExecutionResult(
                exit_code=0,
                stdout=output,
                stderr="",
                duration=0.0
            )
        
        return ExecutionResult(
            exit_code=-1,
            stdout="",
            stderr=result.get("error", "Execution failed"),
            duration=0.0
        )


if __name__ == "__main__":
    import sys
    
    async def main():
        runtime = DockerRuntime()
        
        print("Checking Docker connection...")
        connected = await runtime.check_docker()
        
        if not connected:
            print("Docker not available. Is Docker running?")
            sys.exit(1)
        
        print("Docker is connected!")
        
        print("\nListing containers...")
        containers = await runtime.list_containers(all=True)
        print(f"Found {len(containers)} container(s)")
        
        print("\nListing images...")
        images = await runtime.list_images()
        print(f"Found {len(images)} image(s)")
    
    asyncio.run(main())
