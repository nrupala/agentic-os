"""
Paradise Stack - Self-Correcting Memory
Remembers solutions, validates quality, discards inferior ones.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

@dataclass
class Solution:
    task: str
    code: str
    files: List[str]
    success: bool
    task_type: str
    keywords: List[str]
    quality_score: float = 0.0
    code_snippets: Dict[str, str] = None
    
    def __post_init__(self):
        if self.code_snippets is None:
            self.code_snippets = {}

class QualityValidator:
    """Validates code quality and detects inferior solutions."""
    
    MIN_CODE_LENGTH = 300
    REQUIRED_PATTERNS = {
        "python": ["def ", "import ", "class "],
        "javascript": ["function", "const ", "let ", "="],
        "html": ["<!DOCTYPE", "<html", "<body"]
    }
    
    @staticmethod
    def validate(code: str, language: str) -> Tuple[bool, float]:
        """
        Validate code quality.
        Returns (is_valid, quality_score)
        """
        if not code or len(code.strip()) < QualityValidator.MIN_CODE_LENGTH:
            return False, 0.0
        
        score = 0.5
        
        required = QualityValidator.REQUIRED_PATTERNS.get(language, ["def ", "function"])
        for pattern in required:
            if pattern in code:
                score += 0.1
        
        if "error" in code.lower() or "except" in code.lower():
            score += 0.1
        
        has_functions = len(re.findall(r'def \w+\(', code)) > 0
        has_classes = "class " in code
        if has_functions:
            score += 0.1
        if has_classes:
            score += 0.1
        
        if score > 1.0:
            score = 1.0
            
        return score >= 0.5, score
    
    @staticmethod
    def is_inferior(code: str, language: str) -> bool:
        """Check if code is clearly inferior."""
        if not code:
            return True
        
        if len(code.strip()) < 100:
            return True
        
        if code.count('\n') < 5:
            return True
        
        templates = ["TODO", "placeholder", "# Your code here", "pass  # TODO"]
        if any(t in code for t in templates):
            return True
        
        return False


class SelfCorrectingMemory:
    """
    Memory that learns, validates, and self-corrects.
    """
    
    def __init__(self):
        self.solutions_file = OUTPUT_DIR / ".solutions_v2.json"
        self.quality_threshold = 0.6
        self.solutions: List[Solution] = self._load_solutions()
        
    def _load_solutions(self) -> List[Solution]:
        if self.solutions_file.exists():
            try:
                data = json.loads(self.solutions_file.read_text())
                return [Solution(**s) for s in data]
            except:
                pass
        return []
    
    def _save_solutions(self):
        data = [asdict(s) for s in self.solutions[-100:]]
        self.solutions_file.write_text(json.dumps(data, indent=2))
    
    def remember(self, task: str, code: str, files: List[str], language: str = "python") -> bool:
        """
        Remember a solution with quality validation.
        Returns True if remembered, False if discarded.
        """
        is_valid, quality_score = QualityValidator.validate(code, language)
        
        if is_inferior := QualityValidator.is_inferior(code, language):
            print(f"    [Memory] Discarding inferior solution ({len(code)} chars)")
            return False
        
        if not is_valid:
            print(f"    [Memory] Discarding low quality solution (score: {quality_score:.2f})")
            return False
        
        task_type = self._classify_task(task)
        keywords = self._extract_keywords(task)
        snippets = self._extract_snippets(code)
        
        solution = Solution(
            task=task,
            code=code,
            files=files,
            success=True,
            task_type=task_type,
            keywords=keywords,
            quality_score=quality_score,
            code_snippets=snippets
        )
        
        self._update_solution(solution)
        self._save_solutions()
        
        print(f"    [Memory] Remembered: {task[:40]}... (quality: {quality_score:.2f})")
        return True
    
    def _update_solution(self, new_solution: Solution):
        """Update or add solution."""
        for i, existing in enumerate(self.solutions):
            if existing.task_type == new_solution.task_type:
                if new_solution.quality_score > existing.quality_score:
                    self.solutions[i] = new_solution
                    print(f"    [Memory] Updated superior solution for: {new_solution.task_type}")
                    return
                else:
                    print(f"    [Memory] Kept existing solution (better quality)")
                    return
        
        self.solutions.append(new_solution)
    
    def find_similar(self, task: str) -> Optional[Solution]:
        """Find similar high-quality solution."""
        task_keywords = set(self._extract_keywords(task))
        task_type = self._classify_task(task)
        
        best = None
        best_score = 0
        
        for sol in reversed(self.solutions):
            if not sol.success:
                continue
            
            score = 0
            
            if sol.task_type == task_type:
                score += 5
            
            sol_keywords = set(sol.keywords)
            overlap = len(task_keywords & sol_keywords)
            score += overlap * 0.5
            
            score += sol.quality_score * 2
            
            if score > best_score and sol.quality_score >= self.quality_threshold:
                best_score = score
                best = sol
        
        return best if best_score >= 3 else None
    
    def discard_inferior(self):
        """Remove all inferior solutions."""
        before = len(self.solutions)
        
        self.solutions = [
            s for s in self.solutions
            if s.quality_score >= self.quality_threshold
        ]
        
        after = len(self.solutions)
        self._save_solutions()
        
        print(f"    [Memory] Cleaned: {before} -> {after} solutions")
    
    def _classify_task(self, task: str) -> str:
        task_lower = task.lower()
        
        patterns = {
            "rest_api": ["rest", "api", "endpoint", "crud"],
            "web_server": ["web server", "http"],
            "cli": ["cli", "command", "tool"],
            "database": ["database", "db", "sql"],
            "auth": ["auth", "login", "password"],
            "web_page": ["html", "web page", "frontend"],
            "worker": ["worker", "background", "queue"],
            "test": ["test", "pytest"],
        }
        
        for type_name, keywords in patterns.items():
            if any(kw in task_lower for kw in keywords):
                return type_name
        
        return "general"
    
    def _extract_keywords(self, task: str) -> List[str]:
        words = re.findall(r'\b\w{4,}\b', task.lower())
        stop = {'this', 'that', 'with', 'from', 'have', 'make', 'also', 'into', 'will', 'using', 'should', 'could', 'build', 'create', 'simple', 'basic'}
        return [w for w in words if w not in stop][:10]
    
    def _extract_snippets(self, code: str) -> Dict[str, str]:
        snippets = {}
        for match in re.finditer(r'(def \w+\(|class \w+)', code):
            name = match.group(1).replace('(', '').replace(':', '')
            start = match.start()
            end = min(start + 200, len(code))
            snippets[name] = code[start:end]
        return snippets
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        by_type = {}
        for s in self.solutions:
            by_type[s.task_type] = by_type.get(s.task_type, 0) + 1
        
        avg_quality = sum(s.quality_score for s in self.solutions) / max(1, len(self.solutions))
        
        return {
            "total": len(self.solutions),
            "avg_quality": avg_quality,
            "by_type": by_type,
            "threshold": self.quality_threshold
        }
    
    def reset(self):
        """Reset memory."""
        self.solutions = []
        self._save_solutions()


async def generate(task: str, language: str = "python") -> Tuple[str, bool]:
    """
    Generate code using self-correcting memory.
    """
    memory = SelfCorrectingMemory()
    
    existing = memory.find_similar(task)
    if existing:
        print(f"    [Memory] Found: {existing.task[:40]}... (quality: {existing.quality_score:.2f})")
        return existing.code, True
    
    return "", False


def remember(task: str, code: str, files: List[str], language: str = "python"):
    """Remember a solution."""
    memory = SelfCorrectingMemory()
    return memory.remember(task, code, files, language)


if __name__ == "__main__":
    memory = SelfCorrectingMemory()
    
    print("\nSelf-Correcting Memory Test")
    print("=" * 40)
    
    print("\n[1] Testing inferior solution...")
    memory.remember("test", "pass  # TODO", ["test.py"], "python")
    
    print("\n[2] Testing good solution...")
    good_code = '''
from flask import Flask

app = Flask(__name__)

@app.route("/api")
def api():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run()
'''
    memory.remember("Build API", good_code, ["api.py"], "python")
    
    print("\n[3] Stats:", memory.get_stats())
    
    print("\n[4] Cleanup inferior...")
    memory.discard_inferior()
    
    print("\n[5] Final stats:", memory.get_stats())
