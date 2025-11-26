"""
Helper script to start the federated learning server.
This can be used to start the server in a separate process.
"""

import subprocess
import sys
import os

def start_server():
    """Start the server as a separate process."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(script_dir, "server.py")
    
    print("Starting federated learning server...")
    print(f"Server script: {server_script}")
    print("\nServer will start on http://0.0.0.0:8000")
    print("You can access the API docs at http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        # Start the server
        subprocess.run([sys.executable, server_script], check=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    start_server()

