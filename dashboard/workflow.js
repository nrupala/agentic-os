const workflowSteps = [
    { id: "step1", agent: "CLINE", action: "Architect", command: "cline --plan \"$PROMPT\"", description: "Generating PLAN.md" },
    { id: "step2", agent: "CRAWL4AI", action: "Knowledge", command: "crwl \"$PROMPT\"", description: "Updating Context" },
    { id: "step3", agent: "AIDER", action: "Implement", command: "aider --message \"Execute PLAN.md\" --auto-test --yes", description: "Applying Code Changes" },
    { id: "step4", agent: "GUARDIAN", action: "Verify", command: "ruff check . && eslint . && prettier --check .", description: "Quality Assurance (FOSS)" }
];

function initWorkflow() {
    const workflowList = document.getElementById('workflow-list');
    if (!workflowList) return;
    
    workflowList.innerHTML = workflowSteps.map(step => `
        <div class="workflow-step">
            <span class="tag">${step.agent}</span>
            <span>${step.description}</span>
        </div>
    `).join('');
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
            const res = await fetch(sense.url, { mode: 'no-cors' });
            el.className = "status-dot online";
        } catch (e) {
            el.className = "status-dot offline";
        }
    }
}

async function startWorkflow() {
    const prompt = document.getElementById('prompt-input').value;
    if (!prompt) return alert("Enter a prompt first!");

    document.getElementById('terminal-output').innerHTML = "> Initializing Paradise Sequence...\n";
    await logToTerminal(`Working Directory: ${window.location.origin}\n`, "#888");
    
    for (const step of workflowSteps) {
        await logToTerminal(`\n[${step.agent}] Executing ${step.action}...`, "#58a6ff");
        await logToTerminal(`Command: ${step.command.replace('$PROMPT', prompt)}`, "#666");
        
        try {
            const response = await fetch('http://localhost:3001/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: step.command.replace('$PROMPT', prompt) })
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (data.output) await logToTerminal(data.output, "#c9d1d9");
                if (data.logPath) await logToTerminal(`Log: ${data.logPath}`, "#3fb950");
                await logToTerminal(`[${step.agent}] Success.`, "#3fb950");
            } else {
                await logToTerminal(`Error: ${data.output || 'Command failed'}`, "#ff7b72");
                if (data.logPath) await logToTerminal(`Log: ${data.logPath}`, "#ff7b72");
            }
        } catch (err) {
            await logToTerminal(`Bridge Error: ${err.message}`, "#ff7b72");
            await logToTerminal(`Ensure server is running: cd dashboard && npm start`, "#ff7b72");
            break;
        }
    }
    await logToTerminal("\n=====================================", "#888");
    await logToTerminal("Logs stored in: /logs/ | Outputs in: /outputs/", "#888");
    await logToTerminal("✅ Sequence Finished.", "#d29922");
}

async function logToTerminal(message, color = "#c9d1d9") {
    const terminal = document.getElementById('terminal-output');
    const line = document.createElement('div');
    line.style.color = color;
    line.textContent = message;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
}

// Initializations
document.addEventListener('DOMContentLoaded', () => {
    initWorkflow();
    checkSenses();
    setInterval(checkSenses, 5000);
});
