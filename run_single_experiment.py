"""
Run Single Test Experiment

Run a single experiment to demonstrate reproducibility.
This runs the dp_inf_alpha_0.5 configuration with seed 42.
"""

import json
import time
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import necessary components from run_complete_experiment
import torch
import numpy as np
import pandas as pd
from run_complete_experiment import (
    load_ratings_csv, split_train_test, create_non_iid_split,
    MatrixFactorization, train_client_local, fedavg_aggregate,
    evaluate_model
)
from scripts.recommendation_metrics import evaluate_recommendations_simple

def main():
    print("=" * 70)
    print("SINGLE TEST EXPERIMENT")
    print("Running: dp_inf_alpha_0.5_dim_64_clients_100_seed_42")
    print("=" * 70)

    # Configuration
    EMBEDDING_DIM = 64
    NUM_CLIENTS = 100
    NUM_ROUNDS = 10
    LOCAL_EPOCHS = 3
    LEARNING_RATE = 0.01
    BATCH_SIZE = 32
    ALPHA = 0.5
    SEED = 42

    start_time = time.time()

    # Set seed
    torch.manual_seed(SEED)
    np.random.seed(SEED)

    # Load data
    print("\nLoading data...")
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ratings.csv")
    interactions, num_users, num_items = load_ratings_csv(csv_path)
    train_data, test_data = split_train_test(interactions, seed=SEED)

    # Create non-IID split
    print(f"Creating non-IID split (alpha={ALPHA})...")
    client_data = create_non_iid_split(train_data, NUM_CLIENTS, alpha=ALPHA, seed=SEED)

    # Initialize global model
    print("Initializing model...")
    global_model = MatrixFactorization(num_users, num_items, EMBEDDING_DIM)

    # Training configuration
    config = {
        'lr': LEARNING_RATE,
        'batch_size': BATCH_SIZE,
        'local_epochs': LOCAL_EPOCHS,
        'use_dp': False
    }

    # Training loop
    print(f"\nStarting federated training ({NUM_ROUNDS} rounds)...")
    for round_num in range(1, NUM_ROUNDS + 1):
        round_start = time.time()
        print(f"\n--- Round {round_num}/{NUM_ROUNDS} ---")

        # Sample clients
        selected_clients = np.random.choice(NUM_CLIENTS, size=min(10, NUM_CLIENTS), replace=False)

        # Train clients
        client_states = []
        client_samples = []

        for client_id in selected_clients:
            if not client_data[client_id]:
                continue

            client_model = MatrixFactorization(num_users, num_items, EMBEDDING_DIM)
            client_model.load_state_dict(global_model.state_dict())

            state, metrics = train_client_local(client_model, client_data[client_id], config)
            client_states.append(state)
            client_samples.append(metrics['samples'])

        # Aggregate
        fedavg_aggregate(global_model, client_states, client_samples)

        # Evaluate
        if round_num % 5 == 0 or round_num == NUM_ROUNDS:
            metrics = evaluate_recommendations_simple(global_model, test_data, num_users, num_items, k=10)
            print(f"  NDCG@10: {metrics.get('NDCG@10', 0):.4f}")
            print(f"  Hit@10:  {metrics.get('Hit@10', 0):.4f}")

        round_time = time.time() - round_start
        print(f"  Round time: {round_time:.1f}s")

    # Final evaluation
    print("\n" + "=" * 70)
    print("FINAL EVALUATION")
    print("=" * 70)

    basic_metrics = evaluate_model(global_model, test_data)
    rec_metrics = evaluate_recommendations_simple(global_model, test_data, num_users, num_items, k=10)
    final_metrics = {**basic_metrics, **rec_metrics}

    print(f"\nNDCG@10: {final_metrics.get('NDCG@10', 0):.4f}")
    print(f"Hit@10:  {final_metrics.get('Hit@10', 0):.4f}")
    print(f"MSE:     {final_metrics.get('mse', 0):.4f}")
    print(f"MAE:     {final_metrics.get('mae', 0):.4f}")

    elapsed = time.time() - start_time
    print(f"\nTotal time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")

    # Compare with published results
    print("\n" + "=" * 70)
    print("COMPARISON WITH PUBLISHED RESULTS")
    print("=" * 70)

    # Load published result
    published_file = Path("results_backup/dp_inf_alpha_0.5_dim_64_clients_100_seed_42.json")
    if published_file.exists():
        with open(published_file) as f:
            published = json.load(f)

        pub_ndcg = published.get("final_metrics", {}).get("NDCG@10", 0)
        pub_hit = published.get("final_metrics", {}).get("Hit@10", 0)

        print(f"\n                  New Run      Published     Difference")
        print("-" * 70)
        print(f"NDCG@10:          {final_metrics.get('NDCG@10', 0):.4f}       {pub_ndcg:.4f}        {abs(final_metrics.get('NDCG@10', 0) - pub_ndcg):.4f}")
        print(f"Hit@10:           {final_metrics.get('Hit@10', 0):.4f}       {pub_hit:.4f}        {abs(final_metrics.get('Hit@10', 0) - pub_hit):.4f}")

        ndcg_close = abs(final_metrics.get('NDCG@10', 0) - pub_ndcg) < 0.01
        hit_close = abs(final_metrics.get('Hit@10', 0) - pub_hit) < 0.01

        if ndcg_close and hit_close:
            print("\n✅ Results are within expected variation (±0.01)")
            print("   The experiment is reproducible!")
        else:
            print("\n⚠️  Results differ by more than expected")
            print("   This could be due to:")
            print("   - PyTorch version differences")
            print("   - Hardware/precision differences")
            print("   - Random variation in sampling")
    else:
        print("\n⚠️  Published results not found in results_backup/")
        print("   Cannot compare with baseline")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

