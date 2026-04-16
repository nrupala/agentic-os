/**
 * Paradise Stack - Dashboard Workflow with Cognitive Features
 * 10+ iterations with Meta-Cognition, Knowledge Graph, Reactive Engine
 */

// Cognitive Systems Configuration
const COGNITIVE_CONFIG = {
    maxIterations: 10,  // Extended from 3 to 10+
    lazyMode: true,
    enableReactivity: true,
    enableMetaCognition: true,
    enableKnowledgeGraph: true,
    enableAgentPairing: true,
    stuckThreshold: 5,  // Break after 5 identical failures
};

// Workflow Steps with enhanced cognitive capabilities
const workflowSteps = [
    { 
        id: "step0", 
        agent: "COGNITION", 
        action: "Initialize",
        command: "python3 /app/paradise.py --status",
        description: "Initialize cognitive systems"
    },
    { 
        id: "step1", 
        agent: "META_COGNITION", 
        action: "Think",
        command: "python3 /app/cognition/meta_cognition.py",
        description: "Analyze request with self-awareness"
    },
    { 
        id: "step2", 
        agent: "PLANNER", 
        action: "Plan",
        command: "python3 /app/planner.py '$PROMPT'",
        description: "Create implementation plan (DAG-based)"
    },
    { 
        id: "step3", 
        agent: "AIDER", 
        action: "Implement",
        command: "aider --no-git --no-auto-commits --message 'Read /app/PLAN.md and implement recursively. Do not stop until complete.'",
        description: "Recursive implementation"
    },
    { 
        id: "step4", 
        agent: "REACTIVE", 
        action: "Validate",
        command: "python3 /app/cognition/reactive_engine.py",
        description: "DAG-based reactive validation"
    },
    { 
        id: "step5", 
        agent: "GUARDIAN", 
        action: "Lint",
        command: "ruff check /app 2>&1 || true",
        description: "Quality assurance"
    },
    { 
        id: "step6", 
        agent: "EXECUTOR", 
        action: "Test",
        command: "cd /app && python3 -m pytest tests/ -v 2>&1 || echo 'Tests complete'",
        description: "Execute tests"
    },
    { 
        id: "step7", 
        agent: "IMPROVER", 
        action: "Fix",
        command: "aider --no-git --no-auto-commits --message 'Fix all issues. Improve quality.'",
        description: "Iterative improvement"
    },
    { 
        id: "step8", 
        agent: "KNOWLEDGE", 
        action: "Learn",
        command: "python3 /app/cognition/knowledge_graph.py",
        description: "Update knowledge graph"
    },
    { 
        id: "step9", 
        agent: "VERIFY", 
        action: "Check",
        command: "python3 /app/cognition/verification.py",
        description: "Final verification"
    }
];

let workflowState = {
    currentStep: 0,
    maxIterations: COGNITIVE_CONFIG.maxIterations,
    iteration: 0,
    errors: [],
    testResults: null,
    cognitiveState: {
        knowledgeGraph: {},
        metaCognition: {},
        reactiveEngine: {},
        agentPairing: {},
    },
    issueHistory: [],
    stuckCount: 0,
    userSatisfied: false,
};

function initWorkflow() {
    const workflowList = document.getElementById('workflow-list');
    if (!workflowList) return;
    
    workflowList.innerHTML = workflowSteps.map((step, index) => `
        <div class="workflow-step" id="step-${index}">
            <span class="step-num">${index + 1}.</span>
            <span class="tag ${getAgentColor(step.agent)}">${step.agent}</span>
            <span>${step.description}</span>
        </div>
    `).join('');
    
    updateCognitiveDisplay();
}

function getAgentColor(agent) {
    const colors = {
        'COGNITION': 'cognition',
        'META_COGNITION': 'meta',
        'PLANNER': 'planner',
        'AIDER': 'aider',
        'REACTIVE': 'reactive',
        'GUARDIAN': 'guardian',
        'EXECUTOR': 'executor',
        'IMPROVER': 'improver',
        'KNOWLEDGE': 'knowledge',
        'VERIFY': 'verify',
    };
    return colors[agent] || '';
}

