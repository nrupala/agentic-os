#!/usr/bin/env python3
"""
Paradise Planner - Research-backed implementation planner
Based on: MapCoder (ACL 2024), Claude Code, KAT-Coder

Supported Languages:
- Python, JavaScript, TypeScript, HTML/CSS
- Rust, Go, Java, C#, Ruby, PHP, Swift, Kotlin
- SQL, Bash/Shell, Docker, Terraform
- React, Vue, Angular, Next.js, Svelte
- Flask, FastAPI, Django, Express, Spring
- PostgreSQL, MySQL, MongoDB, Redis
"""

import sys
import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(os.environ.get('HOST_PROJECT_ROOT', '/app'))

# ============================================================================
# SUPPORTED LANGUAGES & FRAMEWORKS
# ============================================================================
LANGUAGES = {
    "python": [".py", ".pyw", ".pyx", ".pyi"],
    "javascript": [".js", ".mjs", ".cjs", ".jsx"],
    "typescript": [".ts", ".tsx", ".mts"],
    "html": [".html", ".htm", ".svg"],
    "css": [".css", ".scss", ".sass", ".less", ".styl"],
    "rust": [".rs"],
    "go": [".go"],
    "java": [".java", ".kt", ".kts"],
    "csharp": [".cs", ".fs"],
    "ruby": [".rb"],
    "php": [".php"],
    "swift": [".swift"],
    "kotlin": [".kt", ".kts"],
    "scala": [".scala"],
    "cpp": [".cpp", ".cc", ".cxx", ".h", ".hpp"],
    "c": [".c"],
    "sql": [".sql"],
    "bash": [".sh", ".bash"],
    "powershell": [".ps1", ".psm1"],
    "docker": ["Dockerfile", ".dockerignore"],
    "terraform": [".tf", ".tfvars"],
    "yaml": [".yaml", ".yml"],
    "json": [".json"],
    "toml": [".toml"],
    "xml": [".xml"],
    "markdown": [".md", ".mdx"],
    "vue": [".vue"],
    "svelte": [".svelte"],
}

FRAMEWORKS = {
    # Python
    "django": ["django", "DJANGO", "INSTALLED_APPS", "urls.py", "models.py"],
    "flask": ["flask", "Flask", "app.route"],
    "fastapi": ["fastapi", "FastAPI", "uvicorn", "@app.get"],
    "pyramid": ["pyramid", "Pyramid"],
    "bottle": ["bottle", "Bottle"],
    "tornado": ["tornado", "Tornado"],
    
    # JavaScript/TypeScript
    "react": ["react", "jsx", "tsx", "create-react-app", "vite", "useState", "useEffect"],
    "vue": ["vue", "Vue", "nuxt", "composition-api"],
    "angular": ["@angular", "NgModule", "app.component"],
    "nextjs": ["next.js", "Next.js", "pages/", "app/", "getServerSideProps"],
    "svelte": ["svelte", "SvelteKit", "$app"],
    "express": ["express", "Express", "app.use", "app.get", "app.post"],
    "nestjs": ["@nestjs", "NestApplication"],
    "fastify": ["fastify", "Fastify"],
    "koa": ["koa", "Koa"],
    
    # Backend
    "spring": ["org.springframework", "@SpringBootApplication", "@RestController"],
    "springboot": ["spring-boot", "SpringApplication"],
    "rails": ["Rails", "rails", "application.rb"],
    "laravel": ["Laravel", "artisan", "routes/web.php"],
    "aspnet": [".aspnet", "Startup.cs"],
    
    # Databases
    "postgresql": ["postgresql", "postgres", "psycopg"],
    "mysql": ["mysql", "MySQL", "sqlalchemy"],
    "mongodb": ["mongodb", "MongoClient", "pymongo"],
    "redis": ["redis", "Redis", "ioredis"],
    "sqlite": ["sqlite", "sqlite3"],
    
    # DevOps
    "docker": ["docker", "Dockerfile", "docker-compose"],
    "kubernetes": ["kubernetes", "k8s", "kubectl"],
    "terraform": ["terraform", "Terraform", ".tf"],
    
    # Mobile
    "reactnative": ["react-native", "ReactNative"],
    "flutter": ["flutter", "Flutter", "pubspec.yaml"],
    
    # ML/AI
    "tensorflow": ["tensorflow", "tf.", "keras"],
    "pytorch": ["torch", "nn.Module", "torch.nn"],
    "sklearn": ["sklearn", "from sklearn"],
    "pandas": ["pandas", "pd.", "DataFrame"],
    "numpy": ["numpy", "np.", "ndarray"],
}

