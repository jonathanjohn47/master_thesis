"""
Differential Privacy Budget Sweep Experiment

Runs federated learning experiments with different DP budgets (ε ∈ {∞, 8, 4, 2, 1})
to answer RQ1: How does model accuracy degrade across DP budgets?
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
from scripts.rdp_accountant import compute_sigma_for_target_epsilon, compute_epsilon_for_sigma
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
        print(f"[OK] Model initialized: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to initialize model: {e}")
        return False


def load_centralized_baseline():
    """Load centralized baseline metrics for comparison."""
    baseline_path = Path("results/centralized_baseline.json")
    if baseline_path.exists():
        with open(baseline_path, 'r') as f:
            baseline_data = json.load(f)
            return baseline_data.get('final_metrics', {})
    else:
        print("[WARNING] Centralized baseline not found. Run centralized_baseline.py first.")
        return {}


def run_dp_experiment(epsilon: float, 
                     train_interactions, 
                     test_interactions,
                     num_users, 
                     num_items, 
                     embedding_dim,
                     num_clients,
                     alpha,
                     num_rounds,
                     local_epochs,
                     learning_rate,
                     batch_size,
                     seed):
    """
    Run a single federated learning experiment with specified DP budget.
    
    Args:
        epsilon: Target DP budget (use float('inf') for no DP)
        ... other parameters ...
    
    Returns:
        Experiment results dictionary
    """
    print(f"\n{'='*60}")
    print(f"Running experiment with ε = {epsilon}")
    print(f"{'='*60}")
    
    # Calculate DP parameters
    use_dp = epsilon != float('inf')
    dp_sigma = 0.0
    dp_clip_norm = 1.0
    
    if use_dp:
        # Estimate average samples per client
        avg_samples = len(train_interactions) // num_clients
        
        # Find sigma for target epsilon
        dp_sigma = compute_sigma_for_target_epsilon(
            target_epsilon=epsilon,
            num_rounds=num_rounds,
            samples_per_client=avg_samples,
            batch_size=batch_size,
            clip_norm=dp_clip_norm
        )
        
        if dp_sigma is None:
            print(f"[WARNING] Could not find sigma for ε={epsilon}. Using default sigma=1.0")
            dp_sigma = 1.0
        else:
            print(f"  Computed sigma={dp_sigma:.4f} for target ε={epsilon}")
    else:
        print("  No DP (ε=∞)")
    
    # Create experiment ID
    experiment_id = create_experiment_id(
        dp_epsilon=epsilon if use_dp else None,
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
        "dp_epsilon": epsilon if use_dp else None,
        "use_dp": use_dp,
        "dp_sigma": dp_sigma,
        "dp_clip_norm": dp_clip_norm,
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
                dp_clip_norm=dp_clip_norm,
                dp_delta=1e-5
            )
            
            client = FederatedClient(config, client_data_splits[client_id])
            clients.append(client)
            
            try:
                client.register()
                metrics = client.run_training_round()
                
                if client_id < 3 or (client_id + 1) % 20 == 0:
                    print(f"  Client {client_id}: loss={metrics.get('loss', 0):.4f}")
                
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
    
    # Compare with baseline
    baseline_metrics = load_centralized_baseline()
    if baseline_metrics:
        final_metrics = collector.get_summary()
        baseline_ndcg = baseline_metrics.get('NDCG@10', 0)
        baseline_hit = baseline_metrics.get('Hit@10', 0)
        
        federated_ndcg = final_metrics.get('final_ndcg@10', 0)
        federated_hit = final_metrics.get('final_hit@10', 0)
        
        if baseline_ndcg > 0:
            ndcg_loss = ((baseline_ndcg - federated_ndcg) / baseline_ndcg) * 100
            hit_loss = ((baseline_hit - federated_hit) / baseline_hit) * 100
            
            print(f"\nComparison with centralized baseline:")
            print(f"  NDCG@10: Baseline={baseline_ndcg:.4f}, Federated={federated_ndcg:.4f}, Loss={ndcg_loss:.2f}%")
            print(f"  Hit@10: Baseline={baseline_hit:.4f}, Federated={federated_hit:.4f}, Loss={hit_loss:.2f}%")
            print(f"  Target: ≤5% accuracy loss")
            print(f"  Status: {'✓ Meets target' if ndcg_loss <= 5 and hit_loss <= 5 else '✗ Exceeds target'}")
    
    return collector.get_summary()


def main():
    """Main function to run DP sweep experiments"""
    
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
        csv_path, binarize=True, threshold=4.0
    )
    
    train_interactions, test_interactions = split_train_test(all_interactions, test_ratio=0.2)
    
    # Initialize server model
    embedding_dim = 64  # Increased from 16 to 64 for better item representation
    if not initialize_model(SERVER_URL, num_users, num_items, embedding_dim):
        sys.exit(1)
    
    # Experiment configuration
    DP_EPSILONS = [float('inf'), 8, 4, 2, 1]  # As per expose
    num_clients = 100
    alpha = 0.5
    num_rounds = 10
    local_epochs = 3  # Increased from 1 to 3 for better local convergence
    learning_rate = 0.01
    batch_size = 32
    seeds = [42, 123, 456]  # 3 seeds for statistical significance
    
    print(f"\n{'='*60}")
    print("DP Budget Sweep Experiment")
    print(f"{'='*60}")
    print(f"DP Budgets: {DP_EPSILONS}")
    print(f"Seeds: {seeds}")
    print(f"Total experiments: {len(DP_EPSILONS)} × {len(seeds)} = {len(DP_EPSILONS) * len(seeds)}")
    print(f"{'='*60}")
    
    # Run experiments
    all_results = {}
    
    for epsilon in DP_EPSILONS:
        epsilon_results = []
        
        for seed in seeds:
            # Reset server model for each experiment
            if not initialize_model(SERVER_URL, num_users, num_items, embedding_dim):
                print(f"[ERROR] Failed to reset model. Skipping ε={epsilon}, seed={seed}")
                continue
            
            result = run_dp_experiment(
                epsilon=epsilon,
                train_interactions=train_interactions,
                test_interactions=test_interactions,
                num_users=num_users,
                num_items=num_items,
                embedding_dim=embedding_dim,
                num_clients=num_clients,
                alpha=alpha,
                num_rounds=num_rounds,
                local_epochs=local_epochs,
                learning_rate=learning_rate,
                batch_size=batch_size,
                seed=seed
            )
            
            epsilon_results.append(result)
            time.sleep(2)  # Brief pause between experiments
        
        all_results[epsilon] = epsilon_results
    
    # Summary
    print(f"\n{'='*60}")
    print("DP Sweep Summary")
    print(f"{'='*60}")
    
    for epsilon in DP_EPSILONS:
        if epsilon in all_results:
            results = all_results[epsilon]
            ndcg_values = [r.get('final_ndcg@10', 0) for r in results]
            hit_values = [r.get('final_hit@10', 0) for r in results]
            
            avg_ndcg = np.mean(ndcg_values)
            avg_hit = np.mean(hit_values)
            std_ndcg = np.std(ndcg_values)
            std_hit = np.std(hit_values)
            
            print(f"\nε = {epsilon}:")
            print(f"  NDCG@10: {avg_ndcg:.4f} ± {std_ndcg:.4f}")
            print(f"  Hit@10: {avg_hit:.4f} ± {std_hit:.4f}")
    
    print(f"\n{'='*60}")
    print("All experiments completed!")


if __name__ == "__main__":
    main()

