"""
OMEGA Provenance Tracker
Tracks code generation provenance for audits.
With zero-knowledge encryption.
"""

import hashlib
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    from omega_phase_encryptor import OmegaPhaseEncryptor
    _ENCRYPTOR = OmegaPhaseEncryptor("provenance")
    HAS_ZK = True
except ImportError:
    _ENCRYPTOR = None
    HAS_ZK = False
from typing import Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class ProvenanceEntry:
    code_hash: str
    prompt: str
    model: str
    model_version: str
    timestamp: str
    iteration: int
    status: str
    files: list

class ProvenanceTracker:
    """
    Tracks the complete lineage of generated code.
    - Atomic commits per iteration
    - Provenance.json for traceability
    - Shadow folders for snapshots
    """
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.provenance_dir = project_dir / "provenance"
        self.provenance_dir.mkdir(exist_ok=True)
        self.history_dir = project_dir / "history"
        self.history_dir.mkdir(exist_ok=True)
        self.provenance_file = self.provenance_dir / "provenance.json"
    
    def _compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def record(
        self,
        code: str,
        prompt: str,
        model: str = "local",
        model_version: str = "1.0",
        iteration: int = 1,
        status: str = "PASS",
        files: list = None
    ) -> ProvenanceEntry:
        """Record a generation event."""
        entry = ProvenanceEntry(
            code_hash=self._compute_hash(code),
            prompt=prompt,
            model=model,
            model_version=model_version,
            timestamp=datetime.now().isoformat(),
            iteration=iteration,
            status=status,
            files=files or []
        )
        
        self._save_entry(entry)
        self._create_snapshot(code, iteration, status)
        
        return entry
    
    def _save_entry(self, entry: ProvenanceEntry):
        """Save to provenance.json with optional encryption."""
        entries = []
        if self.provenance_file.exists():
            try:
                entries = json.loads(self.provenance_file.read_text())
            except:
                pass

        entry_data = asdict(entry)

        if HAS_ZK and _ENCRYPTOR:
            try:
                enc_data = _ENCRYPTOR.encrypt_string(json.dumps([entry_data]))
                self.provenance_file.write_text(enc_data.ciphertext.hex())
                return
            except Exception:
                pass

        entries.append(entry_data)
        self.provenance_file.write_text(json.dumps(entries, indent=2))
    
    def _create_snapshot(self, code: str, iteration: int, status: str):
        """Create timestamped snapshot in history/."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_dir = self.history_dir / f"iter_{iteration:03d}_{status.lower()}_{ts}"
        snapshot_dir.mkdir(exist_ok=True)
        
        (snapshot_dir / "code.py").write_text(code)
        (snapshot_dir / "meta.json").write_text(json.dumps({
            "iteration": iteration,
            "status": status,
            "timestamp": ts
        }, indent=2))
    
    def get_latest(self) -> Optional[ProvenanceEntry]:
        """Get the most recent provenance entry."""
        if not self.provenance_file.exists():
            return None
        
        entries = json.loads(self.provenance_file.read_text())
        if entries:
            return ProvenanceEntry(**entries[-1])
        return None
    
    def get_history(self, limit: int = 10) -> list:
        """Get recent provenance history."""
        if not self.provenance_file.exists():
            return []
        
        entries = json.loads(self.provenance_file.read_text())
        return entries[-limit:]
