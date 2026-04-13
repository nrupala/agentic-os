const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');
const cors = require('cors');
const { execSync } = require('child_process');
const app = express();

const projectRoot = path.resolve(__dirname, '..');
const LOGS_DIR = path.join(projectRoot, 'logs');
const OUTPUTS_DIR = path.join(projectRoot, 'outputs');
const PROJECTS_DIR = path.join(projectRoot, 'projects');

[LOGS_DIR, OUTPUTS_DIR, PROJECTS_DIR].forEach(dir => {
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname)));

function logToFile(filename, content) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filepath = path.join(LOGS_DIR, `${filename}_${timestamp}.log`);
    fs.writeFileSync(filepath, content);
    return filepath;
}

function getShellEnv() {
    let env = { ...process.env };
    
    if (process.platform === 'win32') {
        try {
            const result = execSync('cmd /c "echo %PATH%"', { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
            env.PATH = result.trim();
        } catch (e) {}
        
        try {
            const result = execSync('cmd /c "echo %PATHEXT%"', { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
            env.PATHEXT = result.trim();
        } catch (e) {}
        
        try {
            const result = execSync('cmd /c "echo %COMSPEC%"', { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
            env.COMSPEC = result.trim();
        } catch (e) {}
        
        try {
            const result = execSync('cmd /c "echo %SystemRoot%"', { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
            env.SystemRoot = result.trim();
        } catch (e) {}
    } else {
        try {
            const result = execSync('/bin/sh -c "echo $PATH"', { encoding: 'utf8' });
            env.PATH = result.trim();
        } catch (e) {}
    }
    
    return env;
}

function executeCommand(command, res) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] Executing: ${command}`);
    
    const logPath = logToFile('command', `[${timestamp}]\nCommand: ${command}\n`);
    const env = getShellEnv();
    
    let output = '';
    let errorOutput = '';
    
    const shell = process.platform === 'win32' ? 'cmd.exe' : '/bin/sh';
    const shellArgs = process.platform === 'win32' ? ['/c', command] : ['-c', command];
    
    const child = spawn(shell, shellArgs, {
        cwd: projectRoot,
        env,
        stdio: ['pipe', 'pipe', 'pipe'],
        windowsHide: false
    });
    
    child.stdout.on('data', (data) => {
        output += data.toString();
    });
    
    child.stderr.on('data', (data) => {
        errorOutput += data.toString();
    });
    
    child.on('error', (error) => {
        logToFile('command', fs.readFileSync(logPath, 'utf8') + `Error: ${error.message}\n`);
        res.json({ success: false, output: `Error: ${error.message}`, logPath });
    });
    
    child.on('close', (code) => {
        const finalOutput = output || errorOutput;
        const success = code === 0 && !errorOutput.includes('not recognized');
        
        logToFile('command', fs.readFileSync(logPath, 'utf8') + 
            `Exit Code: ${code}\nOutput:\n${finalOutput}\n`);
        
        res.json({ success, output: finalOutput, logPath, exitCode: code });
    });
}

app.post('/execute', (req, res) => {
    const { command } = req.body;
    if (!command) {
        return res.json({ success: false, output: 'No command provided' });
    }
    executeCommand(command, res);
});

app.get('/logs', (req, res) => {
    const files = fs.readdirSync(LOGS_DIR).filter(f => f.endsWith('.log'))
        .map(f => ({ name: f, path: `/logs/${f}`, size: fs.statSync(path.join(LOGS_DIR, f)).size }))
        .sort((a, b) => b.name.localeCompare(a.name));
    res.json(files);
});

app.get('/log/:filename', (req, res) => {
    res.sendFile(path.join(LOGS_DIR, req.params.filename));
});

app.get('/status', (req, res) => {
    res.json({
        status: 'running',
        platform: process.platform,
        nodeVersion: process.version,
        projectRoot,
        timestamp: new Date().toISOString()
    });
});

app.listen(3001, () => {
    console.log('Paradise Bridge running on port 3001');
    console.log(`Platform: ${process.platform}`);
    console.log(`Project Root: ${projectRoot}`);
});
