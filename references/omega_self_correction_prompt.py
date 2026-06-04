# SPDX-License-Identifier: MIT OR Apache-2.0
def generate_disciplined_prompt(project_history):
    # Analyze the SQLite DB for patterns
    meta = MetaCognition("omega_state.db")
    patterns = meta.analyze_failure_patterns()
    rules = meta.derive_constraints(patterns)
    
    # Format rules into a 'Disciplined Injection'
    formatted_rules = "\n".join([f"RULE {idx+1}: {rule}" for idx, rule in enumerate(rules)])
    
    return f"""
    ### CURRENT THINKING RULES (MANDATORY):
    {formatted_rules}
    
    ### PREVIOUS LOGS:
    {patterns}
    
    Execute the next recursive step. Be disciplined. Be precise.
    """
