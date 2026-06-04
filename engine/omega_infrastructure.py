#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
OMEGA Infrastructure
====================
Underlying infrastructure for seamless coding:
- Temp directories for sandboxed execution
- Cache directories for repo map, embeddings
- State directories for checkpoints, logs
- Working directories for active sessions

This is the backbone that makes context, tools, and feedback loop work.
"""

import os
import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import tempfile

logging.basicConfig(level=logging.INFO, format='[INFRA] %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class InfrastructureConfig:
    """Configuration for infrastructure paths."""
    base_dir: str = ".omega"
    temp_dir: str = "temp"
    cache_dir: str = "cache"
    state_dir: str = "state"
    logs_dir: str = "logs"
    sessions_dir: str = "sessions"
    workspaces_dir: str = "workspaces"
    max_cache_age_days: int = 7
    max_temp_age_hours: int = 24


class OmegaInfrastructure:
    """
    Manages all underlying infrastructure for the OMEGA engine.
    Creates and maintains directories for temp files, caches, state, etc.
    """
    
    def __init__(self, root_path: Optional[str] = None, config: Optional[InfrastructureConfig] = None):
        self.root = Path(root_path) if root_path else PROJECT_ROOT
        self.config = config or InfrastructureConfig()
        
        # Create all directories
        self._base_dir = self.root / self.config.base_dir
        self._temp_dir = self._base_dir / self.config.temp_dir
        self._cache_dir = self._base_dir / self.config.cache_dir
        self._state_dir = self._base_dir / self.config.state_dir
        self._logs_dir = self._base_dir / self.config.logs_dir
        self._sessions_dir = self._base_dir / self.config.sessions_dir
        self._workspaces_dir = self._base_dir / self.config.workspaces_dir
        
        # Initialize directories
        self._init_directories()
    
    def _init_directories(self):
        """Create all required directories."""
        for dir_path in [self._temp_dir, self._cache_dir, self._state_dir, 
                         self._logs_dir, self._sessions_dir, self._workspaces_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized: {dir_path}")
    
    @property
    def base_dir(self) -> Path:
        return self._base_dir
    
    @property
    def temp_dir(self) -> Path:
        return self._temp_dir
    
    @property
    def cache_dir(self) -> Path:
        return self._cache_dir
    
    @property
    def state_dir(self) -> Path:
        return self._state_dir
    
    @property
    def logs_dir(self) -> Path:
        return self._logs_dir
    
    @property
    def sessions_dir(self) -> Path:
        return self._sessions_dir
    
    @property
    def workspaces_dir(self) -> Path:
        return self._workspaces_dir
    
    # ==================== Temp Directory Management ====================
    
    def create_temp_file(self, suffix: str = "", prefix: str = "omega_") -> Path:
        """Create a temp file in the sandbox."""
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=str(self._temp_dir))
        os.close(fd)
        return Path(path)
    
    def create_temp_dir(self, prefix: str = "omega_") -> Path:
        """Create a temp directory in the sandbox."""
        path = tempfile.mkdtemp(prefix=prefix, dir=str(self._temp_dir))
        return Path(path)
    
    def clean_temp(self, max_age_hours: int = None):
        """Clean temp directory, removing files older than max_age_hours."""
        max_age = max_age_hours or self.config.max_temp_age_hours
        current_time = datetime.now().timestamp()
        max_age_seconds = max_age * 3600
        
        removed = 0
        for path in self._temp_dir.iterdir():
            try:
                if path.is_file():
                    age = current_time - path.stat().st_mtime
                    if age > max_age_seconds:
                        path.unlink()
                        removed += 1
                elif path.is_dir():
                    shutil.rmtree(path)
                    removed += 1
            except Exception as e:
                logger.warning(f"Failed to clean {path}: {e}")
        
        logger.info(f"Cleaned {removed} items from temp")
        return removed
    
    # ==================== Cache Management ====================
    
    def cache_path(self, key: str, category: str = "default") -> Path:
        """Get cache path for a key."""
        category_dir = self._cache_dir / category
        category_dir.mkdir(exist_ok=True)
        
        # Hash the key to make it filesystem-safe
        key_hash = hashlib.md5(key.encode()).hexdigest()[:16]
        return category_dir / f"{key_hash}.cache"
    
    def get_cache(self, key: str, category: str = "default") -> Optional[Any]:
        """Get cached data."""
        cache_file = self.cache_path(key, category)
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Check if expired
            if 'expires' in data:
                if datetime.fromisoformat(data['expires']) < datetime.now():
                    cache_file.unlink()
                    return None
            
            return data.get('value')
        except Exception:
            return None
    
    def set_cache(self, key: str, value: Any, category: str = "default", ttl_hours: int = 24):
        """Set cache with optional TTL."""
        cache_file = self.cache_path(key, category)
        
        expires = datetime.now() + datetime.timedelta(hours=ttl_hours)
        
        data = {
            'value': value,
            'expires': expires.isoformat(),
            'created': datetime.now().isoformat()
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            return True
        except Exception:
            return False
    
    def clear_cache(self, category: Optional[str] = None):
        """Clear cache directory or category."""
        if category:
            category_dir = self._cache_dir / category
            if category_dir.exists():
                shutil.rmtree(category_dir)
                category_dir.mkdir()
        else:
            for item in self._cache_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
    
    # ==================== State Management ====================
    
    def state_file(self, name: str) -> Path:
        """Get state file path."""
        return self._state_dir / f"{name}.json"
    
    def save_state(self, name: str, data: Dict):
        """Save state to file."""
        state_file = self.state_file(name)
        state_file.parent.mkdir(exist_ok=True)
        
        with open(state_file, 'w') as f:
            json.dump({
                'data': data,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
    
    def load_state(self, name: str) -> Optional[Dict]:
        """Load state from file."""
        state_file = self.state_file(name)
        if not state_file.exists():
            return None
        
        try:
            with open(state_file, 'r') as f:
                return json.load(f).get('data')
        except Exception:
            return None
    
    def checkpoint(self, name: str, data: Dict):
        """Create a checkpoint - essentially a named state."""
        checkpoint_dir = self._state_dir / "checkpoints"
        checkpoint_dir.mkdir(exist_ok=True)
        
        checkpoint_file = checkpoint_dir / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Keep only last 10 checkpoints
        checkpoints = sorted(checkpoint_dir.glob(f"{name}_*.json"))
        for old in checkpoints[:-10]:
            old.unlink()
    
    # ==================== Session Management ====================
    
    def create_session(self, session_type: str = "default") -> str:
        """Create a new session and return session ID."""
        import uuid
        session_id = f"{session_type}_{uuid.uuid4().hex[:12]}"
        
        session_dir = self._sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create session metadata
        session_file = session_dir / "meta.json"
        with open(session_file, 'w') as f:
            json.dump({
                'id': session_id,
                'type': session_type,
                'created': datetime.now().isoformat(),
                'cwd': str(self.root)
            }, f)
        
        # Create session working directories
        (session_dir / "input").mkdir()
        (session_dir / "output").mkdir()
        (session_dir / "logs").mkdir()
        
        return session_id
    
    def get_session_dir(self, session_id: str) -> Optional[Path]:
        """Get session directory."""
        session_dir = self._sessions_dir / session_id
        return session_dir if session_dir.exists() else None
    
    def session_workspace(self, session_id: str) -> Path:
        """Get session workspace directory for active files."""
        session_dir = self.get_session_dir(session_id)
        if not session_dir:
            session_dir = self._sessions_dir / session_id
            session_dir.mkdir(parents=True)
        
        return session_dir / "workspace"
    
    def list_sessions(self) -> List[Dict]:
        """List all sessions."""
        sessions = []
        
        for session_dir in self._sessions_dir.iterdir():
            if not session_dir.is_dir():
                continue
            
            meta_file = session_dir / "meta.json"
            if meta_file.exists():
                with open(meta_file, 'r') as f:
                    sessions.append(json.load(f))
        
        return sessions
    
    def cleanup_sessions(self, max_age_hours: int = 24):
        """Clean up old sessions."""
        current_time = datetime.now().timestamp()
        max_age_seconds = max_age_hours * 3600
        
        removed = 0
        for session_dir in self._sessions_dir.iterdir():
            if not session_dir.is_dir():
                continue
            
            try:
                age = current_time - session_dir.stat().st_mtime
                if age > max_age_seconds:
                    shutil.rmtree(session_dir)
                    removed += 1
            except Exception:
                pass
        
        return removed
    
    # ==================== Workspace Management ====================
    
    def create_workspace(self, name: str) -> Path:
        """Create a named workspace."""
        workspace_dir = self._workspaces_dir / name
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Create standard workspace structure
        (workspace_dir / "src").mkdir(exist_ok=True)
        (workspace_dir / "tests").mkdir(exist_ok=True)
        (workspace_dir / "docs").mkdir(exist_ok=True)
        (workspace_dir / "output").mkdir(exist_ok=True)
        
        return workspace_dir
    
    def get_workspace(self, name: str) -> Optional[Path]:
        """Get workspace directory."""
        workspace_dir = self._workspaces_dir / name
        return workspace_dir if workspace_dir.exists() else None
    
    # ==================== Logging ====================
    
    def log_file(self, name: str = "omega") -> Path:
        """Get log file path."""
        return self._logs_dir / f"{name}.log"
    
    def write_log(self, message: str, level: str = "INFO"):
        """Write to log file."""
        log_file = self.log_file()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        with open(log_file, 'a') as f:
            f.write(log_line)
    
    def get_recent_logs(self, lines: int = 100) -> str:
        """Get recent log lines."""
        log_file = self.log_file()
        if not log_file.exists():
            return ""
        
        try:
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except Exception:
            return ""
    
    # ==================== Cleanup ====================
    
    def full_cleanup(self):
        """Run full cleanup of all temporary and cached data."""
        results = {
            'temp_cleaned': self.clean_temp(),
            'cache_cleared': 0,
            'sessions_cleaned': self.cleanup_sessions()
        }
        
        # Count cache files
        for f in self._cache_dir.rglob("*"):
            if f.is_file():
                results['cache_cleared'] += 1
        
        self.clear_cache()
        
        logger.info(f"Cleanup complete: {results}")
        return results
    
    def get_disk_usage(self) -> Dict:
        """Get disk usage of all OMEGA directories."""
        def get_dir_size(path: Path) -> int:
            total = 0
            try:
                for item in path.rglob("*"):
                    if item.is_file():
                        total += item.stat().st_size
            except:
                pass
            return total
        
        return {
            'base': str(self._base_dir),
            'temp_mb': round(get_dir_size(self._temp_dir) / 1024 / 1024, 2),
            'cache_mb': round(get_dir_size(self._cache_dir) / 1024 / 1024, 2),
            'state_mb': round(get_dir_size(self._state_dir) / 1024 / 1024, 2),
            'logs_mb': round(get_dir_size(self._logs_dir) / 1024 / 1024, 2),
            'sessions_mb': round(get_dir_size(self._sessions_dir) / 1024 / 1024, 2),
            'workspaces_mb': round(get_dir_size(self._workspaces_dir) / 1024 / 1024, 2)
        }


# Singleton instance
_infrastructure: Optional[OmegaInfrastructure] = None


def get_infrastructure(root_path: Optional[str] = None) -> OmegaInfrastructure:
    """Get or create the infrastructure singleton."""
    global _infrastructure
    if _infrastructure is None:
        _infrastructure = OmegaInfrastructure(root_path)
    return _infrastructure


if __name__ == "__main__":
    import sys
    
    infra = OmegaInfrastructure()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "cleanup":
            print("Running full cleanup...")
            print(json.dumps(infra.full_cleanup(), indent=2))
        
        elif cmd == "disk":
            print(json.dumps(infra.get_disk_usage(), indent=2))
        
        elif cmd == "sessions":
            print(json.dumps(infra.list_sessions(), indent=2))
        
        elif cmd == "logs":
            print(infra.get_recent_logs(50))
        
        elif cmd == "create-session":
            sid = infra.create_session("coding")
            print(f"Created session: {sid}")
    
    else:
        print("OMEGA Infrastructure")
        print(f"Base: {infra.base_dir}")
        print(json.dumps(infra.get_disk_usage(), indent=2))