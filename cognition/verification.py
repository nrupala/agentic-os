#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
Paradise Verification System - Engineering Compliance Checks
Following strict verification principles from Recommended_Agent
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class VerificationResult:
    valid: bool
    message: str
    details: Optional[dict] = None


class VerificationEngine:
    """Core verification engine following Paradise Agent Policy"""
    
    ASSUMPTION_INDICATORS = [
        'assume', 'assuming', 'assumption', 'presume', 'presuming',
        'if we assume', 'given that', 'supposing', 'presuppose',
        'likely', 'probably', 'might be', 'could be'
    ]
    
    VERIFICATION_INDICATORS = [
        'test', 'verify', 'validation', 'assert', 'check',
        'confirm', 'validate', 'ensure', 'pytest', 'unittest',
        'should', 'must', 'expect', 'guard'
    ]
    
    FAILURE_INDICATORS = [
        'fail', 'error', 'exception', 'fault', 'bug', 'issue',
        'problem', 'risk', 'danger', 'edge case', 'what if',
        'handle error', 'catch exception', 'fallback', 'rollback'
    ]
    
    SAFETY_INDICATORS = [
        'safe', 'unsafe', 'security', 'vulnerability', 'sanitize',
        'escape', 'validate input', 'check bounds', 'null check',
        'type check', 'permission', 'authorization'
    ]
    
    @staticmethod
    def check_assumptions_stated(text: str) -> VerificationResult:
        """Check if assumptions are explicitly stated"""
        text_lower = text.lower()
        
        found = []
        for indicator in VerificationEngine.ASSUMPTION_INDICATORS:
            if indicator in text_lower:
                found.append(indicator)
        
        valid = len(found) > 0
        return VerificationResult(
            valid=valid,
            message="Assumptions appear to be explicitly stated" if valid 
                    else "WARNING: Assumptions should be explicitly stated per engineering guidelines",
            details={"found": found, "count": len(found)}
        )
    
    @staticmethod
    def check_verification_present(text: str) -> VerificationResult:
        """Check if verification mechanisms are mentioned"""
        text_lower = text.lower()
        
        found = []
        for indicator in VerificationEngine.VERIFICATION_INDICATORS:
            if indicator in text_lower:
                found.append(indicator)
        
        valid = len(found) > 0
        return VerificationResult(
            valid=valid,
            message="Verification mechanisms appear to be present" if valid
                    else "WARNING: Consider adding verification or testing mechanisms",
            details={"found": found, "count": len(found)}
        )
    
    @staticmethod
    def check_failure_modes(text: str) -> VerificationResult:
        """Check if failure modes are considered"""
        text_lower = text.lower()
        
        found = []
        for indicator in VerificationEngine.FAILURE_INDICATORS:
            if indicator in text_lower:
                found.append(indicator)
        
        valid = len(found) > 0
        return VerificationResult(
            valid=valid,
            message="Failure modes appear to be considered" if valid
                    else "WARNING: Consider potential failure modes and error handling",
            details={"found": found, "count": len(found)}
        )
    
    @staticmethod
    def check_safety_considered(text: str) -> VerificationResult:
        """Check if safety considerations are present"""
        text_lower = text.lower()
        
        found = []
        for indicator in VerificationEngine.SAFETY_INDICATORS:
            if indicator in text_lower:
                found.append(indicator)
        
        valid = len(found) > 0
        return VerificationResult(
            valid=valid,
            message="Safety considerations appear to be present" if valid
                    else "INFO: Safety considerations not detected (may not be required)",
            details={"found": found, "count": len(found)}
        )
    
    @staticmethod
    def verify_response(text: str) -> VerificationResult:
        """Comprehensive verification of a response"""
        checks = {
            "assumptions": VerificationEngine.check_assumptions_stated(text),
            "verification": VerificationEngine.check_verification_present(text),
            "failure_modes": VerificationEngine.check_failure_modes(text),
            "safety": VerificationEngine.check_safety_considered(text),
        }
        
        all_valid = all(c.valid for c in checks.values())
        warnings = [c.message for c in checks.values() if not c.valid and "WARNING" in c.message]
        
        return VerificationResult(
            valid=all_valid,
            message="Response meets all engineering guidelines" if all_valid else "; ".join(warnings),
            details={"checks": {k: {"valid": v.valid, "message": v.message} for k, v in checks.items()}}
        )
    
    @staticmethod
    def verify_code_file(filepath: str, content: str) -> VerificationResult:
        """Verify a code file meets standards"""
        issues = []
        
        if "except:" in content:
            issues.append("Bare except clause found - should catch specific exception")
        
        if "pass  # TODO" in content or "pass # TODO" in content:
            issues.append("TODO comment found - incomplete implementation")
        
        if re.search(r'print\s*\(\s*["\']', content) and "logging" not in content:
            issues.append("Print statement found - consider using logging instead")
        
        if "import *" in content:
            issues.append("Wildcard import found - be explicit with imports")
        
        if content.count("    ") < 2 and len(content.split('\n')) > 10:
            issues.append("Possible inconsistent indentation")
        
        valid = len(issues) == 0
        return VerificationResult(
            valid=valid,
            message="Code file passes quality checks" if valid else f"Issues found: {'; '.join(issues)}",
            details={"issues": issues}
        )
    
    @staticmethod
    def verify_plan(plan_text: str) -> VerificationResult:
        """Verify an implementation plan is complete"""
        checks = {
            "has_intent": "Intent" in plan_text or "Goal" in plan_text or "Objective" in plan_text,
            "has_constraints": "Constraint" in plan_text or "Limit" in plan_text,
            "has_assumptions": "Assumption" in plan_text or any(a in plan_text.lower() for a in ["assume", "given that"]),
            "has_steps": re.search(r"Step \d+", plan_text) is not None,
            "has_verification": "Test" in plan_text or "Verify" in plan_text or "Check" in plan_text,
            "has_failure_handling": any(w in plan_text.lower() for w in ["error", "fail", "exception", "handle"]),
        }
        
        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        
        return VerificationResult(
            valid=passed >= 4,
            message=f"Plan completeness: {passed}/{total} criteria met",
            details={"checks": checks, "score": passed / total}
        )


