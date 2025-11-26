"""
Federated Learning Client for Mobile Movie Recommendation Systems
Using AIJack for federated learning with DP-SGD support.
"""

import base64
import json
import logging
from typing import List, Optional, Dict
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import requests
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ClientConfig:
    """Client configuration"""
    client_id: str
    server_url: str
    num_users: int
    num_items: int
    embedding_dim: int = 16
    local_epochs: int = 1
    learning_rate: float = 0.01
    batch_size: int = 32
    
    # Differential Privacy parameters
    use_dp: bool = False
    dp_sigma: float = 1.0  # Noise multiplier
    dp_clip_norm: float = 1.0  # Gradient clipping norm
    dp_delta: float = 1e-5  # Delta for (ε, δ)-DP


class MovieLensDataset(Dataset):
    """MovieLens dataset for recommendation"""
    
    def __init__(self, interactions: List[tuple]):
        """
        Args:
            interactions: List of (user_id, item_id, rating) tuples
        """
        self.interactions = interactions
        
    def __len__(self):
        return len(self.interactions)
    
    def __getitem__(self, idx):
        user_id, item_id, rating = self.interactions[idx]
        return torch.LongTensor([user_id]), torch.LongTensor([item_id]), torch.FloatTensor([rating])


def create_matrix_factorization_model(num_users: int, num_items: int, embedding_dim: int = 16):
    """
    Create a Matrix Factorization model (same as server).
    
    Args:
        num_users: Number of users
        num_items: Number of items
        embedding_dim: Embedding dimension
    
    Returns:
        PyTorch model
    """
    class MatrixFactorization(nn.Module):
        def __init__(self, num_users, num_items, embedding_dim):
            super().__init__()
            self.user_embedding = nn.Embedding(num_users, embedding_dim)
            self.item_embedding = nn.Embedding(num_items, embedding_dim)
            
            nn.init.normal_(self.user_embedding.weight, std=0.01)
            nn.init.normal_(self.item_embedding.weight, std=0.01)
            
        def forward(self, user_ids, item_ids):
            user_emb = self.user_embedding(user_ids)
            item_emb = self.item_embedding(item_ids)
            return (user_emb * item_emb).sum(dim=1)
            
        def predict(self, user_ids, item_ids):
            return self.forward(user_ids, item_ids)
    
    return MatrixFactorization(num_users, num_items, embedding_dim)


class ModelParamsEncoder:
    """Encode/decode model parameters to/from JSON format"""
    
    @staticmethod
    def model_to_json_params(model: nn.Module) -> List[Dict]:
        """Convert PyTorch model to portable JSON format"""
        params = []
        state_dict = model.state_dict()
        
        for name, tensor in state_dict.items():
            np_array = tensor.detach().cpu().numpy().astype(np.float32)
            data_bytes = np_array.tobytes()
            data_b64 = base64.b64encode(data_bytes).decode('utf-8')
            
            params.append({
                "name": name,
                "shape": list(np_array.shape),
                "dtype": "float32",
                "data": data_b64
            })
        
        return params
    
    @staticmethod
    def json_params_to_model(params: List[Dict], model: nn.Module) -> nn.Module:
        """Load parameters from JSON format into model"""
        state_dict = {}
        
        for param in params:
            data_bytes = base64.b64decode(param["data"])
            np_array = np.frombuffer(data_bytes, dtype=np.float32).reshape(param["shape"])
            tensor = torch.from_numpy(np_array.copy())
            state_dict[param["name"]] = tensor
        
        model.load_state_dict(state_dict)
        return model


class DPNoise:
    """Differential Privacy noise addition utilities for DP-SGD"""
    
    @staticmethod
    def clip_gradients(model: nn.Module, clip_norm: float):
        """
        Clip gradients of model parameters in-place.
        
        Args:
            model: PyTorch model
            clip_norm: Maximum gradient norm
        """
        # Collect all gradients
        gradients = []
        for param in model.parameters():
            if param.grad is not None:
                gradients.append(param.grad.data.flatten())
        
        if not gradients:
            return
        
        # Compute total norm
        total_norm = torch.norm(torch.cat(gradients))
        
        # Clip if necessary
        if total_norm > clip_norm:
            clip_coef = clip_norm / (total_norm + 1e-6)
            for param in model.parameters():
                if param.grad is not None:
                    param.grad.data.mul_(clip_coef)
    
    @staticmethod
    def add_gaussian_noise(model: nn.Module, sigma: float, clip_norm: float):
        """
        Add Gaussian noise to gradients for DP-SGD (after clipping).
        
        Args:
            model: PyTorch model
            sigma: Noise multiplier
            clip_norm: Gradient clipping norm (for noise scaling)
        """
        for param in model.parameters():
            if param.grad is not None:
                noise = torch.normal(
                    0.0,
                    sigma * clip_norm,
                    size=param.grad.shape,
                    device=param.grad.device,
                    dtype=param.grad.dtype
                )
                param.grad.data.add_(noise)


