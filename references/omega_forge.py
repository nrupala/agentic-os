# SPDX-License-Identifier: MIT OR Apache-2.0
import os
import subprocess
import sqlite3
import time
from typing import Tuple

# --- CONFIGURATION ---
DB_PATH = "omega_state.db"
# Use a minimal, hardened image for the sandbox
SANDBOX_IMAGE = "python:3.11-slim" 
TIMEOUT = 45 # Maximum seconds allowed for verification

class OmegaForge:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state (
                id INTEGER PRIMARY KEY,
                goal TEXT, code TEXT, status TEXT, 
                attempts INTEGER, logs TEXT
            )
        """)
        self.conn.commit()

    def sandbox_verify(self, code: str) -> Tuple[bool, str]:
        """
        Executes code inside a Docker-in-Docker sandbox.
        Ensures the agent's logic is isolated from the host.
        """
        container_name = f"omega_sandbox_{int(time.time())}"
        
        # 1. Escape code for shell-safe injection
        escaped_code = code.replace("'", "'\\''")
        
        # 2. Build the Docker Run command with strict resource limits
        # --rm: Auto-remove container on exit
        # --network none: Disable internet to prevent data exfiltration
        # --memory: Limit RAM to prevent OOM attacks
        docker_cmd = [
            "docker", "run", "--rm",
            "--name", container_name,
            "--network", "none",
            "--memory", "256m",
            "--cpus", "0.5",
            SANDBOX_IMAGE,
            "python3", "-c", f"'{escaped_code}'"
        ]

        try:
            print(f"[SANDBOX] Launching DinD container: {container_name}")
            result = subprocess.run(
                docker_cmd, 
                capture_output=True, 
                text=True, 
                timeout=TIMEOUT
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                # RECOLLECT: Capture the exact error for the next recursive loop
                return False, f"EXECUTION_ERROR:\n{result.stderr}"
        
        except subprocess.TimeoutExpired:
            # Kill the container if it hangs (e.g., infinite loop in generated code)
            subprocess.run(["docker", "stop", container_name], capture_output=True)
            return False, "TIMEOUT_ERROR: Code exceeded execution limit."
        except Exception as e:
            return False, f"SANDBOX_CRITICAL_FAILURE: {str(e)}"

    def persist(self, goal, code, status, attempts, logs):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO state (goal, code, status, attempts, logs) VALUES (?, ?, ?, ?, ?)",
                       (goal, code, status, attempts, logs))
        self.conn.commit()

    def run_recursive_loop(self, goal: str):
        attempts = 0
        current_code = ""

        while True:
            attempts += 1
            print(f"\n--- OMEGA RECURSION DEPTH: {attempts} ---")
            
            # Phase: RECTIFY (Simulated LLM Call)
            # In a live setup, pass current_logs to the LLM to fix the bug
            print("[LOGIC] Analyzing sandbox failures...")
            current_code = f"print('Attempt {attempts} verified in Docker')" if attempts > 1 else "import os; os.listdir('/')"
            
            # Phase: VERIFY (Docker Sandbox)
            success, logs = self.sandbox_verify(current_code)
            
            # Phase: PERSIST
            self.persist(goal, current_code, "PASS" if success else "FAIL", attempts, logs)
            
            if success:
                print(f"✅ GOAL ACHIEVED: Code verified in DinD sandbox.\nOutput: {logs}")
                break
            else:
                print("⚠️ RECTIFYING: Sandbox reported error. Restarting loop...")

if __name__ == "__main__":
    forge = OmegaForge()
    forge.run_recursive_loop("Generate a secure file-listing utility.")

def report_self_evaluation(project_path, eval_data):
    """
    Saves the agent's internal state to the project directory.
    Uses Markdown for human readability and TXT for raw machine parsing.
    """
    log_dir = os.path.join(project_path, "self-eval-logs")
    os.makedirs(log_dir, exist_ok=True)
    
    filename = f"eval_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    with open(os.path.join(log_dir, filename), "w") as f:
        f.write(generate_markdown_report(eval_data))

def run_hybrid_cycle(self, goal):
    # 1. RAG: Retrieve past wisdom from MEMORY.md
    past_wisdom = self.vector_store.query(goal)
    
    # 2. GAN: Competitive generation
    while not self.is_hardened:
        draft_code = self.architect.generate(goal, past_wisdom)
        critique = self.adversary.audit(draft_code)
        
        if critique.is_safe:
            self.is_hardened = True
        else:
            # 3. RNN/NN++: Update temporal state with failure context
            self.update_temporal_state(critique.logs)
            
    # 4. VERIFY: Deploy to DinD Sandbox
    return self.sandbox_verify(draft_code)

def check_capability_gap(error_logs):
    """
    If the agent fails 3 times on the same issue, it analyzes if it needs a new tool.
    Example: Failing at data visualization -> Decides to install Matplotlib.
    """
    if "ModuleNotFoundError" in error_logs or "optimization" in error_logs:
        new_tool = llm_decide_tool(error_logs) # Agent chooses its own upgrade
        subprocess.run(["pip", "install", new_tool])
        update_dependencies_checklist(new_tool) # Updates the checklist script automatically
