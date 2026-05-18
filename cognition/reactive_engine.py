#!/usr/bin/env python3
"""
Paradise Reactive Engine - DAG-based Reactive Execution
Inspired by marimo's reactive programming model

Key concepts adopted:
- Cells = Agents/Tasks as reactive units
- DAG = Dependency graph for execution order
- No Hidden State = Automatic cleanup
- Lazy/Stale Mode = Manual trigger with state marking
- Reactive Execution = Run dependents when source changes
"""

import json
import uuid
from datetime import datetime
from typing import Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


class CellState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    STALE = "stale"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class Cell:
    """A reactive cell - the fundamental unit of execution"""
    id: str
    name: str
    code: str
    refs: list[str] = field(default_factory=list)
    defs: list[str] = field(default_factory=list)
    state: CellState = CellState.IDLE
    output: Any = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_run: Optional[str] = None
    run_count: int = 0
    
    def invalidate(self):
        """Mark cell and all dependents as stale"""
        self.state = CellState.STALE
    
    def run(self, func: Callable):
        """Execute the cell's function"""
        self.state = CellState.RUNNING
        try:
            self.output = func()
            self.state = CellState.COMPLETED
            self.last_run = datetime.now().isoformat()
            self.run_count += 1
            self.error = None
            return True
        except Exception as e:
            self.state = CellState.ERROR
            self.error = str(e)
            return False
    
    def clear_output(self):
        """Clear output and mark as idle"""
        self.output = None
        self.error = None
        self.state = CellState.IDLE


class DAG:
    """Directed Acyclic Graph for reactive execution ordering"""
    
    def __init__(self):
        self.nodes: dict[str, Cell] = {}
        self.edges: dict[str, set[str]] = defaultdict(set)
        self.reverse_edges: dict[str, set[str]] = defaultdict(set)
    
    def add_node(self, cell: Cell):
        """Add a cell to the DAG"""
        self.nodes[cell.id] = cell
        self._compute_edges(cell)
    
    def remove_node(self, cell_id: str):
        """Remove a cell and its edges"""
        if cell_id not in self.nodes:
            return
        
        for ref in self.nodes[cell_id].refs:
            if ref in self.reverse_edges:
                self.reverse_edges[ref].discard(cell_id)
        
        for target in self.edges[cell_id]:
            if target in self.reverse_edges:
                self.reverse_edges[target].discard(cell_id)
        
        del self.nodes[cell_id]
        del self.edges[cell_id]
        if cell_id in self.reverse_edges:
            del self.reverse_edges[cell_id]
    
    def _compute_edges(self, cell: Cell):
        """Compute edges based on refs and defs"""
        for target_id, target in self.nodes.items():
            if target_id == cell.id:
                continue
            
            if any(ref in target.defs for ref in cell.refs):
                self.edges[cell.id].add(target_id)
                self.reverse_edges[target_id].add(cell.id)
    
    def get_execution_order(self, cell_id: str) -> list[str]:
        """Get topological order for executing a cell and its dependents"""
        if cell_id not in self.nodes:
            return []
        
        visited = set()
        order = []
        
        def dfs(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)
            for dep in self.reverse_edges.get(node_id, []):
                dfs(dep)
            order.append(node_id)
        
        dfs(cell_id)
        return order
    
    def get_ancestors(self, cell_id: str) -> set[str]:
        """Get all cells that this cell depends on"""
        ancestors = set()
        
        def dfs(node_id: str):
            for dep in self.reverse_edges.get(node_id, []):
                if dep not in ancestors:
                    ancestors.add(dep)
                    dfs(dep)
        
        dfs(cell_id)
        return ancestors
    
    def get_descendants(self, cell_id: str) -> set[str]:
        """Get all cells that depend on this cell"""
        descendants = set()
        
        def dfs(node_id: str):
            for target in self.edges.get(node_id, []):
                if target not in descendants:
                    descendants.add(target)
                    dfs(target)
        
        dfs(cell_id)
        return descendants


