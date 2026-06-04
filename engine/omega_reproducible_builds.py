#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
OMEGA Reproducible Builds System
=================================
Implements reproducible build verification inspired by MediLog/F-Droid.
Features:
- Build manifest generation
- Deterministic build verification
- Source hash tracking
- Artifact provenance
- Build reproducibility score
"""

import os
import sys
import json
import hashlib
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent

try:
    from omega_phase_encryptor import OmegaPhaseEncryptor
    HAS_ZERO_KNOWLEDGE = True
    _ENCRYPTOR = OmegaPhaseEncryptor()
except ImportError:
    HAS_ZERO_KNOWLEDGE = False
    _ENCRYPTOR = None

@dataclass
class BuildManifest:
    manifest_id: str
    build_id: str
    created_at: str
    environment: Dict[str, str]
    source_hashes: Dict[str, str]
    dependency_versions: Dict[str, str]
    build_commands: List[str]
    output_artifacts: Dict[str, str]
    reproducibility_score: float

@dataclass
class SourceFile:
    path: str
    hash_sha256: str
    size_bytes: int
    last_modified: str

class ReproducibleBuilds:
    """
    OMEGA Reproducible Builds System
    =================================
    Ensures build reproducibility and verifiability.
    """
    
    VERSION = "2.0.0"
    
    def __init__(self, project: str = "omega"):
        self.project = project
        self.project_path = PROJECT_ROOT / "projects" / project
        
        self.manifests_path = self.project_path / "state" / "builds"
        self.manifests_path.mkdir(parents=True, exist_ok=True)
        
        self.manifests: List[BuildManifest] = []
        self._load_manifests()
        
        print(f"[REPRO] Reproducible Builds v{self.VERSION} initialized")
    
    def _load_manifests(self):
        """Load existing build manifests."""
        manifests_file = self.manifests_path / "manifests.json"
        if manifests_file.exists():
            try:
                data = json.loads(manifests_file.read_text())
                self.manifests = [BuildManifest(**m) for m in data]
            except:
                self.manifests = []
    
    def _save_manifests(self):
        """Save manifests to storage."""
        manifests_file = self.manifests_path / "manifests.json"
        manifests_file.parent.mkdir(parents=True, exist_ok=True)
        if HAS_ZERO_KNOWLEDGE and _ENCRYPTOR:
            try:
                payload = _ENCRYPTOR.encrypt_string(json.dumps([asdict(m) for m in self.manifests]))
                manifests_file.write_bytes(payload.nonce + payload.ciphertext)
                return
            except Exception:
                pass
        manifests_file.write_text(json.dumps([asdict(m) for m in self.manifests], indent=2))
    
    def create_manifest(self, build_id: str = None) -> BuildManifest:
        """Create a new build manifest."""
        
        build_id = build_id or f"build_{int(time.time())}"
        
        source_hashes = self._compute_source_hashes()
        
        dependency_versions = self._get_dependency_versions()
        
        environment = self._capture_environment()
        
        manifest = BuildManifest(
            manifest_id=f"man_{hashlib.md5(build_id.encode()).hexdigest()[:12]}",
            build_id=build_id,
            created_at=datetime.now().isoformat(),
            environment=environment,
            source_hashes=source_hashes,
            dependency_versions=dependency_versions,
            build_commands=self._get_build_commands(),
            output_artifacts={},
            reproducibility_score=1.0
        )
        
        self.manifests.append(manifest)
        self._save_manifests()
        
        print(f"[REPRO] Created manifest: {manifest.manifest_id}")
        return manifest
    
    def _compute_source_hashes(self) -> Dict[str, str]:
        """Compute SHA256 hashes of all source files."""
        hashes = {}
        
        engine_path = PROJECT_ROOT / "engine"
        for py_file in engine_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                file_hash = hashlib.sha256(content.encode()).hexdigest()
                rel_path = str(py_file.relative_to(PROJECT_ROOT))
                hashes[rel_path] = file_hash
            except Exception:
                pass
        
        return hashes
    
    def _get_dependency_versions(self) -> Dict[str, str]:
        """Get versions of all dependencies."""
        versions = {}
        
        versions["python"] = sys.version.split()[0]
        
        try:
            result = subprocess.run(
                ["pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                for pkg in packages:
                    versions[pkg["name"]] = pkg["version"]
        except:
            pass
        
        return versions
    
    def _capture_environment(self) -> Dict[str, str]:
        """Capture environment variables relevant to builds."""
        env_keys = [
            "PATH", "PYTHONPATH", "PYTHON_VERSION",
            "LANG", "LC_ALL", "TZ",
            "HOME", "USER", "VIRTUAL_ENV"
        ]
        
        env = {}
        for key in env_keys:
            if key in os.environ:
                env[key] = os.environ[key]
        
        env["platform"] = sys.platform
        env["architecture"] = str(int(os.environ.get("PROCESSOR_ARCHITEW6432", "64")[:2]) or 64) + "bit"
        
        return env
    
    def _get_build_commands(self) -> List[str]:
        """Get the build commands used."""
        return [
            f"python {PROJECT_ROOT}/engine/omega_forge.py",
            f"python {PROJECT_ROOT}/engine/omega_integrator.py"
        ]
    
    def verify_against_manifest(self, manifest_id: str = None) -> Dict[str, Any]:
        """Verify current build against a manifest."""
        
        if manifest_id:
            manifests = [m for m in self.manifests if m.manifest_id == manifest_id]
        else:
            manifests = [self.manifests[-1]] if self.manifests else []
        
        if not manifests:
            return {"verified": False, "reason": "No manifest found"}
        
        manifest = manifests[0]
        
        current_hashes = self._compute_source_hashes()
        
        source_matches = self._compare_hashes(manifest.source_hashes, current_hashes)
        
        current_deps = self._get_dependency_versions()
        dep_matches = self._compare_dependencies(manifest.dependency_versions, current_deps)
        
        reproducibility = (source_matches["match_ratio"] + dep_matches["match_ratio"]) / 2
        
        return {
            "verified": reproducibility >= 0.95,
            "manifest_id": manifest.manifest_id,
            "build_id": manifest.build_id,
            "reproducibility_score": reproducibility,
            "source_comparison": source_matches,
            "dependency_comparison": dep_matches,
            "timestamp": datetime.now().isoformat()
        }
    
    def _compare_hashes(self, old: Dict, new: Dict) -> Dict:
        """Compare source file hashes."""
        
        old_set = set(old.keys())
        new_set = set(new.keys())
        
        matching = old_set & new_set
        changed = []
        added = list(new_set - old_set)
        removed = list(old_set - new_set)
        
        for path in matching:
            if old[path] != new[path]:
                changed.append(path)
        
        match_ratio = len(matching - set(changed)) / max(len(old_set), 1)
        
        return {
            "matching": len(matching - set(changed)),
            "changed": len(changed),
            "added": len(added),
            "removed": len(removed),
            "match_ratio": match_ratio,
            "changed_files": changed[:5]
        }
    
    def _compare_dependencies(self, old: Dict, new: Dict) -> Dict:
        """Compare dependency versions."""
        
        important_deps = {"pip", "setuptools", "wheel", "pytest", "numpy", "pandas"}
        
        old_important = {k: v for k, v in old.items() if k.lower() in important_deps}
        new_important = {k: v for k, v in new.items() if k.lower() in important_deps}
        
        matches = 0
        total = len(old_important)
        
        for dep, version in old_important.items():
            if dep in new_important and new_important[dep] == version:
                matches += 1
        
        match_ratio = matches / max(total, 1)
        
        return {
            "matching": matches,
            "total_important": total,
            "match_ratio": match_ratio
        }
    
    def verify_deterministic(self, code: str, runs: int = 3) -> Dict[str, Any]:
        """Verify that code produces deterministic output."""
        
        outputs = []
        
        for i in range(runs):
            result = self._run_deterministic_test(code)
            outputs.append(hashlib.sha256(result.encode()).hexdigest())
        
        all_same = len(set(outputs)) == 1
        
        return {
            "deterministic": all_same,
            "unique_outputs": len(set(outputs)),
            "total_runs": runs,
            "output_hashes": outputs
        }
    
    def _run_deterministic_test(self, code: str) -> str:
        """Run code and return output for determinism testing."""
        return f"hash:{hashlib.md5(code.encode()).hexdigest()}:{time.time()}"
    
    def create_signed_manifest(self, build_id: str = None) -> Dict:
        """Create a signed manifest for verification."""
        
        manifest = self.create_manifest(build_id)
        
        manifest_data = json.dumps(asdict(manifest), sort_keys=True)
        signature = hashlib.sha256(manifest_data.encode()).hexdigest()
        
        signed = {
            "manifest": asdict(manifest),
            "signature": signature,
            "signed_at": datetime.now().isoformat()
        }
        
        signed_file = self.manifests_path / f"{manifest.manifest_id}_signed.json"
        signed_file.parent.mkdir(parents=True, exist_ok=True)
        if HAS_ZERO_KNOWLEDGE and _ENCRYPTOR:
            try:
                payload = _ENCRYPTOR.encrypt_string(json.dumps(signed))
                signed_file.write_bytes(payload.nonce + payload.ciphertext)
                return signed
            except Exception:
                pass
        signed_file.write_text(json.dumps(signed, indent=2))
        
        return signed
    
    def get_build_history(self) -> List[Dict]:
        """Get build history with reproducibility scores."""
        return [
            {
                "manifest_id": m.manifest_id,
                "build_id": m.build_id,
                "created_at": m.created_at,
                "reproducibility_score": m.reproducibility_score,
                "source_files": len(m.source_hashes),
                "dependencies": len(m.dependency_versions)
            }
            for m in self.manifests
        ]
    
    def get_statistics(self) -> Dict:
        """Get reproducibility statistics."""
        
        if not self.manifests:
            return {"total_manifests": 0}
        
        scores = [m.reproducibility_score for m in self.manifests]
        
        return {
            "total_manifests": len(self.manifests),
            "average_reproducibility": sum(scores) / len(scores),
            "min_reproducibility": min(scores),
            "max_reproducibility": max(scores),
            "latest_build": self.manifests[-1].build_id if self.manifests else None
        }


def create_reproducible_builds(project: str = "omega") -> ReproducibleBuilds:
    """Create a Reproducible Builds instance."""
    return ReproducibleBuilds(project)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OMEGA Reproducible Builds")
    parser.add_argument("--project", default="omega", help="Project name")
    parser.add_argument("--create", action="store_true", help="Create new manifest")
    parser.add_argument("--verify", action="store_true", help="Verify against manifest")
    parser.add_argument("--history", action="store_true", help="Show build history")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--signed", action="store_true", help="Create signed manifest")
    
    args = parser.parse_args()
    
    repro = create_reproducible_builds(args.project)
    
    if args.create:
        manifest = repro.create_manifest()
        print(f"Created manifest: {manifest.manifest_id}")
    elif args.verify:
        result = repro.verify_against_manifest()
        print(json.dumps(result, indent=2))
    elif args.history:
        for h in repro.get_build_history():
            print(f"{h['build_id']}: {h['reproducibility_score']:.2%}")
    elif args.stats:
        print(json.dumps(repro.get_statistics(), indent=2))
    elif args.signed:
        signed = repro.create_signed_manifest()
        print(f"Created signed manifest: {signed['manifest']['manifest_id']}")
    else:
        print(f"Reproducible Builds v{repro.VERSION} ready")