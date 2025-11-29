"""
Metrics Collector for Federated Learning Experiments
Collects and saves all experimental metrics to JSON/CSV for thesis analysis.
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and stores experimental metrics"""
    
    def __init__(self, experiment_id: str, results_dir: str = "results"):
        """
        Initialize metrics collector.
        
        Args:
            experiment_id: Unique identifier for this experiment
            results_dir: Directory to save results
        """
        self.experiment_id = experiment_id
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Store all collected metrics
        self.experiment_data = {
            "experiment_id": experiment_id,
            "timestamp": datetime.now().isoformat(),
            "config": {},
            "rounds": [],
            "final_metrics": {},
            "client_metrics": [],
            "mobile_metrics": []
        }
        
        logger.info(f"Initialized metrics collector for experiment: {experiment_id}")
    
    def set_config(self, config: Dict[str, Any]):
        """
        Set experiment configuration.
        
        Args:
            config: Dictionary with experiment parameters
        """
        self.experiment_data["config"] = config
        logger.info(f"Set experiment config: {config}")
    
    def add_round_metrics(
        self,
        round_num: int,
        train_loss: float,
        test_metrics: Optional[Dict[str, float]] = None,
        aggregation_info: Optional[Dict[str, Any]] = None,
        client_metrics: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Add metrics for a training round.
        
        Args:
            round_num: Round number
            train_loss: Average training loss
            test_metrics: Test set evaluation metrics (NDCG, Hit Rate, etc.)
            aggregation_info: Aggregation statistics
            client_metrics: Per-client metrics
        """
        round_data = {
            "round": round_num,
            "train_loss": train_loss,
            "test_metrics": test_metrics or {},
            "aggregation": aggregation_info or {},
            "client_metrics": client_metrics or [],
            "timestamp": datetime.now().isoformat()
        }
        
        self.experiment_data["rounds"].append(round_data)
        logger.info(f"Added metrics for round {round_num}")
    
    def add_final_metrics(self, metrics: Dict[str, Any]):
        """
        Add final evaluation metrics.
        
        Args:
            metrics: Final metrics dictionary
        """
        self.experiment_data["final_metrics"] = metrics
        logger.info(f"Added final metrics: {metrics}")
    
    def add_client_metrics(self, client_id: str, metrics: Dict[str, Any]):
        """
        Add per-client metrics.
        
        Args:
            client_id: Client identifier
            metrics: Client-specific metrics
        """
        client_data = {
            "client_id": client_id,
            **metrics,
            "timestamp": datetime.now().isoformat()
        }
        self.experiment_data["client_metrics"].append(client_data)
    
    def add_mobile_metrics(self, device_id: str, metrics: Dict[str, Any]):
        """
        Add mobile device resource metrics.
        
        Args:
            device_id: Device identifier
            metrics: Resource metrics (battery, memory, CPU, etc.)
        """
        mobile_data = {
            "device_id": device_id,
            **metrics,
            "timestamp": datetime.now().isoformat()
        }
        self.experiment_data["mobile_metrics"].append(mobile_data)
    
    def save_json(self, filename: Optional[str] = None) -> str:
        """
        Save metrics to JSON file.
        
        Args:
            filename: Optional custom filename (default: experiment_id.json)
        
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"{self.experiment_id}.json"
        
        filepath = self.results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.experiment_data, f, indent=2)
        
        logger.info(f"Saved metrics to {filepath}")
        return str(filepath)
    
    def save_csv_summary(self, filename: Optional[str] = None) -> str:
        """
        Save summary to CSV file (useful for quick analysis).
        
        Args:
            filename: Optional custom filename
        
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"{self.experiment_id}_summary.csv"
        
        filepath = self.results_dir / filename
        
        # Create summary CSV with key metrics per round
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Round', 'Train_Loss', 'NDCG@10', 'Hit@10', 'Precision@10', 
                'Recall@10', 'MSE', 'MAE', 'Accuracy', 'Num_Clients', 'Total_Samples'
            ])
            
            # Round data
            for round_data in self.experiment_data["rounds"]:
                test_metrics = round_data.get("test_metrics", {})
                agg = round_data.get("aggregation", {})
                
                writer.writerow([
                    round_data["round"],
                    round_data.get("train_loss", ""),
                    test_metrics.get("NDCG@10", ""),
                    test_metrics.get("Hit@10", ""),
                    test_metrics.get("Precision@10", ""),
                    test_metrics.get("Recall@10", ""),
                    test_metrics.get("mse", ""),
                    test_metrics.get("mae", ""),
                    test_metrics.get("accuracy", ""),
                    agg.get("num_clients", ""),
                    agg.get("total_samples", "")
                ])
            
            # Final metrics row
            final = self.experiment_data.get("final_metrics", {})
            writer.writerow([
                "FINAL",
                "",
                final.get("NDCG@10", ""),
                final.get("Hit@10", ""),
                final.get("Precision@10", ""),
                final.get("Recall@10", ""),
                final.get("mse", ""),
                final.get("mae", ""),
                final.get("accuracy", ""),
                "",
                ""
            ])
        
        logger.info(f"Saved CSV summary to {filepath}")
        return str(filepath)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of collected metrics.
        
        Returns:
            Summary dictionary
        """
        rounds = self.experiment_data["rounds"]
        
        if not rounds:
            return {"message": "No rounds collected yet"}
        
        # Extract metrics across rounds
        train_losses = [r["train_loss"] for r in rounds if "train_loss" in r]
        ndcg_scores = [r["test_metrics"].get("NDCG@10", 0) for r in rounds if "test_metrics" in r]
        hit_scores = [r["test_metrics"].get("Hit@10", 0) for r in rounds if "test_metrics" in r]
        
        return {
            "experiment_id": self.experiment_id,
            "num_rounds": len(rounds),
            "final_train_loss": train_losses[-1] if train_losses else None,
            "final_ndcg@10": ndcg_scores[-1] if ndcg_scores else None,
            "final_hit@10": hit_scores[-1] if hit_scores else None,
            "best_ndcg@10": max(ndcg_scores) if ndcg_scores else None,
            "best_hit@10": max(hit_scores) if hit_scores else None,
            "config": self.experiment_data["config"]
        }


def create_experiment_id(
    dp_epsilon: Optional[float] = None,
    alpha: Optional[float] = None,
    embedding_dim: int = 16,
    num_clients: int = 3,
    seed: int = 42
) -> str:
    """
    Create standardized experiment ID.
    
    Args:
        dp_epsilon: DP budget (None for no DP)
        alpha: Heterogeneity parameter
        embedding_dim: Model embedding dimension
        num_clients: Number of clients
        seed: Random seed
    
    Returns:
        Experiment ID string
    """
    parts = []
    
    if dp_epsilon is None:
        parts.append("dp_inf")
    else:
        parts.append(f"dp_{dp_epsilon}")
    
    if alpha is not None:
        parts.append(f"alpha_{alpha}")
    
    parts.append(f"dim_{embedding_dim}")
    parts.append(f"clients_{num_clients}")
    parts.append(f"seed_{seed}")
    
    return "_".join(parts)

