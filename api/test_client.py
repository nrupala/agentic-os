#!/usr/bin/env python3
"""
agentic-OS: Test API Client
===========================
Test the API server endpoints
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8080"

def test_health():
    """Test health endpoint."""
    print("[TEST] Health Check...")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"    Status: {resp.status_code}")
        print(f"    Response: {resp.json()}")
        return True
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

def test_execute():
    """Test execute endpoint."""
    print("\n[TEST] Execute Goal...")
    try:
        payload = {
            "goal": "Build a Zero Trust Chat Server with encryption",
            "request_type": "feature_add",
            "max_iterations": 3,
            "files_to_create": ["src/server.py", "src/crypto.py"]
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/execute",
            json=payload,
            timeout=10
        )
        print(f"    Status: {resp.status_code}")
        print(f"    Response: {resp.json()}")
        return resp.json().get("execution_id")
    except Exception as e:
        print(f"    ERROR: {e}")
        return None

def test_status(execution_id):
    """Test status endpoint."""
    print(f"\n[TEST] Get Status for {execution_id}...")
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/status/{execution_id}", timeout=5)
        print(f"    Status: {resp.status_code}")
        print(f"    Response: {resp.json()}")
        return resp.json()
    except Exception as e:
        print(f"    ERROR: {e}")
        return None

def test_list_executions():
    """Test list executions endpoint."""
    print("\n[TEST] List Executions...")
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/executions", timeout=5)
        print(f"    Status: {resp.status_code}")
        data = resp.json()
        print(f"    Total: {data.get('total', 0)}")
        return True
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

def main():
    print("=" * 70)
    print("agentic-OS API Test Client")
    print("=" * 70)
    
    # Check if server is running
    print("\n[CHECK] Is API server running on port 8080?")
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=2)
        print(f"    YES - Server is running")
        print(f"    Response: {resp.json()}")
    except:
        print("    NO - Server not running")
        print("\n    To start server, run:")
        print("    python -m uvicorn api.server:app --host 0.0.0.0 --port 8080")
        print("\n    Or install dependencies first:")
        print("    pip install fastapi uvicorn requests")
        return
    
    # Run tests
    print("\n" + "=" * 70)
    print("Running Tests")
    print("=" * 70)
    
    test_health()
    test_list_executions()
    
    # Test execution
    exec_id = test_execute()
    
    if exec_id:
        # Wait a moment
        time.sleep(1)
        # Check status
        test_status(exec_id)
    
    print("\n" + "=" * 70)
    print("Tests Complete")
    print("=" * 70)

if __name__ == "__main__":
    main()
