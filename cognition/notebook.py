#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
Paradise Notebook System - Interactive Development Sessions
Inspired by marimo's notebook model

Features adopted from marimo:
- Pure Python storage (.py files)
- Reactive execution
- UI elements for interactivity
- App mode (run as web app)
- Script mode (run as CLI)
- No hidden state
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum

PROJECT_ROOT = Path(os.environ.get("HOST_PROJECT_ROOT", "/app"))
sys.path.insert(0, str(PROJECT_ROOT))


class ElementType(Enum):
    TEXT = "text"
    SLIDER = "slider"
    BUTTON = "button"
    DROPDOWN = "dropdown"
    INPUT = "input"
    TABLE = "table"
    PLOT = "plot"
    MARKDOWN = "markdown"
    CODE = "code"


@dataclass
class UIElement:
    """Interactive UI element (like marimo's mo.ui.*)"""
    name: str
    element_type: ElementType
    value: Any = None
    label: str = ""
    options: list = field(default_factory=list)
    min_value: float = 0
    max_value: float = 100
    step: float = 1
    on_change: Optional[str] = None
    enabled: bool = True
    hidden: bool = False
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.element_type.value,
            "value": self.value,
            "label": self.label,
            "options": self.options,
            "min": self.min_value,
            "max": self.max_value,
            "step": self.step,
            "enabled": self.enabled,
            "hidden": self.hidden,
        }


class ParadiseUI:
    """Paradise UI Elements (like marimo's mo.ui.*)"""
    
    @staticmethod
    def slider(
        name: str,
        label: str = "",
        value: float = 50,
        min_value: float = 0,
        max_value: float = 100,
        step: float = 1,
    ) -> UIElement:
        return UIElement(
            name=name,
            element_type=ElementType.SLIDER,
            value=value,
            label=label,
            min_value=min_value,
            max_value=max_value,
            step=step,
        )
    
    @staticmethod
    def button(name: str, label: str = "", on_click: str = "") -> UIElement:
        return UIElement(
            name=name,
            element_type=ElementType.BUTTON,
            label=label,
            on_change=on_click,
        )
    
    @staticmethod
    def text(name: str, label: str = "", value: str = "") -> UIElement:
        return UIElement(
            name=name,
            element_type=ElementType.TEXT,
            value=value,
            label=label,
        )
    
    @staticmethod
    def dropdown(
        name: str,
        label: str = "",
        options: list = None,
        value: Any = None,
    ) -> UIElement:
        return UIElement(
            name=name,
            element_type=ElementType.DROPDOWN,
            value=value or (options[0] if options else None),
            label=label,
            options=options or [],
        )
    
    @staticmethod
    def table(name: str, data: list = None) -> UIElement:
        return UIElement(
            name=name,
            element_type=ElementType.TABLE,
            value=data or [],
        )
    
    @staticmethod
    def code(name: str, code: str = "") -> UIElement:
        return UIElement(
            name=name,
            element_type=ElementType.CODE,
            value=code,
        )
    
    @staticmethod
    def markdown(content: str) -> UIElement:
        return UIElement(
            name="md",
            element_type=ElementType.MARKDOWN,
            value=content,
        )


class NotebookCell:
    """A single cell in the Paradise notebook"""
    
    def __init__(
        self,
        cell_id: str,
        code: str,
        refs: list[str] = None,
        defs: list[str] = None,
    ):
        self.id = cell_id
        self.code = code
        self.refs = refs or []
        self.defs = defs or []
        self.output = None
        self.error = None
        self.last_run = None
        self.run_count = 0
        self.is_stale = False
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "refs": self.refs,
            "defs": self.defs,
            "output": self.output,
            "error": self.error,
            "last_run": self.last_run,
            "run_count": self.run_count,
            "is_stale": self.is_stale,
        }


