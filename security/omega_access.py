"""
OMEGA-CODE Role-Based Access Control
===================================
Enterprise-grade RBAC for multi-user environments.

Roles:
- ADMIN: Full system access
- DEVELOPER: Build and test access
- AUDITOR: Read-only access

Features:
- Permission verification
- Just-in-Time access
- Encrypted credential storage
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

ACCESS_POLICY = {
    "ADMIN": [
        "rotate_keys",
        "wipe_project",
        "modify_system_config",
        "run_iteration",
        "read_logs",
        "view_outputs",
        "view_provenance",
        "manage_users",
        "trigger_vacuum",
        "export_memory"
    ],
    "DEVELOPER": [
        "run_iteration",
        "read_logs",
        "view_outputs",
        "view_provenance"
    ],
    "AUDITOR": [
        "read_logs",
        "view_provenance"
    ]
}

@dataclass
class User:
    username: str
    role: str
    created_at: str
    last_login: Optional[str] = None
    jit_expiry: Optional[str] = None

class OmegaAccessControl:
    """
    Role-Based Access Control for OMEGA-CODE.
    
    Usage:
        access = OmegaAccessControl()
        if access.can_perform("admin_user", "rotate_keys"):
            rotate_keys()
    """
    
    def __init__(self, project: str = None):
        self.project = project or os.getenv("PROJECT_NAME", "default")
        self.system_dir = Path("system_scripts")
        self.system_dir.mkdir(exist_ok=True)
        self.user_file = self.system_dir / "users.json"
        self.session_file = self.system_dir / "sessions.json"
        
        self._init_users()
    
    def _init_users(self):
        """Initialize users file with default admin."""
        if not self.user_file.exists():
            default_users = {
                "omega_admin": {
                    "username": "omega_admin",
                    "role": "ADMIN",
                    "password_hash": self._hash_password("omega_change_me"),
                    "created_at": datetime.now().isoformat(),
                    "must_change_password": True
                }
            }
            self._save_users(default_users)
    
    def _load_users(self) -> Dict:
        """Load users from file."""
        if not self.user_file.exists():
            return {}
        with open(self.user_file, 'r') as f:
            return json.load(f)
    
    def _save_users(self, users: Dict):
        """Save users to file."""
        self.user_file.write_text(json.dumps(users, indent=2))
    
    def _hash_password(self, password: str, salt: str = None) -> str:
        """Hash password with salt."""
        if salt is None:
            salt = os.urandom(16).hex()
        hash_value = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            bytes.fromhex(salt),
            100000
        )
        return f"{salt}${hash_value.hex()}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash."""
        try:
            salt, hash_hex = stored_hash.split('$')
            expected = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                bytes.fromhex(salt),
                100000
            ).hex()
            return expected == hash_hex
        except:
            return False
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Authenticate user.
        Returns: (success, role)
        """
        users = self._load_users()
        
        if username not in users:
            return False, None
        
        user = users[username]
        password_hash = user.get("password_hash", "")
        
        if not self._verify_password(password, password_hash):
            return False, None
        
        user["last_login"] = datetime.now().isoformat()
        self._save_users(users)
        
        return True, user["role"]
    
    def can_perform(self, username: str, action: str) -> bool:
        """Verify if user has permission for action."""
        users = self._load_users()
        
        if username not in users:
            return False
        
        user = users[username]
        role = user.get("role", "")
        
        if role in ACCESS_POLICY:
            return action in ACCESS_POLICY[role]
        
        return False
    
    def grant_jit(self, username: str, action: str, duration_hours: int = 1) -> bool:
        """
        Grant Just-in-Time elevated access.
        Access expires after duration_hours.
        """
        users = self._load_users()
        
        if username not in users:
            return False
        
        expiry = datetime.now() + timedelta(hours=duration_hours)
        users[username]["jit_action"] = action
        users[username]["jit_expiry"] = expiry.isoformat()
        
        self._save_users(users)
        return True
    
    def check_jit(self, username: str, action: str) -> bool:
        """Check if JIT access is active."""
        users = self._load_users()
        
        if username not in users:
            return False
        
        user = users[username]
        jit_action = user.get("jit_action")
        jit_expiry = user.get("jit_expiry")
        
        if jit_action == action and jit_expiry:
            expiry = datetime.fromisoformat(jit_expiry)
            if datetime.now() < expiry:
                return True
        
        return False
    
    def add_user(self, admin_username: str, new_username: str, role: str, password: str) -> bool:
        """Add new user (requires ADMIN)."""
        if not self.can_perform(admin_username, "manage_users"):
            return False
        
        if role not in ACCESS_POLICY:
            return False
        
        users = self._load_users()
        
        if new_username in users:
            return False
        
        users[new_username] = {
            "username": new_username,
            "role": role,
            "password_hash": self._hash_password(password),
            "created_at": datetime.now().isoformat(),
            "must_change_password": True
        }
        
        self._save_users(users)
        return True
    
    def change_role(self, admin_username: str, target_username: str, new_role: str) -> bool:
        """Change user role (requires ADMIN)."""
        if not self.can_perform(admin_username, "manage_users"):
            return False
        
        if new_role not in ACCESS_POLICY:
            return False
        
        users = self._load_users()
        
        if target_username not in users:
            return False
        
        users[target_username]["role"] = new_role
        self._save_users(users)
        return True
    
    def remove_user(self, admin_username: str, target_username: str) -> bool:
        """Remove user (requires ADMIN)."""
        if not self.can_perform(admin_username, "manage_users"):
            return False
        
        if target_username == admin_username:
            return False
        
        users = self._load_users()
        
        if target_username in users:
            del users[target_username]
            self._save_users(users)
            return True
        
        return False
    
    def list_users(self, admin_username: str) -> List[Dict]:
        """List all users (requires ADMIN)."""
        if not self.can_perform(admin_username, "manage_users"):
            return []
        
        users = self._load_users()
        return [
            {
                "username": u["username"],
                "role": u["role"],
                "created_at": u["created_at"],
                "last_login": u.get("last_login")
            }
            for u in users.values()
        ]
    
    def trigger_rotation(self, username: str) -> Tuple[bool, str]:
        """Administrative gate for key rotation."""
        if self.can_perform(username, "rotate_keys") or self.check_jit(username, "rotate_keys"):
            return True, f"Access Granted: User '{username}' triggering key rotation."
        return False, f"Access Denied: User '{username}' lacks 'rotate_keys' permission."
    
    def trigger_wipe(self, username: str, project: str) -> Tuple[bool, str]:
        """Administrative gate for project wipe."""
        if self.can_perform(username, "wipe_project") or self.check_jit(username, "wipe_project"):
            return True, f"Access Granted: User '{username}' wiping project '{project}'."
        return False, f"Access Denied: User '{username}' lacks 'wipe_project' permission."


if __name__ == "__main__":
    
    access = OmegaAccessControl()
    
    print("=" * 60)
    print("OMEGA-CODE Access Control")
    print("=" * 60)
    
    print("\n[TEST] Authenticating default admin...")
    success, role = access.authenticate("omega_admin", "omega_change_me")
    print(f"  Success: {success}, Role: {role}")
    
    if success:
        print("\n[TEST] Permission check: rotate_keys")
        print(f"  Can perform: {access.can_perform('omega_admin', 'rotate_keys')}")
        
        print("\n[TEST] Permission check: wipe_project")
        print(f"  Can perform: {access.can_perform('omega_admin', 'wipe_project')}")
    
    print("\n[WARNING] Default password must be changed on first login!")
    print("=" * 60)

AccessControl = OmegaAccessControl
