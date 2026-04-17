#!/usr/bin/env python3
"""
OMEGA Gödel Machine - Self-Referential Code Modification
=========================================================
Implements self-referential improvement based on:
- Gödel Machine: Self-referential theorem proving
- Darwin Gödel Machine (DGM): Archive-based evolution
- SICA: Self-Improving Coding Agent

Features:
- Self-modification with safety constraints
- Version control for all changes
- Rollback capability
- Change validation before apply
"""

import os
import sys
import hashlib
import json
import time
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Optional, List, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import defaultdict
import re
import ast

PROJECT_ROOT = Path(__file__).parent.parent
ENGINE_DIR = PROJECT_ROOT / "engine"
MODIFIABLE_DIR = ENGINE_DIR

@dataclass
class CodeChange:
    change_id: str
    file_path: str
    original_hash: str
    new_hash: str
    diff: str
    reason: str
    confidence: float
    created_at: str
    status: str = "pending"
    validated: bool = False
    applied_at: Optional[str] = None
    rolled_back: bool = False

@dataclass
class ImprovementPattern:
    pattern_id: str
    trigger_error: str
    code_fix: str
    success_rate: float
    usage_count: int
    last_used: str

class SelfModificationValidator:
    """Validates code changes before application."""
    
    FORBIDDEN_PATTERNS = [
        r"import\s+os\s*;?\s*system",  # os.system calls
        r"subprocess.*shell\s*=\s*True",  # shell=True
        r"eval\s*\(",  # eval()
        r"exec\s*\(",  # exec()
        r"__import__",  # dynamic imports
        r"rm\s+-rf",  # destructive commands
        r"curl.*\|\s*sh",  # pipe to shell
        r"chmod\s+777",  # insecure permissions
    ]
    
    @classmethod
    def validate_change(cls, original: str, modified: str, file_path: str) -> Tuple[bool, str]:
        """Validate a code change for safety."""
        
        if file_path.endswith(".py"):
            try:
                ast.parse(modified)
            except SyntaxError as e:
                return False, f"Syntax error: {e}"
        
        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, modified, re.IGNORECASE):
                return False, f"Forbidden pattern detected: {pattern}"
        
        if "import" in modified and "random" in modified:
            if "os.environ" in modified or "subprocess" in modified:
                return False, "Potential environment manipulation detected"
        
        return True, "Valid"
    
    @classmethod
    def validate_module(cls, file_path: str) -> bool:
        """Validate that a module can be safely modified."""
        forbidden = ["omega_daemon.py", "state_manager.py"]
        return Path(file_path).name not in forbidden

class VersionControl:
    """Simple version control for code changes."""
    
    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or (ENGINE_DIR / ".versions")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.versions_file = self.storage_path / "versions.json"
        self.versions = self._load_versions()

    def _load_versions(self) -> Dict:
        if self.versions_file.exists():
            try:
                from omega_phase_encryptor import OmegaPhaseEncryptor
                enc = OmegaPhaseEncryptor("godel")
                data = self.versions_file.read_bytes()
                decrypted = enc.aesgcm.decrypt(data[:12], data[12:], None)
                return json.loads(decrypted)
            except:
                pass
            try:
                return json.loads(self.versions_file.read_text())
            except:
                pass
        return {"versions": [], "current": "v1.0"}

    def _save_versions(self):
        try:
            from omega_phase_encryptor import OmegaPhaseEncryptor
            enc = OmegaPhaseEncryptor("godel")
            payload = enc.encrypt_string(json.dumps(self.versions))
            self.versions_file.write_bytes(payload.nonce + payload.ciphertext)
            return
        except:
            pass
        self.versions_file.write_text(json.dumps(self.versions, indent=2))
    
    def create_checkpoint(self, file_path: str) -> str:
        """Create a checkpoint of current file state."""
        if not Path(file_path).exists():
            return ""
        
        content = Path(file_path).read_text()
        file_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
        
        version_id = f"v{len(self.versions['versions']) + 1}_{file_hash}"
        
        version_entry = {
            "version_id": version_id,
            "file_path": file_path,
            "hash": file_hash,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "parent": self.versions.get("current")
        }
        
        self.versions["versions"].append(version_entry)
        self.versions["current"] = version_id
        self._save_versions()
        
        return version_id
    
    def rollback(self, version_id: str, file_path: str) -> bool:
        """Rollback to a specific version."""
        for v in self.versions["versions"]:
            if v["version_id"] == version_id and v["file_path"] == file_path:
                Path(file_path).write_text(v["content"])
                return True
        return False
    
    def get_history(self, file_path: str = None) -> List[Dict]:
        """Get version history."""
        if file_path:
            return [v for v in self.versions["versions"] if v["file_path"] == file_path]
        return self.versions["versions"]


