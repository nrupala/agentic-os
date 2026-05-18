import os
import json
from datetime import datetime

class OmegaAudit:
    """Enterprise-grade audit logging for OMEGA-CODE."""
    def __init__(self, project_path):
        self.audit_log_path = os.path.join(project_path, "logs", "audit_trail.jsonl")
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)

    def log_event(self, user, action, status, details=""):
        """Records a tamper-evident audit entry."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "action": action,
            "status": status,
            "details": details,
            "session_id": os.environ.get("SESSION_ID", "omega-default-session")
        }
        with open(self.audit_log_path, "a") as f:
            f.write(json.dumps(event) + "\n")

# Inside omega_access.py trigger_rotation
auditor = OmegaAudit(project_path)
if authorized:
    auditor.log_event(username, "ROTATE_KEYS", "SUCCESS")
    # Execute rotation...
else:
    auditor.log_event(username, "ROTATE_KEYS", "DENIED", "Unauthorized attempt")
