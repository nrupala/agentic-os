#!/usr/bin/env python3
"""
Paradise Planner - Research-backed implementation planner
Based on: MapCoder (ACL 2024), Claude Code, KAT-Coder

Pipeline:
1. Explore → Understand codebase structure
2. Design → Architecture planning  
3. Plan → Step-by-step implementation
4. Verify → Testing & validation
"""

import sys
import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(os.environ.get('HOST_PROJECT_ROOT', '/app'))

class CodebaseExplorer:
    """Phase 1: Explore - Understand the codebase"""
    
    def __init__(self):
        self.structure = {
            "languages": set(),
            "frameworks": set(),
            "files_by_type": defaultdict(list),
            "key_files": [],
            "config_files": [],
            "test_files": [],
            "src_dirs": [],
            "dependencies": {}
        }
        
    def scan(self):
        """Scan project structure"""
        if not PROJECT_ROOT.exists():
            return self.structure
            
        extensions = {
            "python": [".py", ".pyw", ".pyx"],
            "javascript": [".js", ".mjs", ".cjs"],
            "typescript": [".ts", ".tsx"],
            "html": [".html", ".htm"],
            "css": [".css", ".scss", ".sass", ".less"],
            "json": [".json"],
            "yaml": [".yaml", ".yml"],
            "markdown": [".md"],
            "config": [".toml", ".ini", ".cfg", ".conf"],
            "rust": [".rs"],
            "go": [".go"],
            "java": [".java", ".kt"],
        }
        
        framework_markers = {
            "react": ["react", "jsx", "tsx", "create-react-app", "vite"],
            "vue": ["vue", "nuxt", "@vue/"],
            "angular": ["@angular"],
            "django": ["django", "DJANGO", "INSTALLED_APPS"],
            "flask": ["flask", "Flask"],
            "fastapi": ["fastapi", "FastAPI", "uvicorn"],
            "express": ["express", "Express"],
            "nextjs": ["next.js", "Next.js", "pages/", "app/"],
            "spring": ["org.springframework", "@SpringBootApplication"],
            "fastapi": ["fastapi", "FastAPI"],
            "pandas": ["pandas", "pd."],
            "numpy": ["numpy", "np."],
        }
        
        for f in PROJECT_ROOT.rglob("*"):
            if not f.is_file():
                continue
                
            # Skip common ignore patterns
            ignore_dirs = {".git", "node_modules", "__pycache__", ".venv", 
                          "venv", ".pytest_cache", "dist", "build", ".next", ".nuxt"}
            if any(ig in f.parts for ig in ignore_dirs):
                continue
                
            rel_path = f.relative_to(PROJECT_ROOT)
            ext = f.suffix.lower()
            
            # Categorize by type
            for lang, exts in extensions.items():
                if ext in exts:
                    self.structure["files_by_type"][lang].append(str(rel_path))
                    self.structure["languages"].add(lang)
                    
                    if lang in ["python", "javascript", "typescript"]:
                        self.structure["src_dirs"].append(str(rel_path.parent))
                    break
            
            # Detect frameworks
            try:
                content = f.read_text(errors="ignore").lower()
                for fw, markers in framework_markers.items():
                    if any(m in content or m.lower() in str(f).lower() for m in markers):
                        self.structure["frameworks"].add(fw)
            except:
                pass
            
            # Categorize key files
            name_lower = str(rel_path).lower()
            if any(k in name_lower for k in ["main", "app", "index", "server", "setup"]):
                self.structure["key_files"].append(str(rel_path))
            if any(k in name_lower for k in ["config", ".env", "settings"]):
                self.structure["config_files"].append(str(rel_path))
            if any(k in name_lower for k in ["test", "spec"]):
                self.structure["test_files"].append(str(rel_path))
        
        # Dedupe
        self.structure["languages"] = list(self.structure["languages"])
        self.structure["frameworks"] = list(self.structure["frameworks"])
        self.structure["src_dirs"] = list(set(self.structure["src_dirs"]))
        
        return self.structure

    def get_summary(self):
        """Get readable summary"""
        return f"""
**Languages**: {', '.join(self.structure['languages']) or 'None detected'}
**Frameworks**: {', '.join(self.structure['frameworks']) or 'None detected'}
**Total Files**: {sum(len(v) for v in self.structure['files_by_type'].values())}
**Test Files**: {len(self.structure['test_files'])}
"""


