#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
agentic-OS Demo: Zero Trust, Zero Knowledge, Zero Identifier Chat Server
============================================================================
This demo shows agentic-OS developing a complete secure chat system.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engine.bridge import PlanToOmegaBridge

def main():
    print("""
================================================================================
           agentic-OS DEMO: Zero Trust / Zero Knowledge Chat Server
================================================================================
""")
    
    # Define the goal - a comprehensive security-focused chat server
    goal = """
    Build a Zero Trust, Zero Knowledge, Zero Identifier Chat Server with:
    
    1. ZERO TRUST:
       - mTLS with mutual certificate validation
       - Every request authenticated and authorized
       - No implicit trust - verify everything
       - RBAC with just-in-time access
       
    2. ZERO KNOWLEDGE:
       - End-to-end encryption where server NEVER sees plaintext
       - Server only stores encrypted blobs
       - Zero-knowledge proofs for authentication
       - Private set intersection for contact discovery
       
    3. ZERO IDENTIFIER:
       - No email, phone, or personal identifiers
       - Anonymous credential system
       - Self-sovereign identity (DID/VC)
       - Ephemeral session identifiers
       
    Features:
    - Anonymous registration (proof of humanity)
    - Encrypted message storage
    - Blind key exchange
    - Forward secrecy
    - Server cannot read messages
    - Server cannot identify users
    - Metadata minimization
    """

    print("[1] Creating plan for:", goal[:100], "...")
    print()
    
    # Create bridge and run the full pipeline
    bridge = PlanToOmegaBridge("chat-demo")
    
    # Create the plan JSON
    plan_json = {
        "goal": goal.strip(),
        "request_type": "feature_add",
        "steps": [
            "design_architecture",
            "implement_crypto",
            "build_server",
            "add_client",
            "test_security"
        ],
        "files_to_create": [
            "src/crypto.py",
            "src/server.py", 
            "src/auth.py",
            "src/database.py",
            "client/chat_client.py"
        ],
        "detected_patterns": ["zero_trust", "zkp", "end_to_end_encryption"],
        "constraints": {
            "language": "python",
            "security_level": "maximum",
            "privacy": "full"
        },
        "metadata": {
            "source": "agentic-os-demo",
            "user_id": "demo-user"
        }
    }
    
    print("[2] Executing through Paradise -> Bridge -> Omega pipeline...")
    print()
    
    # Run the full execution
    result = bridge.execute(plan_json, max_iterations=5, interactive=False)
    
    print()
    print("=" * 80)
    print("EXECUTION RESULTS")
    print("=" * 80)
    print("Status:", result.status.value)
    print("Iterations:", result.iteration)
    print("Output Files:", result.output_files)
    print("User Validation:", result.user_validation)
    
    # Show generated code preview
    if result.output_files:
        print()
        print("=" * 80)
        print("GENERATED CODE PREVIEW")
        print("=" * 80)
        for f in result.output_files:
            try:
                with open(f, 'r') as file:
                    content = file.read()
                    print(f"\n--- {Path(f).name} ({len(content)} chars) ---")
                    print(content[:500] + "..." if len(content) > 500 else content)
            except:
                pass
    
    bridge.close()
    
    return result

if __name__ == "__main__":
    main()
