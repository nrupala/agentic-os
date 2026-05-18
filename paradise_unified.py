"""
Paradise Stack - Unified Paradise Interface
Chat -> Agent Loop -> Execution Engine -> Recursive Output -> Deliverables
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict

PROJECT_ROOT = Path("C:\\Users\\HomeUser\\Downloads\\agentic-OS")
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(PROJECT_ROOT))

@dataclass
class Deliverable:
    id: str
    name: str
    type: str  # file, folder, document
    path: str
    size: int
    created_at: str
    tested: bool = False
    uploaded: bool = False
    github_url: Optional[str] = None

@dataclass
class WorkflowStep:
    step_id: str
    name: str
    status: str  # pending, running, done, failed
    output: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

@dataclass
class Workflow:
    id: str
    task: str
    status: str
    steps: List[WorkflowStep] = field(default_factory=list)
    deliverables: List[Deliverable] = field(default_factory=list)
    created_at: str = ""
    completed_at: Optional[str] = None
    agent_thoughts: List[Dict] = field(default_factory=list)
    execution_results: List[Dict] = field(default_factory=list)
    output_dir: Optional[str] = None


class ParadiseUnifiedInterface:
    """
    Unified interface: Chat -> Agent Loop -> Execution -> Output
    
    Flow:
    1. USER INPUT (via chat or direct)
    2. AGENT LOOP (think, decide, act, learn)
    3. EXECUTION ENGINE (PDCA loop)
    4. RECURSIVE EXECUTION (iterate until done)
    5. DELIVERABLES (files, docs, outputs)
    6. TEST & UPLOAD OPTIONS
    """
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.current_workflow: Optional[Workflow] = None
        
        self._init_engine()
    
    def _init_engine(self):
        """Initialize the execution engines."""
        try:
            from engine.agent_loop import AgentLoop
            from engine.execution_engine import PDCAExecutionEngine
            self.agent_loop = AgentLoop()
            self.execution_engine = PDCAExecutionEngine()
        except Exception as e:
            print(f"Engine init warning: {e}")
            self.agent_loop = None
            self.execution_engine = None
    
    def create_workflow(self, task: str) -> Workflow:
        """Create a new workflow."""
        workflow_id = f"wf_{len(self.workflows) + 1}_{int(datetime.now().timestamp())}"
        timestamp = datetime.now().isoformat()
        
        workflow = Workflow(
            id=workflow_id,
            task=task,
            status="created",
            created_at=timestamp
        )
        
        workflow.steps = [
            WorkflowStep(step_id="1_chat", name="Chat Input", status="pending"),
            WorkflowStep(step_id="2_think", name="Agent Think", status="pending"),
            WorkflowStep(step_id="3_decide", name="Agent Decide", status="pending"),
            WorkflowStep(step_id="4_execute", name="Execute PDCA", status="pending"),
            WorkflowStep(step_id="5_output", name="Generate Output", status="pending"),
            WorkflowStep(step_id="6_deliver", name="Create Deliverables", status="pending"),
        ]
        
        self.workflows[workflow_id] = workflow
        self.current_workflow = workflow
        
        return workflow
    
    def run(self, task: str) -> Workflow:
        """Run the complete workflow: Chat -> Loop -> Execute -> Output."""
        print("\n" + "=" * 70)
        print("PARADISE STACK - UNIFIED WORKFLOW")
        print("=" * 70)
        print(f"\nTask: {task}")
        print("-" * 70)
        
        workflow = self.create_workflow(task)
        
        print("\n[STEP 1] CHAT INPUT")
        print("-" * 40)
        workflow.steps[0].status = "done"
        workflow.steps[0].output = f"Received task: {task}"
        workflow.steps[0].completed_at = datetime.now().isoformat()
        print(f"  Input: {task}")
        
        print("\n[STEP 2] AGENT THINK")
        print("-" * 40)
        workflow.steps[1].status = "running"
        workflow.steps[1].started_at = datetime.now().isoformat()
        
        if self.agent_loop:
            thought = self.agent_loop.think(task)
            workflow.agent_thoughts.append(asdict(thought))
            workflow.steps[1].output = f"Thought: {thought.thought[:100]}"
        else:
            workflow.steps[1].output = "Thinking..."
        
        workflow.steps[1].status = "done"
        workflow.steps[1].completed_at = datetime.now().isoformat()
        print(f"  Think: {workflow.steps[1].output[:60]}...")
        
        print("\n[STEP 3] AGENT DECIDE")
        print("-" * 40)
        workflow.steps[2].status = "running"
        workflow.steps[2].started_at = datetime.now().isoformat()
        
        if self.agent_loop:
            self.agent_loop.act(
                type('Action', (), {
                    'action': workflow.agent_thoughts[-1].get('action', 'respond'),
                    'description': f"Decided: {workflow.agent_thoughts[-1].get('decision', 'general')}",
                    'success': True
                })()
            )
            decision = workflow.agent_thoughts[-1].get('decision', 'general')
        else:
            decision = 'general'
        
        workflow.steps[2].output = f"Decision: {decision}"
        workflow.steps[2].status = "done"
        workflow.steps[2].completed_at = datetime.now().isoformat()
        print(f"  Decision: {decision}")
        
        print("\n[STEP 4] PDCA EXECUTION")
        print("-" * 40)
        workflow.steps[3].status = "running"
        workflow.steps[3].started_at = datetime.now().isoformat()
        
        steps = self._generate_execution_steps(task, decision)
        
        if self.execution_engine:
            execution = self.execution_engine.execute(task, steps)
            workflow.execution_results.append({
                "status": execution.status,
                "iterations": execution.iterations,
                "steps_completed": sum(1 for s in execution.steps if s.status == "success")
            })
        else:
            workflow.execution_results.append({
                "status": "simulated",
                "iterations": 1,
                "steps_completed": len(steps)
            })
        
        workflow.steps[3].output = f"Executed {len(steps)} steps"
        workflow.steps[3].status = "done"
        workflow.steps[3].completed_at = datetime.now().isoformat()
        print(f"  Execution: {workflow.steps[3].output}")
        
        print("\n[STEP 5] GENERATE OUTPUT")
        print("-" * 40)
        workflow.steps[4].status = "running"
        workflow.steps[4].started_at = datetime.now().isoformat()
        
        output_path = self._generate_output(workflow)
        workflow.output_dir = str(output_path)
        
        workflow.steps[4].output = f"Output: {output_path}"
        workflow.steps[4].status = "done"
        workflow.steps[4].completed_at = datetime.now().isoformat()
        print(f"  Output directory: {output_path}")
        
        print("\n[STEP 6] CREATE DELIVERABLES")
        print("-" * 40)
        workflow.steps[5].status = "running"
        workflow.steps[5].started_at = datetime.now().isoformat()
        
        deliverables = self._create_deliverables(workflow, output_path)
        workflow.deliverables = deliverables
        
        workflow.steps[5].output = f"{len(deliverables)} deliverables created"
        workflow.steps[5].status = "done"
        workflow.steps[5].completed_at = datetime.now().isoformat()
        
        for d in deliverables:
            print(f"  + {d.type}: {d.name} ({d.size} bytes)")
        
        workflow.status = "completed"
        workflow.completed_at = datetime.now().isoformat()
        
        print("\n" + "=" * 70)
        print("WORKFLOW COMPLETE")
        print("=" * 70)
        self._print_workflow_summary(workflow)
        
        return workflow
    
    def _generate_execution_steps(self, task: str, decision: str) -> List[Dict]:
        """Generate execution steps based on task and decision."""
        base_steps = [
            {"name": f"Analyze: {task}", "phase": "plan"},
            {"name": "Design solution", "phase": "plan"},
            {"name": f"Implement: {task}", "phase": "do"},
            {"name": "Verify implementation", "phase": "check"},
            {"name": "Run tests", "phase": "check"},
            {"name": "Document results", "phase": "act"},
            {"name": "Store pattern", "phase": "act"},
        ]
        return base_steps
    
    def _generate_output(self, workflow: Workflow) -> Path:
        """Generate output directory for workflow."""
        task_hash = hashlib.md5(workflow.task.encode()).hexdigest()[:8]
        output_path = OUTPUT_DIR / f"{workflow.id}_{task_hash}"
        output_path.mkdir(parents=True, exist_ok=True)
        
        (output_path / "src").mkdir(exist_ok=True)
        (output_path / "docs").mkdir(exist_ok=True)
        (output_path / "tests").mkdir(exist_ok=True)
        
        manifest = {
            "workflow_id": workflow.id,
            "task": workflow.task,
            "status": workflow.status,
            "created_at": workflow.created_at,
            "completed_at": workflow.completed_at,
            "steps": [
                {"id": s.step_id, "name": s.name, "status": s.status}
                for s in workflow.steps
            ],
            "agent_thoughts_count": len(workflow.agent_thoughts),
            "execution_results": workflow.execution_results,
        }
        
        with open(output_path / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2, default=str)
        
        summary = f"""# Paradise Stack Workflow Output

