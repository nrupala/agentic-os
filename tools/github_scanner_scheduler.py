"""
Monthly Intelligence Scheduler
Schedules GitHub scans on monthly basis using Windows Task Scheduler.
"""

import os
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent / "github_intelligence_scanner.py"
INTELLIGENCE_DIR = Path("C:\\Users\\HomeUser\\Downloads\\agentic-OS\\intelligence")
CACHE_PATH = INTELLIGENCE_DIR / "cache" / "schedule.json"

def create_task_scheduler_entry():
    """Create Windows Task Scheduler entry for monthly scan."""
    task_name = "ParadiseStack_GitHubIntelligenceScan"
    
    command = [
        "schtasks",
        "/create",
        "/tn", task_name,
        "/tr", f'python "{SCRIPT_PATH}"',
        "/sc", "monthly",
        "/d", "1",
        "/st", "02:00",
        "/f"
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Task '{task_name}' created successfully")
            print(result.stdout)
            return True
        else:
            print(f"Failed to create task: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error creating task: {e}")
        return False

def remove_task_scheduler_entry():
    """Remove Windows Task Scheduler entry."""
    task_name = "ParadiseStack_GitHubIntelligenceScan"
    
    command = ["schtasks", "/delete", "/tn", task_name, "/f"]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Task '{task_name}' removed")
            return True
        return False
    except Exception as e:
        print(f"Error removing task: {e}")
        return False

def get_schedule_status() -> dict:
    """Get current schedule status."""
    status = {
        "task_exists": False,
        "last_run": None,
        "next_run": None,
        "interval_days": 30
    }
    
    if CACHE_PATH.exists():
        with open(CACHE_PATH, "r") as f:
            cache = json.load(f)
            status["last_run"] = cache.get("last_scan")
            status["next_run"] = cache.get("next_scan_due")
    
    task_name = "ParadiseStack_GitHubIntelligenceScan"
    command = ["schtasks", "/query", "/tn", task_name, "/fo", "LIST", "/v"]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        status["task_exists"] = result.returncode == 0
    except:
        pass
    
    return status

def run_now():
    """Run the scanner immediately."""
    import asyncio
    from tools.github_intelligence_scanner import main
    
    print("Running GitHub Intelligence Scanner immediately...")
    result = asyncio.run(main())
    
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump({
            "last_scan": datetime.now().isoformat(),
            "next_scan_due": (datetime.now() + timedelta(days=30)).isoformat()
        }, f, indent=2)
    
    return result

def main_menu():
    """Interactive menu for scheduler management."""
    print("=" * 60)
    print("Paradise Stack - GitHub Intelligence Scanner Scheduler")
    print("=" * 60)
    print()
    
    status = get_schedule_status()
    print(f"Task Scheduler Entry: {'Active' if status['task_exists'] else 'Not Set'}")
    print(f"Last Scan: {status['last_run'] or 'Never'}")
    print(f"Next Scan Due: {status['next_run'] or 'Not scheduled'}")
    print()
    
    print("Options:")
    print("  1. Schedule monthly scan (Task Scheduler)")
    print("  2. Remove scheduled scan")
    print("  3. Run scan now")
    print("  4. Check status")
    print("  5. Exit")
    print()
    
    choice = input("Select option (1-5): ").strip()
    
    if choice == "1":
        create_task_scheduler_entry()
    elif choice == "2":
        remove_task_scheduler_entry()
    elif choice == "3":
        run_now()
    elif choice == "4":
        print(json.dumps(status, indent=2))
    elif choice == "5":
        return
    else:
        print("Invalid option")
    
    main_menu()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        run_now()
    elif len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        create_task_scheduler_entry()
    elif len(sys.argv) > 1 and sys.argv[1] == "--remove":
        remove_task_scheduler_entry()
    else:
        main_menu()