async function logToTerminal(message, color = "#c9d1d9") {
    const terminal = document.getElementById('terminal-output');
    const line = document.createElement('div');
    line.style.color = color;
    line.textContent = message;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
}

async function executeStep(step, iteration = 0) {
    await logToTerminal(`\n[${step.agent}] ${step.action}...`, "#58a6ff");
    
    try {
        const response = await fetch('http://localhost:3001/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: step.command })
        });
        const data = await response.json();
        
        if (data.output) {
            await logToTerminal(data.output.substring(0, 2000), "#c9d1d9");
        }
        
        return {
            success: data.success,
            output: data.output || "",
            exitCode: data.exitCode
        };
    } catch (err) {
        await logToTerminal(`Error: ${err.message}`, "#ff7b72");
        return { success: false, output: err.message };
    }
}

async function checkApiKey() {
    try {
        const response = await fetch('http://localhost:3001/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: 'echo $OPENAI_API_KEY' })
        });
        const data = await response.json();
        return data.output && data.output.trim().length > 0 && !data.output.includes('$OPENAI_API_KEY');
    } catch {
        return false;
    }
}

async function runCognitivePhase(phase) {
    await logToTerminal(`\n🧠 [${phase.toUpperCase()}] Cognitive Phase`, "#a855f7");
    const result = await executeStep({
        agent: "COGNITION",
        action: phase,
        command: `python3 /app/cognition/${phase.toLowerCase().replace(' ', '_')}.py`
    });
    return result;
}

async function checkLoopDetection() {
    if (workflowState.issueHistory.length >= 3) {
        const recent = workflowState.issueHistory.slice(-3);
        const allSame = recent.every(i => i.type === recent[0].type);
        
        if (allSame) {
            workflowState.stuckCount++;
            await logToTerminal(`\n⚠️  Loop detected! Same issue repeated ${workflowState.stuckCount} times`, "#f59e0b");
            
            if (workflowState.stuckCount >= COGNITIVE_CONFIG.stuckThreshold) {
                await logToTerminal(`\n🚨 System stuck - breaking cycle`, "#ef4444");
                return true;
            }
        }
    }
    return false;
}

async function runLintCheck() {
    const result = await executeStep({
        agent: "GUARDIAN",
        action: "Lint",
        command: "ruff check /app --output-format=concise 2>&1 || true"
    });
    
    if (result.output && (result.output.includes("error") || result.output.includes("Error"))) {
        workflowState.errors.push({ type: "lint", output: result.output, iteration: workflowState.iteration });
        workflowState.issueHistory.push({ type: "lint", iteration: workflowState.iteration });
        return false;
    }
    return true;
}

async function runTests() {
    const result = await executeStep({
        agent: "EXECUTOR",
        action: "Run Tests",
        command: "cd /app && python3 -m pytest tests/ -v --tb=short 2>&1 || true"
    });
    
    workflowState.testResults = result;
    
    if (result.output.includes("FAILED") || result.output.includes("ERROR")) {
        workflowState.errors.push({ type: "test", output: result.output, iteration: workflowState.iteration });
        workflowState.issueHistory.push({ type: "test", iteration: workflowState.iteration });
        return false;
    }
    
    return result.success;
}

async function fixIssues() {
    if (workflowState.errors.length === 0) return true;
    
    await logToTerminal(`\n🔧 [IMPROVER] Fixing ${workflowState.errors.length} issues...`, "#d29922");
    
    const errorSummary = workflowState.errors.map(e => 
        `- ${e.type} (iteration ${e.iteration}): ${e.output.substring(0, 150)}`
    ).join("\n");
    
    const fixCommand = `aider --no-git --no-auto-commits --message "Fix ALL issues found:\n${errorSummary}\n\nDo not stop until all issues are resolved."`;
    
    const result = await executeStep({
        agent: "IMPROVER",
        action: "Fix issues",
        command: fixCommand
    });
    
    workflowState.errors = [];
    return result.success;
}

