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

# Import metrics collection
from scripts.metrics_collector import MetricsCollector, create_experiment_id
from scripts.recommendation_metrics import evaluate_recommendations_simple

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
embedding_dim = 16
print(f"\nInitializing server model: {num_users} users, {num_items} items, embedding_dim={embedding_dim}...")
if not initialize_model(SERVER_URL, num_users=num_users, num_items=num_items, embedding_dim=embedding_dim):
    print("\nFailed to initialize model. Exiting.")
    sys.exit(1)

# Step 4: Set up metrics collection
# Configuration for thesis experiments:
# - 50 simulated Python clients
# - 2 Android devices/emulators (connected separately)
# - 10 training rounds minimum for meaningful results
experiment_config = {
    "num_users": num_users,
    "num_items": num_items,
    "embedding_dim": embedding_dim,
    "num_clients": 50,  # 50 simulated clients (plus 2 Android devices)
    "alpha": 0.5,
    "dp_epsilon": None,  # No DP for baseline
    "use_dp": False,
    "num_rounds": 10,  # 10 rounds minimum for thesis
    "local_epochs": 1,
    "learning_rate": 0.01,
    "batch_size": 32,
    "seed": 42
}

experiment_id = create_experiment_id(
    dp_epsilon=experiment_config["dp_epsilon"],
    alpha=experiment_config["alpha"],
    embedding_dim=embedding_dim,
    num_clients=experiment_config["num_clients"],
    seed=experiment_config["seed"]
)

collector = MetricsCollector(experiment_id=experiment_id, results_dir="results")
collector.set_config(experiment_config)

print(f"\nExperiment ID: {experiment_id}")
print(f"Results will be saved to: results/{experiment_id}.json")
print(f"\n{'='*60}")
print("EXPERIMENT CONFIGURATION")
print(f"{'='*60}")
print(f"  Simulated Clients: {experiment_config['num_clients']}")
print(f"  Android Devices: 2 (connect separately)")
print(f"  Total Clients: {experiment_config['num_clients']} + 2 = {experiment_config['num_clients'] + 2}")
print(f"  Training Rounds: {experiment_config['num_rounds']}")
print(f"  Data Heterogeneity (α): {experiment_config['alpha']}")
print(f"  Embedding Dimension: {embedding_dim}")
print(f"{'='*60}")

# Step 5: Create non-IID data splits across clients (using training data only)
num_clients = experiment_config["num_clients"]
alpha = experiment_config["alpha"]

print(f"\nSplitting training data across {num_clients} simulated clients (non-IID, α={alpha})...")
print(f"Note: Android devices will use their own local data (not included in this split)")
client_data_splits = create_non_iid_split(train_interactions, num_clients, alpha=alpha)

# Print client data distribution (sample of first 5 and last 5)
print(f"\nClient data distribution (showing first 5 and last 5):")
for i in range(min(5, len(client_data_splits))):
    print(f"  Client {i}: {len(client_data_splits[i])} samples")
    collector.add_client_metrics(f"client_{i}", {"samples": len(client_data_splits[i])})

if len(client_data_splits) > 10:
    print(f"  ... ({len(client_data_splits) - 10} more clients) ...")
    for i in range(max(5, len(client_data_splits) - 5), len(client_data_splits)):
        print(f"  Client {i}: {len(client_data_splits[i])} samples")
        collector.add_client_metrics(f"client_{i}", {"samples": len(client_data_splits[i])})
else:
    for i in range(5, len(client_data_splits)):
        print(f"  Client {i}: {len(client_data_splits[i])} samples")
        collector.add_client_metrics(f"client_{i}", {"samples": len(client_data_splits[i])})

total_samples = sum(len(split) for split in client_data_splits)
print(f"\nTotal samples across {num_clients} simulated clients: {total_samples}")
print(f"Average samples per client: {total_samples / num_clients:.1f}")

# Step 6: Run multiple training rounds
num_rounds = experiment_config["num_rounds"]

