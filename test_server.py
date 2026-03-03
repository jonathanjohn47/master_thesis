#!/usr/bin/env python3
"""Test script to verify server is running and responding"""

import time
import requests
import subprocess
import sys

# Start server in background
print("Starting server on port 8001...")
server_process = subprocess.Popen(
    [sys.executable, "server.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Give server time to start
time.sleep(3)

# Test health endpoint
try:
    response = requests.get("http://localhost:8001/healthz", timeout=5)
    print(f"✓ Server responded: {response.json()}")
    print(f"✓ Server is running on port 8001")
    print("\nServer startup successful!")
except Exception as e:
    print(f"✗ Server test failed: {e}")
    print("\nServer output:")
    # Read some output from server
    import select
    if select.select([server_process.stdout], [], [], 0)[0]:
        output = server_process.stdout.read(500)
        print(output)

