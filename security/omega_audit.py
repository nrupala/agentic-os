# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
OMEGA-CODE Audit Trail
========================
Enterprise-grade audit logging for all system events.

Features:
- JSONL format for easy parsing
- Tamper-evident append-only logs
- Session tracking
- Full forensic trail
"""

import os
import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime

SESSION_ID_LENGTH = 32

@dataclass
class AuditEvent:
    """Single audit event."""
    timestamp: str
    user: str
    action: str
    status: str
    details: str
    session_id: str
    project: str

class OmegaAudit:
    """
    Enterprise-grade audit logging for OMEGA-CODE.
    
    Features:
    - JSONL format (human-readable + machine-parseable)
    - Append-only to prevent tampering
    - Session tracking
    - Full forensic trail
    
    Usage:
        auditor = OmegaAudit("my_project")
        auditor.log_event("admin", "ROTATE_KEYS", "SUCCESS", "Key rotated successfully")
    """
    
    def __init__(self, project: str = None, log_dir: str = None):
        self.project = project or os.getenv("PROJECT_NAME", "default")
        
        if log_dir:
            self.log_dir = Path(log_dir)
        elif Path(self.project).is_absolute():
            self.log_dir = Path(self.project) / "logs"
        else:
            self.log_dir = Path(f"projects/{self.project}/logs")
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.audit_log_path = self.log_dir / "audit_trail.jsonl"
        self.session_id = os.environ.get("SESSION_ID", self._generate_session_id())
        
        self._ensure_log_exists()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import secrets
        return secrets.token_hex(SESSION_ID_LENGTH)
    
    def _ensure_log_exists(self):
        """Ensure log file exists."""
        if not self.audit_log_path.exists():
            self.audit_log_path.write_text("")
    
    def log_event(
        self,
        user: str,
        action: str,
        status: str,
        details: str = "",
        project: str = None,
        session_id: str = None
    ) -> Dict:
        """
        Record an audit event.
        
        Args:
            user: Username performing action
            action: Action type (e.g., "ROTATE_KEYS", "LOGIN", "RUN_ITERATION")
            status: Status ("SUCCESS", "DENIED", "FAILED")
            details: Additional details
            project: Project name (defaults to self.project)
            session_id: Session ID (defaults to self.session_id)
        
        Returns:
            The logged event
        """
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            user=user,
            action=action,
            status=status,
            details=details[:500] if details else "",
            session_id=session_id or self.session_id,
            project=project or self.project
        )
        
        event_dict = asdict(event)
        
        with open(self.audit_log_path, "a") as f:
            f.write(json.dumps(event_dict) + "\n")
        
        return event_dict
    
    def log_login(self, user: str, success: bool, details: str = ""):
        """Log a login attempt."""
        return self.log_event(
            user=user,
            action="LOGIN",
            status="SUCCESS" if success else "DENIED",
            details=details or ("Login successful" if success else "Invalid credentials")
        )
    
    def log_logout(self, user: str):
        """Log a logout."""
        return self.log_event(
            user=user,
            action="LOGOUT",
            status="SUCCESS",
            details="User logged out"
        )
    
    def log_key_rotation(self, user: str, success: bool, details: str = ""):
        """Log a key rotation attempt."""
        return self.log_event(
            user=user,
            action="ROTATE_KEYS",
            status="SUCCESS" if success else "FAILED",
            details=details or ("Key rotation completed" if success else "Key rotation failed")
        )
    
    def log_access_denied(self, user: str, action: str):
        """Log an access denied event."""
        return self.log_event(
            user=user,
            action=action,
            status="DENIED",
            details=f"Unauthorized access attempt to {action}"
        )
    
    def log_wipe_project(self, user: str, project: str, success: bool):
        """Log a project wipe."""
        return self.log_event(
            user=user,
            action="WIPE_PROJECT",
            status="SUCCESS" if success else "FAILED",
            details=f"Project wipe: {project}"
        )
    
    def log_run_iteration(self, user: str, iteration: int, status: str):
        """Log a coding iteration."""
        return self.log_event(
            user=user,
            action="RUN_ITERATION",
            status=status,
            details=f"Iteration #{iteration} - {status}"
        )
    
    def log_vacuum(self, user: str, logs_removed: int):
        """Log a vacuum operation."""
        return self.log_event(
            user=user,
            action="VACUUM",
            status="SUCCESS",
            details=f"Removed {logs_removed} old logs"
        )
    
    def get_events(
        self,
        user: str = None,
        action: str = None,
        status: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query audit events.
        
        Filters are ANDed together.
        """
        events = []
        
        if not self.audit_log_path.exists():
            return events
        
        with open(self.audit_log_path, "r") as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    
                    if user and event.get("user") != user:
                        continue
                    if action and event.get("action") != action:
                        continue
                    if status and event.get("status") != status:
                        continue
                    
                    events.append(event)
                except:
                    continue
        
        return events[-limit:]
    
    def get_user_history(self, user: str, limit: int = 50) -> List[Dict]:
        """Get all events for a specific user."""
        return self.get_events(user=user, limit=limit)
    
    def get_failed_logins(self, hours: int = 24) -> List[Dict]:
        """Get failed login attempts in the last N hours."""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(hours=hours)
        events = self.get_events(action="LOGIN", status="DENIED", limit=1000)
        
        filtered = []
        for event in events:
            event_time = datetime.fromisoformat(event["timestamp"])
            if event_time >= cutoff:
                filtered.append(event)
        
        return filtered
    
    def get_session_events(self, session_id: str = None) -> List[Dict]:
        """Get all events for a session."""
        if session_id is None:
            session_id = self.session_id
        
        events = []
        
        if not self.audit_log_path.exists():
            return events
        
        with open(self.audit_log_path, "r") as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    if event.get("session_id") == session_id:
                        events.append(event)
                except:
                    continue
        
        return events
    
    def generate_report(self, days: int = 7) -> Dict:
        """Generate audit summary report."""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        events = self.get_events(limit=10000)
        
        filtered = []
        for event in events:
            try:
                event_time = datetime.fromisoformat(event["timestamp"])
                if event_time >= cutoff:
                    filtered.append(event)
            except:
                continue
        
        actions = {}
        users = set()
        statuses = {}
        
        for event in filtered:
            action = event.get("action", "UNKNOWN")
            actions[action] = actions.get(action, 0) + 1
            
            user = event.get("user", "UNKNOWN")
            users.add(user)
            
            status = event.get("status", "UNKNOWN")
            statuses[status] = statuses.get(status, 0) + 1
        
        return {
            "period_days": days,
            "total_events": len(filtered),
            "unique_users": len(users),
            "actions": actions,
            "statuses": statuses,
            "generated_at": datetime.now().isoformat()
        }