for round_num in range(num_rounds):
    print(f"\n{'='*60}")
    print(f"=== Round {round_num + 1}/{num_rounds} ===")
    print(f"{'='*60}")
    
    # Each simulated client participates
    clients = []
    client_metrics_list = []
    total_train_loss = 0.0
    
    print(f"Training {num_clients} simulated clients...")
    for client_id in range(num_clients):
        config = ClientConfig(
            client_id=f"client_{client_id}",
            server_url=SERVER_URL,
            num_users=num_users,
            num_items=num_items,
            embedding_dim=embedding_dim,
            local_epochs=experiment_config["local_epochs"],
            learning_rate=experiment_config["learning_rate"],
            batch_size=experiment_config["batch_size"],
            use_dp=experiment_config["use_dp"],
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
            
            # Show progress for every 10th client, or first/last few
            if client_id < 3 or client_id >= num_clients - 3 or (client_id + 1) % 10 == 0:
                print(f"  Client {client_id}: loss={metrics.get('loss', 0):.4f}, samples={metrics.get('samples', 0)}")
            
            # Collect client metrics
            client_metrics_list.append({
                "client_id": f"client_{client_id}",
                "loss": metrics.get('loss', 0.0),
                "samples": metrics.get('samples', 0),
                "epochs": metrics.get('epochs', 0)
            })
            
            total_train_loss += metrics.get('loss', 0.0)
            
        except Exception as e:
            print(f"  [ERROR] Client {client_id} error: {e}")
    
    print(f"\nCompleted: {len(client_metrics_list)}/{num_clients} simulated clients trained")
    print(f"Note: Android devices should also participate in this round (connect them separately)")
    
    avg_train_loss = total_train_loss / len(client_metrics_list) if client_metrics_list else 0.0
    
    # Wait a moment for Android devices to finish (if they're participating)
    print("\nWaiting 5 seconds for Android devices to complete training...")
    print("(Make sure your 2 Android devices are also running training rounds)")
    time.sleep(5)
    
    # Aggregate (includes both simulated clients and Android devices)
    print("\nAggregating parameters from all clients (simulated + Android)...")
    aggregation_info = {}
    try:
        response = requests.post(f"{SERVER_URL}/aggregate", timeout=60)  # Longer timeout for many clients
        response.raise_for_status()
        aggregation_info = response.json()
        print(f"[OK] Aggregation result:")
        print(f"  Total clients aggregated: {aggregation_info.get('num_clients', 'N/A')}")
        print(f"  Total samples: {aggregation_info.get('total_samples', 'N/A')}")
        print(f"  Round: {aggregation_info.get('round', 'N/A')}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Aggregation failed: {e}")
        continue
    
    # Evaluate on test set after each round
    print(f"\nEvaluating model on test set after round {round_num + 1}...")
    try:
        # Fetch current global model
        test_model = create_matrix_factorization_model(num_users, num_items, embedding_dim=embedding_dim)
        encoder = ModelParamsEncoder()
        
        response = requests.get(f"{SERVER_URL}/global-params-json")
        response.raise_for_status()
        data = response.json()
        params = data["params"]
        test_model = encoder.json_params_to_model(params, test_model)
        
        # Basic evaluation metrics
        basic_metrics = evaluate_model(test_model, test_interactions)
        
        # Recommendation metrics (NDCG@10, Hit@10, etc.)
        rec_metrics = evaluate_recommendations_simple(
            test_model,
            test_interactions,
            num_users,
            num_items,
            k=10
        )
        
        # Combine all metrics
        test_metrics = {**basic_metrics, **rec_metrics}
        
        print(f"  NDCG@10: {test_metrics.get('NDCG@10', 0):.4f}")
        print(f"  Hit@10: {test_metrics.get('Hit@10', 0):.4f}")
        print(f"  MSE: {test_metrics.get('mse', 0):.4f}")
        print(f"  Accuracy: {test_metrics.get('accuracy', 0):.4f}")
        
        # Save round metrics
        collector.add_round_metrics(
            round_num=round_num + 1,
            train_loss=avg_train_loss,
            test_metrics=test_metrics,
            aggregation_info=aggregation_info,
            client_metrics=client_metrics_list
        )
        
    except Exception as e:
        print(f"[ERROR] Evaluation failed: {e}")
        # Still save round metrics without test results
        collector.add_round_metrics(
            round_num=round_num + 1,
            train_loss=avg_train_loss,
            test_metrics={},
            aggregation_info=aggregation_info,
            client_metrics=client_metrics_list
        )
    
    time.sleep(1)  # Brief pause between rounds

# Step 7: Final evaluation (comprehensive)
print("\n" + "="*60)
print("Final Model Evaluation")
print("="*60)

# Fetch final global model
print("Fetching final global model...")
test_model = create_matrix_factorization_model(num_users, num_items, embedding_dim=embedding_dim)
encoder = ModelParamsEncoder()

try:
    response = requests.get(f"{SERVER_URL}/global-params-json")
    response.raise_for_status()
    data = response.json()
    params = data["params"]
    test_model = encoder.json_params_to_model(params, test_model)
    print(f"[OK] Fetched global model from round {data.get('round', 0)}")
    
    # Comprehensive evaluation
    print(f"\nEvaluating on {len(test_interactions)} test samples...")
    
    # Basic metrics
    basic_metrics = evaluate_model(test_model, test_interactions)
    
    # Recommendation metrics
    print("Computing recommendation metrics (NDCG@10, Hit@10, etc.)...")
    rec_metrics = evaluate_recommendations_simple(
        test_model,
        test_interactions,
        num_users,
        num_items,
        k=10
    )
    
    # Combine all final metrics
    final_metrics = {**basic_metrics, **rec_metrics}
    
    collector.add_final_metrics(final_metrics)
    
    print("\n" + "="*60)
    print("Final Test Set Evaluation Results:")
    print("="*60)
    print("Recommendation Metrics:")
    print(f"  NDCG@10: {final_metrics.get('NDCG@10', 0):.4f}")
    print(f"  Hit@10: {final_metrics.get('Hit@10', 0):.4f}")
    print(f"  Precision@10: {final_metrics.get('Precision@10', 0):.4f}")
    print(f"  Recall@10: {final_metrics.get('Recall@10', 0):.4f}")
    print("\nRegression Metrics:")
    print(f"  MSE: {final_metrics.get('mse', 0):.4f}")
    print(f"  MAE: {final_metrics.get('mae', 0):.4f}")
    print(f"  Accuracy (Binary): {final_metrics.get('accuracy', 0):.4f}")
    print(f"  Test Samples: {final_metrics.get('samples', 0)}")
    print("="*60)
    
except requests.exceptions.RequestException as e:
    print(f"[ERROR] Failed to fetch global model: {e}")
    final_metrics = {}
except Exception as e:
    print(f"[ERROR] Evaluation failed: {e}")
    final_metrics = {}
    collector.add_final_metrics(final_metrics)

# Step 8: Save results
print("\n" + "="*60)
print("Saving Results")
print("="*60)

json_path = collector.save_json()
csv_path = collector.save_csv_summary()

print(f"[OK] Results saved to:")
print(f"  JSON: {json_path}")
print(f"  CSV:  {csv_path}")

# Print summary
summary = collector.get_summary()
print("\n" + "="*60)
print("Experiment Summary")
print("="*60)
print(f"Experiment ID: {summary['experiment_id']}")
print(f"Rounds: {summary['num_rounds']}")
print(f"Final NDCG@10: {summary.get('final_ndcg@10', 'N/A')}")
print(f"Final Hit@10: {summary.get('final_hit@10', 'N/A')}")
print(f"Best NDCG@10: {summary.get('best_ndcg@10', 'N/A')}")
print(f"Best Hit@10: {summary.get('best_hit@10', 'N/A')}")
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
print(f"\nAll metrics saved to: results/{experiment_id}.json")
print("="*60)