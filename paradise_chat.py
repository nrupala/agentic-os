"""
Paradise Stack - Interactive Agentic Chat
The core interactive system where users talk to Paradise Stack,
create plans, execute tasks, and see results in real-time.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

class ParadiseChat:
    """Enhanced Paradise Chat interface."""
    
    def __init__(self):
        self.output_dir = PROJECT_ROOT / "outputs"
        self.agent_loop = None
        self.execution_engine = None
        self.task_console = None
        
        # Initialize components if available
        try:
            from engine.agent_loop import AgentLoop
            self.agent_loop = AgentLoop()
            
            from engine.execution_engine import PDCAExecutionEngine
            self.execution_engine = PDCAExecutionEngine()
            
            from engine.task_console import TaskConsole
            self.task_console = TaskConsole()
        except Exception as e:
            print(f"Warning: Could not initialize components - {e}")
    
    def run_interactive(self):
        """Run interactive chat interface."""
        print("\nWelcome to Paradise Chat v2.0")
        print("=" * 70)
        
        # Display available commands
        self.display_commands()
        
        while True:
            try:
                cmd = input("Paradise> ").strip()
                
                if not cmd:
                    continue
                
                parts = cmd.split(maxsplit=1)
                action = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""
                
                # Handle different commands
                if action == "exit":
                    print("\nGoodbye!")
                    break
                    
                elif action == "run":
                    self.run_workflow(arg)
                    
                elif action == "list":
                    self.list_workflows()
                    
                elif action == "show":
                    self.show_workflow(arg)
                    
                elif action == "test":
                    self.test_deliverables(arg)
                    
                elif action == "upload":
                    self.upload_to_github(arg)
                    
                elif action == "outputs":
                    self.list_outputs()
                    
                elif action == "open":
                    self.open_output_dir(arg)
                    
                else:
                    print(f"Unknown command: {action}")
                    
            except Exception as e:
                print(f"Error: {e}")
    
    def display_commands(self):
        """Display available commands."""
        print("\nAvailable Commands:")
        print("  run <task>      - Run workflow (e.g., 'run Build API')")
        print("  list           - List recent workflows")
        print("  show <id>      - Show workflow details")
        print("  test <id>      - Test a deliverable")
        print("  upload <id>    - Upload to GitHub")
        print("  outputs       - List output directories")
        print("  open <path>    - Open output directory")
    
    def run_workflow(self, task):
        """Run workflow with enhanced integration."""
        try:
            # Create temporary directory for this workflow
            workflow_dir = self.output_dir / f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            workflow_dir.mkdir(exist_ok=True)
            
            # Initialize workflow manifest
            manifest = workflow_dir / "manifest.json"
            with open(manifest, 'w') as f:
                json.dump({
                    "workflow_id": f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "task": task,
                    "status": "pending",
                    "created_at": datetime.now().isoformat(),
                    "deliverables": []
                }, f)
            
            # Execute workflow through Agent Loop
            if self.agent_loop:
                result = self.agent_loop.run(task, workflow_dir=workflow_dir)
                
                # Update manifest with results
                with open(manifest, 'r') as f:
                    wf_data = json.load(f)
                wf_data["status"] = "completed"
                wf_data["output_dir"] = str(workflow_dir)
                wf_data["deliverables"] = result.get("deliverables", [])
                
                with open(manifest, 'w') as f:
                    json.dump(wf_data, f)
                
                print(f"\nWorkflow complete: {task}")
                print(f"Deliverables created in directory: {workflow_dir}")
            else:
                print("Warning: Agent Loop not available")
            
        except Exception as e:
            print(f"Error running workflow: {e}")
    
    def list_workflows(self):
        """List recent workflows."""
        try:
            workflows = []
            for wf_file in self.output_dir.glob("wf_*"):
                manifest = wf_file / "manifest.json"
                
                if manifest.exists():
                    try:
                        with open(manifest, 'r') as f:
                            wf_data = json.load(f)
                            workflows.append({
                                **wf_data,
                                "output_dir": str(wf_file)
                            })
                    except Exception:
                        pass
            
            if not workflows:
                print("No workflows found")
            else:
                for wf in sorted(workflows, key=lambda x: x.get("created_at", ""), reverse=True):
                    task_preview = wf.get('task', 'Unknown')[:50]
                    wf_id = wf.get('workflow_id', 'unknown')
                    status = wf.get('status', 'unknown')
                    print(f"[{status}]: {wf_id}: {task_preview}...")
        except Exception as e:
            print(f"Error listing workflows: {e}")
    
    def show_workflow(self, id_):
        """Show workflow details."""
        try:
            # Find matching workflow
            for wf_file in self.output_dir.glob("wf_*"):
                manifest = wf_file / "manifest.json"
                
                if manifest.exists():
                    with open(manifest, 'r') as f:
                        wf_data = json.load(f)
                    
                    if str(wf_data.get("workflow_id")) == id_:
                        print(f"\nWorkflow: {id_}")
                        print(f"Task: {wf_data['task']}")
                        print(f"Status: {wf_data['status']}")
                        print(f"Created: {wf_data['created_at'][:10]}")
                        
                        # List deliverables
                        if wf_data.get("deliverables"):
                            print("\nDeliverables:")
                            for d in wf_data["deliverables"]:
                                print(f"- {d['name']} (size: {d['size']} bytes)")
        except Exception as e:
            print(f"Error showing workflow: {e}")
    
    def test_deliverables(self, id_):
        """Test deliverable."""
        try:
            # Find matching deliverable
            for wf_file in self.output_dir.glob("wf_*"):
                manifest = wf_file / "manifest.json"
                
                if manifest.exists():
                    with open(manifest, 'r') as f:
                        wf_data = json.load(f)
                    
                    deliverables = []
                    for d in wf_data.get("deliverables", []):
                        if str(d.get("id")) == id_:
                            deliverables.append(d)
                            
                            # Test the deliverable
                            print(f"\nTesting deliverable: {d['name']}")
                            
                            # Simple test - could be enhanced later
                            try:
                                content = d["path"].read_text()
                                print(f"Content length: {len(content)} characters")
                                print("Test passed!")
                            except Exception as e:
                                print(f"Test failed: {e}")
        except Exception as e:
            print(f"Error testing deliverable: {e}")
    
    def upload_to_github(self, id_):
        """Upload to GitHub."""
        github_token = os.environ.get("GITHUB_TOKEN")
        
        if not github_token:
            print("GitHub token not set. Set with: $env:GITHUB_TOKEN = 'your_token'")
            return
            
        # Find matching deliverable
        try:
            for wf_file in self.output_dir.glob("wf_*"):
                manifest = wf_file / "manifest.json"
                
                if manifest.exists():
                    with open(manifest, 'r') as f:
                        wf_data = json.load(f)
                    
                    deliverables = []
                    for d in wf_data.get("deliverables", []):
                        if str(d.get("id")) == id_:
                            deliverables.append(d)
                            
                            # Prepare upload
                            print(f"\nPreparing to upload: {d['name']}")
                            
                            # In real implementation would use GitHub API
                            print("Upload would be processed via GitHub API")
        except Exception as e:
            print(f"Error uploading to GitHub: {e}")
    
    def list_outputs(self):
        """List output directories."""
        try:
            outputs = sorted(list(self.output_dir.glob("wf_*")), key=lambda x: x.stat().st_mtime, reverse=True)
            
            if not outputs:
                print("No output directories found")
            else:
                for out in outputs[:20]:
                    manifest = out / "manifest.json"
                    
                    if manifest.exists():
                        try:
                            with open(manifest, 'r') as f:
                                wf_data = json.load(f)
                                
                            print(f"  [{wf_data['status']:10}] {wf_data['workflow_id']}: {wf_data['task'][:50]}")
                        except Exception:
                            pass
        except Exception as e:
            print(f"Error listing outputs: {e}")
    
    def open_output_dir(self, path):
        """Open output directory."""
        try:
            # Convert to absolute path
            abs_path = Path(path).expanduser().resolve()
            
            if not abs_path.exists():
                print(f"Directory does not exist: {path}")
                return
                
            # In real environment would use system command
            print(f"\nOpening directory: {abs_path}")
        except Exception as e:
            print(f"Error opening directory: {e}")


def main():
    """Main entry point."""
    chat = ParadiseChat()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode - run tests
        try:
            from tests.test_paradise_stack import test_main
            
            print("\nRunning full test suite...")
            test_main()
            
        except Exception as e:
            print(f"Test failed: {e}")
    else:
        # Interactive mode
        chat.run_interactive()


if __name__ == '__main__':
    main()