DATABASES = ["postgresql", "mysql", "mongodb", "redis", "sqlite", "sql"]


class CodebaseExplorer:
    """Phase 1: Explore - Understand the codebase"""
    
    def __init__(self):
        self.structure = {
            "languages": set(),
            "frameworks": set(),
            "databases": set(),
            "files_by_type": defaultdict(list),
            "key_files": [],
            "config_files": [],
            "test_files": [],
            "src_dirs": [],
        }
    
    def scan(self):
        """Scan project structure"""
        if not PROJECT_ROOT.exists():
            return self.structure
        
        for f in PROJECT_ROOT.rglob("*"):
            if not f.is_file():
                continue
            
            ignore_dirs = {".git", "node_modules", "__pycache__", ".venv",
                          "venv", ".pytest_cache", "dist", "build", ".next", ".nuxt", "target"}
            if any(ig in f.parts for ig in ignore_dirs):
                continue
            
            rel_path = f.relative_to(PROJECT_ROOT)
            ext = f.suffix.lower()
            name_lower = str(rel_path).lower()
            
            # Detect languages
            for lang, extensions in LANGUAGES.items():
                if ext in extensions or any(name_lower.endswith(e) for e in extensions):
                    self.structure["files_by_type"][lang].append(str(rel_path))
                    self.structure["languages"].add(lang)
                    break
            
            # Detect frameworks
            try:
                content = f.read_text(errors="ignore").lower()
                for fw, markers in FRAMEWORKS.items():
                    if any(m.lower() in content or m.lower() in name_lower for m in markers):
                        self.structure["frameworks"].add(fw)
                
                # Detect databases
                for db in DATABASES:
                    if db.lower() in content or db.lower() in name_lower:
                        self.structure["databases"].add(db)
            except:
                pass
            
            # Categorize files
            if any(k in name_lower for k in ["main", "app", "index", "server", "setup"]):
                self.structure["key_files"].append(str(rel_path))
            if any(k in name_lower for k in ["config", ".env", "settings", "pyproject", "package"]):
                self.structure["config_files"].append(str(rel_path))
            if any(k in name_lower for k in ["test", "spec", "_test", "tests/"]):
                self.structure["test_files"].append(str(rel_path))
            if any(k in name_lower for k in ["src/", "lib/", "app/", "source/"]):
                self.structure["src_dirs"].append(str(rel_path.parent))
        
        self.structure["languages"] = list(self.structure["languages"])
        self.structure["frameworks"] = list(self.structure["frameworks"])
        self.structure["databases"] = list(self.structure["databases"])
        self.structure["src_dirs"] = list(set(self.structure["src_dirs"]))
        
        return self.structure
    
    def get_summary(self):
        s = self.structure
        return f"""
**Languages**: {', '.join(sorted(s['languages'])) or 'None detected'}
**Frameworks**: {', '.join(sorted(s['frameworks'])) or 'None detected'}
**Databases**: {', '.join(sorted(s['databases'])) or 'None detected'}
**Total Files**: {sum(len(v) for v in s['files_by_type'].values())}
**Test Files**: {len(s['test_files'])}
"""


