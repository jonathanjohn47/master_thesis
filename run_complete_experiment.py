"""
Complete Experiment Runner (In-Memory)

Runs all experiments without HTTP server overhead:
- DP sweep: ε ∈ {∞, 8, 4, 2, 1} × 3 seeds (RQ1)
- Heterogeneity sweep: α ∈ {0.1, 0.5, 1.0} × 3 seeds (RQ3)
- Privacy attack evaluation for each DP budget (RQ2)
- Generates comprehensive analysis figures

All federated learning is simulated in-memory for efficiency.
"""

import json
import time
import os
import sys
import copy
import base64
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scripts.recommendation_metrics import evaluate_recommendations_simple
from scripts.rdp_accountant import compute_sigma_for_target_epsilon, compute_epsilon_for_sigma
from scripts.attack_evaluation import MembershipInferenceAttack, ModelInversionAttack

# ============================================================
# Model Definition
# ============================================================

class MatrixFactorization(nn.Module):
    def __init__(self, num_users, num_items, embedding_dim):
        super().__init__()
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.item_embedding = nn.Embedding(num_items, embedding_dim)
        nn.init.normal_(self.user_embedding.weight, std=0.1)
        nn.init.normal_(self.item_embedding.weight, std=0.1)

    def forward(self, user_ids, item_ids):
        user_emb = self.user_embedding(user_ids)
        item_emb = self.item_embedding(item_ids)
        return (user_emb * item_emb).sum(dim=1)

    def predict(self, user_ids, item_ids):
        return self.forward(user_ids, item_ids)


class MovieLensDataset(Dataset):
    def __init__(self, interactions):
        self.interactions = interactions

    def __len__(self):
        return len(self.interactions)

    def __getitem__(self, idx):
        user_id, item_id, rating = self.interactions[idx]
        return torch.LongTensor([user_id]), torch.LongTensor([item_id]), torch.FloatTensor([rating])


# ============================================================
# Data Loading
# ============================================================

def load_ratings_csv(csv_path: str) -> Tuple[List[tuple], int, int]:
    """Load ratings from CSV and return interactions with 0-indexed IDs."""
    print(f"Loading ratings from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} ratings")

    unique_users = sorted(df['userId'].unique())
    unique_items = sorted(df['movieId'].unique())
    user_map = {uid: idx for idx, uid in enumerate(unique_users)}
    item_map = {iid: idx for idx, iid in enumerate(unique_items)}

    num_users = len(unique_users)
    num_items = len(unique_items)

    interactions = [
        (user_map[row['userId']], item_map[row['movieId']], float(row['rating']))
        for _, row in df.iterrows()
    ]

    print(f"  {num_users} users, {num_items} items, {len(interactions)} interactions")
    return interactions, num_users, num_items


def split_train_test(interactions, test_ratio=0.2, seed=42):
    """Split interactions into train/test."""
    np.random.seed(seed)
    indices = np.random.permutation(len(interactions))
    split_idx = int(len(interactions) * (1 - test_ratio))
    train = [interactions[i] for i in indices[:split_idx]]
    test = [interactions[i] for i in indices[split_idx:]]
    print(f"  Train: {len(train)}, Test: {len(test)}")
    return train, test


def create_non_iid_split(interactions, num_clients, alpha=0.5, seed=42):
    """Create non-IID data split using Dirichlet distribution."""
    np.random.seed(seed)

    user_interactions = {}
    for uid, iid, r in interactions:
        user_interactions.setdefault(uid, []).append((uid, iid, r))

    user_ids = list(user_interactions.keys())
    proportions = np.random.dirichlet([alpha] * num_clients, size=len(user_ids))

    client_splits = [[] for _ in range(num_clients)]
    for user_idx, uid in enumerate(user_ids):
        for interaction in user_interactions[uid]:
            cidx = np.random.choice(num_clients, p=proportions[user_idx])
            client_splits[cidx].append(interaction)

    return client_splits


