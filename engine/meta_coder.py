"""
Paradise Stack - MetaCoder
Meta-cognitive code generation that reuses learned solutions.
"""

import asyncio
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
    code_snippets: Dict[str, str]

class MetaCoder:
    """
    Meta-cognitive code generator.
    Remembers solutions and reuses them intelligently.
    """
    
    def __init__(self):
        self.solutions_file = OUTPUT_DIR / ".solutions.json"
        self.solutions: List[Solution] = self._load_solutions()
        self.cache_file = OUTPUT_DIR / ".code_cache.json"
        self.cache: Dict[str, str] = self._load_cache()
        
    def _load_solutions(self) -> List[Solution]:
        if self.solutions_file.exists():
            try:
                data = json.loads(self.solutions_file.read_text())
                return [Solution(**s) for s in data]
            except:
                pass
        return []
    
    def _load_cache(self) -> Dict[str, str]:
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text())
            except:
                pass
        return {}
    
    def _save_solutions(self):
        data = [asdict(s) for s in self.solutions[-100:]]
        self.solutions_file.write_text(json.dumps(data, indent=2))
    
    def _save_cache(self):
        self.cache_file.write_text(json.dumps(self.cache, indent=2))
    
    def remember_solution(self, task: str, code: str, files: List[str], success: bool):
        """Store a learned solution."""
        task_type = self._classify_task(task)
        keywords = self._extract_keywords(task)
        snippets = self._extract_snippets(code)
        
        solution = Solution(
            task=task,
            code=code,
            files=files,
            success=success,
            task_type=task_type,
            keywords=keywords,
            code_snippets=snippets
        )
        
        existing = next((i for i, s in enumerate(self.solutions) 
                        if s.task_type == task_type and s.success), None)
        
        if existing is not None:
            self.solutions[existing] = solution
        else:
            self.solutions.append(solution)
        
        self._save_solutions()
        
        for kw in keywords[:5]:
            self.cache[f"kw_{kw}"] = code[:1000]
    
    def _classify_task(self, task: str) -> str:
        """Classify task type."""
        task_lower = task.lower()
        
        patterns = {
            "rest_api": ["rest", "api", "endpoint", "route", "http"],
            "web_server": ["server", "listen", "port", "serve"],
            "database": ["db", "database", "query", "sql", "crud"],
            "auth": ["auth", "login", "password", "token", "jwt", "session"],
            "file_ops": ["file", "read", "write", "upload", "download"],
            "web_page": ["html", "page", "website", "frontend", "ui"],
            "cli": ["cli", "command", "args", "argv"],
            "config": ["config", "settings", "env", "yaml", "json"],
            "test": ["test", "pytest", "unittest", "verify"],
            "model": ["model", "ml", "ai", "predict", "train"],
        }
        
        for type_name, keywords in patterns.items():
            if any(kw in task_lower for kw in keywords):
                return type_name
        
        return "general"
    
    def _extract_keywords(self, task: str) -> List[str]:
        """Extract keywords from task."""
        words = re.findall(r'\b\w{4,}\b', task.lower())
        stop_words = {'this', 'that', 'with', 'from', 'have', 'make', 'also', 'into', 'will', 'using', 'should', 'could'}
        return [w for w in words if w not in stop_words][:10]
    
    def _extract_snippets(self, code: str) -> Dict[str, str]:
        """Extract reusable code snippets."""
        snippets = {}
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if stripped.startswith('def ') or stripped.startswith('async def '):
                name = stripped.split('(')[0].split()[-1]
                snippet = '\n'.join(lines[i:i+10])
                snippets[f"fn_{name}"] = snippet
            
            elif 'class ' in stripped and ':' in stripped:
                name = stripped.split('(')[0].replace('class ', '').strip()
                snippet = '\n'.join(lines[i:i+15])
                snippets[f"class_{name}"] = snippet
            
            elif 'import ' in stripped or 'from ' in stripped:
                snippets[f"import_{i}"] = stripped
        
        return snippets
    
    def find_solution(self, task: str) -> Optional[Solution]:
        """Find a similar learned solution."""
        task_keywords = set(self._extract_keywords(task))
        task_type = self._classify_task(task)
        
        best_match = None
        best_score = 0
        
        for sol in reversed(self.solutions):
            if not sol.success:
                continue
            
            score = 0
            
            if sol.task_type == task_type:
                score += 5
            
            sol_keywords = set(sol.keywords)
            overlap = len(task_keywords & sol_keywords)
            score += overlap
            
            for kw in task_keywords:
                if kw in sol.keywords:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = sol
        
        if best_score >= 2:
            return best_match
        
        return None
    
    def get_snippet(self, snippet_key: str) -> Optional[str]:
        """Get a reusable code snippet."""
        if snippet_key in self.cache:
            return self.cache[snippet_key]
        
        for sol in self.solutions:
            if snippet_key in sol.code_snippets:
                return sol.code_snippets[snippet_key]
        
        return None
    
    async def generate(self, task: str, language: str = "python") -> Tuple[str, bool]:
        """
        Meta-cognitive generation that reuses past solutions.
        Only reuses if the solution is substantial (500+ chars).
        """
        existing = self.find_solution(task)
        
        if existing and len(existing.code) >= 500:
            print(f"    [MetaCog] Found substantial solution: {existing.task[:50]}...")
            return self._adapt_solution(existing, task, language), True
        
        print(f"    [MetaCog] No good solution - will generate new...")
        return "", False
    
    def _adapt_solution(self, solution: Solution, new_task: str, language: str) -> str:
        """Adapt an existing solution to new task."""
        adapted = solution.code
        
        new_keywords = self._extract_keywords(new_task)
        old_keywords = solution.keywords
        
        for old, new in zip(old_keywords[:3], new_keywords[:3]):
            adapted = adapted.replace(old, new)
            adapted = adapted.replace(old.capitalize(), new.capitalize())
        
        if new_keywords:
            main_kw = new_keywords[0].replace('_', ' ').title()
            adapted = adapted.replace(solution.keywords[0].replace('_', ' ').title() 
                                     if solution.keywords else 'Main', main_kw)
        
        return adapted
    
    async def _generate_new(self, task: str, language: str) -> str:
        """Generate new code using template."""
        templates = {
            "python": {
                "rest_api": '''from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route("/api", methods=["GET"])
def api():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000)
''',
                "web_server": '''from http.server import HTTPServer, SimpleHTTPRequestHandler
port = 8000
server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
print(f"Serving on port {port}")
server.serve_forever()
''',
                "auth": '''import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed
''',
                "web_page": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page</title>
</head>
<body>
    <h1>Welcome</h1>
</body>
</html>
''',
                "cli": '''import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    args = parser.parse_args()
    print(f"Running: {args.command}")

if __name__ == "__main__":
    main()
''',
                "general": '''"""Generated code"""

def main():
    print("Hello from Paradise Stack")
    return 0

if __name__ == "__main__":
    main()
'''
            }
        }
        
        task_type = self._classify_task(task)
        templates_map = templates.get(language, templates["python"])
        
        return templates_map.get(task_type, templates_map["general"])
    
    def get_stats(self) -> Dict:
        """Get meta-coder statistics."""
        task_types = {}
        for s in self.solutions:
            task_types[s.task_type] = task_types.get(s.task_type, 0) + 1
        
        return {
            "solutions_learned": len(self.solutions),
            "successful": sum(1 for s in self.solutions if s.success),
            "cache_size": len(self.cache),
            "by_type": task_types,
        }


async def test():
    """Test meta-coder."""
    print("Paradise MetaCoder")
    print("=" * 40)
    
    mc = MetaCoder()
    
    print("\n[1] First task - generates new code...")
    code1, reused1 = await mc.generate("Create a REST API with Flask", "python")
    print(f"    Reused: {reused1}")
    print(f"    Code: {code1[:100]}...")
    
    print("\n[2] Remember solution...")
    mc.remember_solution("Create a REST API with Flask", code1, ["api.py"], True)
    
    print("\n[3] Similar task - should reuse...")
    code2, reused2 = await mc.generate("Build a REST API endpoint", "python")
    print(f"    Reused: {reused2}")
    print(f"    Code: {code2[:100]}...")
    
    print("\n[4] Stats...")
    print(f"    {mc.get_stats()}")


if __name__ == "__main__":
    asyncio.run(test())
