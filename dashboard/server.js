const express = require('express');
const { exec } = require('child_process');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

app.post('/execute', (req, res) => {
    const { command } = req.body;
    console.log(`Executing: ${command}`);

    // This runs the command in your project root
    exec(command, { cwd: '../' }, (error, stdout, stderr) => {
        if (error) {
            return res.json({ success: false, output: stderr });
        }
        res.json({ success: true, output: stdout });
    });
});

app.listen(3001, () => console.log('Paradise Bridge running on port 3001'));