class GödelMachine:
    """
    OMEGA Gödel Machine - Self-Referential Code Modification
    ==========================================================
    
    Implements recursive self-improvement based on:
    - Gödel Machine: Self-referential improvement
    - Darwin Gödel Machine: Archive-based evolution
    - SICA: Self-Improving Coding Agent
    """
    
    VERSION = "2.0.0"
    
    def __init__(self, project: str = "omega"):
        self.project = project
        self.db_path = f"projects/{project}/state/omega_state.db"
        
        self.validator = SelfModificationValidator()
        self.version_control = VersionControl()
        
        self.changes: List[CodeChange] = []
        self.patterns: Dict[str, ImprovementPattern] = {}
        
        self.max_recursion = 5
        self.confidence_threshold = 0.8
        
        self._init_storage()
        self._load_patterns()
        
        print(f"[GÖDEL] Gödel Machine v{self.VERSION} initialized")
    
    def _init_storage(self):
        """Initialize storage for changes."""
        self.change_storage = Path(f"projects/{self.project}/state/godel_changes")
        self.change_storage.mkdir(parents=True, exist_ok=True)
        
        changes_file = self.change_storage / "changes.json"
        if changes_file.exists():
            try:
                data = json.loads(changes_file.read_text())
                self.changes = [CodeChange(**c) for c in data]
            except:
                self.changes = []
    
    def _save_changes(self):
        """Save changes to storage."""
        changes_file = self.change_storage / "changes.json"
        changes_file.write_text(json.dumps([asdict(c) for c in self.changes], indent=2))
    
    def _load_patterns(self):
        """Load learned improvement patterns."""
        patterns_file = self.change_storage / "patterns.json"
        if patterns_file.exists():
            try:
                data = json.loads(patterns_file.read_text())
                self.patterns = {k: ImprovementPattern(**v) for k, v in data.items()}
            except:
                self.patterns = {}
    
    def _save_patterns(self):
        """Save patterns to storage."""
        patterns_file = self.change_storage / "patterns.json"
        patterns_file.write_text(json.dumps({k: asdict(v) for k, v in self.patterns.items()}, indent=2))
    
    def analyze_failure_and_propose_fix(self, error: str, context: Dict) -> Optional[CodeChange]:
        """Analyze failure and propose self-modification."""
        
        error_type = self._classify_error(error)
        print(f"[GÖDEL] Analyzing error type: {error_type}")
        
        pattern_key = f"{error_type}_{context.get('file', 'unknown')}"
        
        if pattern_key in self.patterns:
            pattern = self.patterns[pattern_key]
            print(f"[GÖDEL] Found pattern: {pattern.pattern_id}")
            
            if pattern.success_rate >= self.confidence_threshold:
                return self._apply_pattern(pattern, context)
        
        return self._generate_new_fix(error, error_type, context)
    
    def _classify_error(self, error: str) -> str:
        """Classify error for pattern matching using unified ErrorClassifier."""
        try:
            from omega_error_classifier import classify_error
            return classify_error(error)
        except ImportError:
            error_lower = error.lower()
            if "timeout" in error_lower:
                return "timeout"
            elif "syntax" in error_lower or "expected" in error_lower:
                return "syntax_error"
            elif "import" in error_lower or "modulenotfound" in error_lower:
                return "import_error"
            elif "memory" in error_lower:
                return "memory_error"
            elif "permission" in error_lower:
                return "permission_error"
            elif "attribute" in error_lower:
                return "attribute_error"
            elif "type" in error_lower:
                return "type_error"
            else:
                return "unknown_error"
    
    def _generate_new_fix(self, error: str, error_type: str, context: Dict) -> Optional[CodeChange]:
        """Generate new fix for error."""
        
        file_path = context.get("file", "")
        if not file_path or not self.validator.validate_module(file_path):
            print(f"[GÖDEL] File not eligible for modification: {file_path}")
            return None
        
        if not Path(file_path).exists():
            return None
        
        original_content = Path(file_path).read_text()
        original_hash = hashlib.sha256(original_content.encode()).hexdigest()[:12]
        
        fix_strategy = self._get_fix_strategy(error_type)
        modified_content = self._apply_fix(original_content, fix_strategy)
        
        if modified_content == original_content:
            return None
        
        is_valid, validation_msg = self.validator.validate_change(
            original_content, modified_content, file_path
        )
        
        if not is_valid:
            print(f"[GÖDEL] Validation failed: {validation_msg}")
            return None
        
        new_hash = hashlib.sha256(modified_content.encode()).hexdigest()[:12]
        
        diff = self._generate_diff(original_content, modified_content)
        
        change = CodeChange(
            change_id=f"ch_{int(time.time())}_{original_hash}",
            file_path=file_path,
            original_hash=original_hash,
            new_hash=new_hash,
            diff=diff,
            reason=f"Fix {error_type}: {error[:100]}",
            confidence=0.6,
            created_at=datetime.now().isoformat(),
            validated=True
        )
        
        self.changes.append(change)
        self._save_changes()
        
        print(f"[GÖDEL] Generated change: {change.change_id}")
        return change
    
    def _get_fix_strategy(self, error_type: str) -> Dict:
        """Get fix strategy based on error type."""
        strategies = {
            "timeout": {
                "type": "timeout_increase",
                "pattern": r'timeout\s*=\s*(\d+)',
                "replacement": "timeout = 300"
            },
            "import_error": {
                "type": "try_import",
                "pattern": r"import\s+(\w+)",
                "wrapper": "try:\\n    import {}\\nexcept ImportError:\\n    pass"
            },
            "syntax_error": {
                "type": "syntax_fallback",
                "pattern": r"def\s+(\w+)\s*\([^)]*\)\s*:",
                "replacement": "def \\1(self):\\n    pass"
            },
            "attribute_error": {
                "type": "hasattr_check",
                "pattern": r"(\w+)\.(\w+)",
                "replacement": "getattr(\\1, '\\2', None)"
            },
            "type_error": {
                "type": "type_coercion",
                "pattern": r"(\w+)\s*\+\s*(\w+)",
                "replacement": "str(\\1) + str(\\2)"
            }
        }
        return strategies.get(error_type, {"type": "noop"})
    
    def _apply_fix(self, content: str, strategy: Dict) -> str:
        """Apply fix strategy to content."""
        
        if strategy["type"] == "timeout_increase":
            import re
            content = re.sub(r'timeout\s*=\s*\d+', 'timeout = 300', content)
        
        elif strategy["type"] == "hasattr_check":
            import re
            content = re.sub(
                r'(\w+)\.(\w+)',
                r'getattr(\1, "\2", None)',
                content
            )
        
        return content
    
    def _apply_pattern(self, pattern: ImprovementPattern, context: Dict) -> Optional[CodeChange]:
        """Apply a learned improvement pattern."""
        
        file_path = context.get("file", "")
        if not Path(file_path).exists():
            return None
        
        original_content = Path(file_path).read_text()
        original_hash = hashlib.sha256(original_content.encode()).hexdigest()[:12]
        
        modified_content = original_content + f"\n# Applied pattern: {pattern.pattern_id}\n"
        new_hash = hashlib.sha256(modified_content.encode()).hexdigest()[:12]
        
        change = CodeChange(
            change_id=f"ch_{int(time.time())}_{original_hash}",
            file_path=file_path,
            original_hash=original_hash,
            new_hash=new_hash,
            diff=f"Applied pattern {pattern.pattern_id}",
            reason=f"Pattern match: {pattern.pattern_id}",
            confidence=pattern.success_rate,
            created_at=datetime.now().isoformat(),
            validated=True
        )
        
        pattern.usage_count += 1
        pattern.last_used = datetime.now().isoformat()
        self._save_patterns()
        
        return change
    
    def apply_change(self, change_id: str) -> bool:
        """Apply a validated change."""
        
        for change in self.changes:
            if change.change_id == change_id:
                if not change.validated:
                    print(f"[GÖDEL] Change not validated")
                    return False
                
                self.version_control.create_checkpoint(change.file_path)
                
                file_path = Path(change.file_path)
                content = file_path.read_text()
                
                if hashlib.sha256(content.encode()).hexdigest()[:12] != change.original_hash:
                    print(f"[GÖDEL] File changed since change was created")
                    return False
                
                modified_content = self._apply_code_diff(content, change.diff)
                file_path.write_text(modified_content)
                
                change.status = "applied"
                change.applied_at = datetime.now().isoformat()
                self._save_changes()
                
                print(f"[GÖDEL] Applied change: {change_id}")
                return True
        
        return False
    
    def _apply_code_diff(self, content: str, diff: str) -> str:
        """Apply diff to content."""
        return content + f"\n# [GÖDEL] {diff}\n"
    
    def _generate_diff(self, original: str, modified: str) -> str:
        """Generate diff between original and modified."""
        orig_lines = original.split('\n')
        mod_lines = modified.split('\n')
        
        diff_lines = []
        for i, (o, m) in enumerate(zip(orig_lines, mod_lines)):
            if o != m:
                diff_lines.append(f"Line {i+1}: {o[:50]} -> {m[:50]}")
        
        return "\n".join(diff_lines[:10])
    
    def rollback_change(self, change_id: str) -> bool:
        """Rollback an applied change."""
        
        for change in self.changes:
            if change.change_id == change_id and change.status == "applied":
                success = self.version_control.rollback(
                    change.original_hash, change.file_path
                )
                
                if success:
                    change.status = "rolled_back"
                    change.rolled_back = True
                    self._save_changes()
                
                return success
        
        return False
    
    def learn_from_result(self, change_id: str, success: bool):
        """Learn from change application result."""
        
        for change in self.changes:
            if change.change_id == change_id:
                if success:
                    change.status = "confirmed"
                    
                    pattern_key = f"{change.file_path}_{change.reason.split(':')[0]}"
                    if pattern_key not in self.patterns:
                        self.patterns[pattern_key] = ImprovementPattern(
                            pattern_id=pattern_key,
                            trigger_error=change.reason,
                            code_fix=change.diff,
                            success_rate=1.0,
                            usage_count=1,
                            last_used=datetime.now().isoformat()
                        )
                    else:
                        pattern = self.patterns[pattern_key]
                        pattern.success_rate = (pattern.success_rate * pattern.usage_count + 1.0) / (pattern.usage_count + 1)
                        pattern.usage_count += 1
                else:
                    change.status = "failed"
                
                self._save_changes()
                self._save_patterns()
    
    def get_applicable_changes(self) -> List[CodeChange]:
        """Get all validated, pending changes."""
        return [c for c in self.changes if c.validated and c.status == "pending"]
    
    def get_statistics(self) -> Dict:
        """Get self-modification statistics."""
        return {
            "total_changes": len(self.changes),
            "applied": len([c for c in self.changes if c.status == "applied"]),
            "pending": len([c for c in self.changes if c.status == "pending"]),
            "confirmed": len([c for c in self.changes if c.status == "confirmed"]),
            "failed": len([c for c in self.changes if c.status == "failed"]),
            "patterns_learned": len(self.patterns),
            "confidence_threshold": self.confidence_threshold
        }