class TaskAnalyzer:
    """Phase 2: Analyze the request"""
    
    REQUEST_PATTERNS = {
        "feature_add": {
            "keywords": ["add", "new", "create", "implement", "build", "generate", "make"],
            "steps": ["requirement_analysis", "architecture_design", "implementation", "testing"]
        },
        "bug_fix": {
            "keywords": ["fix", "bug", "error", "issue", "crash", "broken"],
            "steps": ["reproduce", "identify", "fix", "verify"]
        },
        "refactor": {
            "keywords": ["refactor", "improve", "optimize", "restructure", "clean"],
            "steps": ["analyze", "plan_changes", "implement", "test"]
        },
        "api": {
            "keywords": ["api", "endpoint", "route", "controller", "rest", "graphql"],
            "steps": ["define_schema", "implement_routes", "add_tests", "document"]
        },
        "test": {
            "keywords": ["test", "spec", "coverage", "unit", "integration"],
            "steps": ["identify_scope", "write_tests", "run_coverage"]
        },
        "security": {
            "keywords": ["security", "auth", "authenticate", "authorize", "permission"],
            "steps": ["identify_surface", "implement_auth", "test_security"]
        },
        "database": {
            "keywords": ["database", "db", "migration", "model", "schema", "sql"],
            "steps": ["design_schema", "create_migration", "implement_model", "test_queries"]
        }
    }
    
    def __init__(self, prompt):
        self.prompt = prompt
        self.prompt_lower = prompt.lower()
        self.detected_type = self._detect_type()
        
    def _detect_type(self):
        """Detect request type based on keywords"""
        scores = {}
        for req_type, config in self.REQUEST_PATTERNS.items():
            score = sum(1 for kw in config["keywords"] if kw in self.prompt_lower)
            scores[req_type] = score
        return max(scores, key=scores.get) if scores else "general"
    
    def get_config(self):
        """Get configuration for detected type"""
        return self.REQUEST_PATTERNS.get(self.detected_type, 
            {"keywords": [], "steps": ["analyze", "implement", "test"]})


