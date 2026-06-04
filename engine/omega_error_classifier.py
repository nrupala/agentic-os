#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
OMEGA Error Classification - Unified Error Handling
===================================================
Centralized error classification used by:
- omega_forge.py
- omega_meta_logic.py  
- omega_meta_learner.py
- omega_godel_machine.py
- omega_feedback_loop.py

This ensures CONSISTENT error classification across the entire system.
"""

from typing import Dict, List
from enum import Enum

class ErrorCategory(Enum):
    """Unified error categories."""
    TIMEOUT = "timeout"
    SYNTAX_ERROR = "syntax_error"
    IMPORT_ERROR = "import_error"
    MEMORY = "memory"
    NETWORK = "network"
    PERMISSION = "permission"
    TYPE_ERROR = "type_error"
    VALUE_ERROR = "value_error"
    RUNTIME_ERROR = "runtime_error"
    ASSERTION_ERROR = "assertion_error"
    NOT_IMPLEMENTED = "not_implemented"
    CHILD_PROCESS = "child_process"
    UNKNOWN = "unknown"

class ErrorClassifier:
    """
    Unified error classification system.
    All OMEGA components should use this class.
    """
    
    # Error keywords mapping
    KEYWORDS: Dict[ErrorCategory, List[str]] = {
        ErrorCategory.TIMEOUT: ["timeout", "timed out", "deadline exceeded"],
        ErrorCategory.SYNTAX_ERROR: ["syntax", "parse error", "expected", "invalid syntax"],
        ErrorCategory.IMPORT_ERROR: ["import", "modulenotfound", "no module", "cannot import"],
        ErrorCategory.MEMORY: ["memory", "out of memory", "oom", "allocation"],
        ErrorCategory.NETWORK: ["connection", "network", "refused", "timeout", "dns"],
        ErrorCategory.PERMISSION: ["permission", "access denied", "unauthorized", "forbidden"],
        ErrorCategory.TYPE_ERROR: ["type error", "type mismatch", "not a function"],
        ErrorCategory.VALUE_ERROR: ["value error", "invalid value", "invalid argument"],
        ErrorCategory.RUNTIME_ERROR: ["runtime", "execution", "failed", "error"],
        ErrorCategory.ASSERTION_ERROR: ["assertion", "assert failed"],
        ErrorCategory.NOT_IMPLEMENTED: ["not implemented", "abstract"],
        ErrorCategory.CHILD_PROCESS: ["subprocess", "spawn", "child", "fork"],
    }
    
    # Error to constraint mapping
    ERROR_TO_CONSTRAINT: Dict[str, str] = {
        "timeout": "Add timeout handling and retry logic",
        "syntax_error": "Fix syntax and parsing issues",
        "import_error": "Ensure all dependencies are installed",
        "memory": "Add memory management and cleanup",
        "network": "Add network error handling and retry",
        "permission": "Check file permissions and access rights",
        "type_error": "Add proper type checking",
        "value_error": "Validate input values",
        "runtime_error": "Add try-except error handling",
        "assertion_error": "Fix assertion logic",
        "not_implemented": "Implement missing functionality",
        "child_process": "Handle subprocess errors",
    }
    
    @classmethod
    def classify(cls, error: str) -> ErrorCategory:
        """
        Classify an error string into an ErrorCategory.
        
        Args:
            error: Error message string
            
        Returns:
            ErrorCategory enum value
        """
        error_lower = error.lower()
        
        for category, keywords in cls.KEYWORDS.items():
            if any(kw in error_lower for kw in keywords):
                return category
        
        return ErrorCategory.UNKNOWN
    
    @classmethod
    def classify_str(cls, error: str) -> str:
        """Classify error and return string."""
        return cls.classify(error).value
    
    @classmethod
    def to_constraint(cls, error: str) -> str:
        """
        Convert error to constraint string.
        
        Args:
            error: Error message
            
        Returns:
            Constraint string for LLM
        """
        category = cls.classify(error)
        return cls.ERROR_TO_CONSTRAINT.get(category.value, "Add error handling")
    
    @classmethod
    def to_constraint_list(cls, errors: List[str]) -> List[str]:
        """Convert multiple errors to constraints."""
        constraints = set()
        for error in errors:
            constraint = cls.to_constraint(error)
            if constraint:
                constraints.add(constraint)
        return list(constraints)
    
    @classmethod
    def suggest_fix(cls, error: str) -> str:
        """
        Suggest a fix for the given error.
        
        Args:
            error: Error message
            
        Returns:
            Suggestion string
        """
        category = cls.classify(error)
        
        fixes = {
            ErrorCategory.TIMEOUT: "Add timeout parameter and retry logic",
            ErrorCategory.SYNTAX_ERROR: "Check syntax and fix parse errors",
            ErrorCategory.IMPORT_ERROR: "Install missing module or fix import path",
            ErrorCategory.MEMORY: "Add memory cleanup and GC.collect()",
            ErrorCategory.NETWORK: "Add retry logic with exponential backoff",
            ErrorCategory.PERMISSION: "Check file/directory permissions",
            ErrorCategory.TYPE_ERROR: "Add type hints and type checking",
            ErrorCategory.VALUE_ERROR: "Validate input before processing",
            ErrorCategory.RUNTIME_ERROR: "Wrap in try-except block",
            ErrorCategory.ASSERTION_ERROR: "Fix assertion logic",
            ErrorCategory.NOT_IMPLEMENTED: "Implement the missing method",
            ErrorCategory.CHILD_PROCESS: "Handle subprocess return codes",
            ErrorCategory.UNKNOWN: "Analyze error and add appropriate handling",
        }
        
        return fixes.get(category, "Unknown error - investigate")


# Backward compatibility aliases
def classify_error(error: str) -> str:
    """Backward compatible error classification."""
    return ErrorClassifier.classify_str(error)

def error_to_constraint(error: str) -> str:
    """Backward compatible error to constraint."""
    return ErrorClassifier.to_constraint(error)

def suggest_fix(error: str) -> str:
    """Backward compatible fix suggestion."""
    return ErrorClassifier.suggest_fix(error)


if __name__ == "__main__":
    # Test the classifier
    test_errors = [
        "ModuleNotFoundError: No module named 'requests'",
        "SyntaxError: invalid syntax",
        "TimeoutError: connection timed out",
        "PermissionError: access denied",
        "TypeError: unsupported operand type",
    ]
    
    print("=== Error Classification Tests ===\n")
    for error in test_errors:
        category = ErrorClassifier.classify_str(error)
        constraint = ErrorClassifier.to_constraint(error)
        fix = ErrorClassifier.suggest_fix(error)
        print(f"Error: {error}")
        print(f"  Category: {category}")
        print(f"  Constraint: {constraint}")
        print(f"  Fix: {fix}")
        print()