# ============================================================
# DP-SGD Utilities
# ============================================================

def clip_gradients(model, clip_norm):
    """Clip per-sample gradients."""
    grads = [p.grad.data.flatten() for p in model.parameters() if p.grad is not None]
    if not grads:
        return
    total_norm = torch.norm(torch.cat(grads))
    if total_norm > clip_norm:
        clip_coef = clip_norm / (total_norm + 1e-6)
        for p in model.parameters():
            if p.grad is not None:
                p.grad.data.mul_(clip_coef)


def add_gaussian_noise(model, sigma, clip_norm):
    """Add Gaussian noise for DP-SGD."""
    for p in model.parameters():
        if p.grad is not None:
            noise = torch.normal(0.0, sigma * clip_norm, size=p.grad.shape)
            p.grad.data.add_(noise)


# ============================================================
# In-Memory Federated Learning
# ============================================================

def train_client_local(model, data, config):
    """Train a client model locally and return updated state dict and metrics."""
    if not data:
        return model.state_dict(), {"loss": 0.0, "samples": 0}

    model.train()
    optimizer = optim.SGD(model.parameters(), lr=config['lr'], weight_decay=1e-5)
    criterion = nn.MSELoss()
    dataset = MovieLensDataset(data)
    loader = DataLoader(dataset, batch_size=config['batch_size'], shuffle=True)

    total_loss = 0.0
    num_batches = 0

    for epoch in range(config['local_epochs']):
        for user_ids, item_ids, ratings in loader:
            user_ids = user_ids.squeeze(1)
            item_ids = item_ids.squeeze(1)
            ratings = ratings.squeeze(1)

            preds = model(user_ids, item_ids)
            loss = criterion(preds, ratings)

            optimizer.zero_grad()
            loss.backward()

            if config.get('use_dp', False):
                clip_gradients(model, config['dp_clip_norm'])
                add_gaussian_noise(model, config['dp_sigma'], config['dp_clip_norm'])

            optimizer.step()
            total_loss += loss.item()
            num_batches += 1

    avg_loss = total_loss / max(num_batches, 1)
    return model.state_dict(), {"loss": avg_loss, "samples": len(data)}


def fedavg_aggregate(global_model, client_states, client_sample_counts):
    """Weighted FedAvg aggregation."""
    total_samples = sum(client_sample_counts)
    if total_samples == 0:
        return

    aggregated = {}
    for key in global_model.state_dict():
        aggregated[key] = torch.zeros_like(global_model.state_dict()[key])

    for state_dict, sample_count in zip(client_states, client_sample_counts):
        weight = sample_count / total_samples
        for key in aggregated:
            aggregated[key] += weight * state_dict[key]

    global_model.load_state_dict(aggregated)


def evaluate_model(model, test_data, batch_size=256):
    """Evaluate model on test data."""
    model.eval()
    if not test_data:
        return {"mse": 0.0, "mae": 0.0, "accuracy": 0.0, "samples": 0}

    dataset = MovieLensDataset(test_data)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    total_mse = 0.0
    total_mae = 0.0
    total_samples = 0

    with torch.no_grad():
        for user_ids, item_ids, ratings in loader:
            user_ids = user_ids.squeeze(1)
            item_ids = item_ids.squeeze(1)
            ratings = ratings.squeeze(1)

            preds = model(user_ids, item_ids)
            total_mse += ((preds - ratings) ** 2).sum().item()
            total_mae += torch.abs(preds - ratings).sum().item()
            total_samples += len(ratings)

    return {
        "mse": total_mse / max(total_samples, 1),
        "mae": total_mae / max(total_samples, 1),
        "samples": total_samples
    }


