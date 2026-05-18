#!/bin/bash
# Paradise Stack - Autonomous Development Pipeline
# Claude Code Replacement

set -e

PROJECT_ROOT="/app"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"

echo "🏝️  Paradise Stack - Autonomous Development"
echo "============================================"
echo ""

# Check for OpenAI API Key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set"
    echo "   Aider requires an LLM API key to function."
    echo "   Set it with: export OPENAI_API_KEY=sk-..."
    echo ""
fi

# Step 1: Planner
echo "📋 Step 1: [PLANNER] Creating implementation plan..."
echo "--------------------------------------------------"
if [ $# -eq 0 ]; then
    echo "Usage: $0 '<feature request>'"
    echo "Example: $0 'create a todo app with React'"
    exit 1
fi

PROMPT="$@"
python3 "$PROJECT_ROOT/planner.py" "$PROMPT"
echo "✅ Plan generated: $PROJECT_ROOT/PLAN.md"
echo ""

# Step 2: Aider Implementation
echo "📝 Step 2: [AIDER] Implementing solution..."
echo "--------------------------------------------------"
echo "Reading plan and implementing..."

# Aider command - reads PLAN.md and implements recursively
AIDER_CMD="aider --no-git --no-auto-commits --message \"Read /app/PLAN.md carefully. Implement the complete solution step by step. Create ALL necessary files with FULL working code. Do not stop until the entire plan is implemented. Write complete, production-ready code for every file.\""

eval $AIDER_CMD
echo "✅ Implementation phase complete"
echo ""

# Step 3: Quality Assurance Loop
echo "🔍 Step 3: [GUARDIAN] Quality Assurance..."
echo "--------------------------------------------------"

MAX_ITERATIONS=3
ITERATION=0

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ITERATION=$((ITERATION + 1))
    echo ""
    echo "--- QA Iteration $ITERATION/$MAX_ITERATIONS ---"
    
    # Run linter
    echo "Running ruff linter..."
    ruff check "$PROJECT_ROOT" || true
    echo ""
    
    # Run tests
    echo "Running pytest..."
    if [ -f "$PROJECT_ROOT/tests/test_suite.py" ]; then
        python3 -m pytest "$PROJECT_ROOT/tests/" -v --tb=short 2>&1 | head -100 || true
    else
        echo "No tests directory found"
    fi
    echo ""
    
    # Check for Python syntax errors
    echo "Checking Python syntax..."
    find "$PROJECT_ROOT" -name "*.py" -exec python3 -m py_compile {} \; 2>&1 || true
    echo ""
    
    # If there were issues, fix them
    echo "Checking for issues..."
    ISSUES=$(python3 -m pytest "$PROJECT_ROOT/tests/" --collect-only 2>&1 || echo "tests found")
    
    if echo "$ISSUES" | grep -q "error\|failed\|FAILED"; then
        echo "⚠️  Issues found - running Aider to fix..."
        AIDER_FIX_CMD="aider --no-git --no-auto-commits --message \"Fix all failing tests and lint errors. Review the test output above and resolve every issue. Make all tests pass.\""
        eval $AIDER_FIX_CMD || true
    else
        echo "✅ All checks passed!"
        break
    fi
done

echo ""
echo "============================================"
echo "🏁  Paradise Development Complete"
echo "============================================"
echo "📋 Plan: $PROJECT_ROOT/PLAN.md"
echo "🔄 QA Iterations: $ITERATION/$MAX_ITERATIONS"
