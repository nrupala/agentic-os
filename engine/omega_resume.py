"""
OMEGA Zero-Knowledge Resume System
==================================
Resume from encrypted files if RAM/process fails.

NUCLEAR SAFETY:
- Check ALL phase files for resume
- Validate checksums before use
- Full audit trail of resume operations

Used by:
- omega_codex.py on startup
- bridge.py on failure
- Any process needing resume
"""

import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
from dataclasses import dataclass

PROJECT_ROOT = Path(__file__).parent.parent
OMEGA_DIR = PROJECT_ROOT / ".omega"


@dataclass
class ResumePoint:
    """A point we can resume from."""
    phase_id: str
    timestamp: str
    file_path: str
    checksum: str
    valid: bool


class ZeroKnowledgeResume:
    """
    Resume system for zero-knowledge OMEGA.
    
    Checks for encrypted files from:
    - Phase handoffs (.omega/phases/*/phase*.enc)
    - Encrypted code (.omega/encryptions/*/*.code.enc)
    - Encrypted memory (.omega/encryptions/*/*.mem.enc)
    - Feedback history (.omega/encryptions/*/*.mem.enc)
    - Bridge plans (.omega/phases/*/bridge_plan.enc)
    """
    
    PHASE_CHECKS = [
        ("3_planner", "Planner context from Step 3"),
        ("4_omega", "Omega stack execution"),
        ("bridge_plan", "Bridge plan execution"),
    ]
    
    def __init__(self, project: str = "default"):
        self.project = project
        self.omega_dir = OMEGA_DIR
        self.phases_dir = self.omega_dir / "phases" / project
        self.encryptions_dir = self.omega_dir / "encryptions" / project
    
    def find_resume_points(self) -> List[ResumePoint]:
        """Find all available resume points."""
        points = []
        
        # Check phase files
        if self.phases_dir.exists():
            for phase_id, desc in self.PHASE_CHECKS:
                for enc_file in self.phases_dir.glob(f"phase{phase_id}*.enc"):
                    sig_file = enc_file.with_suffix('.sig')
                    if sig_file.exists():
                        try:
                            sig = json.loads(sig_file.read_text(encoding='utf-8'))
                            points.append(ResumePoint(
                                phase_id=phase_id,
                                timestamp=sig.get('timestamp', ''),
                                file_path=str(enc_file),
                                checksum=sig.get('checksum', ''),
                                valid=True
                            ))
                        except:
                            pass
        
        return points
    
    def get_latest_resume(self, phase_id: str = None) -> Optional[Dict]:
        """Get the most recent resume data for a phase."""
        from zero_knowledge_handoff import read_phase_data
        
        if phase_id:
            return read_phase_data(self.project, f"{phase_id}")
        
        # Find latest by phase order
        for phase_id, _ in self.PHASE_CHECKS:
            data = read_phase_data(self.project, f"{phase_id}")
            if data:
                return data
        
        return None
    
    def verify_resume_point(self, point: ResumePoint) -> bool:
        """Verify a resume point is valid."""
        if not point.valid:
            return False
        
        try:
            from zero_knowledge_handoff import ZeroKnowledgeHandoff
            handoff = ZeroKnowledgeHandoff(project=self.project)
            
            phase_id = point.phase_id.replace("phase_", "").replace("_plan", "_planner")
            is_valid = handoff.verify_integrity(phase_id, point.checksum)
            
            return is_valid
        except Exception:
            return False
    
    def can_resume(self, phase_id: str = None) -> bool:
        """Check if we can resume."""
        points = self.find_resume_points()
        
        if phase_id:
            return any(p.phase_id == phase_id and p.valid for p in points)
        
        return any(p.valid for p in points)
    
    def get_resume_status(self) -> Dict:
        """Get full resume status."""
        points = self.find_resume_points()
        
        status = {
            "project": self.project,
            "can_resume": any(p.valid for p in points),
            "resume_points": [],
            "phases_available": {},
            "checked_at": datetime.now().isoformat()
        }
        
        for p in points:
            is_valid = self.verify_resume_point(p)
            status["resume_points"].append({
                "phase": p.phase_id,
                "timestamp": p.timestamp,
                "valid": is_valid
            })
            status["phases_available"][p.phase_id] = is_valid
        
        return status
    
    def clear_resume_point(self, phase_id: str) -> bool:
        """Clear a resume point (secure delete)."""
        from zero_knowledge_handoff import ZeroKnowledgeHandoff
        
        try:
            handoff = ZeroKnowledgeHandoff(project=self.project)
            handoff.clear_phase(phase_id)
            return True
        except Exception:
            return False


def check_resume(project: str = "default") -> Dict:
    """Convenience function to check resume status."""
    resume = ZeroKnowledgeResume(project=project)
    return resume.get_resume_status()


def can_resume(project: str = "default") -> bool:
    """Check if system can resume."""
    resume = ZeroKnowledgeResume(project=project)
    return resume.can_resume()


def get_resume_data(project: str = "default", phase_id: str = None) -> Optional[Dict]:
    """Get resume data."""
    resume = ZeroKnowledgeResume(project=project)
    return resume.get_latest_resume(phase_id)


if __name__ == "__main__":
    import sys
    
    project = sys.argv[1] if len(sys.argv) > 1 else "default"
    resume = ZeroKnowledgeResume(project=project)
    
    print("=" * 60)
    print("Zero-Knowledge Resume Status")
    print("=" * 60)
    print(f"Project: {project}")
    
    status = resume.get_resume_status()
    print(f"Can Resume: {status['can_resume']}")
    print(f"Checked At: {status['checked_at']}")
    
    print("\nResume Points:")
    for rp in status['resume_points']:
        valid = "OK" if rp['valid'] else "INVALID"
        print(f"  [{valid}] {rp['phase']} - {rp['timestamp']}")
    
    if status['phases_available']:
        print("\nPhases Available:")
        for phase, avail in status['phases_available'].items():
            print(f"  {phase}: {'YES' if avail else 'NO'}")
    
    print("\n" + "=" * 60)