class TaskAnalyzer:
    """Phase 2: Analyze the request"""
    
    REQUEST_PATTERNS = {
        "feature_add": {
            "keywords": ["add", "new", "create", "implement", "build", "generate", "make", "develop"],
            "steps": ["requirement_analysis", "architecture_design", "implementation", "testing"]
        },
        "bug_fix": {
            "keywords": ["fix", "bug", "error", "issue", "crash", "broken", "debug"],
            "steps": ["reproduce", "identify", "fix", "verify"]
        },
        "refactor": {
            "keywords": ["refactor", "improve", "optimize", "restructure", "clean", "modernize"],
            "steps": ["analyze", "plan_changes", "implement", "test"]
        },
        "api": {
            "keywords": ["api", "endpoint", "route", "controller", "rest", "graphql", "grpc"],
            "steps": ["define_schema", "implement_routes", "add_tests", "document"]
        },
        "frontend": {
            "keywords": ["ui", "frontend", "component", "page", "dashboard", "form", "button"],
            "steps": ["design_ui", "create_components", "add_interactivity", "test_ui"]
        },
        "database": {
            "keywords": ["database", "db", "migration", "model", "schema", "sql", "crud"],
            "steps": ["design_schema", "create_migration", "implement_model", "test_queries"]
        },
        "auth": {
            "keywords": ["auth", "login", "signup", "jwt", "oauth", "permission", "role"],
            "steps": ["design_auth", "implement_login", "add_protection", "test_auth"]
        },
        "test": {
            "keywords": ["test", "spec", "coverage", "unit", "integration", "e2e"],
            "steps": ["identify_scope", "write_tests", "run_coverage", "fix_failures"]
        },
        "deploy": {
            "keywords": ["deploy", "docker", "kubernetes", "ci/cd", "pipeline", "production"],
            "steps": ["configure_deploy", "setup_docker", "setup_ci", "deploy"]
        },
        "ml": {
            "keywords": ["ml", "machine learning", "model", "train", "predict", "ai", "nlp"],
            "steps": ["data_prep", "feature_engineering", "train_model", "evaluate"]
        },
    }
    
    def __init__(self, prompt):
        self.prompt = prompt
        self.prompt_lower = prompt.lower()
        self.detected_type = self._detect_type()
    
    def _detect_type(self):
        scores = {}
        for req_type, config in self.REQUEST_PATTERNS.items():
            score = sum(1 for kw in config["keywords"] if kw in self.prompt_lower)
            scores[req_type] = score
        return max(scores, key=scores.get) if scores and max(scores.values()) > 0 else "general"
    
    def get_config(self):
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
        s = self.explorer.structure
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
        for f in s["key_files"][:8]:
            plan += f"- `{f}`\n"
        
        plan += f"""
```

---

## Phase 2: Requirements Analysis

### What We Need to Build
{self._extract_features()}

---

## Phase 3: Implementation Steps

"""
        for i, step in enumerate(self.analyzer.get_config()["steps"], 1):
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

### Commands
```bash
# Run tests
pytest tests/ -v

# Lint
ruff check .
ruff format --check .
```

---

## Phase 6: Technology Recommendations

### Recommended Stack
```
Language: {', '.join(list(s['languages'])[:3]) or 'Python/JavaScript'}
Backend: {', '.join(list(s['frameworks'])[:2]) or 'Flask/Express'}
Database: {', '.join(list(s['databases'])[:2]) or 'SQLite/PostgreSQL'}
```

---

*🤖 Generated by Paradise Stack Planner*
*Based on: MapCoder (ACL 2024), Claude Code, KAT-Coder*
"""
        return plan
    
    def _extract_features(self):
        actions = re.findall(r'\b(add|create|build|implement|make|generate)\s+\w+', self.prompt_lower)
        return f"""Based on: "{self.prompt}"