class ReactiveEngine:
    """
    Reactive execution engine inspired by marimo
    
    Key features:
    - DAG-based execution ordering
    - Reactive cell updates
    - No hidden state (automatic cleanup)
    - Lazy/stale mode
    - Variable dependency tracking
    """
    
    def __init__(self, lazy_mode: bool = False):
        self.dag = DAG()
        self.variables: dict[str, Any] = {}
        self.lazy_mode = lazy_mode
        self.execution_log = []
        self._cell_functions: dict[str, Callable] = {}
    
    def register_cell(
        self,
        name: str,
        code: str,
        refs: list[str],
        defs: list[str],
        func: Callable,
    ) -> Cell:
        """Register a new reactive cell"""
        cell_id = str(uuid.uuid4())[:8]
        cell = Cell(
            id=cell_id,
            name=name,
            code=code,
            refs=refs,
            defs=defs,
        )
        
        self.dag.add_node(cell)
        self._cell_functions[cell_id] = func
        
        for var in defs:
            self.variables[var] = None
        
        return cell
    
    def update_cell(self, cell_id: str, code: str, refs: list[str], defs: list[str]):
        """Update a cell - invalidates dependents"""
        if cell_id not in self.dag.nodes:
            return
        
        cell = self.dag.nodes[cell_id]
        cell.code = code
        cell.refs = refs
        cell.defs = defs
        
        self._recompute_edges()
        self.invalidate_cell(cell_id)
    
    def remove_cell(self, cell_id: str):
        """Remove a cell - cleans up variables"""
        if cell_id not in self.dag.nodes:
            return
        
        cell = self.dag.nodes[cell_id]
        
        for var in cell.defs:
            if var in self.variables:
                del self.variables[var]
        
        self.dag.remove_node(cell_id)
        
        if cell_id in self._cell_functions:
            del self._cell_functions[cell_id]
    
    def _recompute_edges(self):
        """Recompute DAG edges after cell update"""
        self.dag.edges.clear()
        self.dag.reverse_edges.clear()
        
        for cell_id, cell in self.dag.nodes.items():
            for target_id, target in self.dag.nodes.items():
                if target_id == cell_id:
                    continue
                
                if any(ref in target.defs for ref in cell.refs):
                    self.dag.edges[cell_id].add(target_id)
                    self.dag.reverse_edges[target_id].add(cell_id)
    
    def invalidate_cell(self, cell_id: str):
        """Mark cell and all its dependents as stale"""
        if cell_id not in self.dag.nodes:
            return
        
        cell = self.dag.nodes[cell_id]
        cell.invalidate()
        
        for descendant_id in self.dag.get_descendants(cell_id):
            if descendant_id in self.dag.nodes:
                self.dag.nodes[descendant_id].invalidate()
    
    def run_cell(self, cell_id: str) -> bool:
        """Run a single cell and update its dependents"""
        if cell_id not in self.dag.nodes:
            return False
        
        cell = self.dag.nodes[cell_id]
        
        for ref in cell.refs:
            if ref not in self.variables:
                self.variables[ref] = None
        
        func = self._cell_functions.get(cell_id)
        if func:
            success = cell.run(lambda: func(**{v: self.variables.get(v) for v in cell.refs}))
        else:
            cell.state = CellState.COMPLETED
            success = True
        
        if success:
            for var in cell.defs:
                self.variables[var] = cell.output
        
        self.execution_log.append({
            "cell_id": cell_id,
            "cell_name": cell.name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "state": cell.state.value,
        })
        
        return success
    
    def run_dependents(self, cell_id: str) -> dict:
        """Run a cell and all its dependent cells (reactive behavior)"""
        if cell_id not in self.dag.nodes:
            return {"error": "Cell not found"}
        
        execution_order = self.dag.get_execution_order(cell_id)
        results = {
            "executed": [],
            "failed": [],
            "stale_remaining": [],
        }
        
        for cid in execution_order:
            if cid == cell_id:
                continue
            
            cell = self.dag.nodes[cid]
            if cell.state == CellState.STALE:
                success = self.run_cell(cid)
                if success:
                    results["executed"].append(cid)
                else:
                    results["failed"].append(cid)
            elif cell.state == CellState.IDLE and not self.lazy_mode:
                success = self.run_cell(cid)
                if success:
                    results["executed"].append(cid)
        
        stale_count = sum(
            1 for c in self.dag.nodes.values() 
            if c.state == CellState.STALE
        )
        results["stale_remaining"] = stale_count
        
        return results
    
    def run_all(self) -> dict:
        """Run all cells in proper DAG order"""
        results = {"executed": [], "failed": [], "errors": []}
        
        sorted_cells = []
        for cell_id in self.dag.nodes:
            for dep_id in self.dag.get_execution_order(cell_id):
                if dep_id not in sorted_cells:
                    sorted_cells.append(dep_id)
        
        for cell_id in sorted_cells:
            cell = self.dag.nodes[cell_id]
            success = self.run_cell(cell_id)
            if success:
                results["executed"].append(cell_id)
            else:
                results["failed"].append(cell_id)
                results["errors"].append({
                    "cell_id": cell_id,
                    "error": cell.error,
                })
        
        return results
    
    def get_state(self) -> dict:
        """Get current state of the reactive engine"""
        return {
            "total_cells": len(self.dag.nodes),
            "lazy_mode": self.lazy_mode,
            "total_variables": len(self.variables),
            "stale_cells": sum(1 for c in self.dag.nodes.values() if c.state == CellState.STALE),
            "running_cells": sum(1 for c in self.dag.nodes.values() if c.state == CellState.RUNNING),
            "completed_cells": sum(1 for c in self.dag.nodes.values() if c.state == CellState.COMPLETED),
            "error_cells": sum(1 for c in self.dag.nodes.values() if c.state == CellState.ERROR),
            "execution_log_count": len(self.execution_log),
        }
    
    def get_dag_visualization(self) -> dict:
        """Get DAG structure for visualization"""
        return {
            "nodes": [
                {
                    "id": cell.id,
                    "name": cell.name,
                    "state": cell.state.value,
                    "refs": cell.refs,
                    "defs": cell.defs,
                }
                for cell in self.dag.nodes.values()
            ],
            "edges": [
                {"from": source, "to": target}
                for source, targets in self.dag.edges.items()
                for target in targets
            ],
        }
    
    def to_python_file(self) -> str:
        """Export to a marimo-style Python file"""
        lines = [
            "# Paradise Stack - Reactive Session",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Lazy Mode: {self.lazy_mode}",
            "",
            "import marimo as mo",
            "",
        ]
        
        for cell in self.dag.nodes.values():
            lines.append(f"# Cell: {cell.name}")
            lines.append(f"# State: {cell.state.value}")
            lines.append(f"# Refs: {cell.refs}")
            lines.append(f"# Defs: {cell.defs}")
            lines.append(cell.code)
            lines.append("")
        
        return "\n".join(lines)
    
    def from_python_file(self, code: str):
        """Import from a marimo-style Python file"""
        pass


