import time
import random

def call_llm_with_discipline(prompt, meta_rules, attempts=10):
    """Binds the LLM to listen to meta_rules and handles delays patiently."""
    full_prompt = f"SYSTEM RULES: {meta_rules}\n\nUSER GOAL: {prompt}"
    
    for i in range(attempts):
        try:
            # Simulated LLM Call
            response = llm_provider.generate(full_prompt)
            return response
        except Exception:
            wait_time = (2 ** i) + random.random()
            print(f"⚠️ [DELAY] Companion is busy or API is throttled. Waiting {wait_time:.2f}s...")
            time.sleep(wait_time)
            
    raise Exception("Critical: LLM Liaison lost after maximum retries.")
