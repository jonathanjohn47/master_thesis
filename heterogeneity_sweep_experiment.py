"""
Data Heterogeneity Sweep Experiment

Runs federated learning experiments with different heterogeneity levels (α ∈ {0.1, 0.5, 1.0})
to answer RQ3: How does data heterogeneity affect accuracy and privacy?
"""

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
from scripts.metrics_collector import MetricsCollector, create_experiment_id
from scripts.recommendation_metrics import evaluate_recommendations_simple
import json
from pathlib import Path


SERVER_URL = "http://localhost:8000"
MAX_WAIT_TIME = 30


def wait_for_server(url: str, max_wait: int = MAX_WAIT_TIME) -> bool:
    """Wait for the server to become available."""
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
        print(f"[OK] Model initialized")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to initialize model: {e}")
        return False


def run_heterogeneity_experiment(alpha: float,
                                train_interactions,
                                test_interactions,
                                num_users,
                                num_items,
                                embedding_dim,
                                num_clients,
                                num_rounds,
                                local_epochs,
                                learning_rate,
                                batch_size,
                                seed,
                                use_dp=False,
                                dp_epsilon=None,
                                dp_sigma=1.0):
    """
    Run a single federated learning experiment with specified heterogeneity.
    
    Args:
        alpha: Dirichlet parameter for data heterogeneity (lower = more heterogeneous)
        ... other parameters ...
    
    Returns:
        Experiment results dictionary
    """
    print(f"\n{'='*60}")
    print(f"Running experiment with α = {alpha}")
    print(f"{'='*60}")
    
    # Create experiment ID
    experiment_id = create_experiment_id(
        dp_epsilon=dp_epsilon,
        alpha=alpha,
        embedding_dim=embedding_dim,
        num_clients=num_clients,
        seed=seed
    )
    
    # Initialize metrics collector
    collector = MetricsCollector(experiment_id=experiment_id, results_dir="results")
    
    experiment_config = {
        "num_users": num_users,
        "num_items": num_items,
        "embedding_dim": embedding_dim,
        "num_clients": num_clients,
        "alpha": alpha,
        "dp_epsilon": dp_epsilon,
        "use_dp": use_dp,
        "dp_sigma": dp_sigma,
        "dp_clip_norm": 1.0,
        "num_rounds": num_rounds,
        "local_epochs": local_epochs,
        "learning_rate": learning_rate,
        "batch_size": batch_size,
        "seed": seed
    }
    collector.set_config(experiment_config)
    
    # Create non-IID data splits
    print(f"\nSplitting data across {num_clients} clients (α={alpha})...")
    client_data_splits = create_non_iid_split(train_interactions, num_clients, alpha=alpha)
    
    # Analyze data distribution
    sample_counts = [len(split) for split in client_data_splits]
    print(f"  Min samples per client: {min(sample_counts)}")
    print(f"  Max samples per client: {max(sample_counts)}")
    print(f"  Mean samples per client: {np.mean(sample_counts):.1f}")
    print(f"  Std samples per client: {np.std(sample_counts):.1f}")
    
    # Run federated learning rounds
    for round_num in range(num_rounds):
        print(f"\n--- Round {round_num + 1}/{num_rounds} ---")
        
        clients = []
        client_metrics_list = []
        total_train_loss = 0.0
        
        # Train all clients
        for client_id in range(num_clients):
            config = ClientConfig(
                client_id=f"client_{client_id}",
                server_url=SERVER_URL,
                num_users=num_users,
                num_items=num_items,
                embedding_dim=embedding_dim,
                local_epochs=local_epochs,
                learning_rate=learning_rate,
                batch_size=batch_size,
                use_dp=use_dp,
                dp_sigma=dp_sigma,
                dp_clip_norm=1.0,
                dp_delta=1e-5
            )
            
            client = FederatedClient(config, client_data_splits[client_id])
            clients.append(client)
            
            try:
                client.register()
                metrics = client.run_training_round()
                
                if client_id < 3 or (client_id + 1) % 20 == 0:
                    print(f"  Client {client_id}: loss={metrics.get('loss', 0):.4f}, samples={len(client_data_splits[client_id])}")
                
                client_metrics_list.append({
                    "client_id": f"client_{client_id}",
                    "loss": metrics.get('loss', 0.0),
                    "samples": metrics.get('samples', 0),
                    "epochs": metrics.get('epochs', 0)
                })
                
                total_train_loss += metrics.get('loss', 0.0)
                
            except Exception as e:
                print(f"  [ERROR] Client {client_id} error: {e}")
        
        avg_train_loss = total_train_loss / len(client_metrics_list) if client_metrics_list else 0.0
        
        # Aggregate
        print("Aggregating parameters...")
        try:
            response = requests.post(f"{SERVER_URL}/aggregate", timeout=120)
            response.raise_for_status()
            aggregation_info = response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Aggregation failed: {e}")
            aggregation_info = {}
        
        # Evaluate on test set
        print("Evaluating model...")
        try:
            test_model = create_matrix_factorization_model(num_users, num_items, embedding_dim=embedding_dim)
            encoder = ModelParamsEncoder()
            
            response = requests.get(f"{SERVER_URL}/global-params-json")
            response.raise_for_status()
            data = response.json()
            params = data["params"]
            test_model = encoder.json_params_to_model(params, test_model)
            
            basic_metrics = evaluate_model(test_model, test_interactions)
            rec_metrics = evaluate_recommendations_simple(
                test_model, test_interactions, num_users, num_items, k=10
            )
            
            test_metrics = {**basic_metrics, **rec_metrics}
            
            print(f"  NDCG@10: {test_metrics.get('NDCG@10', 0):.4f}, "
                  f"Hit@10: {test_metrics.get('Hit@10', 0):.4f}")
            
            collector.add_round_metrics(
                round_num=round_num + 1,
                train_loss=avg_train_loss,
                test_metrics=test_metrics,
                aggregation_info=aggregation_info,
                client_metrics=client_metrics_list
            )
            
        except Exception as e:
            print(f"[ERROR] Evaluation failed: {e}")
            collector.add_round_metrics(
                round_num=round_num + 1,
                train_loss=avg_train_loss,
                test_metrics={},
                aggregation_info=aggregation_info,
                client_metrics=client_metrics_list
            )
        
        time.sleep(1)
    
    # Final evaluation
    print("\nFinal evaluation...")
    try:
        test_model = create_matrix_factorization_model(num_users, num_items, embedding_dim=embedding_dim)
        encoder = ModelParamsEncoder()
        
        response = requests.get(f"{SERVER_URL}/global-params-json")
        response.raise_for_status()
        data = response.json()
        params = data["params"]
        test_model = encoder.json_params_to_model(params, test_model)
        
        basic_metrics = evaluate_model(test_model, test_interactions)
        rec_metrics = evaluate_recommendations_simple(
            test_model, test_interactions, num_users, num_items, k=10
        )
        
        final_metrics = {**basic_metrics, **rec_metrics}
        collector.add_final_metrics(final_metrics)
        
    except Exception as e:
        print(f"[ERROR] Final evaluation failed: {e}")
        collector.add_final_metrics({})
    
    # Save results
    json_path = collector.save_json()
    csv_path = collector.save_csv_summary()
    
    print(f"\nResults saved:")
    print(f"  JSON: {json_path}")
    print(f"  CSV:  {csv_path}")
    
    return collector.get_summary()