class ReactiveOrchestrator:
    """Orchestrator using reactive execution for Paradise Stack"""
    
    def __init__(self):
        self.engine = ReactiveEngine(lazy_mode=True)
        self._setup_agents()
    
    def _setup_agents(self):
        """Set up reactive cells for each agent"""
        
        def planner_func(**deps):
            return {"plan": "Generated plan"}
        
        self.planner_cell = self.engine.register_cell(
            name="planner",
            code="def planner(): return {'plan': 'Generated plan'}",
            refs=[],
            defs=["plan"],
            func=planner_func,
        )
        
        def implement_func(**deps):
            return {"code": f"Code implementing: {deps.get('plan', '')}"}
        
        self.implement_cell = self.engine.register_cell(
            name="implementer",
            code="def implement(plan): return {'code': 'Implementation'}",
            refs=["plan"],
            defs=["code"],
            func=implement_func,
        )
        
        def guardian_func(**deps):
            return {"issues": [], "quality": 1.0}
        
        self.guardian_cell = self.engine.register_cell(
            name="guardian",
            code="def guardian(code): return {'issues': [], 'quality': 1.0}",
            refs=["code"],
            defs=["issues", "quality"],
            func=guardian_func,
        )
        
        def executor_func(**deps):
            return {"tests_passed": True, "coverage": 0.8}
        
        self.executor_cell = self.engine.register_cell(
            name="executor",
            code="def executor(code): return {'tests_passed': True}",
            refs=["code"],
            defs=["tests_passed", "coverage"],
            func=executor_func,
        )
        
        def improver_func(**deps):
            return {"improved": True}
        
        self.improver_cell = self.engine.register_cell(
            name="improver",
            code="def improver(issues): return {'improved': True}",
            refs=["issues"],
            defs=["improved"],
            func=improver_func,
        )
    
    def run_full_pipeline(self, prompt: str) -> dict:
        """Run the full development pipeline reactively"""
        
        print("🔄 Reactive Pipeline Execution")
        print("=" * 40)
        
        results = {
            "prompt": prompt,
            "cells_executed": [],
            "final_state": {},
        }
        
        self.engine.run_cell(self.planner_cell.id)
        results["cells_executed"].append(self.planner_cell.name)
        
        self.engine.run_dependents(self.planner_cell.id)
        results["cells_executed"].append(self.implement_cell.name)
        
        self.engine.run_cell(self.guardian_cell.id)
        results["cells_executed"].append(self.guardian_cell.name)
        
        self.engine.run_cell(self.executor_cell.id)
        results["cells_executed"].append(self.executor_cell.name)
        
        results["final_state"] = self.engine.get_state()
        
        return results
    
    def get_visualization_data(self) -> dict:
        """Get data for visualization"""
        return {
            "dag": self.engine.get_dag_visualization(),
            "state": self.engine.get_state(),
            "variables": self.engine.variables,
        }


