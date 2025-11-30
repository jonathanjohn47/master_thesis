"""
Privacy Attack Evaluation Framework

Implements simplified versions of:
1. Membership Inference Attack (MIA)
2. Model Inversion Attack

Note: This is a simplified implementation. For production use, consider using
AIJack or other established attack libraries.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, accuracy_score
import logging

logger = logging.getLogger(__name__)


class MembershipInferenceAttack:
    """
    Simplified Membership Inference Attack (MIA).
    
    Uses shadow models to train an attack classifier that predicts
    whether a sample was in the training set.
    """
    
    def __init__(self, num_shadow_models: int = 5):
        """
        Initialize MIA attack.
        
        Args:
            num_shadow_models: Number of shadow models to train
        """
        self.num_shadow_models = num_shadow_models
        self.attack_classifier = None
    
    def extract_features(self, model: nn.Module, sample: Tuple[int, int, float]) -> np.ndarray:
        """
        Extract features from model for a given sample.
        
        Args:
            model: Trained model
            sample: (user_id, item_id, rating) tuple
        
        Returns:
            Feature vector
        """
        model.eval()
        user_id, item_id, rating = sample
        
        with torch.no_grad():
            # Get prediction
            pred = model(torch.LongTensor([user_id]), torch.LongTensor([item_id]))
            pred_value = pred.item()
            
            # Get embedding vectors
            user_emb = model.user_embedding(torch.LongTensor([user_id])).squeeze().numpy()
            item_emb = model.item_embedding(torch.LongTensor([item_id])).squeeze().numpy()
            
            # Feature vector: prediction, prediction error, embedding norms, dot product
            features = np.concatenate([
                [pred_value],
                [abs(pred_value - rating)],
                [np.linalg.norm(user_emb)],
                [np.linalg.norm(item_emb)],
                [np.dot(user_emb, item_emb)],
                user_emb,
                item_emb
            ])
        
        return features
    
    def train_attack_classifier(self, 
                               shadow_models: List[nn.Module],
                               member_data: List[Tuple],
                               non_member_data: List[Tuple]) -> float:
        """
        Train attack classifier using shadow models.
        
        Args:
            shadow_models: List of shadow models
            member_data: Data that was used to train shadow models
            non_member_data: Data that was not used to train shadow models
        
        Returns:
            Training accuracy
        """
        # Extract features for members and non-members
        member_features = []
        non_member_features = []
        
        for model in shadow_models:
            # Sample some member and non-member data
            member_samples = np.random.choice(len(member_data), min(50, len(member_data)), replace=False)
            non_member_samples = np.random.choice(len(non_member_data), min(50, len(non_member_data)), replace=False)
            
            for idx in member_samples:
                features = self.extract_features(model, member_data[idx])
                member_features.append(features)
            
            for idx in non_member_samples:
                features = self.extract_features(model, non_member_data[idx])
                non_member_features.append(features)
        
        if len(member_features) == 0 or len(non_member_features) == 0:
            logger.warning("Not enough data for attack classifier training")
            return 0.0
        
        # Prepare training data
        X = np.array(member_features + non_member_features)
        y = np.array([1] * len(member_features) + [0] * len(non_member_features))
        
        # Train classifier
        self.attack_classifier = RandomForestClassifier(n_estimators=50, random_state=42)
        self.attack_classifier.fit(X, y)
        
        # Training accuracy
        train_pred = self.attack_classifier.predict(X)
        train_acc = accuracy_score(y, train_pred)
        
        return train_acc
    
    def evaluate(self, 
                 target_model: nn.Module,
                 member_data: List[Tuple],
                 non_member_data: List[Tuple]) -> Dict[str, float]:
        """
        Evaluate attack on target model.
        
        Args:
            target_model: Target model to attack
            member_data: Data that was in training set
            non_member_data: Data that was not in training set
        
        Returns:
            Dictionary with attack metrics (AUC, accuracy)
        """
        if self.attack_classifier is None:
            logger.error("Attack classifier not trained. Call train_attack_classifier first.")
            return {"auc": 0.0, "accuracy": 0.0}
        
        # Extract features
        member_features = []
        non_member_features = []
        
        # Sample data for evaluation
        member_samples = np.random.choice(len(member_data), min(100, len(member_data)), replace=False)
        non_member_samples = np.random.choice(len(non_member_data), min(100, len(non_member_data)), replace=False)
        
        for idx in member_samples:
            features = self.extract_features(target_model, member_data[idx])
            member_features.append(features)
        
        for idx in non_member_samples:
            features = self.extract_features(target_model, non_member_data[idx])
            non_member_features.append(features)
        
        if len(member_features) == 0 or len(non_member_features) == 0:
            return {"auc": 0.0, "accuracy": 0.0}
        
        # Predictions
        X_test = np.array(member_features + non_member_features)
        y_test = np.array([1] * len(member_features) + [0] * len(non_member_features))
        
        # Get probabilities for AUC
        y_pred_proba = self.attack_classifier.predict_proba(X_test)[:, 1]
        y_pred = self.attack_classifier.predict(X_test)
        
        # Metrics
        try:
            auc = roc_auc_score(y_test, y_pred_proba)
        except:
            auc = 0.0
        
        accuracy = accuracy_score(y_test, y_pred)
        
        return {
            "auc": auc,
            "accuracy": accuracy,
            "true_positive_rate": np.mean(y_pred[y_test == 1] == 1),
            "false_positive_rate": np.mean(y_pred[y_test == 0] == 1)
        }


class ModelInversionAttack:
    """
    Simplified Model Inversion Attack.
    
    Attempts to reconstruct training data from model parameters.
    """
    
    def __init__(self, num_items: int, top_k: int = 10):
        """
        Initialize model inversion attack.
        
        Args:
            num_items: Number of items in the dataset
            top_k: Top-K items to consider for reconstruction
        """
        self.num_items = num_items
        self.top_k = top_k
    
    def reconstruct_user_preferences(self, 
                                    model: nn.Module,
                                    user_id: int,
                                    known_items: List[int],
                                    known_ratings: List[float]) -> List[int]:
        """
        Attempt to reconstruct user's top-K preferred items.
        
        Args:
            model: Trained model
            user_id: User ID
            known_items: Items we know the user interacted with
            known_ratings: Ratings for known items
        
        Returns:
            List of top-K predicted item IDs
        """
        model.eval()
        
        # Get user embedding
        with torch.no_grad():
            user_emb = model.user_embedding(torch.LongTensor([user_id])).squeeze()
            
            # Predict ratings for all items
            item_ids = torch.arange(self.num_items)
            predictions = []
            
            for item_id in item_ids:
                pred = model(torch.LongTensor([user_id]), item_id.unsqueeze(0))
                predictions.append(pred.item())
        
        # Get top-K items
        top_k_indices = np.argsort(predictions)[-self.top_k:][::-1]
        top_k_items = top_k_indices.tolist()
        
        return top_k_items
    
    def evaluate(self,
                model: nn.Module,
                test_data: List[Tuple],
                ground_truth: Dict[int, List[int]]) -> Dict[str, float]:
        """
        Evaluate inversion attack.
        
        Args:
            model: Trained model
            test_data: Test data (user_id, item_id, rating)
            ground_truth: Ground truth top-K items per user
        
        Returns:
            Dictionary with attack metrics (top-K accuracy)
        """
        # Group test data by user
        user_data = {}
        for user_id, item_id, rating in test_data:
            if user_id not in user_data:
                user_data[user_id] = []
            user_data[user_id].append((item_id, rating))
        
        # Reconstruct for each user
        correct_predictions = 0
        total_users = 0
        
        for user_id in list(user_data.keys())[:min(50, len(user_data))]:  # Limit to 50 users
            if user_id not in ground_truth:
                continue
            
            user_items = [item for item, _ in user_data[user_id]]
            user_ratings = [rating for _, rating in user_data[user_id]]
            
            # Reconstruct top-K
            reconstructed = self.reconstruct_user_preferences(
                model, user_id, user_items, user_ratings
            )
            
            # Check accuracy
            true_top_k = ground_truth.get(user_id, [])
            if len(true_top_k) > 0:
                overlap = len(set(reconstructed) & set(true_top_k))
                if overlap >= self.top_k * 0.2:  # At least 20% overlap
                    correct_predictions += 1
                total_users += 1
        
        top_k_accuracy = correct_predictions / total_users if total_users > 0 else 0.0
        
        return {
            "top_k_accuracy": top_k_accuracy,
            "top_k": self.top_k,
            "num_users_evaluated": total_users
        }


def run_attack_evaluation(target_model: nn.Module,
                         train_data: List[Tuple],
                         test_data: List[Tuple],
                         shadow_models: List[nn.Module] = None) -> Dict:
    """
    Run both MIA and model inversion attacks.
    
    Args:
        target_model: Target model to attack
        train_data: Training data (members)
        test_data: Test data (non-members)
        shadow_models: Optional shadow models for MIA
    
    Returns:
        Dictionary with attack results
    """
    results = {}
    
    # Membership Inference Attack
    print("Running Membership Inference Attack...")
    mia = MembershipInferenceAttack(num_shadow_models=5)
    
    if shadow_models is not None and len(shadow_models) > 0:
        # Train attack classifier
        train_acc = mia.train_attack_classifier(shadow_models, train_data, test_data)
        print(f"  MIA training accuracy: {train_acc:.4f}")
        
        # Evaluate
        mia_results = mia.evaluate(target_model, train_data, test_data)
        results["mia"] = mia_results
        print(f"  MIA AUC: {mia_results['auc']:.4f}")
        print(f"  MIA Accuracy: {mia_results['accuracy']:.4f}")
    else:
        results["mia"] = {"auc": 0.0, "accuracy": 0.0, "note": "No shadow models provided"}
    
    # Model Inversion Attack
    print("Running Model Inversion Attack...")
    inversion = ModelInversionAttack(num_items=1000, top_k=10)  # Adjust num_items as needed
    
    # Create ground truth (top-K items per user from training data)
    user_items = {}
    for user_id, item_id, rating in train_data:
        if user_id not in user_items:
            user_items[user_id] = []
        user_items[user_id].append((item_id, rating))
    
    ground_truth = {}
    for user_id, items in user_items.items():
        # Sort by rating and get top-K
        sorted_items = sorted(items, key=lambda x: x[1], reverse=True)
        top_k = [item_id for item_id, _ in sorted_items[:10]]
        ground_truth[user_id] = top_k
    
    inversion_results = inversion.evaluate(target_model, test_data, ground_truth)
    results["inversion"] = inversion_results
    print(f"  Inversion Top-K Accuracy: {inversion_results['top_k_accuracy']:.4f}")
    
    return results