class PDCAVerifier:
    """PDCA Cycle Verification"""
    
    @staticmethod
    def verify_plan_phase(plan_output: str) -> VerificationResult:
        """Verify PLAN phase completion"""
        required = ["Intent", "Constraint", "Assumption"]
        found = [r for r in required if r in plan_output]
        
        return VerificationResult(
            valid=len(found) == len(required),
            message=f"PLAN phase: {len(found)}/{len(required)} required elements found",
            details={"required": required, "found": found}
        )
    
    @staticmethod
    def verify_do_phase(files_created: list) -> VerificationResult:
        """Verify DO phase completion"""
        if not files_created:
            return VerificationResult(
                valid=False,
                message="DO phase: No files were created",
                details={"files": []}
            )
        
        valid_files = [f for f in files_created if f.get("exists", False)]
        
        return VerificationResult(
            valid=len(valid_files) > 0,
            message=f"DO phase: {len(valid_files)}/{len(files_created)} files created",
            details={"total": len(files_created), "created": len(valid_files)}
        )
    
    @staticmethod
    def verify_check_phase(lint_output: str, test_output: str) -> VerificationResult:
        """Verify CHECK phase completion"""
        lint_pass = "error" not in lint_output.lower() or "0 errors" in lint_output.lower()
        test_pass = "passed" in test_output.lower() and "failed" not in test_output.lower()
        
        return VerificationResult(
            valid=lint_pass and test_pass,
            message=f"CHECK phase: Lint={'PASS' if lint_pass else 'FAIL'}, Tests={'PASS' if test_pass else 'FAIL'}",
            details={"lint_pass": lint_pass, "test_pass": test_pass}
        )
    
    @staticmethod
    def verify_act_phase(fixes_applied: int, issues_remaining: int) -> VerificationResult:
        """Verify ACT phase completion"""
        return VerificationResult(
            valid=issues_remaining == 0 or fixes_applied > 0,
            message=f"ACT phase: {fixes_applied} fixes applied, {issues_remaining} issues remaining",
            details={"fixes": fixes_applied, "remaining": issues_remaining}
        )


class LoopDetector:
    """Detect if system is stuck in a loop"""
    
    def __init__(self):
        self.history = []
        self.max_history = 10
    
    def record(self, action: str, result: str):
        self.history.append({
            "action": action,
            "result": result,
        })
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def is_stuck(self) -> bool:
        if len(self.history) < 5:
            return False
        
        recent = self.history[-5:]
        actions = [h["action"] for h in recent]
        results = [h["result"] for h in recent]
        
        if len(set(actions)) == 1 and len(set(results)) == 1:
            return True
        
        return False
    
    def get_status(self) -> dict:
        return {
            "stuck": self.is_stuck(),
            "history_length": len(self.history),
            "last_action": self.history[-1]["action"] if self.history else None,
            "last_result": self.history[-1]["result"] if self.history else None,
        }


def main():
    print("🔍 Paradise Verification Engine")
    print("=" * 40)
    
    verifier = VerificationEngine()
    PDCAVerifier()
    loop_detector = LoopDetector()
    
    test_text = """
    ASSUMPTIONS:
    - We assume the user wants a REST API
    - Given that we have a database available
    
    FAILURE HANDLING:
    - Handle connection errors with retry logic
    - Catch database exceptions and return 500
    
    VERIFICATION:
    - Tests should verify all endpoints
    - Assert response codes are correct
    """
    
    print("\n📋 Testing Response Verification:")
    result = verifier.verify_response(test_text)
    print(f"   Valid: {result.valid}")
    print(f"   Message: {result.message}")
    
    print("\n📊 Testing Loop Detection:")
    loop_detector.record("lint", "errors_found")
    loop_detector.record("fix", "fixed_1")
    loop_detector.record("lint", "errors_found")
    loop_detector.record("fix", "fixed_1")
    loop_detector.record("lint", "errors_found")
    status = loop_detector.get_status()
    print(f"   Stuck: {status['stuck']}")
    print(f"   Last action: {status['last_action']}")


if __name__ == "__main__":
    main()
