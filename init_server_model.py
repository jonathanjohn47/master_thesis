"""
Quick script to initialize the server model.
Run this before starting federated learning experiments.
"""

import requests
import sys

SERVER_URL = "http://localhost:8000"

def initialize_model(num_users=50, num_items=4032, embedding_dim=16):
    """Initialize the global model on the server"""
    try:
        print(f"Initializing model on server at {SERVER_URL}...")
        print(f"Parameters: {num_users} users, {num_items} items, embedding_dim={embedding_dim}")
        
        response = requests.post(
            f"{SERVER_URL}/init-model",
            params={
                "num_users": num_users,
                "num_items": num_items,
                "embedding_dim": embedding_dim
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] Model initialized successfully!")
            print(f"Response: {result}")
            return True
        else:
            print(f"[ERROR] Failed to initialize model: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to server at {SERVER_URL}")
        print("Make sure the server is running:")
        print("  python server.py")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def check_server_health():
    """Check if server is running"""
    try:
        response = requests.get(f"{SERVER_URL}/healthz", timeout=5)
        if response.status_code == 200:
            print("[OK] Server is running")
            return True
        else:
            print(f"[WARNING] Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Server is not running or not accessible at {SERVER_URL}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Federated Learning Server Model Initialization")
    print("=" * 60)
    print()
    
    # Check server health first
    if not check_server_health():
        print("\nPlease start the server first:")
        print("  python server.py")
        sys.exit(1)
    
    print()
    
    # Initialize model
    success = initialize_model()
    
    print()
    print("=" * 60)
    
    if success:
        print("[OK] Ready! You can now connect Android devices or Python clients.")
        print("=" * 60)
        sys.exit(0)
    else:
        print("[ERROR] Initialization failed. Please check the error above.")
        print("=" * 60)
        sys.exit(1)

