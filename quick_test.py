#!/usr/bin/env python3
"""
Quick test to verify model fixes are working.
Runs a mini experiment with 5 clients and 3 rounds.
Should complete in ~5 minutes.
"""

import sys
import time
import requests
from client import (
    load_ratings_csv, split_train_test, create_non_iid_split,
    create_matrix_factorization_model, ClientConfig, FederatedClient,
    ModelParamsEncoder
)

SERVER_URL = "http://127.0.0.1:8000"

def initialize_model(server_url, num_users, num_items, embedding_dim):
    """Initialize the server model"""
    try:
        response = requests.post(
            f"{server_url}/init-model?num_users={num_users}&num_items={num_items}&embedding_dim={embedding_dim}"
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error initializing model: {e}")
        return False

def main():
    print("="*60)
    print("QUICK TEST - Verifying Model Fixes")
    print("="*60)

    # Load data
    print("\n1. Loading data...")
    csv_path = "ratings.csv"
    all_interactions, num_users, num_items, _, _ = load_ratings_csv(csv_path)
    train_interactions, test_interactions = split_train_test(all_interactions, test_ratio=0.2)
    print(f"   ✓ Loaded {len(train_interactions)} training samples")
    print(f"   ✓ Users: {num_users}, Items: {num_items}")

    # Initialize server
    print("\n2. Initializing server with embedding_dim=64...")
    embedding_dim = 64
    if not initialize_model(SERVER_URL, num_users, num_items, embedding_dim):
        print("   ✗ Server not running or initialization failed")
        print("\n   Please start the server in another terminal:")
        print("   python3 server.py")
        sys.exit(1)
    print(f"   ✓ Server initialized (embedding_dim={embedding_dim})")

    # Create client splits
    print("\n3. Creating client splits (5 clients)...")
    num_clients = 5
    client_splits = create_non_iid_split(train_interactions, num_clients, alpha=0.5)
    print(f"   ✓ Created {num_clients} client splits")

    # Run quick training
    print("\n4. Running training (3 rounds)...")
    num_rounds = 3

    for round_num in range(1, num_rounds + 1):
        print(f"\n   Round {round_num}/{num_rounds}:")
        round_start = time.time()

        # Train clients
        for client_id in range(num_clients):
            config = ClientConfig(
                client_id=f"client_{client_id}",
                server_url=SERVER_URL,
                num_users=num_users,
                num_items=num_items,
                embedding_dim=embedding_dim,
                local_epochs=3,  # Should be 3 now
                learning_rate=0.01,
                batch_size=32,
                use_dp=False
            )

            client = FederatedClient(config, client_splits[client_id])
            result = client.run_training_round()

        # Get test metrics from server
        try:
            response = requests.get(f"{SERVER_URL}/global-params-json")
            params = response.json()

            # Create test model
            test_model = create_matrix_factorization_model(num_users, num_items, embedding_dim)
            encoder = ModelParamsEncoder()
            test_model = encoder.json_params_to_model(params, test_model)

            # Evaluate
            from client import evaluate_model, evaluate_recommendations_simple
            basic_metrics = evaluate_model(test_model, test_interactions)
            rec_metrics = evaluate_recommendations_simple(test_model, test_interactions, num_users, num_items, k=10)

            # Display results
            print(f"      Loss: {basic_metrics.get('mse', 0):.4f}")
            print(f"      Accuracy: {basic_metrics.get('accuracy', 0):.4f}")
            print(f"      NDCG@10: {rec_metrics.get('NDCG@10', 0):.4f}")
            print(f"      Hit@10: {rec_metrics.get('Hit@10', 0):.4f}")

        except Exception as e:
            print(f"      ✗ Error evaluating: {e}")

        round_time = time.time() - round_start
        print(f"      Time: {round_time:.1f}s")

    print("\n" + "="*60)
    print("QUICK TEST COMPLETE")
    print("="*60)
    print("\n✓ If you see NDCG@10 > 0.10 and Hit@10 > 0.20, the fixes are working!")
    print("  (Old model had NDCG@10 = 0.0 and Hit@10 = 0.04-0.08)")
    print("\nNext steps:")
    print("  1. Run full centralized baseline: python3 centralized_baseline.py")
    print("  2. Run full federated experiment: python3 run_experiment.py")
    print("  3. Run DP sweep: python3 dp_sweep_experiment.py")
    print("  4. Run heterogeneity sweep: python3 heterogeneity_sweep_experiment.py")

if __name__ == "__main__":
    main()
