"""
OMEGA-CODE Meta-Cognition Engine
================================
Pre-frontal cortex for self-aware recursive improvement.

Functions:
- analyze_failure_patterns() - Query SQLite for last N failures
- derive_constraints() - Auto-generate Thinking Rules
- generate_disciplined_prompt() - Inject constraints into LLM
"""

import os
import sqlite3
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import Counter

PROJECT_ROOT = Path(__file__).parent.parent

@dataclass
class FailurePattern:
    error_type: str
    count: int
    example: str
    constraint: str

@dataclass
class ThinkingRule:
    rule_id: str
    constraint: str
    reason: str
    confidence: float
    created_at: str

class MetaCognition:
    """
    Pre-frontal cortex for OMEGA-CODE.
    
    Analyzes failure patterns from SQLite history and generates
    hard constraints that the LLM must follow in subsequent
    iterations.
    """
    
    DISCIPLINE_PROTOCOL = """# OMEGA-CODE DISCIPLINE PROTOCOL
You are an autonomous engineering unit. You are NOT a chatbot.
You are bound by the following operational constraints:

1. LISTEN BEFORE ACTING: Acknowledge the 'Current Thinking Rules' 
   derived from previous failures. These are MANDATORY.

2. DISCIPLINED OUTPUT: Your response MUST be strictly valid JSON containing:
   - "thought_process": Your reasoning for the current fix
   - "rectified_code": The full, executable script
   - "validation_test": A new test case to prevent the previous failure

3. NO QUITTING: If you do not know the answer, analyze the provided 
   documentation and propose a hypothesis. Silence or 'I cannot do this' 
   is a protocol violation.

4. PATIENT COMPANIONSHIP: Acknowledge the user's project goals with 
   high-fidelity technical alignment.
"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv(
            "DB_PATH", 
            f"projects/{os.getenv('PROJECT_NAME', 'default')}/state/omega_state.db"
        )
        self.conn = self._connect()
        self.rules: List[ThinkingRule] = self._load_rules()
    
    def _connect(self) -> sqlite3.Connection:
        """Connect to the state database."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS failures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT,
                error TEXT,
                error_type TEXT,
                timestamp TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS thinking_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT UNIQUE,
                constraint_text TEXT,
                reason TEXT,
                confidence REAL,
                created_at TEXT
            )
        """)
        conn.commit()
        return conn
    
    def _load_rules(self) -> List[ThinkingRule]:
        """Load existing thinking rules from database."""
        rules = []
        cursor = self.conn.cursor()
        cursor.execute("SELECT rule_id, constraint_text, reason, confidence, created_at FROM thinking_rules")
        for row in cursor.fetchall():
            rules.append(ThinkingRule(
                rule_id=row[0],
                constraint=row[1],
                reason=row[2],
                confidence=row[3],
                created_at=row[4]
            ))
        return rules
    
    def analyze_failure_patterns(self, limit: int = 10) -> List[FailurePattern]:
        """
        Extract patterns from the last N failures.
        Identifies recurring error types and their frequencies.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT error, error_type FROM failures ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        failures = cursor.fetchall()
        
        if not failures:
            return []
        
        patterns = []
        error_groups = {}
        
        for error, error_type in failures:
            if error_type:
                if error_type not in error_groups:
                    error_groups[error_type] = []
                error_groups[error_type].append(error)
        
        for error_type, errors in error_groups.items():
            counter = Counter(errors)
            most_common = counter.most_common(1)[0]
            
            pattern = FailurePattern(
                error_type=error_type,
                count=len(errors),
                example=most_common[0][:200],
                constraint=self._error_type_to_constraint(error_type)
            )
            patterns.append(pattern)
        
        return sorted(patterns, key=lambda p: p.count, reverse=True)
    
    def _error_type_to_constraint(self, error_type: str) -> str:
        """Map error types to hard constraints."""
        constraint_map = {
            "timeout": "CONSTRAINT_TIMEOUT: Implement explicit timeout handling for all I/O operations.",
            "syntax_error": "CONSTRAINT_SYNTAX: Verify Python syntax before execution. Use ast.parse().",
            "import_error": "CONSTRAINT_IMPORTS: Verify all imports exist before using. Handle ImportError explicitly.",
            "memory": "CONSTRAINT_MEMORY: Use generators for large data. Implement chunked processing.",
            "network": "CONSTRAINT_NETWORK: Use exponential backoff for network calls. Handle ConnectionError.",
            "file": "CONSTRAINT_FILES: Use absolute paths via pathlib. Verify file existence before access.",
            "permission": "CONSTRAINT_PERMS: Check write permissions before file operations. Handle PermissionError.",
            "type_error": "CONSTRAINT_TYPES: Add explicit type hints. Use isinstance() for type checking.",
            "value_error": "CONSTRAINT_VALUES: Validate all inputs. Use try/except for parsing.",
            "assertion": "CONSTRAINT_TESTS: Write at least one test case for every function.",
            "docker": "CONSTRAINT_DOCKER: Validate container state before operations. Handle docker.errors.",
            "sqlite": "CONSTRAINT_DB: Always close database connections. Use context managers.",
            "json": "CONSTRAINT_JSON: Validate JSON structure before parsing. Handle json.JSONDecodeError.",
            "generic": "CONSTRAINT_GENERIC: Add comprehensive error handling. Never let exceptions propagate silently.",
        }
        
        error_lower = error_type.lower()
        for key, constraint in constraint_map.items():
            if key in error_lower:
                return constraint
        
        return constraint_map["generic"]
    
    def derive_constraints(self, patterns: List[FailurePattern] = None) -> List[str]:
        """
        Generate 'Hard Thinking Rules' that the LLM must follow.
        These are injected into the prompt for subsequent iterations.
        """
        if patterns is None:
            patterns = self.analyze_failure_patterns()
        
        constraints = []
        
        for i, pattern in enumerate(patterns[:5], 1):
            constraint = pattern.constraint
            if constraint not in constraints:
                constraints.append(constraint)
        
        if not constraints:
            constraints = [
                "CONSTRAINT_ALPHA: Use absolute paths for all file operations via pathlib.",
                "CONSTRAINT_BETA: Implement explicit retry logic for third-party API calls.",
                "CONSTRAINT_GAMMA: Strictly type all function signatures with type hints.",
                "CONSTRAINT_DELTA: Write tests before code implementation.",
            ]
        
        self._save_constraints(constraints, patterns)
        return constraints
    
    def _save_constraints(self, constraints: List[str], patterns: List[FailurePattern]):
        """Persist constraints and patterns to database."""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("DELETE FROM thinking_rules")
        
        for i, constraint in enumerate(constraints):
            rule_id = f"CONSTRAINT_{chr(65+i)}"  # ALPHA, BETA, GAMMA, etc.
            
            reason = "Recurring failure pattern detected"
            for pattern in patterns:
                if pattern.constraint == constraint:
                    reason = f"Error type: {pattern.error_type} ({pattern.count} occurrences)"
                    break
            
            cursor.execute("""
                INSERT INTO thinking_rules (rule_id, constraint_text, reason, confidence, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (rule_id, constraint, reason, 0.8, now))
            
            self.rules.append(ThinkingRule(
                rule_id=rule_id,
                constraint=constraint,
                reason=reason,
                confidence=0.8,
                created_at=now
            ))
        
        self.conn.commit()
    
    def generate_disciplined_prompt(
        self, 
        goal: str, 
        constraints: List[str] = None,
        patterns: List[FailurePattern] = None,
        previous_logs: str = ""
    ) -> str:
        """
        Generate a disciplined prompt with constraints injected.
        This is the prompt that goes to the LLM.
        """
        if constraints is None:
            constraints = self.derive_constraints(patterns)
        
        formatted_rules = "\n".join([f"RULE {idx+1}: {rule}" for idx, rule in enumerate(constraints)])
        
        patterns_summary = ""
        if patterns:
            patterns_summary = "\n\n".join([
                f"- {p.error_type} ({p.count}x): {p.example[:100]}..."
                for p in patterns[:3]
            ])
        
        return f"""{self.DISCIPLINE_PROTOCOL}

## CURRENT THINKING RULES (MANDATORY):
{formatted_rules}

## PROJECT GOAL:
{goal}

## PREVIOUS FAILURES (DO NOT REPEAT):
{patterns_summary or "No previous failures. Apply standard best practices."}

## EXECUTION LOGS:
{previous_logs[:500] if previous_logs else "Initial attempt."}

---

Execute the next recursive step. Be disciplined. Be precise.
Your output MUST be valid JSON with: thought_process, rectified_code, validation_test
"""
    
    def get_active_rules(self) -> List[ThinkingRule]:
        """Get all currently active thinking rules."""
        return self.rules
    
    def clear_rules(self):
        """Clear all thinking rules (use with caution)."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM thinking_rules")
        self.conn.commit()
        self.rules = []
    
    def close(self):
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DisciplineParser:
    """
    Parses LLM output to extract thought_process, rectified_code, validation_test.
    Ensures the LLM follows the Discipline Protocol.
    """
    
    @staticmethod
    def parse(response: str) -> Tuple[bool, Dict]:
        """
        Parse LLM response into structured format.
        Returns (success, parsed_data)
        """
        try:
            data = json.loads(response)
            
            required_fields = ["thought_process", "rectified_code", "validation_test"]
            for field in required_fields:
                if field not in data:
                    return False, {"error": f"Missing required field: {field}"}
            
            return True, data
        
        except json.JSONDecodeError:
            return DisciplineParser._fuzzy_parse(response)
    
    @staticmethod
    def _fuzzy_parse(response: str) -> Tuple[bool, Dict]:
        """
        Fallback parser when strict JSON fails.
        Attempts to extract code from markdown blocks.
        """
        code_blocks = re.findall(r'```(?:python)?\s*(.*?)```', response, re.DOTALL)
        code = "\n\n".join(code_blocks) if code_blocks else response
        
        thought_match = re.search(r'thought_process["\s:]+([^}"]+)', response, re.DOTALL)
        thought = thought_match.group(1) if thought_match else "Analysis performed"
        
        test_match = re.findall(r'(?:def test_|assert |pytest\.)', code)
        validation_test = "def test_validation():\n    pass" if not test_match else "Test cases found in code"
        
        return True, {
            "thought_process": thought.strip(),
            "rectified_code": code.strip(),
            "validation_test": validation_test
        }


