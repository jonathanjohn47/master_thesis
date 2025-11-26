import requests
import time
import sys
from client import FederatedClient, ClientConfig, create_non_iid_split
import numpy as np

SERVER_URL = "http://localhost:8000"
MAX_WAIT_TIME = 30  # Maximum seconds to wait for server


def wait_for_server(url: str, max_wait: int = MAX_WAIT_TIME) -> bool:
    """
    Wait for the server to become available.
    
    Args:
        url: Server URL
        max_wait: Maximum time to wait in seconds
    
    Returns:
        True if server is available, False otherwise
    """
    print(f"Waiting for server at {url}...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{url}/healthz", timeout=2)
            if response.status_code == 200:
                print(f"[OK] Server is available!")
                return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass
        
        print(".", end="", flush=True)
        time.sleep(1)
    
    print(f"\n[ERROR] Server not available after {max_wait} seconds")
    return False


def initialize_model(url: str, num_users: int, num_items: int, embedding_dim: int):
    """Initialize the server model."""
    print("Initializing server model...")
    try:
        response = requests.post(
            f"{url}/init-model",
            params={
                "num_users": num_users,
                "num_items": num_items,
                "embedding_dim": embedding_dim
            },
            timeout=10
        )
        response.raise_for_status()
        print(f"[OK] Model initialized: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to initialize model: {e}")
        return False


# Step 1: Wait for server to be available
if not wait_for_server(SERVER_URL):
    print("\n" + "="*60)
    print("ERROR: Server is not running!")
    print("="*60)
    print("\nPlease start the server first by running:")
    print("  python server.py")
    print("\nThen run this script again in a different terminal.")
    print("="*60)
    sys.exit(1)

# Step 2: Initialize server model
if not initialize_model(SERVER_URL, num_users=943, num_items=1682, embedding_dim=16):
    print("\nFailed to initialize model. Exiting.")
    sys.exit(1)

# Step 3: Create synthetic data for multiple clients
num_users = 943
num_items = 1682
num_clients = 3

# Generate synthetic interactions
all_interactions = []
for _ in range(5000):
    user_id = np.random.randint(0, num_users)
    item_id = np.random.randint(0, num_items)
    rating = np.random.choice([1, 2, 3, 4, 5])
    all_interactions.append((user_id, item_id, float(rating)))

# Split data non-IID across clients
client_data_splits = create_non_iid_split(all_interactions, num_clients, alpha=0.5)

# Step 4: Run multiple training rounds
num_rounds = 3

for round_num in range(num_rounds):
    print(f"\n=== Round {round_num + 1} ===")
    
    # Each client participates
    clients = []
    for client_id in range(num_clients):
        config = ClientConfig(
            client_id=f"client_{client_id}",
            server_url=SERVER_URL,
            num_users=num_users,
            num_items=num_items,
            embedding_dim=16,
            local_epochs=1,
            learning_rate=0.01,
            batch_size=32,
            use_dp=False,  # Set to True to enable DP-SGD
            dp_sigma=1.0,
            dp_clip_norm=1.0,
            dp_delta=1e-5
        )
        
        client = FederatedClient(config, client_data_splits[client_id])
        clients.append(client)
        
        # Register and run training
        try:
            client.register()
            metrics = client.run_training_round()
            print(f"Client {client_id} completed: {metrics}")
        except Exception as e:
            print(f"Client {client_id} error: {e}")
    
    # Aggregate
    print("\nAggregating parameters...")
    try:
        response = requests.post(f"{SERVER_URL}/aggregate", timeout=30)
        response.raise_for_status()
        print(f"[OK] Aggregation result: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Aggregation failed: {e}")
        continue
    
    time.sleep(1)  # Brief pause between rounds

print("\nTraining complete!")