class Planner:
    """Phase 3: Generate implementation plan"""
    
    def __init__(self, prompt, explorer, analyzer):
        self.prompt = prompt
        self.prompt_lower = prompt.lower()
        self.explorer = explorer
        self.analyzer = analyzer
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    def generate(self):
        """Generate complete plan document"""
        plan = f"""# 📋 Implementation Plan

> **Generated**: {self.timestamp}  
> **Request**: {self.prompt}  
> **Type**: `{self.analyzer.detected_type}`  
> **Status**: Draft

---

## Phase 1: Understanding

### Current Project State
{self.explorer.get_summary()}

### Key Files (detected)
```
"""
        
        for f in self.explorer.structure["key_files"][:8]:
            plan += f"- `{f}`\n"
        
        plan += f"""
```

---

## Phase 2: Requirements Analysis

### What We Need to Build
{self._extract_features()}

### Constraints
- Language: {', '.join(self.explorer.structure['languages']) or 'Any'}
- Framework: {', '.join(self.explorer.structure['frameworks']) or 'None'}
- Existing patterns: Follow project's coding style

---

## Phase 3: Implementation Steps

"""
        
        steps = self.analyzer.get_config()["steps"]
        for i, step in enumerate(steps, 1):
            plan += f"### Step {i}: {self._format_step_name(step)}\n"
            plan += f"{self._get_step_details(step)}\n\n"
        
        plan += f"""---

## Phase 4: Files to Create/Modify

### New Files
```
"""
        
        plan += self._suggest_new_files()
        
        plan += f"""
```

### Files to Modify
```
"""
        
        plan += self._suggest_modify_files()
        
        plan += f"""
```

---

## Phase 5: Testing Strategy

### Unit Tests
```bash
pytest tests/ -v
```

### Linting
```bash
ruff check .
ruff format --check .
```

### Manual Verification
- [ ] Feature works as expected
- [ ] No console errors
- [ ] Tests pass
- [ ] Linting clean

---

## Phase 6: Dependencies

### Required Packages
```
# Add to requirements.txt or package.json
```

---

## Quick Commands

```bash
# 1. Create files
touch src/main.py tests/test_main.py

# 2. Run tests
pytest tests/

# 3. Lint
ruff check .
ruff format .
```

---

*🤖 Generated by Paradise Stack Planner*  
*Based on: MapCoder (ACL 2024), Claude Code, KAT-Coder*
"""
        return plan
    
    def _extract_features(self):
        """Extract key features from prompt"""
        # Extract action words
        actions = re.findall(r'\b(add|create|build|implement|make|generate)\s+\w+', self.prompt_lower)
        
        # Extract nouns (things being built)
        nouns = re.findall(r'\b(a|an|the)?\s*([\w\s]+?)(?:app|list|feature|system|api|service|component)\b', self.prompt_lower)
        
        return f"""Based on request: "{self.prompt}"

**Core Action**: {' + '.join(set(actions)) if actions else 'build/implement'}

**Key Components**:
- {self.prompt}
"""
    
    def _format_step_name(self, step):
        """Convert step slug to readable name"""
        return ' '.join(word.capitalize() for word in step.split('_'))
    
    def _get_step_details(self, step):
        """Get details for each step"""
        details = {
            "requirement_analysis": "- Understand user needs\n- Define acceptance criteria\n- Identify edge cases",
            "architecture_design": "- Design file structure\n- Define interfaces\n- Plan data flow",
            "implementation": "- Create/update files\n- Follow existing patterns\n- Keep code clean",
            "testing": "- Write unit tests\n- Test edge cases\n- Verify functionality",
            "reproduce": "- Create minimal reproduction\n- Identify root cause\n- Document the bug",
            "identify": "- Find affected code\n- Understand dependencies\n- Plan fix approach",
            "fix": "- Apply fix\n- Handle edge cases\n- Prevent recurrence",
            "verify": "- Run tests\n- Manual verification\n- Check for regressions",
            "analyze": "- Review current code\n- Identify improvements\n- Document changes",
            "plan_changes": "- Design new structure\n- Map old → new\n- Plan migration",
            "define_schema": "- Design API/data structure\n- Document endpoints\n- Define validation",
            "implement_routes": "- Create handlers\n- Add validation\n- Error handling",
            "add_tests": "- Cover edge cases\n- Mock dependencies\n- Test failures",
            "document": "- Update README\n- Add docstrings\n- API documentation",
            "identify_scope": "- Find untested code\n- Prioritize by risk\n- Plan test structure",
            "write_tests": "- Write unit tests\n- Write integration tests\n- Verify coverage",
            "run_coverage": "- Check coverage report\n- Identify gaps\n- Add missing tests",
            "identify_surface": "- Map attack surface\n- Review permissions\n- Check inputs",
            "implement_auth": "- Add authentication\n- Add authorization\n- Secure data",
            "test_security": "- Test auth flows\n- Check permissions\n- Pen test",
            "design_schema": "- Define tables/collections\n- Plan relationships\n- Index strategy",
            "create_migration": "- Write migration\n- Handle data\n- Rollback plan",
            "implement_model": "- Create model\n- Add relationships\n- Add validation",
            "test_queries": "- Test CRUD\n- Performance test\n- Edge cases"
        }
        return details.get(step, "- Implement the change\n- Test thoroughly")
    
    def _suggest_new_files(self):
        """Suggest new files to create"""
        files = []
        
        if "python" in self.explorer.structure["languages"]:
            files.extend([
                "src/__init__.py",
                "src/main.py",
                "tests/test_main.py",
                "requirements.txt"
            ])
        
        if "javascript" in self.explorer.structure["languages"] or "typescript" in self.explorer.structure["languages"]:
            files.extend([
                "src/index.js",
                "src/components/",
                "tests/test_main.js",
                "package.json"
            ])
        
        files.extend([
            "README.md",
            ".gitignore"
        ])
        
        return '\n'.join(f"- `{f}`" for f in set(files))
    
    def _suggest_modify_files(self):
        """Suggest files to modify"""
        files = self.explorer.structure["key_files"][:5]
        if files:
            return '\n'.join(f"- `{f}`" for f in files)
        return "- No existing files to modify"


def main():
    if len(sys.argv) < 2:
        print("Usage: planner '<prompt>'")
        sys.exit(1)
    
    prompt = ' '.join(sys.argv[1:])
    
    print("🔍 Phase 1: Exploring codebase...")
    explorer = CodebaseExplorer()
    explorer.scan()
    
    print("📊 Phase 2: Analyzing request...")
    analyzer = TaskAnalyzer(prompt)
    print(f"   Detected type: {analyzer.detected_type}")
    
    print("📝 Phase 3: Generating plan...")
    planner = Planner(prompt, explorer, analyzer)
    plan = planner.generate()
    
    # Write PLAN.md
    plan_path = PROJECT_ROOT / "PLAN.md"
    with open(plan_path, 'w') as f:
        f.write(plan)
    
    print(f"\n✅ PLAN.md generated: {plan_path}")
    print(f"   Languages: {', '.join(explorer.structure['languages']) or 'None'}")
    print(f"   Type: {analyzer.detected_type}")
    print(f"   Files: {sum(len(v) for v in explorer.structure['files_by_type'].values())}")

if __name__ == '__main__':
    main()
