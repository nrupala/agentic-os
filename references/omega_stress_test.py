# SPDX-License-Identifier: MIT OR Apache-2.0
import json
import os
import time
from datetime import datetime

# Configuration matching your handover spec
PROJECT_NAME = os.getenv("PROJECT_NAME", "omega_test_run")
LOG_PATH = f"projects/{PROJECT_NAME}/logs/audit_trail.jsonl"

def simulate_recursion_overload():
    """
    Simulates a high-recursion failure to test the Grafana/Loki/SMTP pipeline.
    It writes 51 logs to exceed the 50-attempt alert threshold.
    """
    print(f"🚀 [OMEGA-TEST] Initializing Integrity Validation for: {PROJECT_NAME}")
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    for i in range(1, 52):  # Triggers the >50 threshold
        event = {
            "timestamp": datetime.now().isoformat(),
            "user": "system_validator",
            "action": "ITERATION",
            "status": "FAIL",
            "details": f"Synthetic recursion stress test: {i}/50",
            "project": PROJECT_NAME
        }
        
        # Write to the JSONL audit trail
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps(event) + "\n")
        
        if i % 10 == 0:
            print(f"   [+] {i} iterations logged to audit trail...")
        
        # Minor sleep to simulate real-time log streaming
        time.sleep(0.1)

    print("\n✅ Simulation Complete.")
    print("📈 CHECK DASHBOARD: Look for the 'Recursion Efficiency' spike at http://localhost:3000")
    print("📩 CHECK EMAIL: An automated alert should arrive at your inbox shortly.")

if __name__ == "__main__":
    simulate_recursion_overload()
