"""
Centralized Baseline Training Script

Trains a model on all data without federated learning to establish
a baseline for comparison. This is required to measure the "≤5% accuracy loss"
target mentioned in the research questions.
"""

import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from client import (
    load_ratings_csv,
    split_train_test,
    create_matrix_factorization_model,
    evaluate_model
)
from scripts.recommendation_metrics import evaluate_recommendations_simple
from scripts.metrics_collector import MetricsCollector, create_experiment_id
import json
from pathlib import Path


class CentralizedDataset(Dataset):
    """Dataset for centralized training"""
    
    def __init__(self, interactions):
        self.interactions = interactions
    
    def __len__(self):
        return len(self.interactions)
    
    def __getitem__(self, idx):
        user_id, item_id, rating = self.interactions[idx]
        return torch.LongTensor([user_id]), torch.LongTensor([item_id]), torch.FloatTensor([rating])


def train_centralized_model(train_data, test_data, num_users, num_items, embedding_dim=16,
                           num_epochs=50, learning_rate=0.01, batch_size=64, seed=42):
    """
    Train a centralized model on all training data.
    
    Args:
        train_data: Training interactions
        test_data: Test interactions
        num_users: Number of users
        num_items: Number of items
        embedding_dim: Embedding dimension
        num_epochs: Number of training epochs
        learning_rate: Learning rate
        batch_size: Batch size
        seed: Random seed
    
    Returns:
        Trained model and metrics
    """
    # Set random seed
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    # Create model
    model = create_matrix_factorization_model(num_users, num_items, embedding_dim)
    
    # Create dataset and dataloader
    train_dataset = CentralizedDataset(train_data)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    # Training setup
    optimizer = optim.SGD(
        model.parameters(),
        lr=learning_rate,
        weight_decay=1e-5  # L2 regularization for stability
    )
    criterion = nn.MSELoss()  # MSE loss for rating prediction
    
    print(f"\nTraining centralized model...")
    print(f"  Training samples: {len(train_data)}")
    print(f"  Test samples: {len(test_data)}")
    print(f"  Epochs: {num_epochs}")
    print(f"  Learning rate: {learning_rate}")
    print(f"  Batch size: {batch_size}")
    
    # Training loop
    train_losses = []
    test_metrics_history = []
    
    for epoch in range(num_epochs):
        model.train()
        epoch_loss = 0.0
        num_batches = 0
        
        for user_ids, item_ids, ratings in train_loader:
            user_ids = user_ids.squeeze()
            item_ids = item_ids.squeeze()
            ratings = ratings.squeeze()
            
            # Forward pass
            predictions = model(user_ids, item_ids)
            loss = criterion(predictions, ratings)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            num_batches += 1
        
        avg_loss = epoch_loss / num_batches if num_batches > 0 else 0.0
        train_losses.append(avg_loss)
        
        # Evaluate on test set every 10 epochs
        if (epoch + 1) % 10 == 0 or epoch == num_epochs - 1:
            model.eval()
            
            # Basic metrics
            basic_metrics = evaluate_model(model, test_data)
            
            # Recommendation metrics
            rec_metrics = evaluate_recommendations_simple(
                model, test_data, num_users, num_items, k=10
            )
            
            test_metrics = {**basic_metrics, **rec_metrics}
            test_metrics_history.append({
                'epoch': epoch + 1,
                'metrics': test_metrics
            })
            
            print(f"  Epoch {epoch + 1}/{num_epochs}: Loss={avg_loss:.4f}, "
                  f"NDCG@10={test_metrics.get('NDCG@10', 0):.4f}, "
                  f"Hit@10={test_metrics.get('Hit@10', 0):.4f}, "
                  f"Accuracy={test_metrics.get('accuracy', 0):.4f}")
    
    # Final evaluation
    model.eval()
    final_basic_metrics = evaluate_model(model, test_data)
    final_rec_metrics = evaluate_recommendations_simple(
        model, test_data, num_users, num_items, k=10
    )
    final_metrics = {**final_basic_metrics, **final_rec_metrics}
    
    return model, {
        'train_losses': train_losses,
        'test_metrics_history': test_metrics_history,
        'final_metrics': final_metrics
    }


def main():
    """Main function to run centralized baseline"""
    
    # Load data
    csv_path = "ratings.csv"
    if not os.path.exists(csv_path):
        print(f"[ERROR] Dataset file not found: {csv_path}")
        sys.exit(1)
    
    print("Loading MovieLens 100K dataset...")
    all_interactions, num_users, num_items, user_id_map, item_id_map = load_ratings_csv(
        csv_path, binarize=False  # Use original ratings (1-5) for regression
    )
    
    print(f"Dataset loaded: {num_users} users, {num_items} items, {len(all_interactions)} interactions")
    
    # Split train/test
    train_interactions, test_interactions = split_train_test(all_interactions, test_ratio=0.2)
    
    # Training configuration
    embedding_dim = 64  # Increased from 16 to 64 for better item representation
    num_epochs = 50
    learning_rate = 0.01
    batch_size = 64
    seed = 42
    
    # Train model
    model, results = train_centralized_model(
        train_interactions,
        test_interactions,
        num_users,
        num_items,
        embedding_dim=embedding_dim,
        num_epochs=num_epochs,
        learning_rate=learning_rate,
        batch_size=batch_size,
        seed=seed
    )
    
    # Save results
    experiment_id = "centralized_baseline"
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    output_data = {
        "experiment_id": experiment_id,
        "config": {
            "num_users": num_users,
            "num_items": num_items,
            "embedding_dim": embedding_dim,
            "num_epochs": num_epochs,
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "seed": seed,
            "train_samples": len(train_interactions),
            "test_samples": len(test_interactions)
        },
        "train_losses": results['train_losses'],
        "test_metrics_history": results['test_metrics_history'],
        "final_metrics": results['final_metrics']
    }
    
    json_path = results_dir / f"{experiment_id}.json"
    with open(json_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n{'='*60}")
    print("Centralized Baseline Results")
    print(f"{'='*60}")
    print(f"Final Metrics:")
    final = results['final_metrics']
    print(f"  NDCG@10: {final.get('NDCG@10', 0):.4f}")
    print(f"  Hit@10: {final.get('Hit@10', 0):.4f}")
    print(f"  Precision@10: {final.get('Precision@10', 0):.4f}")
    print(f"  Recall@10: {final.get('Recall@10', 0):.4f}")
    print(f"  Accuracy: {final.get('accuracy', 0):.4f}")
    print(f"  MSE: {final.get('mse', 0):.4f}")
    print(f"  MAE: {final.get('mae', 0):.4f}")
    print(f"{'='*60}")
    print(f"\nResults saved to: {json_path}")
    print(f"\nThis baseline will be used to measure accuracy loss in federated experiments.")


if __name__ == "__main__":
    main()

