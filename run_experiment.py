import requests
import time
import sys
import os
from client import (
    FederatedClient, 
    ClientConfig, 
    create_non_iid_split,
    load_ratings_csv,
    split_train_test,
    evaluate_model,
    create_matrix_factorization_model,
    ModelParamsEncoder
)
import torch
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

# Step 2: Load real MovieLens data from CSV
csv_path = "ratings.csv"
if not os.path.exists(csv_path):
    print(f"\n[ERROR] Dataset file not found: {csv_path}")
    print("Please make sure ratings.csv is in the current directory.")
    sys.exit(1)

print(f"\nLoading dataset from {csv_path}...")
# Load and preprocess data (binarize ratings as per expose: ≥4 → positive)
all_interactions, num_users, num_items, user_id_map, item_id_map = load_ratings_csv(
    csv_path, 
    binarize=True, 
    threshold=4.0
)

print(f"Dataset loaded: {num_users} users, {num_items} items, {len(all_interactions)} interactions")

# Split into train/test sets
train_interactions, test_interactions = split_train_test(all_interactions, test_ratio=0.2)

# Step 3: Initialize server model with actual data dimensions
print(f"\nInitializing server model: {num_users} users, {num_items} items...")
if not initialize_model(SERVER_URL, num_users=num_users, num_items=num_items, embedding_dim=16):
    print("\nFailed to initialize model. Exiting.")
    sys.exit(1)

# Step 4: Create non-IID data splits across clients (using training data only)
num_clients = 3
alpha = 0.5  # Dirichlet parameter (lower = more heterogeneous)

print(f"\nSplitting training data across {num_clients} clients (non-IID, α={alpha})...")
client_data_splits = create_non_iid_split(train_interactions, num_clients, alpha=alpha)

# Print client data distribution
for i, split in enumerate(client_data_splits):
    print(f"  Client {i}: {len(split)} samples")

# Step 5: Run multiple training rounds
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

# Step 6: Evaluate final model on test set
print("\n" + "="*60)
print("Evaluating final model on test set...")
print("="*60)

# Create a model instance and fetch global parameters
print("Fetching final global model...")
test_model = create_matrix_factorization_model(num_users, num_items, embedding_dim=16)
encoder = ModelParamsEncoder()

# Fetch global model parameters from server
try:
    response = requests.get(f"{SERVER_URL}/global-params-json")
    response.raise_for_status()
    data = response.json()
    params = data["params"]
    test_model = encoder.json_params_to_model(params, test_model)
    print(f"[OK] Fetched global model from round {data.get('round', 0)}")
except requests.exceptions.RequestException as e:
    print(f"[ERROR] Failed to fetch global model: {e}")
    eval_metrics = {"mse": 0.0, "mae": 0.0, "accuracy": 0.0, "samples": 0}
else:
    # Evaluate on test set using standalone function
    print(f"Evaluating on {len(test_interactions)} test samples...")
    eval_metrics = evaluate_model(test_model, test_interactions)

print("\n" + "="*60)
print("Test Set Evaluation Results:")
print("="*60)
print(f"MSE (Mean Squared Error): {eval_metrics['mse']:.4f}")
print(f"MAE (Mean Absolute Error): {eval_metrics['mae']:.4f}")
print(f"Accuracy (Binary Classification): {eval_metrics['accuracy']:.4f}")
print(f"Test Samples: {eval_metrics['samples']}")
print("="*60)

print("\n" + "="*60)
print("Training complete!")
print("="*60)
print(f"Training data: {len(train_interactions)} interactions")
print(f"Test data: {len(test_interactions)} interactions")
print(f"Total users: {num_users}")
print(f"Total items: {num_items}")
print(f"Training rounds: {num_rounds}")
print(f"Clients per round: {num_clients}")
print("="*60)