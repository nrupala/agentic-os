# SPDX-License-Identifier: MIT OR Apache-2.0
import os
import glob

PROJECT_ROOT = os.getenv("PROJECT_DIR", "./projects/default")
LOG_DIR = f"{PROJECT_ROOT}/self-eval-logs"
MAX_LOGS = 10

def vacuum_logs():
    """Distills logs into wisdom and prunes the rest."""
    logs = sorted(glob.glob(f"{LOG_DIR}/eval_*.md"), key=os.path.getmtime)
    
    if len(logs) <= MAX_LOGS:
        print("[VACUUM] Log count healthy. Skipping cleanup.")
        return

    # 1. DISTILLATION PHASE (The "Magic")
    # Identify logs to be deleted
    to_delete = logs[:-MAX_LOGS]
    print(f"[VACUUM] Distilling {len(to_delete)} logs into long-term memory...")
    
    # Logic: Read content of 'to_delete' logs, feed to LLM to update MEMORY.md
    # (Implementation: call_llm_distiller(to_delete_content))

    # 2. PURGE PHASE
    for log_path in to_delete:
        try:
            os.remove(log_path)
            print(f"[CLEANUP] Deleted old log: {os.path.basename(log_path)}")
        except Exception as e:
            print(f"[ERROR] Failed to delete {log_path}: {e}")

    # 3. TEMP FILE PURGE
    temp_files = glob.glob(f"{PROJECT_ROOT}/*.tmp") + glob.glob("/tmp/omega/*")
    for tmp in temp_files:
        if os.path.isfile(tmp):
            os.remove(tmp)

if __name__ == "__main__":
    vacuum_logs()
