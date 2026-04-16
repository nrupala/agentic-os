const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');
const cors = require('cors');
const { execSync } = require('child_process');
const app = express();

const PROJECT_ROOT = process.env.HOST_PROJECT_ROOT || path.resolve(__dirname, '..');
const LOGS_DIR = path.join(PROJECT_ROOT, 'logs');
const OUTPUTS_DIR = path.join(PROJECT_ROOT, 'outputs');
const PROJECTS_DIR = path.join(PROJECT_ROOT, 'projects');

const VERSIONS = {
    platform: '1.1.0-dev',
    node: process.version,
    python: '3.11',
    docker: 'containerized',
    dependencies: {
        aider: '0.2.6',
        crawl4ai: '0.8.6',
        ruff: '0.15.10',
        express: '4.x'
    }
};

const EXECUTION_TIMEOUT = parseInt(process.env.EXECUTION_TIMEOUT || '30000');
const MAX_COMMAND_LENGTH = parseInt(process.env.MAX_COMMAND_LENGTH || '5000');

[LOGS_DIR, OUTPUTS_DIR, PROJECTS_DIR].forEach(dir => {
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

app.use(cors({
    origin: process.env.ALLOWED_ORIGINS ? process.env.ALLOWED_ORIGINS.split(',') : '*',
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type']
}));
app.use(express.json({ limit: '1mb' }));
app.use(express.static(path.join(__dirname)));

app.use((req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('X-XSS-Protection', '1; mode=block');
    next();
});

app.use((req, res, next) => {
    const start = Date.now();
    res.on('finish', () => {
        const duration = Date.now() - start;
        console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} ${res.statusCode} ${duration}ms`);
    });
    next();
});

function logToFile(filename, content) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filepath = path.join(LOGS_DIR, `${filename}_${timestamp}.log`);
    try {
        fs.writeFileSync(filepath, content);
        return filepath;
    } catch (err) {
        console.error(`Failed to write log: ${err.message}`);
        return null;
    }
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
    if (!command || typeof command !== 'string') {
        return res.json({ success: false, output: 'Invalid command' });
    }
    
    if (command.length > MAX_COMMAND_LENGTH) {
        return res.json({ success: false, output: `Command exceeds maximum length of ${MAX_COMMAND_LENGTH} characters` });
    }
    
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] Executing: ${command.substring(0, 100)}...`);
    
    const logPath = logToFile('command', `[${timestamp}]\nCommand: ${command}\n`);
    const env = getShellEnv();
    
    let output = '';
    let errorOutput = '';
    let timedOut = false;
    
    const shell = process.platform === 'win32' ? 'cmd.exe' : '/bin/sh';
    const shellArgs = process.platform === 'win32' ? ['/c', command] : ['-c', command];
    
    const child = spawn(shell, shellArgs, {
        cwd: PROJECT_ROOT,
        env,
        stdio: ['pipe', 'pipe', 'pipe'],
        windowsHide: false
    });
    
    const timeout = setTimeout(() => {
        timedOut = true;
        child.kill('SIGTERM');
        console.log(`[${new Date().toISOString()}] Command timed out after ${EXECUTION_TIMEOUT}ms`);
    }, EXECUTION_TIMEOUT);
    
    child.stdout.on('data', (data) => {
        output += data.toString();
        if (output.length > 100000) {
            output = output.substring(0, 100000) + '\n[OUTPUT TRUNCATED]';
            child.kill();
        }
    });
    
    child.stderr.on('data', (data) => {
        errorOutput += data.toString();
    });
    
    child.on('error', (error) => {
        clearTimeout(timeout);
        const errorMsg = timedOut ? 'Command timed out' : `Error: ${error.message}`;
        if (logPath) logToFile('command', `${fs.readFileSync(logPath, 'utf8')}\n${errorMsg}\n`);
        res.json({ success: false, output: errorMsg, logPath });
    });
    
    child.on('close', (code) => {
        clearTimeout(timeout);
        const finalOutput = output || errorOutput;
        const success = code === 0 && !errorOutput.includes('not recognized') && !timedOut;
        
        if (logPath) {
            logToFile('command', fs.readFileSync(logPath, 'utf8') + 
                `Exit Code: ${code}\nTimed Out: ${timedOut}\nOutput:\n${finalOutput}\n`);
        }
        
        res.json({ success, output: finalOutput, logPath, exitCode: code, timedOut });
    });
}

app.post('/execute', (req, res) => {
    try {
        const { command } = req.body;
        if (!command) {
            return res.status(400).json({ success: false, output: 'No command provided' });
        }
        executeCommand(command, res);
    } catch (err) {
        console.error(`Execute error: ${err.message}`);
        res.status(500).json({ success: false, output: 'Internal server error' });
    }
});

app.get('/logs', (req, res) => {
    try {
        const files = fs.readdirSync(LOGS_DIR)
            .filter(f => f.endsWith('.log'))
            .map(f => ({ 
                name: f, 
                path: `/logs/${f}`, 
                size: fs.statSync(path.join(LOGS_DIR, f)).size,
                created: fs.statSync(path.join(LOGS_DIR, f)).mtime
            }))
            .sort((a, b) => new Date(b.created) - new Date(a.created));
        res.json(files);
    } catch (err) {
        res.status(500).json({ error: 'Failed to list logs' });
    }
});

app.get('/log/:filename', (req, res) => {
    const filename = req.params.filename;
    if (!filename || filename.includes('..') || filename.includes('/')) {
        return res.status(400).json({ error: 'Invalid filename' });
    }
    const filepath = path.join(LOGS_DIR, filename);
    if (!fs.existsSync(filepath)) {
        return res.status(404).json({ error: 'Log not found' });
    }
    res.sendFile(filepath);
});

app.get('/status', (req, res) => {
    res.json({
        status: 'running',
        platform: process.platform,
        nodeVersion: process.version,
        projectRoot: PROJECT_ROOT,
        timestamp: new Date().toISOString()
    });
});

app.get('/version', (req, res) => {
    res.json(VERSIONS);
});

app.get('/health', (req, res) => {
    const health = {
        status: 'healthy',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        timestamp: new Date().toISOString()
    };
    res.json(health);
});

app.use((err, req, res, next) => {
    console.error(`Unhandled error: ${err.message}`);
    res.status(500).json({ error: 'Internal server error', message: err.message });
});

app.use((req, res) => {
    res.status(404).json({ error: 'Not found' });
});

const PORT = parseInt(process.env.PORT || '3001');
app.listen(PORT, () => {
    console.log(`Paradise Bridge running on port ${PORT}`);
    console.log(`Platform: ${process.platform}`);
    console.log(`Project Root: ${PROJECT_ROOT}`);
});
