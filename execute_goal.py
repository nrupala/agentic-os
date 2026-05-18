#!/usr/bin/env python3
"""Execute goal via API"""
import requests
import json
import sys

goal = {
    "goal": "Build a secure tokenized file sharing server with: Token-based upload/download auth, File encryption at rest, Self-hosted option, Google Cloud Storage wrapper, REST API with FastAPI, WebSocket for real-time transfer progress, SQLite database for file metadata, Docker support for self-hosting"
}

try:
    resp = requests.post("http://localhost:8080/api/v1/execute", json=goal, timeout=300)
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)