class ParadiseNotebook:
    """
    Paradise Notebook - A marimo-inspired reactive notebook
    
    Key features:
    - Pure Python storage
    - Reactive execution
    - Interactive UI elements
    - App and script modes
    - No hidden state
    - DAG-based execution
    """
    
    def __init__(self, notebook_id: Optional[str] = None):
        self.id = notebook_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.name = f"notebook_{self.id}"
        self.cells: dict[str, NotebookCell] = {}
        self.variables: dict[str, Any] = {}
        self.ui_elements: dict[str, UIElement] = {}
        self.outputs: list[Any] = []
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "author": "Paradise Stack",
            "version": "1.0",
        }
        self.mode = "notebook"
        self.lazy_mode = False
    
    def add_cell(self, code: str, refs: list[str] = None, defs: list[str] = None) -> NotebookCell:
        """Add a new cell to the notebook"""
        import uuid
        cell_id = str(uuid.uuid4())[:8]
        cell = NotebookCell(cell_id, code, refs, defs)
        self.cells[cell_id] = cell
        self._update_metadata()
        return cell
    
    def remove_cell(self, cell_id: str):
        """Remove a cell and clean up its variables"""
        if cell_id not in self.cells:
            return
        
        cell = self.cells[cell_id]
        for var in cell.defs:
            if var in self.variables:
                del self.variables[var]
        
        del self.cells[cell_id]
        self._update_metadata()
    
    def add_ui_element(self, element: UIElement):
        """Add a UI element"""
        self.ui_elements[element.name] = element
        self.variables[element.name] = element.value
    
    def get_ui_value(self, name: str) -> Any:
        """Get value of a UI element"""
        if name in self.ui_elements:
            return self.ui_elements[name].value
        return None
    
    def set_ui_value(self, name: str, value: Any):
        """Set value of a UI element"""
        if name in self.ui_elements:
            self.ui_elements[name].value = value
            self.variables[name] = value
            self._invalidate_dependents(name)
    
    def _update_metadata(self):
        """Update notebook metadata"""
        self.metadata["last_modified"] = datetime.now().isoformat()
    
    def _invalidate_dependents(self, var_name: str):
        """Mark cells that use this variable as stale"""
        for cell in self.cells.values():
            if var_name in cell.refs:
                cell.is_stale = True
    
    def execute_cell(self, cell_id: str) -> bool:
        """Execute a single cell"""
        if cell_id not in self.cells:
            return False
        
        cell = self.cells[cell_id]
        
        for ref in cell.refs:
            if ref not in self.variables:
                self.variables[ref] = None
        
        try:
            local_vars = {k: v for k, v in self.variables.items()}
            exec(cell.code, {}, local_vars)
            
            for var in cell.defs:
                if var in local_vars:
                    self.variables[var] = local_vars[var]
                    cell.output = local_vars[var]
            
            cell.error = None
            cell.last_run = datetime.now().isoformat()
            cell.run_count += 1
            cell.is_stale = False
            
            self._update_metadata()
            return True
            
        except Exception as e:
            cell.error = str(e)
            cell.is_stale = False
            return False
    
    def execute_all(self) -> dict:
        """Execute all cells in dependency order"""
        results = {"executed": [], "failed": [], "errors": []}
        
        sorted_cells = self._topological_sort()
        
        for cell_id in sorted_cells:
            success = self.execute_cell(cell_id)
            if success:
                results["executed"].append(cell_id)
            else:
                results["failed"].append(cell_id)
                results["errors"].append({
                    "cell_id": cell_id,
                    "error": self.cells[cell_id].error,
                })
        
        return results
    
    def _topological_sort(self) -> list[str]:
        """Get cells in topological order based on dependencies"""
        visited = set()
        order = []
        
        def visit(cell_id: str):
            if cell_id in visited:
                return
            visited.add(cell_id)
            
            cell = self.cells.get(cell_id)
            if not cell:
                return
            
            for ref in cell.refs:
                for other_id, other_cell in self.cells.items():
                    if ref in other_cell.defs and other_id != cell_id:
                        visit(other_id)
            
            order.append(cell_id)
        
        for cell_id in self.cells:
            visit(cell_id)
        
        return order
    
    def run_app(self):
        """Run notebook as a web app (like marimo run)"""
        self.mode = "app"
        print("🏃 Running as app...")
        return self._serve_app()
    
    def run_script(self, args: list[str] = None):
        """Run notebook as a script (like python notebook.py)"""
        self.mode = "script"
        print("📜 Running as script...")
        return self.execute_all()
    
    def _serve_app(self):
        """Serve notebook as web app"""
        return {
            "status": "running",
            "mode": "app",
            "notebook_id": self.id,
            "cells": len(self.cells),
            "ui_elements": [e.to_dict() for e in self.ui_elements.values()],
        }
    
    def to_python_file(self) -> str:
        """Export notebook as Python file (like marimo)"""
        lines = [
            '"""',
            f"Paradise Notebook: {self.name}",
            f"Created: {self.metadata['created_at']}",
            f"Mode: {self.mode}",
            '"""',
            "",
            "import marimo as mo",
            "import paradise as para",
            "",
        ]
        
        for element in self.ui_elements.values():
            if element.element_type == ElementType.SLIDER:
                lines.append(f"{element.name} = mo.ui.slider(")
                lines.append(f"    label='{element.label}',")
                lines.append(f"    value={element.value},")
                lines.append(f"    min={element.min_value},")
                lines.append(f"    max={element.max_value},")
                lines.append(")")
                lines.append("")
            elif element.element_type == ElementType.BUTTON:
                lines.append(f"{element.name} = mo.ui.run_button(")
                lines.append(f"    label='{element.label}',")
                lines.append(")")
                lines.append("")
            elif element.element_type == ElementType.DROPDOWN:
                lines.append(f"{element.name} = mo.ui.dropdown(")
                lines.append(f"    label='{element.label}',")
                lines.append(f"    options={element.options},")
                lines.append(")")
                lines.append("")
        
        for cell in self.cells.values():
            lines.append(f"# Cell {cell.id}")
            for line in cell.code.split("\n"):
                lines.append(line)
            lines.append("")
        
        return "\n".join(lines)
    
    def save(self, filepath: Path = None) -> Path:
        """Save notebook to Python file"""
        filepath = filepath or (PROJECT_ROOT / "notebooks" / f"{self.name}.py")
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w") as f:
            f.write(self.to_python_file())
        
        return filepath
    
    @classmethod
    def load(cls, filepath: Path) -> "ParadiseNotebook":
        """Load notebook from Python file"""
        with open(filepath, "r") as f:
            f.read()
        
        notebook = cls()
        notebook.name = filepath.stem
        
        return notebook
    
    def get_dashboard_data(self) -> dict:
        """Get data for dashboard visualization"""
        return {
            "notebook": {
                "id": self.id,
                "name": self.name,
                "mode": self.mode,
                "lazy_mode": self.lazy_mode,
                "metadata": self.metadata,
            },
            "cells": {
                "total": len(self.cells),
                "stale": sum(1 for c in self.cells.values() if c.is_stale),
                "run_counts": {cid: c.run_count for cid, c in self.cells.items()},
            },
            "variables": list(self.variables.keys()),
            "ui_elements": [e.to_dict() for e in self.ui_elements.values()],
        }


