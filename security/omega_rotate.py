# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
OMEGA-CODE Key Rotation Engine
==============================
Automated 90-day AES-256 key rotation with re-encryption.

Features:
- Generate new key
- Re-encrypt all database entries
- Backup before rotation
- Cron job integration
"""

import os
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

ROTATION_DAYS = 90  # Rotate every 90 days
BACKUP_SUFFIX = ".backup"

class KeyRotation:
    """
    Handles automated AES-256 key rotation.
    
    Process:
    1. Backup current state
    2. Generate new key
    3. Re-encrypt all data
    4. Update key file
    """
    
    def __init__(self, project: str = None):
        self.project = project or os.getenv("PROJECT_NAME", "default")
        self.state_dir = Path(f"projects/{self.project}/state")
        self.db_path = self.state_dir / "omega_state.db"
        self.key_path = self.state_dir / "master.key"
        self.backup_dir = self.state_dir / "backups"
        
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def should_rotate(self) -> bool:
        """Check if key rotation is due."""
        if not self.key_path.exists():
            return True
        
        mtime = datetime.fromtimestamp(self.key_path.stat().st_mtime)
        age = datetime.now() - mtime
        
        return age.days >= ROTATION_DAYS
    
    def get_key_age_days(self) -> int:
        """Get age of current key in days."""
        if not self.key_path.exists():
            return ROTATION_DAYS + 1
        
        mtime = datetime.fromtimestamp(self.key_path.stat().st_mtime)
        age = datetime.now() - mtime
        return age.days
    
    def create_backup(self) -> Path:
        """Create timestamped backup before rotation."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"omega_state_backup_{timestamp}"
        
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        if self.db_path.exists():
            shutil.copy2(self.db_path, backup_path / "omega_state.db")
        
        if self.key_path.exists():
            shutil.copy2(self.key_path, backup_path / "master.key")
        
        return backup_path
    
    def load_key(self, key_path: Path) -> bytes:
        """Load encryption key."""
        with open(key_path, 'rb') as f:
            return f.read()
    
    def generate_new_key(self) -> bytes:
        """Generate a new AES-256 key."""
        if not HAS_CRYPTO:
            raise ImportError("cryptography library required")
        return AESGCM.generate_key(bit_length=256)
    
    def save_key(self, key: bytes):
        """Save new key to file."""
        self.key_path.write_bytes(key)
        self.key_path.chmod(0o600)
    
    def re_encrypt_data(self, old_key: bytes, new_key: bytes) -> int:
        """
        Re-encrypt all data in database with new key.
        Returns number of entries re-encrypted.
        """
        if not self.db_path.exists():
            return 0
        
        old_aes = AESGCM(old_key)
        new_aes = AESGCM(new_key)
        nonce_size = 12
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, logs FROM forge_state WHERE logs IS NOT NULL AND logs != ''")
        rows = cursor.fetchall()
        
        re_encrypted = 0
        
        for row_id, encrypted_data in rows:
            try:
                if isinstance(encrypted_data, str):
                    encrypted_data = bytes.fromhex(encrypted_data)
                
                nonce = encrypted_data[:nonce_size]
                ciphertext = encrypted_data[nonce_size:]
                
                plaintext = old_aes.decrypt(nonce, ciphertext, None)
                
                new_nonce = os.urandom(nonce_size)
                new_ciphertext = new_aes.encrypt(new_nonce, plaintext, None)
                
                new_encrypted = new_nonce + new_ciphertext
                
                cursor.execute(
                    "UPDATE forge_state SET logs = ? WHERE id = ?",
                    (new_encrypted.hex(), row_id)
                )
                re_encrypted += 1
                
            except Exception as e:
                print(f"[ROTATE] Failed to re-encrypt row {row_id}: {e}")
        
        conn.commit()
        conn.close()
        
        return re_encrypted
    
    def rotate(self) -> dict:
        """
        Perform key rotation.
        Returns rotation report.
        """
        print(f"[ROTATE] Starting key rotation for project: {self.project}")
        
        if not self.key_path.exists():
            raise FileNotFoundError("No existing key found")
        
        old_key = self.load_key(self.key_path)
        
        print("[ROTATE] Creating backup...")
        backup_path = self.create_backup()
        
        print("[ROTATE] Generating new key...")
        new_key = self.generate_new_key()
        
        print("[ROTATE] Re-encrypting data...")
        re_encrypted = self.re_encrypt_data(old_key, new_key)
        
        print("[ROTATE] Saving new key...")
        self.save_key(new_key)
        
        report = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "backup_path": str(backup_path),
            "entries_re_encrypted": re_encrypted,
            "key_age_days": 0
        }
        
        print(f"[ROTATE] Complete! {re_encrypted} entries re-encrypted")
        
        return report
    
    def cleanup_old_backups(self, keep: int = 5):
        """Remove old backups, keeping only the most recent."""
        backups = sorted(
            self.backup_dir.iterdir(),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        removed = 0
        for backup in backups[keep:]:
            shutil.rmtree(backup)
            removed += 1
        
        if removed:
            print(f"[ROTATE] Cleaned up {removed} old backups")
        
        return removed


def check_and_rotate(project: str = None) -> Optional[dict]:
    """
    Check if rotation needed, perform if due.
    """
    rotator = KeyRotation(project)
    
    age = rotator.get_key_age_days()
    print(f"[ROTATE] Key age: {age} days (rotation due at {ROTATION_DAYS})")
    
    if rotator.should_rotate():
        return rotator.rotate()
    
    print("[ROTATE] Rotation not due yet")
    return None


if __name__ == "__main__":
    import sys
    
    project = sys.argv[1] if len(sys.argv) > 1 else os.getenv("PROJECT_NAME", "default")
    force = "--force" in sys.argv
    
    print("=" * 60)
    print("OMEGA-CODE KEY ROTATION ENGINE")
    print("=" * 60)
    
    rotator = KeyRotation(project)
    
    if force or rotator.should_rotate():
        print(f"\n[INFO] Rotation required (key age: {rotator.get_key_age_days()} days)")
        
        try:
            report = rotator.rotate()
            
            print("\n--- ROTATION REPORT ---")
            print(f"Success: {report['success']}")
            print(f"Backup: {report['backup_path']}")
            print(f"Re-encrypted: {report['entries_re_encrypted']} entries")
            
        except Exception as e:
            print(f"\n[ERROR] Rotation failed: {e}")
            sys.exit(1)
    else:
        print(f"\n[INFO] Rotation not due (key age: {rotator.get_key_age_days()} days)")
        print(f"[INFO] Next rotation in {ROTATION_DAYS - rotator.get_key_age_days()} days")
    
    print("=" * 60)