def analyze_project(project_name: str = None) -> Dict:
    """Convenience function to analyze a project's failure patterns."""
    project_name = project_name or os.getenv("PROJECT_NAME", "default")
    db_path = f"projects/{project_name}/state/omega_state.db"
    
    with MetaCognition(db_path) as meta:
        patterns = meta.analyze_failure_patterns()
        constraints = meta.derive_constraints(patterns)
        rules = meta.get_active_rules()
        
        return {
            "project": project_name,
            "patterns_found": len(patterns),
            "constraints_generated": len(constraints),
            "active_rules": [asdict(r) for r in rules],
            "patterns": [asdict(p) for p in patterns],
        }


if __name__ == "__main__":
    import sys
    
    project = sys.argv[1] if len(sys.argv) > 1 else os.getenv("PROJECT_NAME", "default")
    
    print("=" * 60)
    print("OMEGA-CODE META-COGNITION ANALYSIS")
    print("=" * 60)
    
    analysis = analyze_project(project)
    
    print(f"\nProject: {analysis['project']}")
    print(f"Patterns Found: {analysis['patterns_found']}")
    print(f"Constraints Generated: {analysis['constraints_generated']}")
    
    print("\n--- ACTIVE THINKING RULES ---")
    for rule in analysis['active_rules']:
        print(f"  [{rule['rule_id']}] {rule['constraint']}")
        print(f"      Reason: {rule['reason']}")
    
    print("\n--- FAILURE PATTERNS ---")
    for pattern in analysis['patterns']:
        print(f"  [{pattern['error_type']}] x{pattern['count']}")
        print(f"      Example: {pattern['example'][:80]}...")
    
    print("=" * 60)