async function updateKnowledgeGraph(outcome) {
    await logToTerminal(`\n📚 [KNOWLEDGE] Updating knowledge graph...`, "#22d3ee");
    
    const result = await executeStep({
        agent: "KNOWLEDGE",
        action: "Learn",
        command: "python3 /app/cognition/knowledge_graph.py"
    });
    
    workflowState.cognitiveState.knowledgeGraph = {
        updated: outcome,
        timestamp: new Date().toISOString(),
    };
}

function updateCognitiveDisplay() {
    const cognitivePanel = document.getElementById('cognitive-panel');
    if (!cognitivePanel) return;
    
    cognitivePanel.innerHTML = `
        <div class="cognitive-metric">
            <span class="label">Iterations:</span>
            <span class="value">${workflowState.iteration}/${workflowState.maxIterations}</span>
        </div>
        <div class="cognitive-metric">
            <span class="label">Errors:</span>
            <span class="value">${workflowState.errors.length}</span>
        </div>
        <div class="cognitive-metric">
            <span class="label">Stuck Count:</span>
            <span class="value ${workflowState.stuckCount > 0 ? 'warning' : ''}">${workflowState.stuckCount}</span>
        </div>
        <div class="cognitive-metric">
            <span class="label">Issues History:</span>
            <span class="value">${workflowState.issueHistory.length}</span>
        </div>
    `;
}

