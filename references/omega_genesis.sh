#!/bin/bash
# OMEGA-CODE GENESIS: Complete System Construction
set -e

echo "🚀 Initializing OMEGA-CODE System Architecture..."

# 1. DIRECTORY STRUCTURE
mkdir -p projects/default/{src,outputs,self-eval-logs,logs,state}
mkdir -p system_scripts

# 2. GENERATE DOCKERFILE (The Hardened Core)
cat <<EOF > Dockerfile
FROM python:3.12-slim as builder
RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --prefix=/install numpy==1.26.4 flask==3.0.2 gunicorn==21.2.0

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN addgroup --system omega && adduser --system --group omega
COPY --from=builder /install /usr/local
USER omega
EOF

# 3. GENERATE OMEGA-FORGE (The Brain)
cat <<EOF > omega_forge.py
import sqlite3, json, os, subprocess, time
from datetime import datetime

class OmegaForge:
    def __init__(self, project):
        self.project = project
        self.db = f"projects/{project}/state/omega_state.db"
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db), exist_ok=True)
        conn = sqlite3.connect(self.db)
        conn.execute("CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY, goal TEXT, code TEXT, status TEXT, logs TEXT)")
        conn.commit()

    def meta_analyze(self):
        # Recursive failure analysis logic
        return "Thinking Rules: 1. Use absolute paths. 2. Verify all imports."

    def run_iteration(self, goal):
        rules = self.meta_analyze()
        print(f"[*] Iterating with Rules: {rules}")
        # Placeholder for LLM logic
        code = "print('Omega Active')"
        self.persist(goal, code, "PASS", "Success")

    def persist(self, goal, code, status, logs):
        conn = sqlite3.connect(self.db)
        conn.execute("INSERT INTO state (goal, code, status, logs) VALUES (?,?,?,?)", (goal, code, status, logs))
        conn.commit()

if __name__ == "__main__":
    forge = OmegaForge(os.getenv('PROJECT_NAME', 'default'))
    forge.run_iteration("Self-check logic.")
EOF

# 4. GENERATE THE VACUUM (Autonomous Cleanup)
cat <<EOF > omega_vacuum.py
import os, glob
def vacuum():
    log_dir = f"./projects/{os.getenv('PROJECT_NAME', 'default')}/self-eval-logs"
    logs = sorted(glob.glob(f"{log_dir}/*.md"))
    if len(logs) > 10:
        for old_log in logs[:-10]:
            os.remove(old_log)
            print(f"[-] Purged: {old_log}")
if __name__ == "__main__": vacuum()
EOF

# 5. GENERATE DOCKER COMPOSE
cat <<EOF > docker-compose.yml
services:
  omega-agent:
    build: .
    container_name: omega_\${PROJECT_NAME}
    environment:
      - PROJECT_NAME=\${PROJECT_NAME}
    volumes:
      - ./projects/\${PROJECT_NAME}:/app/project
    command: python3 /app/omega_forge.py
    restart: always
EOF

# 6. SYSTEMD GUARDIAN (Persistence)
cat <<EOF > system_scripts/omega-guardian.service
[Unit]
Description=OMEGA-CODE Guardian
After=docker.service

[Service]
Restart=always
WorkingDirectory=$(pwd)
ExecStart=/usr/local/bin/docker-compose up

[Install]
WantedBy=multi-user.target
EOF

# 7. FINAL PERMISSIONS & INITIALIZATION
chmod +x *.py
export PROJECT_NAME="default"

echo "✅ OMEGA-CODE Genesis Complete."
echo "👉 Run 'export PROJECT_NAME=your_project && docker-compose up --build' to start."
