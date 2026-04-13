const express = require('express');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const cors = require('cors');
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

function getEnv() {
    const pyScripts = path.join(process.env.APPDATA || '', 'Python', 'pythoncore-3.14-64', 'Scripts');
    return {
        ...process.env,
        PATH: `${pyScripts};${process.env.PATH || ''}`,
        PYTHONPATH: path.join(process.env.APPDATA || '', 'Python', 'pythoncore-3.14-64', 'Lib', 'site-packages')
    };
}

function wrapCommand(command) {
    return `set "PATH=%APPDATA%\\Python\\pythoncore-3.14-64\\Scripts;%PATH%" && ${command}`;
}

app.post('/execute', (req, res) => {
    const { command } = req.body;
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] Executing: ${command}`);

    const wrappedCmd = wrapCommand(command);
    
    exec(wrappedCmd, { cwd: projectRoot, maxBuffer: 10 * 1024 * 1024, shell: 'cmd.exe' }, (error, stdout, stderr) => {
        const output = stdout || stderr || '';
        const logPath = logToFile('command', `[${timestamp}]\nCommand: ${command}\nOutput:\n${output}\nError: ${error?.message || 'None'}\n`);

        if (error && !output) {
            return res.json({ success: false, output: error.message, logPath });
        }
        res.json({ success: true, output: stdout || stderr, logPath });
    });
});

app.get('/logs', (req, res) => {
    const files = fs.readdirSync(LOGS_DIR).filter(f => f.endsWith('.log'))
        .map(f => ({ name: f, path: `/logs/${f}`, size: fs.statSync(path.join(LOGS_DIR, f)).size }));
    res.json(files);
});

app.get('/log/:filename', (req, res) => {
    res.sendFile(path.join(LOGS_DIR, req.params.filename));
});

app.listen(3001, () => console.log('Paradise Bridge running on port 3001'));
