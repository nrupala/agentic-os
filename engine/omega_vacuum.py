#!/usr/bin/env python3
"""
PHASE 8: Vacuum Protocol
=========================
Log distillation, cleanup, and wisdom extraction.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class VacuumProtocol:
    """
    Cleans up logs and distills wisdom.
    
    Features:
    - Log distillation (50 logs -> Top 3 Lessons)
    - Wisdom append to MEMORY.md
    - 10-log rolling window
    - Safe delete with .trash
    - Temp file cleanup
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.logs_dir = self.project_path / "logs"
        self.memory_dir = self.project_path / "memory"
        self.trash_dir = self.project_path / ".trash"
        self.temp_dir = Path("/tmp/omega")
        
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.trash_dir.mkdir(parents=True, exist_ok=True)
    
    def run_vacuum(self) -> Dict:
        """Run full vacuum protocol."""
        results = {
            "logs_reviewed": 0,
            "logs_trashed": 0,
            "lessons_extracted": [],
            "temp_files_cleaned": 0
        }
        
        results["logs_reviewed"], results["lessons_extracted"] = self.distill_logs()
        results["logs_trashed"] = self.clean_old_logs()
        results["temp_files_cleaned"] = self.clean_temp()
        
        if results["lessons_extracted"]:
            self.append_wisdom(results["lessons_extracted"])
        
        return results
    
    def distill_logs(self) -> tuple:
        """
        Distill logs into lessons.
        Returns (count_reviewed, lessons)
        """
        log_files = sorted(self.logs_dir.glob("*.log"), key=lambda p: p.stat().st_mtime)
        
        if len(log_files) < 5:
            return len(log_files), []
        
        lessons = []
        patterns = {
            "import_error": "Always verify imports before use",
            "timeout": "Increase timeout for network operations",
            "memory": "Monitor memory usage closely",
            "permission": "Check file permissions early",
            "syntax": "Validate syntax before execution",
        }
        
        for log_file in log_files[-20:]:
            content = log_file.read_text().lower()
            
            for pattern, lesson in patterns.items():
                if pattern in content and lesson not in lessons:
                    lessons.append(lesson)
                    break
        
        return len(log_files), lessons[:3]
    
    def clean_old_logs(self) -> int:
        """Keep only 10 most recent logs."""
        log_files = sorted(self.logs_dir.glob("*.log"), key=lambda p: p.stat().st_mtime)
        
        trashed = 0
        for old_log in log_files[:-10]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trash_path = self.trash_dir / f"{old_log.stem}_{timestamp}{old_log.suffix}"
            
            shutil.move(str(old_log), str(trash_path))
            trashed += 1
        
        return trashed
    
    def clean_temp(self) -> int:
        """Clean temp files."""
        if not self.temp_dir.exists():
            return 0
        
        count = 0
        for item in self.temp_dir.glob("*"):
            if item.is_file():
                item.unlink()
                count += 1
            elif item.is_dir():
                shutil.rmtree(item)
                count += 1
        
        return count
    
    def append_wisdom(self, lessons: List[str]):
        """Append lessons to MEMORY.md."""
        memory_file = self.memory_dir / "MEMORY.md"
        
        if not memory_file.exists():
            memory_file.write_text("# OMEGA Long-Term Memory\n\n")
        
        timestamp = datetime.now().isoformat()
        
        with open(memory_file, "a") as f:
            f.write(f"\n\n## Lessons Extracted - {timestamp}\n\n")
            for i, lesson in enumerate(lessons, 1):
                f.write(f"{i}. {lesson}\n")
    
    def get_status(self) -> Dict:
        """Get vacuum status."""
        log_files = list(self.logs_dir.glob("*.log"))
        trash_files = list(self.trash_dir.glob("*"))
        
        return {
            "logs_count": len(log_files),
            "trash_count": len(trash_files),
            "temp_dir_exists": self.temp_dir.exists(),
            "memory_file_exists": (self.memory_dir / "MEMORY.md").exists()
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: omega_vacuum.py <project_path>")
        sys.exit(1)
    
    vacuum = VacuumProtocol(sys.argv[1])
    
    print("Running Vacuum Protocol...")
    results = vacuum.run_vacuum()
    
    print(f"\nResults:")
    for key, value in results.items():
        print(f"  {key}: {value}")
    
    status = vacuum.get_status()
    print(f"\nStatus:")
    for key, value in status.items():
        print(f"  {key}: {value}")