_engine = None


def get_reactive_engine() -> ReactiveEngine:
    global _engine
    if _engine is None:
        _engine = ReactiveEngine(lazy_mode=False)
    return _engine


def main():
    print("🧠 Paradise Reactive Engine")
    print("=" * 50)
    
    engine = get_reactive_engine()
    
    def add(a: int, b: int) -> int:
        return a + b
    
    def multiply(result: int, c: int) -> int:
        return result * c
    
    def display(value: int) -> str:
        return f"Final result: {value}"
    
    cell1 = engine.register_cell(
        name="add",
        code="def add(a, b): return a + b",
        refs=["a", "b"],
        defs=["result"],
        func=add,
    )
    
    cell2 = engine.register_cell(
        name="multiply",
        code="def multiply(result, c): return result * c",
        refs=["result", "c"],
        defs=["product"],
        func=multiply,
    )
    
    cell3 = engine.register_cell(
        name="display",
        code="def display(value): return f'Final: {value}'",
        refs=["product"],
        defs=["output"],
        func=display,
    )
    
    engine.variables["a"] = 5
    engine.variables["b"] = 3
    engine.variables["c"] = 2
    
    print("\n📊 Initial State:")
    print(json.dumps(engine.get_state(), indent=2))
    
    print("\n🔄 Running pipeline:")
    engine.run_cell(cell1.id)
    print(f"   ✓ Ran {cell1.name}")
    
    dependents = engine.run_dependents(cell1.id)
    print(f"   ✓ Ran dependents: {dependents['executed']}")
    
    print("\n📊 Final State:")
    print(f"   Variables: {engine.variables}")
    
    print("\n🔗 DAG Structure:")
    print(json.dumps(engine.get_dag_visualization(), indent=2))


if __name__ == "__main__":
    main()
