#!/usr/bin/env python3
"""
PHASE 7: Hierarchical Memory System
Three-tier memory architecture with WAL protocol.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

class HierarchicalMemory:
    """
    Three-tier memory:
    - SESSION-STATE.md: Active working memory (RAM)
    - Daily logs: Medium-term episodic memory
    - MEMORY.md: Long-term distilled wisdom (RAG-ready)
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.memory_dir = self.project_path / "memory"
        self.session_state = self.memory_dir / "SESSION-STATE.md"
        self.long_term = self.memory_dir / "MEMORY.md"
        self.daily_logs = self.memory_dir / "self-eval-logs"
        
        self._ensure_structure()
    
    def _ensure_structure(self):
        """Initialize memory directory structure."""
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.daily_logs.mkdir(parents=True, exist_ok=True)
        
        if not self.session_state.exists():
            self.session_state.write_text(self._default_session())
        
        if not self.long_term.exists():
            self.long_term.write_text(self._default_long_term())
    
    def _default_session(self) -> str:
        return f"""# OMEGA Session State
**Started:** {datetime.now().isoformat()}
**Status:** ACTIVE

## Current Context
- Active branch: unknown
- Iteration: 0
- Last action: init

## Pending Tasks
- None

## Recent Decisions
- None yet
"""
    
    def _default_long_term(self) -> str:
        return """# OMEGA Long-Term Memory
**Last Updated:** {datetime.now().isoformat()}

## Core Principles
- Never quit
- Always validate
- Log everything

## Patterns Learned
- None yet

## Wisdom
- Start with simple solutions
- Add complexity only when needed
"""

    def write_session_state(self, context: dict):
        """WAL Protocol: Write immediately before next tool call."""
        lines = [
            f"# OMEGA Session State",
            f"**Last Updated:** {datetime.now().isoformat()}",
            "",
            "## Current Context",
            f"- Active branch: {context.get('branch', 'unknown')}",
            f"- Iteration: {context.get('iteration', 0)}",
            f"- Last action: {context.get('last_action', 'unknown')}",
            "",
            "## Pending Tasks",
        ]
        
        for task in context.get('pending_tasks', []):
            lines.append(f"- [ ] {task}")
        
        lines.extend([
            "",
            "## Recent Decisions",
        ])
        
        for decision in context.get('decisions', []):
            lines.append(f"- {decision}")
        
        self.session_state.write_text("\n".join(lines))
    
    def append_daily_log(self, entry: str, category: str = "general"):
        """Append to daily episodic log."""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_file = self.daily_logs / f"{today}.md"
        
        timestamp = datetime.now().isoformat()
        new_entry = f"\n## {timestamp} [{category}]\n{entry}\n"
        
        with open(daily_file, "a") as f:
            f.write(new_entry)
    
    def distill_wisdom(self, lessons: list):
        """Distill lessons into long-term memory."""
        if not lessons:
            return
            
        content = self.long_term.read_text()
        
        wisdom_section = "\n\n## Wisdom\n"
        if wisdom_section in content:
            existing = content.split(wisdom_section)[1].split("\n## ")[0]
        else:
            existing = ""
        
        new_wisdom = "\n".join([f"- {lesson}" for lesson in lessons])
        
        updated = content.replace(
            f"{wisdom_section}{existing}",
            f"{wisdom_section}{new_wisdom}\n{existing}"
        )
        
        self.long_term.write_text(updated)
    
    def retrieve_relevant(self, query: str, limit: int = 5) -> list:
        """RAG-style retrieval from long-term memory."""
        if not self.long_term.exists():
            return []
        
        content = self.long_term.read_text()
        lines = content.split("\n")
        
        results = []
        query_lower = query.lower()
        
        for i, line in enumerate(lines):
            if query_lower in line.lower():
                context = lines[max(0, i-1):min(len(lines), i+3)]
                results.append("\n".join(context))
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_session_summary(self) -> dict:
        """Get current session summary."""
        if not self.session_state.exists():
            return {"status": "no_session"}
        
        content = self.session_state.read_text()
        
        return {
            "status": "active",
            "last_updated": self._extract_field(content, "Last Updated"),
            "iteration": int(self._extract_field(content, "Iteration") or 0),
            "pending_tasks": self._extract_tasks(content)
        }
    
    def _extract_field(self, content: str, field: str) -> Optional[str]:
        """Extract field value from markdown."""
        for line in content.split("\n"):
            if line.startswith(f"**{field}:**"):
                return line.split(":**")[1].strip()
        return None
    
    def _extract_tasks(self, content: str) -> list:
        """Extract pending tasks from content."""
        tasks = []
        in_tasks = False
        
        for line in content.split("\n"):
            if "Pending Tasks" in line:
                in_tasks = True
                continue
            if in_tasks and line.startswith("## "):
                break
            if in_tasks and line.strip().startswith("- ["):
                tasks.append(line.strip())
        
        return tasks


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: omega_hierarchical_memory.py <project_path> [command]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    memory = HierarchicalMemory(project_path)
    
    if len(sys.argv) >= 3:
        command = sys.argv[2]
        
        if command == "write":
            context = {
                "branch": "prod-test",
                "iteration": 5,
                "last_action": "code_review",
                "pending_tasks": ["fix_auth_bug", "add_tests"],
                "decisions": ["Use JWT for auth", "Minimize dependencies"]
            }
            memory.write_session_state(context)
            print("Session state written")
        
        elif command == "distill":
            lessons = [
                "Always validate JSON output before parsing",
                "Check API rate limits before retry loops",
                "Use exponential backoff for network calls"
            ]
            memory.distill_wisdom(lessons)
            print("Wisdom distilled")
        
        elif command == "retrieve":
            results = memory.retrieve_relevant("validation")
            print("\n".join(results) if results else "No results found")
        
        elif command == "summary":
            print(json.dumps(memory.get_session_summary(), indent=2))
    else:
        print("Commands: write, distill, retrieve, summary")
