"""
Recommendation Metrics for Movie Recommendation Evaluation
Implements NDCG@10, Hit@10, Precision, Recall as required by the thesis expose.
"""

import numpy as np
import torch
from typing import List, Tuple, Dict


def ndcg_at_k(relevance_scores: List[float], k: int = 10) -> float:
    """
    Compute Normalized Discounted Cumulative Gain at rank k.
    
    Args:
        relevance_scores: List of relevance scores (ratings) for top-k items
        k: Rank cutoff (default 10)
    
    Returns:
        NDCG@k score (0.0 to 1.0)
    """
    if len(relevance_scores) == 0 or k == 0:
        return 0.0
    
    # Take top k
    scores = relevance_scores[:k]
    
    # Compute DCG
    dcg = sum(score / np.log2(idx + 2) for idx, score in enumerate(scores))
    
    # Compute ideal DCG (perfect ranking)
    ideal_scores = sorted(scores, reverse=True)
    idcg = sum(score / np.log2(idx + 2) for idx, score in enumerate(ideal_scores))
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


def hit_rate_at_k(relevant_items: List[bool], k: int = 10) -> float:
    """
    Compute Hit Rate at rank k.
    
    Args:
        relevant_items: List of boolean values indicating relevance in top-k
        k: Rank cutoff (default 10)
    
    Returns:
        Hit@k rate (0.0 to 1.0)
    """
    if len(relevant_items) == 0 or k == 0:
        return 0.0
    
    # Take top k
    top_k_relevant = relevant_items[:k]
    
    # Hit rate = 1 if any item in top-k is relevant, else 0
    return 1.0 if any(top_k_relevant) else 0.0


def precision_at_k(relevant_items: List[bool], k: int = 10) -> float:
    """
    Compute Precision at rank k.
    
    Args:
        relevant_items: List of boolean values indicating relevance in top-k
        k: Rank cutoff (default 10)
    
    Returns:
        Precision@k (0.0 to 1.0)
    """
    if len(relevant_items) == 0 or k == 0:
        return 0.0
    
    # Take top k
    top_k_relevant = relevant_items[:k]
    
    # Precision = relevant items / total items in top-k
    return sum(top_k_relevant) / len(top_k_relevant)


def recall_at_k(relevant_items: List[bool], total_relevant: int, k: int = 10) -> float:
    """
    Compute Recall at rank k.
    
    Args:
        relevant_items: List of boolean values indicating relevance in top-k
        total_relevant: Total number of relevant items for this user
        k: Rank cutoff (default 10)
    
    Returns:
        Recall@k (0.0 to 1.0)
    """
    if total_relevant == 0 or k == 0:
        return 0.0
    
    # Take top k
    top_k_relevant = relevant_items[:k]
    
    # Recall = relevant items found / total relevant items
    return sum(top_k_relevant) / total_relevant


def evaluate_recommendations(
    model: torch.nn.Module,
    test_data: List[Tuple[int, int, float]],
    num_users: int,
    num_items: int,
    k: int = 10,
    all_items: List[int] = None
) -> Dict[str, float]:
    """
    Evaluate recommendation model using standard metrics.
    
    Args:
        model: PyTorch model with predict(user_id, item_id) method
        test_data: List of (user_id, item_id, rating) tuples for testing
        num_users: Total number of users
        num_items: Total number of items
        k: Rank cutoff for metrics (default 10)
        all_items: List of all item IDs to consider for ranking (if None, uses all items)
    
    Returns:
        Dictionary with evaluation metrics: NDCG@k, Hit@k, Precision@k, Recall@k
    """
    model.eval()
    
    # Group test data by user
    user_test_items = {}
    user_ratings = {}
    
    for user_id, item_id, rating in test_data:
        if user_id not in user_test_items:
            user_test_items[user_id] = []
            user_ratings[user_id] = []
        user_test_items[user_id].append(item_id)
        user_ratings[user_id].append(rating)
    
    # Get all items if not provided
    if all_items is None:
        all_items = list(range(num_items))
    
    ndcg_scores = []
    hit_scores = []
    precision_scores = []
    recall_scores = []
    
    with torch.no_grad():
        for user_id in user_test_items.keys():
            # Get ground truth relevant items for this user
            ground_truth_items = set(user_test_items[user_id])
            ground_truth_ratings = dict(zip(user_test_items[user_id], user_ratings[user_id]))
            
            # Score all items for this user
            item_scores = []
            for item_id in all_items:
                # Get prediction
                user_tensor = torch.LongTensor([user_id])
                item_tensor = torch.LongTensor([item_id])
                
                if hasattr(model, 'predict'):
                    score = model.predict(user_tensor, item_tensor).item()
                else:
                    score = model(user_tensor, item_tensor).item()
                
                item_scores.append((item_id, score))
            
            # Sort by score (descending)
            item_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Get top-k predictions
            top_k_items = [item_id for item_id, _ in item_scores[:k]]
            top_k_scores = [score for _, score in item_scores[:k]]
            
            # Check relevance of top-k (relevant = rating >= 4.0)
            top_k_relevant = [
                item_id in ground_truth_items and ground_truth_ratings.get(item_id, 0.0) >= 4.0
                for item_id in top_k_items
            ]
            
            # Get relevance scores for NDCG (use actual ratings 1-5 as relevance)
            relevance_scores = []
            for item_id in top_k_items:
                if item_id in ground_truth_items:
                    # Use actual rating (1-5) as relevance score for NDCG
                    rating = ground_truth_ratings.get(item_id, 0.0)
                    relevance = rating
                else:
                    relevance = 0.0
                relevance_scores.append(relevance)
            
            # Compute metrics for this user
            ndcg_scores.append(ndcg_at_k(relevance_scores, k))
            hit_scores.append(hit_rate_at_k(top_k_relevant, k))
            precision_scores.append(precision_at_k(top_k_relevant, k))
            recall_scores.append(recall_at_k(top_k_relevant, len(ground_truth_items), k))
    
    # Average over all users
    return {
        f'NDCG@{k}': np.mean(ndcg_scores) if ndcg_scores else 0.0,
        f'Hit@{k}': np.mean(hit_scores) if hit_scores else 0.0,
        f'Precision@{k}': np.mean(precision_scores) if precision_scores else 0.0,
        f'Recall@{k}': np.mean(recall_scores) if recall_scores else 0.0,
        'num_users_evaluated': len(ndcg_scores)
    }


def evaluate_recommendations_simple(
    model: torch.nn.Module,
    test_data: List[Tuple[int, int, float]],
    num_users: int,
    num_items: int,
    k: int = 10
) -> Dict[str, float]:
    """
    Simplified evaluation for faster computation (samples users instead of all).
    
    Args:
        model: PyTorch model
        test_data: List of (user_id, item_id, rating) tuples
        num_users: Total number of users
        num_items: Total number of items
        k: Rank cutoff
    
    Returns:
        Dictionary with evaluation metrics
    """
    # Sample users for evaluation (to speed up)
    unique_users = list(set(user_id for user_id, _, _ in test_data))
    
    # Evaluate on sampled users
    sampled_data = []
    for user_id, item_id, rating in test_data:
        if user_id in unique_users[:min(100, len(unique_users))]:  # Sample up to 100 users
            sampled_data.append((user_id, item_id, rating))
    
    return evaluate_recommendations(model, sampled_data, num_users, num_items, k)