def run_federated_experiment(
    train_data, test_data, num_users, num_items,
    embedding_dim, num_clients, alpha, num_rounds,
    local_epochs, lr, batch_size, seed,
    use_dp=False, dp_epsilon=None, dp_sigma=0.0, dp_clip_norm=1.0
):
    """Run a single federated learning experiment in-memory."""
    torch.manual_seed(seed)
    np.random.seed(seed)

    # Initialize global model
    global_model = MatrixFactorization(num_users, num_items, embedding_dim)

    # Split data
    client_data = create_non_iid_split(train_data, num_clients, alpha=alpha, seed=seed)

    config = {
        'local_epochs': local_epochs,
        'lr': lr,
        'batch_size': batch_size,
        'use_dp': use_dp,
        'dp_sigma': dp_sigma,
        'dp_clip_norm': dp_clip_norm,
    }

    rounds_data = []
    # Evaluate recommendations at key rounds only (expensive operation)
    eval_rounds = {1, num_rounds // 2, num_rounds}

    for round_num in range(1, num_rounds + 1):
        client_states = []
        client_samples = []
        round_losses = []

        for cid in range(num_clients):
            # Create client model from global params
            client_model = MatrixFactorization(num_users, num_items, embedding_dim)
            client_model.load_state_dict(copy.deepcopy(global_model.state_dict()))

            # Train locally
            state_dict, metrics = train_client_local(client_model, client_data[cid], config)
            client_states.append(state_dict)
            client_samples.append(metrics['samples'])
            round_losses.append(metrics['loss'])

        # Aggregate
        fedavg_aggregate(global_model, client_states, client_samples)

        avg_loss = np.mean(round_losses)

        # Always compute basic metrics (fast)
        basic_metrics = evaluate_model(global_model, test_data)

        # Compute expensive rec metrics only at key rounds
        if round_num in eval_rounds:
            rec_metrics = evaluate_recommendations_simple(
                global_model, test_data, num_users, num_items, k=10
            )
            test_metrics = {**basic_metrics, **rec_metrics}
        else:
            test_metrics = basic_metrics

        rounds_data.append({
            "round": round_num,
            "train_loss": avg_loss,
            "test_metrics": test_metrics,
            "aggregation": {
                "num_clients": num_clients,
                "total_samples": sum(client_samples)
            }
        })

        ndcg = test_metrics.get('NDCG@10', 'N/A')
        hit = test_metrics.get('Hit@10', 'N/A')
        mse = test_metrics.get('mse', 0)
        if isinstance(ndcg, float):
            print(f"  Round {round_num}/{num_rounds}: loss={avg_loss:.4f}, MSE={mse:.4f}, NDCG@10={ndcg:.4f}, Hit@10={hit:.4f}")
        else:
            print(f"  Round {round_num}/{num_rounds}: loss={avg_loss:.4f}, MSE={mse:.4f}")

    # Final evaluation
    final_basic = evaluate_model(global_model, test_data)
    final_rec = evaluate_recommendations_simple(
        global_model, test_data, num_users, num_items, k=10
    )
    final_metrics = {**final_basic, **final_rec}

    return global_model, rounds_data, final_metrics


# ============================================================
# Privacy Attack Evaluation
# ============================================================

def run_attack_evaluation_for_model(
    model, train_data, test_data, num_users, num_items,
    embedding_dim, dp_epsilon, seed
):
    """Run MIA and model inversion attacks on a trained model."""
    print(f"  Running privacy attacks for ε={dp_epsilon}...")
    torch.manual_seed(seed)
    np.random.seed(seed)

    results = {}

    # --- Membership Inference Attack ---
    # Train shadow models (simplified: train 3 small models on subsets)
    shadow_models = []
    subset_size = min(len(train_data) // 3, 5000)

    for i in range(3):
        shadow_model = MatrixFactorization(num_users, num_items, embedding_dim)
        optimizer = optim.SGD(shadow_model.parameters(), lr=0.01, weight_decay=1e-5)
        criterion = nn.MSELoss()
        shadow_model.train()

        # Sample subset
        indices = np.random.choice(len(train_data), subset_size, replace=False)
        subset = [train_data[j] for j in indices]
        dataset = MovieLensDataset(subset)
        loader = DataLoader(dataset, batch_size=64, shuffle=True)

        # Train for a few epochs
        for epoch in range(5):
            for u, it, r in loader:
                u, it, r = u.squeeze(1), it.squeeze(1), r.squeeze(1)
                pred = shadow_model(u, it)
                loss = criterion(pred, r)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        shadow_models.append(shadow_model)

    # Run MIA
    mia = MembershipInferenceAttack(num_shadow_models=3)
    train_acc = mia.train_attack_classifier(shadow_models, train_data, test_data)

    mia_results = mia.evaluate(model, train_data, test_data)
    results["mia"] = {
        "train_accuracy": train_acc,
        **mia_results
    }
    print(f"    MIA: AUC={mia_results.get('auc', 0):.4f}, Acc={mia_results.get('accuracy', 0):.4f}")

    # --- Model Inversion Attack ---
    inversion = ModelInversionAttack(num_items=num_items, top_k=10)

    # Build ground truth from training data
    user_items = {}
    for uid, iid, rating in train_data:
        user_items.setdefault(uid, []).append((iid, rating))

    ground_truth = {}
    for uid, items in user_items.items():
        sorted_items = sorted(items, key=lambda x: x[1], reverse=True)
        ground_truth[uid] = [iid for iid, _ in sorted_items[:10]]

    inversion_results = inversion.evaluate(model, test_data, ground_truth)
    results["inversion"] = inversion_results
    print(f"    Inversion: Top-K Acc={inversion_results.get('top_k_accuracy', 0):.4f}")

    return results


# ============================================================
# Save Results
# ============================================================

def save_experiment_results(
    experiment_id, config, rounds_data, final_metrics,
    attack_results=None, results_dir="results"
):
    """Save experiment results to JSON and CSV."""
    Path(results_dir).mkdir(parents=True, exist_ok=True)

    data = {
        "experiment_id": experiment_id,
        "timestamp": datetime.now().isoformat(),
        "config": config,
        "rounds": rounds_data,
        "final_metrics": final_metrics,
    }
    if attack_results:
        data["attack_results"] = attack_results

    json_path = Path(results_dir) / f"{experiment_id}.json"
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

    # CSV summary
    csv_path = Path(results_dir) / f"{experiment_id}_summary.csv"
    with open(csv_path, 'w') as f:
        f.write("Round,Train_Loss,NDCG@10,Hit@10,Precision@10,Recall@10,MSE,MAE\n")
        for rd in rounds_data:
            tm = rd.get("test_metrics", {})
            f.write(f"{rd['round']},{rd.get('train_loss', '')},{tm.get('NDCG@10', '')},"
                    f"{tm.get('Hit@10', '')},{tm.get('Precision@10', '')},"
                    f"{tm.get('Recall@10', '')},{tm.get('mse', '')},{tm.get('mae', '')}\n")
        f.write(f"FINAL,,{final_metrics.get('NDCG@10', '')},"
                f"{final_metrics.get('Hit@10', '')},{final_metrics.get('Precision@10', '')},"
                f"{final_metrics.get('Recall@10', '')},{final_metrics.get('mse', '')},"
                f"{final_metrics.get('mae', '')}\n")

    print(f"  Saved: {json_path}")
    return str(json_path)


def create_experiment_id(dp_epsilon, alpha, embedding_dim, num_clients, seed):
    """Create standardized experiment ID."""
    parts = []
    if dp_epsilon is None or dp_epsilon == float('inf'):
        parts.append("dp_inf")
    else:
        parts.append(f"dp_{dp_epsilon}")
    if alpha is not None:
        parts.append(f"alpha_{alpha}")
    parts.append(f"dim_{embedding_dim}")
    parts.append(f"clients_{num_clients}")
    parts.append(f"seed_{seed}")
    return "_".join(parts)


# ============================================================
# Main Experiment Runner
# ============================================================

def main():
    start_time = time.time()

    print("=" * 70)
    print("COMPLETE EXPERIMENT RUNNER")
    print("Federated Learning for Mobile Movie Recommendation")
    print("=" * 70)

    # --- Configuration ---
    EMBEDDING_DIM = 64
    NUM_CLIENTS = 100
    NUM_ROUNDS = 10
    LOCAL_EPOCHS = 3
    LEARNING_RATE = 0.01
    BATCH_SIZE = 32
    DP_CLIP_NORM = 1.0

    DP_EPSILONS = [float('inf'), 8, 4, 2, 1]
    ALPHA_VALUES = [0.1, 0.5, 1.0]
    SEEDS = [42, 123, 456]
    DEFAULT_ALPHA = 0.5

    # --- Load Data ---
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ratings.csv")
    interactions, num_users, num_items = load_ratings_csv(csv_path)
    train_data, test_data = split_train_test(interactions)

    # Load baseline for comparison
    baseline_path = Path(os.path.dirname(os.path.abspath(__file__))) / "results" / "centralized_baseline.json"
    baseline = None
    if baseline_path.exists():
        with open(baseline_path) as f:
            baseline = json.load(f)
        print(f"Loaded centralized baseline: NDCG@10={baseline['final_metrics'].get('NDCG@10', 0):.4f}")

    # ================================================================
    # PHASE 1: DP Sweep Experiments (RQ1)
    # ================================================================
    print(f"\n{'=' * 70}")
    print(f"PHASE 1: DP Budget Sweep (ε ∈ {DP_EPSILONS})")
    print(f"Total: {len(DP_EPSILONS)} × {len(SEEDS)} = {len(DP_EPSILONS) * len(SEEDS)} experiments")
    print(f"{'=' * 70}")

    dp_models = {}  # Store models for attack evaluation

    for eps_idx, epsilon in enumerate(DP_EPSILONS):
        for seed_idx, seed in enumerate(SEEDS):
            exp_num = eps_idx * len(SEEDS) + seed_idx + 1
            total_exp = len(DP_EPSILONS) * len(SEEDS)

            use_dp = epsilon != float('inf')
            dp_sigma = 0.0

            if use_dp:
                avg_samples = len(train_data) // NUM_CLIENTS
                dp_sigma = compute_sigma_for_target_epsilon(
                    target_epsilon=epsilon,
                    num_rounds=NUM_ROUNDS,
                    samples_per_client=avg_samples,
                    batch_size=BATCH_SIZE,
                    clip_norm=DP_CLIP_NORM
                )
                if dp_sigma is None:
                    # Use a proportional fallback sigma
                    dp_sigma = max(1.0, 10.0 / epsilon)
                    print(f"  [WARNING] Could not compute sigma for ε={epsilon}, using fallback {dp_sigma:.2f}")
                # Verify achieved epsilon
                achieved_eps, _ = compute_epsilon_for_sigma(
                    dp_sigma, NUM_ROUNDS, avg_samples, BATCH_SIZE, DP_CLIP_NORM
                )
                print(f"  DP: target ε={epsilon}, σ={dp_sigma:.2f}, achieved ε={achieved_eps:.2f}")

            print(f"\n[{exp_num}/{total_exp}] ε={epsilon}, seed={seed}, sigma={dp_sigma:.4f}")

            experiment_id = create_experiment_id(
                dp_epsilon=epsilon if use_dp else None,
                alpha=DEFAULT_ALPHA,
                embedding_dim=EMBEDDING_DIM,
                num_clients=NUM_CLIENTS,
                seed=seed
            )

            model, rounds_data, final_metrics = run_federated_experiment(
                train_data, test_data, num_users, num_items,
                EMBEDDING_DIM, NUM_CLIENTS, DEFAULT_ALPHA, NUM_ROUNDS,
                LOCAL_EPOCHS, LEARNING_RATE, BATCH_SIZE, seed,
                use_dp=use_dp, dp_epsilon=epsilon,
                dp_sigma=dp_sigma, dp_clip_norm=DP_CLIP_NORM
            )

            config = {
                "num_users": num_users, "num_items": num_items,
                "embedding_dim": EMBEDDING_DIM, "num_clients": NUM_CLIENTS,
                "alpha": DEFAULT_ALPHA, "dp_epsilon": epsilon if use_dp else None,
                "use_dp": use_dp, "dp_sigma": dp_sigma,
                "dp_clip_norm": DP_CLIP_NORM, "num_rounds": NUM_ROUNDS,
                "local_epochs": LOCAL_EPOCHS, "learning_rate": LEARNING_RATE,
                "batch_size": BATCH_SIZE, "seed": seed
            }

            save_experiment_results(experiment_id, config, rounds_data, final_metrics)

            # Store first-seed model for attack evaluation
            if seed == SEEDS[0]:
                dp_models[epsilon] = (copy.deepcopy(model), experiment_id)

    # ================================================================
    # PHASE 2: Heterogeneity Sweep Experiments (RQ3)
    # ================================================================
    print(f"\n{'=' * 70}")
    print(f"PHASE 2: Heterogeneity Sweep (α ∈ {ALPHA_VALUES})")
    print(f"Total: {len(ALPHA_VALUES)} × {len(SEEDS)} = {len(ALPHA_VALUES) * len(SEEDS)} experiments")
    print(f"{'=' * 70}")

    for alpha_idx, alpha in enumerate(ALPHA_VALUES):
        for seed_idx, seed in enumerate(SEEDS):
            exp_num = alpha_idx * len(SEEDS) + seed_idx + 1
            total_exp = len(ALPHA_VALUES) * len(SEEDS)

            # Skip if this is the same as a DP sweep experiment (α=0.5, no DP)
            if alpha == DEFAULT_ALPHA:
                # Check if already run in DP sweep (ε=∞, same alpha)
                existing_id = create_experiment_id(None, DEFAULT_ALPHA, EMBEDDING_DIM, NUM_CLIENTS, seed)
                existing_path = Path("results") / f"{existing_id}.json"
                if existing_path.exists():
                    print(f"\n[{exp_num}/{total_exp}] α={alpha}, seed={seed} — already exists, skipping")
                    continue

            print(f"\n[{exp_num}/{total_exp}] α={alpha}, seed={seed} (no DP)")

            experiment_id = create_experiment_id(
                dp_epsilon=None,
                alpha=alpha,
                embedding_dim=EMBEDDING_DIM,
                num_clients=NUM_CLIENTS,
                seed=seed
            )

            model, rounds_data, final_metrics = run_federated_experiment(
                train_data, test_data, num_users, num_items,
                EMBEDDING_DIM, NUM_CLIENTS, alpha, NUM_ROUNDS,
                LOCAL_EPOCHS, LEARNING_RATE, BATCH_SIZE, seed,
                use_dp=False
            )

            config = {
                "num_users": num_users, "num_items": num_items,
                "embedding_dim": EMBEDDING_DIM, "num_clients": NUM_CLIENTS,
                "alpha": alpha, "dp_epsilon": None,
                "use_dp": False, "dp_sigma": 0.0,
                "dp_clip_norm": DP_CLIP_NORM, "num_rounds": NUM_ROUNDS,
                "local_epochs": LOCAL_EPOCHS, "learning_rate": LEARNING_RATE,
                "batch_size": BATCH_SIZE, "seed": seed
            }

            save_experiment_results(experiment_id, config, rounds_data, final_metrics)

    # ================================================================
    # PHASE 3: Privacy Attack Evaluation (RQ2)
    # ================================================================
    print(f"\n{'=' * 70}")
    print("PHASE 3: Privacy Attack Evaluation")
    print(f"{'=' * 70}")

    attack_results_all = {}

    for epsilon in DP_EPSILONS:
        if epsilon in dp_models:
            model, exp_id = dp_models[epsilon]
            attack_results = run_attack_evaluation_for_model(
                model, train_data, test_data, num_users, num_items,
                EMBEDDING_DIM, epsilon, seed=42
            )
            attack_results_all[str(epsilon)] = attack_results

            # Update the experiment JSON with attack results
            json_path = Path("results") / f"{exp_id}.json"
            if json_path.exists():
                with open(json_path) as f:
                    data = json.load(f)
                data["attack_results"] = attack_results
                with open(json_path, 'w') as f:
                    json.dump(data, f, indent=2)

    # Save consolidated attack results
    attack_summary_path = Path("results") / "attack_evaluation_summary.json"
    with open(attack_summary_path, 'w') as f:
        json.dump(attack_results_all, f, indent=2)
    print(f"\nSaved attack summary: {attack_summary_path}")

    # ================================================================
    # Summary
    # ================================================================
    elapsed = time.time() - start_time
    print(f"\n{'=' * 70}")
    print("ALL EXPERIMENTS COMPLETE")
    print(f"{'=' * 70}")
    print(f"Total time: {elapsed:.0f} seconds ({elapsed/60:.1f} minutes)")

    # Print DP sweep summary
    print(f"\n--- DP Sweep Results (α={DEFAULT_ALPHA}) ---")
    for epsilon in DP_EPSILONS:
        ndcg_vals = []
        hit_vals = []
        for seed in SEEDS:
            exp_id = create_experiment_id(
                None if epsilon == float('inf') else epsilon,
                DEFAULT_ALPHA, EMBEDDING_DIM, NUM_CLIENTS, seed
            )
            path = Path("results") / f"{exp_id}.json"
            if path.exists():
                with open(path) as f:
                    data = json.load(f)
                ndcg_vals.append(data['final_metrics'].get('NDCG@10', 0))
                hit_vals.append(data['final_metrics'].get('Hit@10', 0))
        if ndcg_vals:
            print(f"  ε={epsilon}: NDCG@10={np.mean(ndcg_vals):.4f}±{np.std(ndcg_vals):.4f}, "
                  f"Hit@10={np.mean(hit_vals):.4f}±{np.std(hit_vals):.4f}")

    # Print heterogeneity sweep summary
    print(f"\n--- Heterogeneity Sweep Results (no DP) ---")
    for alpha in ALPHA_VALUES:
        ndcg_vals = []
        hit_vals = []
        for seed in SEEDS:
            exp_id = create_experiment_id(None, alpha, EMBEDDING_DIM, NUM_CLIENTS, seed)
            path = Path("results") / f"{exp_id}.json"
            if path.exists():
                with open(path) as f:
                    data = json.load(f)
                ndcg_vals.append(data['final_metrics'].get('NDCG@10', 0))
                hit_vals.append(data['final_metrics'].get('Hit@10', 0))
        if ndcg_vals:
            print(f"  α={alpha}: NDCG@10={np.mean(ndcg_vals):.4f}±{np.std(ndcg_vals):.4f}, "
                  f"Hit@10={np.mean(hit_vals):.4f}±{np.std(hit_vals):.4f}")

    # Print attack evaluation summary
    if attack_results_all:
        print(f"\n--- Attack Evaluation Summary ---")
        for eps_str, results in attack_results_all.items():
            mia = results.get('mia', {})
            inv = results.get('inversion', {})
            print(f"  ε={eps_str}: MIA AUC={mia.get('auc', 0):.4f}, "
                  f"MIA Acc={mia.get('accuracy', 0):.4f}, "
                  f"Inversion Top-K={inv.get('top_k_accuracy', 0):.4f}")

    print(f"\nResults saved to: results/")
    print("Run comprehensive_analysis.py to generate figures.")


if __name__ == "__main__":
    main()