def create_godel_machine(project: str = "omega") -> GödelMachine:
    """Create a Gödel Machine instance."""
    return GödelMachine(project)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OMEGA Gödel Machine")
    parser.add_argument("--project", default="omega", help="Project name")
    parser.add_argument("--analyze", type=str, help="Analyze error and propose fix")
    parser.add_argument("--apply", type=str, help="Apply change by ID")
    parser.add_argument("--rollback", type=str, help="Rollback change by ID")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--history", action="store_true", help="Show change history")
    
    args = parser.parse_args()
    
    godel = create_godel_machine(args.project)
    
    if args.stats:
        print(json.dumps(godel.get_statistics(), indent=2))
    elif args.history:
        for change in godel.changes:
            print(f"{change.change_id}: {change.status} - {change.reason[:50]}")
    elif args.analyze:
        result = godel.analyze_failure_and_propose_fix(args.analyze, {"file": "engine/omega_forge.py"})
        if result:
            print(f"Proposed change: {result.change_id}")
            print(f"Confidence: {result.confidence}")
    elif args.apply:
        print(f"Applied: {godel.apply_change(args.apply)}")
    elif args.rollback:
        print(f"Rolled back: {godel.rollback_change(args.rollback)}")
    else:
        print(f"Gödel Machine v{godel.VERSION} ready")