def main():
    """Main function to run heterogeneity sweep experiments"""
    
    # Check server
    if not wait_for_server(SERVER_URL):
        print("\nPlease start the server first: python server.py")
        sys.exit(1)
    
    # Load data
    csv_path = "ratings.csv"
    if not os.path.exists(csv_path):
        print(f"[ERROR] Dataset file not found: {csv_path}")
        sys.exit(1)
    
    print("Loading MovieLens 100K dataset...")
    all_interactions, num_users, num_items, user_id_map, item_id_map = load_ratings_csv(
        csv_path, binarize=False  # Use original ratings (1-5) for regression
    )
    
    train_interactions, test_interactions = split_train_test(all_interactions, test_ratio=0.2)
    
    # Initialize server model
    embedding_dim = 64  # Increased from 16 to 64 for better item representation
    if not initialize_model(SERVER_URL, num_users, num_items, embedding_dim):
        sys.exit(1)
    
    # Experiment configuration
    ALPHA_VALUES = [0.1, 0.5, 1.0]  # As per expose
    num_clients = 100
    num_rounds = 10
    local_epochs = 3  # Increased from 1 to 3 for better local convergence
    learning_rate = 0.01
    batch_size = 32
    seeds = [42, 123, 456]  # 3 seeds for statistical significance
    use_dp = False  # Can set to True to test with DP
    dp_epsilon = None
    
    print(f"\n{'='*60}")
    print("Heterogeneity Sweep Experiment")
    print(f"{'='*60}")
    print(f"Alpha values: {ALPHA_VALUES}")
    print(f"Seeds: {seeds}")
    print(f"Total experiments: {len(ALPHA_VALUES)} × {len(seeds)} = {len(ALPHA_VALUES) * len(seeds)}")
    print(f"{'='*60}")
    
    # Run experiments
    all_results = {}
    
    for alpha in ALPHA_VALUES:
        alpha_results = []
        
        for seed in seeds:
            # Reset server model for each experiment
            if not initialize_model(SERVER_URL, num_users, num_items, embedding_dim):
                print(f"[ERROR] Failed to reset model. Skipping α={alpha}, seed={seed}")
                continue
            
            result = run_heterogeneity_experiment(
                alpha=alpha,
                train_interactions=train_interactions,
                test_interactions=test_interactions,
                num_users=num_users,
                num_items=num_items,
                embedding_dim=embedding_dim,
                num_clients=num_clients,
                num_rounds=num_rounds,
                local_epochs=local_epochs,
                learning_rate=learning_rate,
                batch_size=batch_size,
                seed=seed,
                use_dp=use_dp,
                dp_epsilon=dp_epsilon
            )
            
            alpha_results.append(result)
            time.sleep(2)  # Brief pause between experiments
        
        all_results[alpha] = alpha_results
    
    # Summary
    print(f"\n{'='*60}")
    print("Heterogeneity Sweep Summary")
    print(f"{'='*60}")
    
    for alpha in ALPHA_VALUES:
        if alpha in all_results:
            results = all_results[alpha]
            ndcg_values = [r.get('final_ndcg@10', 0) for r in results]
            hit_values = [r.get('final_hit@10', 0) for r in results]
            
            avg_ndcg = np.mean(ndcg_values)
            avg_hit = np.mean(hit_values)
            std_ndcg = np.std(ndcg_values)
            std_hit = np.std(hit_values)
            
            print(f"\nα = {alpha}:")
            print(f"  NDCG@10: {avg_ndcg:.4f} ± {std_ndcg:.4f}")
            print(f"  Hit@10: {avg_hit:.4f} ± {std_hit:.4f}")
    
    print(f"\n{'='*60}")
    print("All experiments completed!")


if __name__ == "__main__":
    main()