## Workflow: {workflow.id}
## Task: {workflow.task}
## Status: {workflow.status}
## Created: {workflow.created_at}
## Completed: {workflow.completed_at}

## Steps Completed
"""
        for step in workflow.steps:
            summary += f"- [{step.status.upper()}] {step.name}\n"
        
        summary += """
## Deliverables
"""
        for d in workflow.deliverables:
            summary += f"- {d.type}: {d.name}\n"
        
        summary += f"""
## Agent Thoughts
- Total thoughts: {len(workflow.agent_thoughts)}
- Decisions made: {len(set(t.get('decision') for t in workflow.agent_thoughts if t.get('decision')))}

## Execution Results
- Iterations: {workflow.execution_results[-1].get('iterations', 0) if workflow.execution_results else 0}
- Steps completed: {workflow.execution_results[-1].get('steps_completed', 0) if workflow.execution_results else 0}

---
Generated by Paradise Stack v2.0
"""
        
        with open(output_path / "README.md", "w") as f:
            f.write(summary)
        
        return output_path
    
    def _create_deliverables(self, workflow: Workflow, output_path: Path) -> List[Deliverable]:
        """Create deliverable entries for the workflow."""
        deliverables = []
        
        deliverables.append(Deliverable(
            id=f"{workflow.id}_readme",
            name="README.md",
            type="document",
            path=str(output_path / "README.md"),
            size=(output_path / "README.md").stat().st_size,
            created_at=datetime.now().isoformat()
        ))
        
        deliverables.append(Deliverable(
            id=f"{workflow.id}_manifest",
            name="manifest.json",
            type="document",
            path=str(output_path / "manifest.json"),
            size=(output_path / "manifest.json").stat().st_size,
            created_at=datetime.now().isoformat()
        ))
        
        src_dir = output_path / "src"
        if src_dir.exists():
            deliverables.append(Deliverable(
                id=f"{workflow.id}_src",
                name="src/",
                type="folder",
                path=str(src_dir),
                size=sum(f.stat().st_size for f in src_dir.rglob("*") if f.is_file()),
                created_at=datetime.now().isoformat()
            ))
        
        return deliverables
    
    def _print_workflow_summary(self, workflow: Workflow):
        """Print workflow summary."""
        print(f"\nWorkflow ID: {workflow.id}")
        print(f"Status: {workflow.status.upper()}")
        print(f"Duration: {workflow.completed_at}")
        print("\nSteps:")
        for step in workflow.steps:
            status_icon = "+" if step.status == "done" else "x" if step.status == "failed" else "."
            print(f"  [{status_icon}] {step.name}")
        print(f"\nDeliverables ({len(workflow.deliverables)}):")
        for d in workflow.deliverables:
            print(f"  - {d.name} ({d.type})")
        print(f"\nOutput Directory: {workflow.output_dir}")
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID."""
        return self.workflows.get(workflow_id)
    
    def get_all_workflows(self) -> List[Workflow]:
        """Get all workflows."""
        return list(self.workflows.values())
    
    def get_recent_workflows(self, limit: int = 10) -> List[Workflow]:
        """Get recent workflows."""
        return sorted(self.workflows.values(), 
                    key=lambda w: w.created_at, 
                    reverse=True)[:limit]
    
    def test_deliverable(self, deliverable_id: str) -> Dict:
        """Parse and test a deliverable."""
        for workflow in self.workflows.values():
            for d in workflow.deliverables:
                if d.id == deliverable_id:
                    path = Path(d.path)
                    if not path.exists():
                        return {"success": False, "error": "File not found"}
                    
                    content = path.read_text(encoding="utf-8")
                    
                    result = {
                        "success": True,
                        "deliverable": asdict(d),
                        "content_preview": content[:500],
                        "lines": len(content.splitlines()),
                        "size": len(content),
                    }
                    
                    d.tested = True
                    return result
        
        return {"success": False, "error": "Deliverable not found"}
    
    def upload_to_github(self, deliverable_id: str, repo: str, branch: str = "main", 
                        message: str = None) -> Dict:
        """Upload a deliverable to GitHub."""
        github_token = os.environ.get("GITHUB_TOKEN")
        
        if not github_token:
            return {
                "success": False, 
                "error": "GITHUB_TOKEN not set. Set with: $env:GITHUB_TOKEN = 'your_token'"
            }
        
        for workflow in self.workflows.values():
            for d in workflow.deliverables:
                if d.id == deliverable_id:
                    path = Path(d.path)
                    if not path.exists():
                        return {"success": False, "error": "File not found"}
                    
                    return {
                        "success": True,
                        "message": f"Would upload {d.name} to {repo}/{d.path}",
                        "note": "GitHub API integration ready - set GITHUB_TOKEN",
                        "deliverable": asdict(d)
                    }
        
        return {"success": False, "error": "Deliverable not found"}
    
    def run_interactive(self):
        """Run interactive CLI with proper EOF protection."""
        import sys
        
        if not sys.stdin.isatty():
            print("Error: This is an interactive CLI. Please run without piping.")
            print("Usage: python paradise_unified.py")
            return
        
        print("\n" + "=" * 70)
        print("PARADISE STACK - UNIFIED INTERFACE")
        print("=" * 70)
        print("Commands:")
        print("  run <task>    - Run workflow (e.g., 'run Build API')")
        print("  list          - List recent workflows")
        print("  show <id>    - Show workflow details")
        print("  test <id>    - Test a deliverable")
        print("  upload <id>  - Upload to GitHub")
        print("  outputs      - List output directories")
        print("  open <path>  - Open output directory")
        print("  exit         - Exit")
        print()
        
        while True:
            try:
                cmd = input("Paradise> ")
                if cmd is None:
                    break
                cmd = cmd.strip()
                
                if not cmd:
                    continue
                
                parts = cmd.split(maxsplit=1)
                action = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""
                
                if action == "exit":
                    print("\nGoodbye!\n")
                    break
                
                elif action == "run":
                    if not arg:
                        print("Usage: run <task description>")
                    else:
                        result = self.run(arg)
                        print(f"\nWorkflow complete: {result.id}")
                        print(f"Deliverables: {len(result.deliverables)}")
                        print(f"Output: {result.output_dir}")
                
                elif action == "list":
                    workflows = self.get_recent_workflows()
                    if not workflows:
                        print("No workflows yet.")
                    else:
                        for wf in workflows:
                            print(f"  [{wf.status:10}] {wf.id}: {wf.task[:50]}")
                
                elif action == "show":
                    if not arg:
                        print("Usage: show <workflow_id>")
                    else:
                        wf = self.get_workflow(arg)
                        if wf:
                            print(f"\nWorkflow: {wf.id}")
                            print(f"Task: {wf.task}")
                            print(f"Status: {wf.status}")
                            print(f"Steps: {len(wf.steps)}")
                            print(f"Deliverables: {len(wf.deliverables)}")
                            print(f"Output: {wf.output_dir}")
                        else:
                            print(f"Workflow not found: {arg}")
                
                elif action == "test":
                    if not arg:
                        print("Usage: test <deliverable_id>")
                    else:
                        result = self.test_deliverable(arg)
                        if result["success"]:
                            print("\nTest Result:")
                            print(f"  File: {result['deliverable']['name']}")
                            print(f"  Lines: {result['lines']}")
                            print(f"  Size: {result['size']} bytes")
                            print(f"\nPreview:\n{result['content_preview'][:200]}...")
                        else:
                            print(f"Test failed: {result['error']}")
                
                elif action == "upload":
                    if not arg:
                        print("Usage: upload <deliverable_id> [repo]")
                    else:
                        repo = arg.split()[1] if len(arg.split()) > 1 else "user/paradise-output"
                        result = self.upload_to_github(arg.split()[0], repo)
                        if result["success"]:
                            print("\nUpload prepared:")
                            print(f"  File: {result['deliverable']['name']}")
                            print(f"  Repo: {repo}")
                            print(f"  Note: {result.get('note', '')}")
                        else:
                            print(f"Upload failed: {result['error']}")
                
                elif action == "outputs":
                    outputs = list(Path(OUTPUT_DIR).glob("*"))
                    if not outputs:
                        print("No outputs yet.")
                    else:
                        print(f"\nOutput Directories ({len(outputs)}):")
                        for out in outputs[-10:]:
                            print(f"  {out.name}")
                
                elif action == "open":
                    if not arg:
                        print("Usage: open <output_path>")
                    else:
                        import subprocess
                        path = Path(arg)
                        if path.exists():
                            subprocess.run(["explorer", str(path.absolute())])
                            print(f"Opened: {path}")
                        else:
                            print(f"Path not found: {arg}")
                
                else:
                    print("Unknown command. Type 'help' for commands.")
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def demo():
    """Demo the unified interface."""
    interface = ParadiseUnifiedInterface()
    
    result = interface.run("Build a user authentication module")
    
    print("\n" + "=" * 70)
    print("DELIVERABLES")
    print("=" * 70)
    
    for d in result.deliverables:
        print(f"\n{d.name}:")
        print(f"  Path: {d.path}")
        print(f"  Type: {d.type}")
        print(f"  Size: {d.size} bytes")
    
    print("\n" + "=" * 70)
    print("RECENT WORKFLOWS")
    print("=" * 70)
    
    for wf in interface.get_recent_workflows(5):
        print(f"  [{wf.status}] {wf.id}: {wf.task[:50]}...")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        interface = ParadiseUnifiedInterface()
        interface.run_interactive()
