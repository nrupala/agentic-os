#!/bin/bash
# OMEGA-CODE Seamless Execution Engine
# Purpose: Persistence, Atomic Versioning, and Fault Tolerance.

PROJECT_DIR="./projects/${PROJECT_NAME}"
LOG_DIR="${PROJECT_DIR}/logs"
SRC_DIR="${PROJECT_DIR}/src"
RETRY_DELAY=5
MAX_RETRIES=10

# 1. ATOMIC INITIALIZATION
init_project() {
    if [ ! -d "${SRC_DIR}/.git" ]; then
        mkdir -p "${SRC_DIR}"
        git init "${SRC_DIR}"
        echo "Omega Engine Initialized" > "${SRC_DIR}/README.md"
        git -C "${SRC_DIR}" add .
        git -C "${SRC_DIR}" commit -m "OMEGA: Initializing persistent state"
    fi
}

# 2. SEAMLESS LLM CALL (With Patience & Retry Logic)
call_llm_with_patience() {
    local attempt=1
    local success=false
    local output=""

    while [ "$success" = false ] && [ $attempt -le $MAX_RETRIES ]; do
        # Call the core python logic (your LLM integration)
        output=$(python3 /app/omega_forge.py --project "${PROJECT_NAME}" 2>&1)
        
        if [[ $output == *"LLM_DELAY"* || $output == *"RATE_LIMIT"* ]]; then
            echo "[WAIT] LLM Overloaded. Throttling for $((RETRY_DELAY * attempt))s..."
            sleep $((RETRY_DELAY * attempt))
            ((attempt++))
        else
            success=true
            echo "$output"
        fi
    done

    if [ "$success" = false ]; then
        echo "[CRITICAL] LLM Lost. Serializing state and hibernating."
        exit 1
    fi
}

# 3. SELF-EVALUATING VERSION CONTROL
commit_iteration() {
    local status=$1
    local message=$2
    TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
    
    git -C "${SRC_DIR}" add .
    git -C "${SRC_DIR}" commit -m "ITERATION: ${TIMESTAMP} | STATUS: ${status} | MSG: ${message}"
    
    # Branching for "Producton Solution" (Pass) vs "Sandbox Solution" (Work-in-progress)
    if [ "$status" == "PASS" ]; then
        git -C "${SRC_DIR}" checkout -b "prod-${TIMESTAMP}"
        echo "[DEPLOY] Production-ready branch created."
    fi
}

# --- THE MAGIC LOOP ---
init_project
while true; do
    echo "[OMEGA] Heartbeat: $(date)"
    
    # Phase: Intelligence (Patient & Persistent)
    CODE_RESULT=$(call_llm_with_patience)
    
    # Phase: Verification (Using your DinD Sandbox)
    /app/verify_env.py
    if [ $? -eq 0 ]; then
        commit_iteration "PASS" "Logic verified in sandbox."
        echo "[SUCCESS] Code refined. Monitoring for new goals..."
        # In a real 'Never Quitting' system, we wait for a new prompt or optimize existing code
        sleep 60 
    else
        commit_iteration "FAIL" "Sandbox failure detected. Recursing..."
    fi
done
# Every 100 iterations, run the vacuum
if (( ITERATION_COUNT % 100 == 0 )); then
    echo "[MAINTENANCE] Running Omega Vacuum..."
    python3 /app/omega_vacuum.py
fi

# Inside omega_engine.sh
LAST_ROTATION=$(stat -c %Y system_scripts/master.key)
NOW=$(date +%s)
if [ $((NOW - LAST_ROTATION)) -gt 7776000 ]; then # 90 days in seconds
    echo "[SECURITY] 90-day threshold reached. Rotating keys..."
    python3 /app/omega_rotate.py
fi