class FederatedClient:
    """Federated Learning Client with DP-SGD support"""
    
    def __init__(self, config: ClientConfig, local_data: List[tuple]):
        """
        Initialize federated client.
        
        Args:
            config: Client configuration
            local_data: Local training data as (user_id, item_id, rating) tuples
        """
        self.config = config
        self.local_data = local_data
        self.model = create_matrix_factorization_model(
            config.num_users, config.num_items, config.embedding_dim
        )
        
        # Create dataset and dataloader
        self.dataset = MovieLensDataset(local_data)
        self.dataloader = DataLoader(
            self.dataset,
            batch_size=config.batch_size,
            shuffle=True
        )
        
        self.encoder = ModelParamsEncoder()
        self.dp_noise = DPNoise()
        
    def register(self):
        """Register with the server"""
        url = f"{self.config.server_url}/register"
        response = requests.post(url, json={"client_id": self.config.client_id})
        response.raise_for_status()
        logger.info(f"Client {self.config.client_id} registered")
        return response.json()
    
    def fetch_global_params(self):
        """Fetch global model parameters from server"""
        url = f"{self.config.server_url}/global-params-json"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        params = data["params"]
        
        # Load into local model
        self.model = self.encoder.json_params_to_model(params, self.model)
        
        logger.info(f"Fetched global params for round {data.get('round', 0)}")
        return data
    
    def train_local(self) -> Dict:
        """
        Train model locally using local data.
        Supports DP-SGD if enabled in config.
        
        Returns:
            Training metrics
        """
        self.model.train()
        optimizer = optim.SGD(self.model.parameters(), lr=self.config.learning_rate)
        criterion = nn.MSELoss()
        
        total_loss = 0.0
        num_batches = 0
        
        for epoch in range(self.config.local_epochs):
            epoch_loss = 0.0
            
            for batch_idx, (user_ids, item_ids, ratings) in enumerate(self.dataloader):
                user_ids = user_ids.squeeze()
                item_ids = item_ids.squeeze()
                ratings = ratings.squeeze()
                
                # Forward pass
                predictions = self.model(user_ids, item_ids)
                loss = criterion(predictions, ratings)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                
                # Apply DP-SGD if enabled
                if self.config.use_dp:
                    # Clip gradients first
                    self.dp_noise.clip_gradients(self.model, self.config.dp_clip_norm)
                    # Then add Gaussian noise
                    self.dp_noise.add_gaussian_noise(
                        self.model,
                        self.config.dp_sigma,
                        self.config.dp_clip_norm
                    )
                
                optimizer.step()
                
                epoch_loss += loss.item()
                num_batches += 1
            
            total_loss += epoch_loss
            logger.info(f"Epoch {epoch+1}/{self.config.local_epochs}, Loss: {epoch_loss/len(self.dataloader):.4f}")
        
        avg_loss = total_loss / (num_batches + 1e-6)
        return {
            "loss": avg_loss,
            "samples": len(self.local_data),
            "epochs": self.config.local_epochs
        }
    
    def upload_params(self):
        """Upload local model parameters to server"""
        params = self.encoder.model_to_json_params(self.model)
        
        payload = {
            "client_id": self.config.client_id,
            "params": params,
            "sample_count": len(self.local_data)
        }
        
        url = f"{self.config.server_url}/upload-params-json"
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        logger.info(f"Uploaded params to server (samples: {len(self.local_data)})")
        return response.json()
    
    def run_training_round(self) -> Dict:
        """
        Execute one complete training round:
        1. Fetch global parameters
        2. Train locally
        3. Upload parameters
        
        Returns:
            Round metrics
        """
        # Fetch global model
        global_info = self.fetch_global_params()
        
        # Train locally
        train_metrics = self.train_local()
        
        # Upload parameters
        upload_info = self.upload_params()
        
        return {
            "round": global_info.get("round", 0),
            **train_metrics,
            **upload_info
        }


def create_non_iid_split(interactions: List[tuple], num_clients: int, alpha: float = 0.5):
    """
    Create non-IID data split using Dirichlet distribution.
    
    Args:
        interactions: List of (user_id, item_id, rating) tuples
        num_clients: Number of clients
        alpha: Dirichlet concentration parameter (lower = more heterogeneous)
    
    Returns:
        List of client data splits
    """
    # Group interactions by user
    user_interactions = {}
    for user_id, item_id, rating in interactions:
        if user_id not in user_interactions:
            user_interactions[user_id] = []
        user_interactions[user_id].append((user_id, item_id, rating))
    
    user_ids = list(user_interactions.keys())
    num_users = len(user_ids)
    
    # Sample Dirichlet distribution for each user
    np.random.seed(42)  # For reproducibility
    proportions = np.random.dirichlet([alpha] * num_clients, size=num_users)
    
    # Assign interactions to clients
    client_splits = [[] for _ in range(num_clients)]
    
    for user_idx, user_id in enumerate(user_ids):
        user_data = user_interactions[user_id]
        # Sample client assignment for each interaction
        for interaction in user_data:
            client_idx = np.random.choice(num_clients, p=proportions[user_idx])
            client_splits[client_idx].append(interaction)
    
    return client_splits


# Example usage
if __name__ == "__main__":
    # Example configuration
    # In practice, load MovieLens 100K data here
    # interactions = load_movielens_data("path/to/ml-100k/u.data")
    
    # For demonstration, create synthetic data
    num_users = 943
    num_items = 1682
    
    # Create synthetic interactions (replace with real data loading)
    interactions = []
    for _ in range(1000):
        user_id = np.random.randint(0, num_users)
        item_id = np.random.randint(0, num_items)
        rating = np.random.choice([1, 2, 3, 4, 5])
        interactions.append((user_id, item_id, float(rating)))
    
    # Create client configuration
    config = ClientConfig(
        client_id="client_1",
        server_url="http://localhost:8000",
        num_users=num_users,
        num_items=num_items,
        embedding_dim=16,
        local_epochs=1,
        learning_rate=0.01,
        batch_size=32,
        use_dp=True,  # Enable DP-SGD
        dp_sigma=1.0,
        dp_clip_norm=1.0,
        dp_delta=1e-5
    )
    
    # Create client with local data
    client = FederatedClient(config, interactions)
    
    # Register with server
    try:
        client.register()
        
        # Run training round
        metrics = client.run_training_round()
        logger.info(f"Training round completed: {metrics}")
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to server. Make sure server is running on http://localhost:8000")