class DevelopmentSession:
    """Interactive development session (like a marimo session)"""
    
    def __init__(self):
        self.notebook = ParadiseNotebook()
        self.history = []
        self.checkpoints = []
    
    def create_cell(self, code: str) -> NotebookCell:
        """Create a new cell with auto-detected refs and defs"""
        refs = self._extract_refs(code)
        defs = self._extract_defs(code)
        
        cell = self.notebook.add_cell(code, refs, defs)
        self.history.append({
            "action": "create_cell",
            "cell_id": cell.id,
            "timestamp": datetime.now().isoformat(),
        })
        
        return cell
    
    def _extract_refs(self, code: str) -> list[str]:
        """Extract variable references from code"""
        refs = set()
        reserved = {"def", "class", "import", "for", "while", "if", "else", "elif", "try", "except", "finally", "with", "as", "return", "yield", "raise", "pass", "break", "continue", "and", "or", "not", "in", "is", "lambda", "True", "False", "None"}
        
        words = code.split()
        for word in words:
            clean = word.strip("()[]{}.,;:=!<>+-*/%@#$^&|~")
            if clean and clean not in reserved and clean[0].islower() and clean.isalnum():
                if not clean.startswith("_"):
                    refs.add(clean)
        
        return list(refs)
    
    def _extract_defs(self, code: str) -> list[str]:
        """Extract variable definitions from code"""
        defs = set()
        
        import re
        for match in re.finditer(r'^(\w+)\s*=', code, re.MULTILINE):
            var = match.group(1)
            if not var.startswith("_") and var[0].islower():
                defs.add(var)
        
        return list(defs)
    
    def checkpoint(self, name: str = ""):
        """Create a checkpoint"""
        checkpoint = {
            "name": name or f"checkpoint_{len(self.checkpoints)}",
            "timestamp": datetime.now().isoformat(),
            "cells": {cid: c.to_dict() for cid, c in self.notebook.cells.items()},
            "variables": dict(self.notebook.variables),
        }
        self.checkpoints.append(checkpoint)
        return checkpoint
    
    def restore(self, checkpoint_index: int):
        """Restore to a checkpoint"""
        if checkpoint_index >= len(self.checkpoints):
            return False
        
        checkpoint = self.checkpoints[checkpoint_index]
        self.notebook.cells = {
            cid: NotebookCell(
                cell["id"],
                cell["code"],
                cell["refs"],
                cell["defs"],
            )
            for cid, cell in checkpoint["cells"].items()
        }
        self.notebook.variables = dict(checkpoint["variables"])
        
        self.history.append({
            "action": "restore",
            "checkpoint": checkpoint["name"],
            "timestamp": datetime.now().isoformat(),
        })
        
        return True
    
    def run(self) -> dict:
        """Run the development session"""
        return self.notebook.execute_all()


