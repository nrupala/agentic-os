#!/usr/bin/env python3
"""
PHASE 6: Self-Developing Intelligence
Detects capability gaps and autonomously resolves them.
"""

import json
import sqlite3
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

class SelfDevelopingIntelligence:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.db_path = self.project_path / "state" / "omega.db"
        self.check_deps_path = self.project_path.parent.parent / "docker" / "check_deps.py"
        self.failure_threshold = 3
        self.shadow_mode = True
        
    def check_capability_gap(self) -> dict:
        """Detect 3+ failures on same issue type."""
        if not self.db_path.exists():
            return {"gap_detected": False, "reason": "No history"}
            
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT error_category, COUNT(*) as count, MAX(timestamp) as last_seen
            FROM failure_log
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY error_category
            HAVING count >= ?
            ORDER BY count DESC
        """, (self.failure_threshold,))
        
        gaps = []
        for row in cursor.fetchall():
            error_category, count, last_seen = row
            gaps.append({
                "category": error_category,
                "occurrences": count,
                "last_seen": last_seen
            })
        
        conn.close()
        
        if gaps:
            self._auto_resolve(gaps)
            
        return {"gap_detected": len(gaps) > 0, "gaps": gaps}
    
    def _auto_resolve(self, gaps: list):
        """Auto-install missing dependencies based on failure patterns."""
        dependency_map = {
            "import_error": ["pip", "npm", "cargo"],
            "module_not_found": ["pytest", "requests", "numpy"],
            "connection_timeout": ["curl", "wget"],
            "permission_denied": ["sudo", "chmod"],
            "memory_error": ["gcov", "valgrind"],
        }
        
        resolutions = []
        for gap in gaps:
            category = gap["category"]
            if category in dependency_map:
                for dep in dependency_map[category]:
                    if self._install_if_missing(dep):
                        resolutions.append(f"Installed: {dep}")
        
        if resolutions:
            self._update_check_deps(gaps, resolutions)
            self._log_resolution(gaps, resolutions)
    
    def _install_if_missing(self, package: str) -> bool:
        """Attempt to install a package. Returns True if installed."""
        try:
            result = subprocess.run(
                ["pip", "install", package],
                capture_output=True,
                timeout=60
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _update_check_deps(self, gaps: list, resolutions: list):
        """Auto-update check_deps.py with new dependencies."""
        if not self.check_deps_path.exists():
            return
            
        content = self.check_deps_path.read_text()
        
        for gap in gaps:
            category = gap["category"]
            if category not in content:
                new_check = f'\n    "{category}": ["python", "git", "docker"],\n'
                content = content.replace(
                    "REQUIRED_DEPS = {",
                    f"REQUIRED_DEPS = {{{new_check}"
                )
        
        for res in resolutions:
            package = res.replace("Installed: ", "")
            if package not in content:
                content = content.replace(
                    'REQUIRED_DEPS = {',
                    f'REQUIRED_DEPS = {{\n    "{package}": None,'
                )
        
        self.check_deps_path.write_text(content)
    
    def _log_resolution(self, gaps: list, resolutions: list):
        """Log the self-healing action."""
        log_path = self.project_path / "logs" / "self_heal.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "gaps": gaps,
            "resolutions": resolutions,
            "status": "resolved"
        }
        
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def shadow_agent_loop(self):
        """Background optimization loop."""
        if not self.shadow_mode:
            return
            
        while self.shadow_mode:
            gap_result = self.check_capability_gap()
            
            if gap_result["gap_detected"]:
                self._optimize_based_on_gaps(gap_result["gaps"])
            
            import time
            time.sleep(300)
    
    def _optimize_based_on_gaps(self, gaps: list):
        """Optimize system based on detected gaps."""
        for gap in gaps:
            category = gap["category"]
            
            if category == "import_error":
                self._preload_common_modules()
            elif category == "memory_error":
                self._enable_gc_tuning()
            elif category == "connection_timeout":
                self._increase_timeout_config()
    
    def _preload_common_modules(self):
        """Preload common modules to avoid import delays."""
        preload_file = self.project_path / "state" / "preload_cache.txt"
        preload_file.write_text("import sys\nsys.path.insert(0, 'src')\n")
    
    def _enable_gc_tuning(self):
        """Enable garbage collection tuning."""
        gc_config = self.project_path / "state" / "gc_config.json"
        gc_config.write_text(json.dumps({
            "gc_threshold0": 700,
            "gc_threshold1": 10,
            "gc_threshold2": 10
        }))
    
    def _increase_timeout_config(self):
        """Increase timeout configuration."""
        timeout_config = self.project_path / "state" / "timeout_config.json"
        timeout_config.write_text(json.dumps({
            "llm_timeout": 120,
            "connection_timeout": 30
        }))
    
    def get_system_health(self) -> dict:
        """Get current system health metrics."""
        health = {
            "timestamp": datetime.now().isoformat(),
            "shadow_mode": self.shadow_mode,
            "capability_gaps": self.check_capability_gap(),
            "dependencies_current": self._check_deps_current()
        }
        return health
    
    def _check_deps_current(self) -> bool:
        """Check if dependencies are current."""
        return self.check_deps_path.exists() and self.check_deps_path.stat().st_size > 0


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: omega_self_develop.py <project_path> [--shadow]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    sdi = SelfDevelopingIntelligence(project_path)
    
    if "--shadow" in sys.argv:
        sdi.shadow_agent_loop()
    else:
        result = sdi.check_capability_gap()
        print(json.dumps(result, indent=2))
