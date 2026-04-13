// The JSON logic defining how agents hand off work
const workflowSteps = [
    {
        id: "step1",
        agent: "CLINE",
        action: "Architect & Plan",
        command: "cline --plan \"$PROMPT\"",
        description: "Analyzing codebase and generating PLAN.md"
    },
    {
        id: "step2",
        agent: "CRAWL4AI",
        action: "Knowledge Retrieval",
        command: "crawl4ai --url $DOCS",
        description: "Updating RAG context with latest docs"
    },
    {
        id: "step3",
        agent: "AIDER",
        action: "Implement",
        command: "aider --msg \"Execute PLAN.md\"",
        description: "Applying multi-file edits and git commits"
    },
    {
        id: "step4",
        agent: "QODO",
        action: "Verify",
        command: "qodo scan .",
        description: "Running automated quality checks"
    }
];

function initWorkflow() {
    const list = document.getElementById('workflow-list');
    list.innerHTML = workflowSteps.map(step => `
        <div style="margin-bottom: 10px;">
            <strong>${step.agent}</strong> <span class="tag">${step.action}</span>
            <div style="font-size: 0.8em; color: #8b949e;">${step.description}</div>
        </div>
    `).join('');
}

async function logToTerminal(text, color = "#00ff00") {
    const term = document.getElementById('terminal-output');
    term.innerHTML += `<br><span style="color: ${color}">${text}</span>`;
    term.scrollTop = term.scrollHeight;
}

async function startWorkflow() {
    const prompt = document.getElementById('prompt-input').value;
    if (!prompt) return alert("Enter a prompt first!");

    document.getElementById('terminal-output').innerHTML = "> Starting Paradise Workflow...";
    
    for (const step of workflowSteps) {
        await logToTerminal(`\n[${step.agent}] Starting: ${step.action}...`, "#58a6ff");
        await logToTerminal(`$ ${step.command.replace('$PROMPT', prompt)}`, "#8b949e");
        
        // Simulating the agent work delay
        await new Promise(r => setTimeout(r, 2000));
        
        await logToTerminal(`[${step.agent}] Task Completed Successfully.`, "#3fb950");
    }
    
    await logToTerminal("\n✅ WORKFLOW COMPLETE: View traces in Langfuse (Port 3000)", "#d29922");
}

initWorkflow();