_notebook_instance = None


def get_notebook() -> ParadiseNotebook:
    global _notebook_instance
    if _notebook_instance is None:
        _notebook_instance = ParadiseNotebook()
    return _notebook_instance


def create_session() -> DevelopmentSession:
    """Create a new development session"""
    return DevelopmentSession()


def main():
    print("📓 Paradise Notebook System")
    print("=" * 50)
    
    notebook = get_notebook()
    
    notebook.add_ui_element(ParadiseUI.slider(
        name="iterations",
        label="Max Iterations",
        value=10,
        min_value=1,
        max_value=20,
    ))
    
    notebook.add_ui_element(ParadiseUI.button(
        name="run_pipeline",
        label="Run Development Pipeline",
    ))
    
    notebook.add_ui_element(ParadiseUI.dropdown(
        name="agent",
        label="Select Agent",
        options=["planner", "implementer", "guardian", "executor", "improver"],
        value="planner",
    ))
    
    session = create_session()
    
    session.create_cell("""
prompt = "Create a REST API"
iterations = 10
""")
    
    session.create_cell("""
def plan(prompt):
    return f"Plan for: {prompt}"
""")
    
    session.create_cell("""
result = plan(prompt)
print(f"Result: {result}")
""")
    
    print("\n📊 Session Data:")
    print(json.dumps(session.notebook.get_dashboard_data(), indent=2, default=str))
    
    print("\n📄 Generated Python File:")
    print(notebook.to_python_file()[:500] + "...")


if __name__ == "__main__":
    main()