**Core Action**: {' + '.join(set(actions)) if actions else 'build/implement'}
"""
    
    def _format_step_name(self, step):
        return ' '.join(word.capitalize() for word in step.split('_'))
    
    def _get_step_details(self, step):
        details = {
            "requirement_analysis": "- Understand user needs\n- Define acceptance criteria\n- Identify edge cases",
            "architecture_design": "- Design file structure\n- Define interfaces\n- Plan data flow",
            "implementation": "- Create/update files\n- Follow existing patterns\n- Keep code clean",
            "testing": "- Write unit tests\n- Test edge cases\n- Verify functionality",
            "reproduce": "- Create minimal reproduction\n- Identify root cause",
            "identify": "- Find affected code\n- Understand dependencies",
            "fix": "- Apply fix\n- Handle edge cases",
            "verify": "- Run tests\n- Check for regressions",
            "design_ui": "- Create mockup\n- Define components\n- Plan responsive design",
            "create_components": "- Build UI components\n- Add styling\n- Implement layouts",
            "add_interactivity": "- Add event handlers\n- Connect to API\n- Handle state",
            "test_ui": "- Test responsiveness\n- Verify accessibility\n- Cross-browser test",
            "define_schema": "- Design data model\n- Define API endpoints\n- Document validation",
            "implement_routes": "- Create handlers\n- Add validation\n- Error handling",
            "add_tests": "- Cover edge cases\n- Mock dependencies",
            "document": "- Update README\n- Add API docs",
            "design_auth": "- Choose auth method\n- Define user model\n- Plan sessions",
            "implement_login": "- Create auth endpoints\n- Add password hashing\n- Implement sessions",
            "add_protection": "- Add middleware\n- Protect routes\n- CSRF protection",
            "test_auth": "- Test login/logout\n- Test protection\n- Security audit",
            "design_schema": "- Define tables\n- Plan relationships\n- Index strategy",
            "create_migration": "- Write migration\n- Handle data\n- Rollback plan",
            "implement_model": "- Create model\n- Add relationships\n- Add validation",
            "test_queries": "- Test CRUD\n- Performance test",
            "configure_deploy": "- Set up hosting\n- Configure domains\n- SSL certificates",
            "setup_docker": "- Create Dockerfile\n- docker-compose.yml\n- Multi-stage build",
            "setup_ci": "- GitHub Actions\n- Test automation\n- Deploy pipeline",
            "deploy": "- Deploy to staging\n- Run smoke tests\n- Deploy to production",
            "data_prep": "- Load data\n- Clean data\n- Split train/test",
            "feature_engineering": "- Extract features\n- Encode data\n- Scale features",
            "train_model": "- Choose model\n- Train\n- Tune hyperparameters",
            "evaluate": "- Measure accuracy\n- Confusion matrix\n- Deploy model",
            "analyze": "- Review current code\n- Identify improvements",
            "plan_changes": "- Design new structure\n- Map old to new",
            "identify_scope": "- Find untested code\n- Prioritize",
            "write_tests": "- Unit tests\n- Integration tests",
            "run_coverage": "- Check coverage\n- Identify gaps",
            "fix_failures": "- Debug failures\n- Fix tests",
        }
        return details.get(step, "- Implement the change\n- Test thoroughly")
    
    def _suggest_new_files(self):
        files = []
        s = self.explorer.structure
        
        if "python" in s["languages"]:
            files.extend(["src/__init__.py", "src/main.py", "tests/test_main.py", "requirements.txt"])
        if "javascript" in s["languages"] or "typescript" in s["languages"]:
            files.extend(["src/index.js", "src/components/", "tests/test_main.js"])
        if "sql" in s["languages"]:
            files.extend(["migrations/001_init.sql", "migrations/002_seed.sql"])
        if "docker" in s["languages"] or "docker" in s["frameworks"]:
            files.extend(["Dockerfile", "docker-compose.yml", ".dockerignore"])
        
        files.extend(["README.md", ".gitignore", "CLAUDE.md"])
        return '\n'.join(f"- `{f}`" for f in set(files))
    
    def _suggest_modify_files(self):
        files = self.explorer.structure["key_files"][:5]
        return '\n'.join(f"- `{f}`" for f in files) if files else "- No existing files to modify"


def main():
    if len(sys.argv) < 2:
        print("Usage: planner '<prompt>'")
        print("\nSupported Types:")
        print("  feature_add, bug_fix, refactor, api, frontend")
        print("  database, auth, test, deploy, ml")
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
    
    plan_path = PROJECT_ROOT / "PLAN.md"
    with open(plan_path, 'w') as f:
        f.write(plan)
    
    print(f"\n✅ PLAN.md generated: {plan_path}")
    print(f"   Languages: {', '.join(explorer.structure['languages']) or 'None'}")
    print(f"   Frameworks: {', '.join(explorer.structure['frameworks']) or 'None'}")
    print(f"   Type: {analyzer.detected_type}")


if __name__ == '__main__':
    main()
