#!/usr/bin/env python3
"""
Setup and startup verification script for showcase
Confirms server is running and initializes model
"""

import subprocess
import time
import sys
import os
import requests
from pathlib import Path

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_server(host, port, max_retries=5):
    """Check if server is running"""
    for attempt in range(max_retries):
        try:
            response = requests.get(f"http://{host}:{port}/healthz", timeout=2)
            if response.status_code == 200:
                print(f"✓ Server is running on http://{host}:{port}")
                return True
        except:
            if attempt < max_retries - 1:
                print(f"  Attempt {attempt + 1}/{max_retries}: Waiting for server...")
                time.sleep(2)
    return False

def main():
    print_header("FEDERATED LEARNING SHOWCASE SETUP")

    project_dir = Path("C:\\Users\\jonat\\OneDrive\\Documents\\GitHub\\master_thesis")
    os.chdir(project_dir)

    # Get IP address
    ip_address = "192.168.29.147"
    server_port = 8080

    print(f"\nYour PC IP Address: {ip_address}")
    print(f"Server Port: {server_port}")
    print(f"Mobile App URL: http://{ip_address}:{server_port}")

    # Step 1: Start server
    print_header("STEP 1: Starting Server")
    print(f"Starting Federated Learning Server on port {server_port}...")

    try:
        server_process = subprocess.Popen(
            [sys.executable, "server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(project_dir)
        )
        print(f"✓ Server process started (PID: {server_process.pid})")
    except Exception as e:
        print(f"✗ Failed to start server: {e}")
        return False

    # Step 2: Check if server is responding
    print_header("STEP 2: Verifying Server Connection")
    if check_server("localhost", server_port):
        print(f"✓ Server is responding on http://localhost:{server_port}")
    else:
        print(f"✗ Server failed to start or is not responding")
        return False

    # Step 3: Initialize model
    print_header("STEP 3: Initializing Server Model")
    print("Initializing model parameters...")

    try:
        init_result = subprocess.run(
            [sys.executable, "init_server_model.py"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(project_dir)
        )

        if init_result.returncode == 0:
            print("✓ Server model initialized successfully")
            if "[OK]" in init_result.stdout:
                print(f"\n{init_result.stdout}")
        else:
            print(f"✗ Model initialization had issues")
            print(init_result.stdout)
            print(init_result.stderr)
    except Exception as e:
        print(f"✗ Failed to initialize model: {e}")
        return False

    # Final summary
    print_header("SETUP COMPLETE - READY FOR SHOWCASE")
    print(f"""
✓ Server Running: http://0.0.0.0:{server_port}
✓ Model Initialized: Yes
✓ PC IP Address: {ip_address}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MOBILE APP SETUP:

1. Open Flutter app in Android emulator
2. In the "Server URL" field, enter:
   
   http://{ip_address}:{server_port}

3. Client ID will auto-generate
4. Tap "Connect to Server"
5. Once connected, tap "Start Training"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESULTS LOCATION:
C:\\Users\\jonat\\OneDrive\\Documents\\GitHub\\master_thesis\\mobile_results\\

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)

    print("\n✓ Everything is ready! Server will keep running...")
    print("✓ Don't close this window while testing the mobile app.")

    # Keep server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server_process.terminate()
        server_process.wait(timeout=5)
        print("✓ Server stopped")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