async function startWorkflow() {
    const prompt = document.getElementById('prompt-input').value;
    if (!prompt) return alert("Enter a prompt first!");

    document.getElementById('terminal-output').innerHTML = "";
    
    workflowState = {
        currentStep: 0,
        maxIterations: COGNITIVE_CONFIG.maxIterations,
        iteration: 0,
        errors: [],
        testResults: null,
        cognitiveState: {},
        issueHistory: [],
        stuckCount: 0,
        userSatisfied: false,
    };
    
    await logToTerminal("🏝️  Paradise Stack v2.0 - Cognitive Development\n", "#58a6ff");
    await logToTerminal("═".repeat(60) + "\n", "#30363d");
    await logToTerminal(`Max Iterations: ${workflowState.maxIterations} (extended for thoroughness)\n`, "#888");
    
    const hasApiKey = await checkApiKey();
    if (!hasApiKey) {
        await logToTerminal("⚠️  Warning: OPENAI_API_KEY not set.\n", "#d29922");
    }
    
    // PHASE 0: Initialize Cognitive Systems
    await logToTerminal("\n🧠 Phase 0: Initialize Cognitive Systems\n", "#a855f7");
    await logToTerminal("─".repeat(60), "#30363d");
    
    await executeStep(workflowSteps[0]);
    
    // PHASE 1: Meta-Cognition - Think about the task
    await logToTerminal("\n🧠 Phase 1: Meta-Cognition - Analyzing request...\n", "#a855f7");
    await logToTerminal("─".repeat(60), "#30363d");
    
    await executeStep(workflowSteps[1]);
    
    // PHASE 2: Planning
    await logToTerminal("\n📋 Phase 2: Planning (DAG-based)...\n", "#58a6ff");
    await logToTerminal("─".repeat(60), "#30363d");
    
    const planResult = await executeStep({
        ...workflowSteps[2],
        command: `python3 /app/planner.py '${prompt.replace(/'/g, "'\"'\"'")}'`
    });
    
    if (!planResult.success) {
        await logToTerminal("\n❌ Planner failed - cannot continue.", "#ff7b72");
        return;
    }
    
    // MAIN QA LOOP: Up to 10+ iterations
    for (let i = 0; i < workflowState.maxIterations; i++) {
        workflowState.iteration = i + 1;
        workflowState.errors = [];
        
        await logToTerminal(`\n${"═".repeat(60)}`, "#30363d");
        await logToTerminal(`\n🔄 ITERATION ${workflowState.iteration}/${workflowState.maxIterations}`, "#d29922");
        await logToTerminal("─".repeat(60), "#30363d");
        
        updateCognitiveDisplay();
        
        // Step 3: Implement
        await logToTerminal("\n📝 [AIDER] Implementing from plan...\n", "#58a6ff");
        const aiderCommand = `aider --no-git --no-auto-commits --message "Read /app/PLAN.md and implement the complete solution recursively. Create ALL necessary files with full working code. Do not stop until everything is implemented."`;
        
        const aiderResult = await executeStep({
            agent: "AIDER",
            action: "Implement",
            command: aiderCommand
        });
        
        // Step 4: Reactive Validation
        await logToTerminal("\n⚡ [REACTIVE] DAG-based validation...\n", "#a855f7");
        await executeStep(workflowSteps[4]);
        
        // Step 5: Lint
        await logToTerminal("\n🔍 [GUARDIAN] Quality check...\n", "#d29922");
        const lintOk = await runLintCheck();
        
        // Step 6: Tests
        await logToTerminal("\n🧪 [EXECUTOR] Running tests...\n", "#d29922");
        const testsOk = await runTests();
        
        // Check if all passed
        if (lintOk && testsOk) {
            workflowState.userSatisfied = true;
            await logToTerminal("\n✅ ALL CHECKS PASSED!", "#3fb950");
            
            await updateKnowledgeGraph({
                prompt: prompt,
                iteration: workflowState.iteration,
                success: true,
            });
            
            break;
        }
        
        // Check for stuck loop
        const isStuck = await checkLoopDetection();
        if (isStuck) {
            await logToTerminal("\n🚨 Breaking - system stuck in loop", "#ef4444");
            break;
        }
        
        // Step 7: Fix Issues
        await logToTerminal(`\n⚠️  Issues found: ${workflowState.errors.length}`, "#d29922");
        await fixIssues();
        
        // Continue loop
    }
    
    // Final Phase: Knowledge Update
    await logToTerminal("\n📚 Phase Final: Updating Knowledge Graph\n", "#22d3ee");
    await logToTerminal("─".repeat(60), "#30363d");
    
    await updateKnowledgeGraph({
        prompt: prompt,
        iterations: workflowState.iteration,
        success: workflowState.userSatisfied,
        errors: workflowState.issueHistory.length,
    });
    
    // Final summary
    await logToTerminal("\n" + "═".repeat(60), "#30363d");
    await logToTerminal("\n🏁  Paradise Development Complete\n", "#58a6ff");
    await logToTerminal(`📋 Plan: /app/PLAN.md`, "#888");
    await logToTerminal(`🔄 Total Iterations: ${workflowState.iteration}/${workflowState.maxIterations}`, "#888");
    await logToTerminal(`❌ Errors remaining: ${workflowState.errors.length}`, workflowState.errors.length > 0 ? "#ff7b72" : "#3fb950");
    await logToTerminal(`✅ User Satisfied: ${workflowState.userSatisfied ? 'YES' : 'PARTIAL'}\n`, workflowState.userSatisfied ? "#3fb950" : "#d29922");
}

async function checkSenses() {
    const senses = [
        { id: "status-phoenix", url: "http://localhost:6006" },
        { id: "status-ollama", url: "http://localhost:11434" },
        { id: "status-langfuse", url: "http://localhost:3000" }
    ];

    for (const sense of senses) {
        const el = document.getElementById(sense.id);
        try {
            await fetch(sense.url, { mode: 'no-cors' });
            el.className = "status-dot online";
        } catch (e) {
            el.className = "status-dot offline";
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initWorkflow();
    checkSenses();
    setInterval(checkSenses, 5000);
});