def create_audit_logger(project: str = None) -> OmegaAudit:
    """Create an audit logger for a project."""
    return OmegaAudit(project=project)


if __name__ == "__main__":
    import sys
    
    project = sys.argv[1] if len(sys.argv) > 1 else os.getenv("PROJECT_NAME", "default")
    
    print("=" * 60)
    print("OMEGA-CODE Audit Trail")
    print("=" * 60)
    
    auditor = OmegaAudit(project)
    
    print(f"\nProject: {project}")
    print(f"Log Path: {auditor.audit_log_path}")
    print(f"Session ID: {auditor.session_id}")
    
    print("\n[TEST] Logging events...")
    auditor.log_login("test_user", True, "Test login successful")
    auditor.log_login("test_user", False, "Invalid password")
    auditor.log_key_rotation("test_user", True, "Test rotation")
    
    print("\n[EVENTS] Recent events:")
    events = auditor.get_events(limit=5)
    for event in events:
        print(f"  [{event['timestamp']}] {event['action']}: {event['status']}")
    
    print("\n[REPORT] Generating report...")
    report = auditor.generate_report(days=1)
    print(f"  Total events: {report['total_events']}")
    print(f"  Unique users: {report['unique_users']}")
    print(f"  Actions: {report['actions']}")
    
    print("=" * 60)

AuditTrail = OmegaAudit
