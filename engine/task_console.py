"""
Paradise Stack - Task Console
The activity center where tasks are created, executed, and tracked.
Real-time execution monitoring and control.
"""

import os
import sys
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict

PROJECT_ROOT = Path("C:\\Users\\HomeUser\\Downloads\\agentic-OS")
sys.path.insert(0, str(PROJECT_ROOT))

class TaskStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class TaskActivity:
    task_id: str
    action: str
    timestamp: str
    details: str
    agent: str
    status: str

@dataclass  
class Task:
    id: str
    title: str
    description: str
    status: str
    priority: int
    created_at: str
    updated_at: str
    activities: List[Dict]
    steps: List[Dict]
    current_step: int

class TaskConsole:
    """
    Task Console - The activity center for Paradise Stack.
    
    Features:
    - Create and manage tasks
    - Execute tasks with real-time monitoring
    - Track all activities
    - Multi-agent coordination
    - Real-time status updates
    """
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.activities: List[Dict] = []
        self.agents = ["Architect", "Builder", "Guardian", "Learner", "Oracle"]
        self.current_agent = "Paradise"
        
        self._load_state()
    
    def _load_state(self):
        """Load previous state if exists."""
        state_file = PROJECT_ROOT / "intelligence" / "cache" / "task_console.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = {k: Task(**v) for k, v in data.get("tasks", {}).items()}
                    self.activities = data.get("activities", [])
            except:
                pass
    
    def _save_state(self):
        """Save current state."""
        state_file = PROJECT_ROOT / "intelligence" / "cache" / "task_console.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(state_file, 'w') as f:
            json.dump({
                "tasks": {k: asdict(v) for k, v in self.tasks.items()},
                "activities": self.activities[-100:],
            }, f, indent=2, default=str)
    
    def create_task(self, title: str, description: str = "", priority: int = 2) -> Task:
        """Create a new task."""
        task_id = f"task_{len(self.tasks) + 1}_{int(time.time())}"
        timestamp = datetime.now().isoformat()
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            status=TaskStatus.CREATED.value,
            priority=priority,
            created_at=timestamp,
            updated_at=timestamp,
            activities=[],
            steps=[],
            current_step=0
        )
        
        self.tasks[task_id] = task
        self._add_activity(task_id, "created", f"Task '{title}' created", self.current_agent)
        self._save_state()
        
        return task
    
    def start_task(self, task_id: str) -> Task:
        """Start executing a task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = TaskStatus.RUNNING.value
        task.updated_at = datetime.now().isoformat()
        
        self._add_activity(task_id, "started", "Task execution started", self.current_agent)
        self._save_state()
        
        return task
    
    def update_task(self, task_id: str, status: str = None, step: int = None) -> Task:
        """Update task status or step."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        
        if status:
            task.status = status
            self._add_activity(task_id, "status_changed", f"Status: {status}", self.current_agent)
        
        if step is not None:
            task.current_step = step
            self._add_activity(task_id, "step_changed", f"Step: {step + 1}", self.current_agent)
        
        task.updated_at = datetime.now().isoformat()
        self._save_state()
        
        return task
    
    def complete_task(self, task_id: str, result: str = None) -> Task:
        """Mark task as completed."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED.value
        task.updated_at = datetime.now().isoformat()
        
        msg = result or "Task completed successfully"
        self._add_activity(task_id, "completed", msg, self.current_agent)
        self._save_state()
        
        return task
    
    def fail_task(self, task_id: str, error: str) -> Task:
        """Mark task as failed."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = TaskStatus.FAILED.value
        task.updated_at = datetime.now().isoformat()
        
        self._add_activity(task_id, "failed", f"Error: {error}", self.current_agent)
        self._save_state()
        
        return task
    
    def _add_activity(self, task_id: str, action: str, details: str, agent: str):
        """Add an activity log entry."""
        activity = {
            "id": str(uuid.uuid4())[:8],
            "task_id": task_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "agent": agent,
            "status": "ok"
        }
        self.activities.append(activity)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return list(self.tasks.values())
    
    def get_active_tasks(self) -> List[Task]:
        """Get currently running tasks."""
        return [t for t in self.tasks.values() if t.status == TaskStatus.RUNNING.value]
    
    def get_recent_activities(self, limit: int = 20) -> List[Dict]:
        """Get recent activities."""
        return self.activities[-limit:]
    
    def get_console_summary(self) -> Dict:
        """Get console summary."""
        tasks = list(self.tasks.values())
        return {
            "total_tasks": len(tasks),
            "running": sum(1 for t in tasks if t.status == TaskStatus.RUNNING.value),
            "completed": sum(1 for t in tasks if t.status == TaskStatus.COMPLETED.value),
            "failed": sum(1 for t in tasks if t.status == TaskStatus.FAILED.value),
            "recent_activities": len(self.activities),
        }
    
    def run_interactive(self):
        """Run interactive task console."""
        print("=" * 70)
        print("PARADISE STACK - TASK CONSOLE")
        print("=" * 70)
        print("Commands: create, list, start, complete, fail, activities, summary, exit")
        print()
        
        while True:
            try:
                cmd = input("Console> ").strip().lower()
                
                if cmd == "exit":
                    print("\nConsole closed.")
                    break
                
                elif cmd == "create":
                    title = input("  Task title: ").strip()
                    if title:
                        desc = input("  Description (optional): ").strip()
                        task = self.create_task(title, desc)
                        print(f"  [CREATED] Task: {task.id}")
                
                elif cmd == "list":
                    tasks = self.get_all_tasks()
                    if not tasks:
                        print("  No tasks found.")
                    else:
                        for t in tasks[-10:]:
                            print(f"  [{t.status.upper():10}] {t.id}: {t.title}")
                
                elif cmd == "start":
                    task_id = input("  Task ID: ").strip()
                    try:
                        self.start_task(task_id)
                        print(f"  [STARTED] Task: {task_id}")
                    except ValueError as e:
                        print(f"  [ERROR] {e}")
                
                elif cmd == "complete":
                    task_id = input("  Task ID: ").strip()
                    result = input("  Result (optional): ").strip()
                    try:
                        self.complete_task(task_id, result or None)
                        print(f"  [COMPLETED] Task: {task_id}")
                    except ValueError as e:
                        print(f"  [ERROR] {e}")
                
                elif cmd == "activities":
                    activities = self.get_recent_activities()
                    for a in activities[-10:]:
                        print(f"  [{a['timestamp'][11:19]}] {a['agent']}: {a['action']} - {a['details'][:50]}")
                
                elif cmd == "summary":
                    summary = self.get_console_summary()
                    print(f"\n  Task Summary:")
                    print(f"    Total: {summary['total_tasks']}")
                    print(f"    Running: {summary['running']}")
                    print(f"    Completed: {summary['completed']}")
                    print(f"    Failed: {summary['failed']}")
                    print(f"    Activities: {summary['recent_activities']}\n")
                
                else:
                    print("  Unknown command. Type 'help' for commands.")
                    
            except KeyboardInterrupt:
                print("\n\nConsole closed.")
                break
            except Exception as e:
                print(f"  [ERROR] {e}")


def asdict(obj):
    """Convert dataclass to dict."""
    if hasattr(obj, '__dataclass_fields__'):
        return {k: asdict(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, list):
        return [asdict(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: asdict(v) for k, v in obj.items()}
    else:
        return obj


def demo():
    """Demo the task console."""
    console = TaskConsole()
    
    print("Creating demo tasks...")
    
    t1 = console.create_task("Build user authentication", "Add login/logout functionality", 3)
    t2 = console.create_task("Write tests", "Unit tests for auth module", 2)
    t3 = console.create_task("Update docs", "Document API endpoints", 1)
    
    print(f"\nCreated: {t1.id}, {t2.id}, {t3.id}")
    
    print("\nStarting tasks...")
    console.start_task(t1.id)
    console.start_task(t2.id)
    
    print("\nCompleting task...")
    console.complete_task(t1.id, "Auth system built and tested")
    
    print("\nConsole Summary:")
    summary = console.get_console_summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")
    
    print("\nRecent Activities:")
    for a in console.get_recent_activities():
        print(f"  [{a['agent']}] {a['action']}: {a['details'][:40]}")


if __name__ == "__main__":
    demo()
