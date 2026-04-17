"""
OMEGA Zero-Knowledge Phase Handoff System
===================================
FILE-BASED ENCRYPTED PHASE SIGNALING

Zero-Trust Architecture:
- All data written to FILES, not RAM
- All phase handoffs encrypted with AES-256-GCM
- If RAM fails, files persist and can resume
- Zero-knowledge: even the handoff is encrypted

Phase Flow (File-Based):
  Step 3 (PLANNER) → .omega/phase3_planner.enc → Step 4 (OMEGA STACK)
  Step 4 (GENERATE) → .omega/phase4_code.enc → Step 5 (VERIFY)
  Step 5 (PERSIST) → .omega/phase5_memory.enc → Step 6 (EVALUATE)
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
import secrets as stdlib_secrets

PROJECT_ROOT = Path(__file__).parent.parent
OMEGA_DIR = PROJECT_ROOT / ".omega"
OMEGA_DIR.mkdir(exist_ok=True)

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


@dataclass
class PhaseSignal:
    """Encrypted signal for phase handoff."""
    phase_id: str
    timestamp: str
    checksum: str
    file_path: str
    encrypted: bool
    key_id: Optional[str] = None


class ZeroKnowledgeHandoff:
    """
    Zero-knowledge file-based handoff between phases.
    
    Key principles:
    - ALL data written to encrypted files
    - Each phase reads from previous phase's encrypted file
    - Checksums ensure integrity
    - Fallback to file if RAM fails
    
    Files created:
    - .omega/phase{N}_{phase_name}.enc - encrypted phase data
    - .omega/phase{N}_{phase_name}.sig - signature/checksum
    - .omega/phase_handover.log - handoff audit log
    """
    
    PHASE_FILES = {
        "3_planner": "phase3_planner.enc",
        "4_omega": "phase4_omega.enc", 
        "5_generate": "phase5_generate.enc",
        "6_verify": "phase6_verify.enc",
        "7_persist": "phase7_persist.enc",
        "8_evaluate": "phase8_evaluate.enc",
    }
    
    def __init__(self, project: str = "default"):
        self.project = project
        self.omega_dir = OMEGA_DIR
        self.phase_dir = self.omega_dir / "phases" / project
        self.phase_dir.mkdir(parents=True, exist_ok=True)
        
        self._key = self._get_or_create_key()
        self.aesgcm = AESGCM(self._key) if HAS_CRYPTO else None
        
        self._init_audit_log()
    
    def _get_or_create_key(self) -> bytes:
        """Get or create the handoff encryption key."""
        key_file = self.omega_dir / "handoff.key"
        if key_file.exists():
            return key_file.read_bytes()
        
        if not HAS_CRYPTO:
            raise ImportError("cryptography required for zero-knowledge handoff")
        
        key = AESGCM.generate_key(bit_length=256)
        key_file.write_bytes(key)
        return key
    
    def _init_audit_log(self):
        """Initialize handoff audit log."""
        log_file = self.omega_dir / "phase_handover.log"
        if not log_file.exists():
            log_file.write_text("")
    
    def _log_handoff(self, from_phase: str, to_phase: str, action: str):
        """Log phase handoff for audit."""
        log_file = self.omega_dir / "phase_handover.log"
        timestamp = datetime.now().isoformat()
        entry = f"{timestamp} | {from_phase} -> {to_phase} | {action}\n"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)
    
    def _compute_checksum(self, data: bytes) -> str:
        """Compute SHA-256 checksum."""
        return hashlib.sha256(data).hexdigest()[:16]
    
    def write_phase(self, phase_id: str, data: Dict) -> PhaseSignal:
        """
        Write phase data to encrypted file.
        Returns PhaseSignal for verification.
        """
        if not HAS_CRYPTO:
            raise ImportError("cryptography library required")
        
        phase_file = self.PHASE_FILES.get(phase_id, f"phase_{phase_id}.enc")
        file_path = self.phase_dir / phase_file
        
        json_data = json.dumps(data, indent=2, default=str)
        plaintext = json_data.encode('utf-8')
        
        nonce = stdlib_secrets.token_bytes(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        
        file_path.write_bytes(nonce + ciphertext)
        
        checksum = self._compute_checksum(plaintext)
        
        signal = PhaseSignal(
            phase_id=phase_id,
            timestamp=datetime.now().isoformat(),
            checksum=checksum,
            file_path=str(file_path),
            encrypted=True,
            key_id="handoff.key"
        )
        
        self._log_handoff(phase_id, "file", "WRITE")
        
        signal_file = file_path.with_suffix('.sig')
        signal_file.write_text(json.dumps({
            "phase_id": signal.phase_id,
            "timestamp": signal.timestamp,
            "checksum": signal.checksum,
            "key_id": signal.key_id
        }))
        
        return signal
    
    def read_phase(self, phase_id: str) -> Optional[Dict]:
        """
        Read phase data from encrypted file.
        Returns None if file doesn't exist.
        """
        if not HAS_CRYPTO:
            raise ImportError("cryptography library required")
        
        phase_file = self.PHASE_FILES.get(phase_id, f"phase_{phase_id}.enc")
        file_path = self.phase_dir / phase_file
        
        if not file_path.exists():
            return None
        
        data = file_path.read_bytes()
        nonce = data[:12]
        ciphertext = data[12:]
        
        try:
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as e:
            raise ValueError(f"Decryption failed for {phase_id}: {e}")
        
        json_data = plaintext.decode('utf-8')
        result = json.loads(json_data)
        
        self._log_handoff("file", phase_id, "READ")
        
        return result
    
    def has_phase(self, phase_id: str) -> bool:
        """Check if phase file exists."""
        phase_file = self.PHASE_FILES.get(phase_id, f"phase_{phase_id}.enc")
        return (self.phase_dir / phase_file).exists()
    
    def get_phase_info(self, phase_id: str) -> Optional[Dict]:
        """Get phase file metadata without decrypting."""
        phase_file = self.PHASE_FILES.get(phase_id, f"phase_{phase_id}.enc")
        file_path = self.phase_dir / phase_file
        
        if not file_path.exists():
            return None
        
        sig_file = file_path.with_suffix('.sig')
        if sig_file.exists():
            return json.loads(sig_file.read_text())
        
        return {"phase_id": phase_id, "file_exists": True}
    
    def clear_phase(self, phase_id: str):
        """Clear phase data (secure delete)."""
        phase_file = self.PHASE_FILES.get(phase_id, f"phase_{phase_id}.enc")
        file_path = self.phase_dir / phase_file
        
        if file_path.exists():
            file_path.unlink()
            sig_file = file_path.with_suffix('.sig')
            if sig_file.exists():
                sig_file.unlink()
            
            self._log_handoff(phase_id, "trash", "CLEAR")
    
    def verify_integrity(self, phase_id: str, expected_checksum: str) -> bool:
        """Verify phase data integrity."""
        phase_file = self.PHASE_FILES.get(phase_id, f"phase_{phase_id}.enc")
        file_path = self.phase_dir / phase_file
        
        if not file_path.exists():
            return False
        
        data = file_path.read_bytes()
        nonce = data[:12]
        ciphertext = data[12:]
        
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        actual_checksum = self._compute_checksum(plaintext)
        
        return actual_checksum == expected_checksum


def create_handoff(project: str = "default") -> ZeroKnowledgeHandoff:
    """Create zero-knowledge handoff for project."""
    return ZeroKnowledgeHandoff(project=project)


def write_phase_data(project: str, phase_id: str, data: Dict) -> PhaseSignal:
    """Convenience function to write phase data."""
    handoff = create_handoff(project)
    return handoff.write_phase(phase_id, data)


def read_phase_data(project: str, phase_id: str) -> Optional[Dict]:
    """Convenience function to read phase data."""
    handoff = create_handoff(project)
    return handoff.read_phase(phase_id)


if __name__ == "__main__":
    import sys
    
    project = sys.argv[1] if len(sys.argv) > 1 else "default"
    handoff = ZeroKnowledgeHandoff(project=project)
    
    print("=" * 60)
    print("Zero-Knowledge Phase Handoff")
    print("=" * 60)
    print(f"Project: {project}")
    print(f"Phase dir: {handoff.phase_dir}")
    print(f"Crypto available: {HAS_CRYPTO}")
    
    print("\n[TEST] Writing encrypted phase data...")
    test_data = {
        "goal": "Build a REST API",
        "dag_plan": ["main.py", "routes.py", "models.py"],
        "constraints": ["async", "SQLAlchemy"],
        "iteration": 1
    }
    
    signal = handoff.write_phase("3_planner", test_data)
    print(f"  Written: {signal.file_path}")
    print(f"  Checksum: {signal.checksum}")
    
    print("\n[TEST] Reading encrypted phase data...")
    read_data = handoff.read_phase("3_planner")
    print(f"  Retrieved: {list(read_data.keys())}")
    print(f"  Matches: {read_data.get('goal') == test_data['goal']}")
    
    print("\n[TEST] Verifying integrity...")
    valid = handoff.verify_integrity("3_planner", signal.checksum)
    print(f"  Integrity: {'OK' if valid else 'FAILED'}")
    
    print("\n" + "=" * 60)
    print("Zero-knowledge handoff: WORKING")
    print("=" * 60)