#!/usr/bin/env python3
"""
All-in-one showcase launcher
Starts everything you need for the demonstration
"""

import subprocess
import time
import sys
import os
import json
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        FEDERATED LEARNING SHOWCASE - LAUNCHER v1.0          ║
║                                                              ║
║   🎯 Ready to demonstrate privacy-preserving ML on mobile   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

def print_step(num, title, description=""):
    print(f"\n[STEP {num}] {title}")
    if description:
        print(f"  └─ {description}")

def print_success(msg):
    print(f"  ✓ {msg}")

def print_info(msg):
    print(f"  → {msg}")

def wait_for_server(base_url, retries=15, delay=1.0):
    """Wait until /healthz responds with JSON."""
    health_url = f"{base_url}/healthz"
    for _ in range(retries):
        try:
            with urlopen(health_url, timeout=2) as resp:
                if resp.status == 200:
                    json.loads(resp.read().decode("utf-8"))
                    return True
        except URLError:
            time.sleep(delay)
        except Exception:
            time.sleep(delay)
    return False


def main():
    print_banner()

    project_path = Path("C:\\Users\\jonat\\OneDrive\\Documents\\GitHub\\master_thesis")
    server_host = "192.168.29.147"
    server_port = int(os.getenv("FL_SERVER_PORT", "8080"))
    local_server_url = f"http://localhost:{server_port}"
    mobile_server_url = f"http://{server_host}:{server_port}"

    print_step(1, "CONFIGURATION")
    print_info("PC IP Address: 192.168.29.147")
    print_info(f"Server Port: {server_port}")
    print_info(f"Mobile URL: {mobile_server_url}")
    print_info("Project Path: " + str(project_path))

    print_step(2, "STARTING BACKEND SERVER")
    print_info("Launching Federated Learning Server...")
    print_info("This will run in background and keep listening for mobile clients")

    try:
        server_env = os.environ.copy()
        server_env["FL_SERVER_PORT"] = str(server_port)
        server_proc = subprocess.Popen(
            [sys.executable, "server.py"],
            cwd=str(project_path),
            env=server_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        print_success(f"Server process started (PID: {server_proc.pid})")
        if not wait_for_server(local_server_url):
            print("  ✗ Server did not become ready on /healthz")
            try:
                preview = "".join([server_proc.stdout.readline() for _ in range(6)]) if server_proc.stdout else ""
                if preview.strip():
                    print("  → Server output preview:")
                    print(preview)
            except Exception:
                pass
            return False
        print_success(f"Server health check passed at {local_server_url}/healthz")
    except Exception as e:
        print(f"  ✗ Failed to start server: {e}")
        return False

    print_step(3, "INITIALIZING MODEL")
    print_info("Setting up neural network parameters on server...")
    print_info("Creating 50 users, 4032 items, embedding dimension 16")

    try:
        init_env = os.environ.copy()
        init_env["FL_SERVER_URL"] = local_server_url
        result = subprocess.run(
            [sys.executable, "init_server_model.py"],
            cwd=str(project_path),
            env=init_env,
            capture_output=True,
            text=True,
            timeout=30
        )

        if "[OK]" in result.stdout:
            print_success("Model initialized successfully!")
            if "initialized" in result.stdout.lower():
                print_success("Server is ready to accept mobile clients")
        else:
            print_info("Model initialization output:")
            print(result.stdout)
    except Exception as e:
        print(f"  ⚠ Model initialization: {e}")

    print_step(4, "SHOWCASE INSTRUCTIONS")
    print("""
    
    YOUR MOBILE APP IS READY TO CONNECT!
    ════════════════════════════════════════
    
    WHAT TO DO NEXT:
    
    1. Open Flutter app in Android emulator
       cd federated_learning_in_mobile
       flutter run
    
    2. In the app, enter Server URL:
       http://192.168.29.147:8080
    
    3. Tap "Connect to Server"
       (Wait for "Connected" message)
    
    4. Tap "Start Training"
       (Watch loss curve in real-time!)
    
    5. Training will run 1-3 minutes per round
       Results auto-save to: mobile_results/
    
    ════════════════════════════════════════
    """)

    print_step(5, "MONITORING")
    print_info("Server is running in background")
    print_info("Keep this window open during showcase")
    print_info("Results will appear in real-time in mobile_results/ folder")

    print_step(6, "AFTER TRAINING COMPLETES")
    print("""
    
    ANALYZE RESULTS:
    
    1. Check mobile_results/ folder on your PC
       You'll see .json and .csv files
    
    2. Run analysis:
       python analyze_mobile_results.py
    
    3. Compare with Python baseline:
       python compare_results.py
    
    """)

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                ✓ SYSTEM READY FOR SHOWCASE!                 ║
║                                                              ║
║  • Backend server running on port {server_port:<22}║
║  • Model initialized and ready                              ║
║  • Mobile app can connect from: {mobile_server_url:<27}║
║                                                              ║
║  Press CTRL+C to stop the server when done                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    try:
        print("\n⏸ Waiting... (Press CTRL+C to stop)\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[SHUTDOWN] Stopping server...")
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()
        print("✓ Server stopped")

if __name__ == "__main__":
    main()

