"""
Federated Learning Server for Mobile Movie Recommendation Systems
Using AIJack for federated learning orchestration with FastAPI endpoints.
"""

import base64
import io
import json
import logging
from typing import Dict, List, Optional
from collections import defaultdict
import numpy as np
import torch
import torch.nn as nn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Federated Learning Server for Movie Recommendations")


class ModelParams(BaseModel):
    """Model parameters in portable JSON format"""
    name: str
    shape: List[int]
    dtype: str
    data: str  # base64 encoded float32


class ClientParams(BaseModel):
    """Client upload parameters"""
    client_id: str
    params: List[ModelParams]
    sample_count: int


class RegisterRequest(BaseModel):
    """Client registration request"""
    client_id: str


class ServerState:
    """Server state management"""
    
    def __init__(self):
        self.clients = {}  # client_id -> metadata
        self.global_model = None
        self.uploaded_params = defaultdict(list)  # round -> [client_params]
        self.current_round = 0
        self.model_config = None
        
    def reset(self):
        """Reset server state"""
        self.clients.clear()
        self.global_model = None
        self.uploaded_params.clear()
        self.current_round = 0
        self.model_config = None


# Global server state
server_state = ServerState()


def create_matrix_factorization_model(num_users: int, num_items: int, embedding_dim: int = 16):
    """
    Create a Matrix Factorization model for movie recommendations.
    
    Args:
        num_users: Number of users in the dataset
        num_items: Number of items (movies) in the dataset
        embedding_dim: Dimension of user/item embeddings
    
    Returns:
        PyTorch model
    """
    class MatrixFactorization(nn.Module):
        def __init__(self, num_users, num_items, embedding_dim):
            super().__init__()
            self.user_embedding = nn.Embedding(num_users, embedding_dim)
            self.item_embedding = nn.Embedding(num_items, embedding_dim)
            
            # Initialize embeddings
            nn.init.normal_(self.user_embedding.weight, std=0.01)
            nn.init.normal_(self.item_embedding.weight, std=0.01)
            
        def forward(self, user_ids, item_ids):
            user_emb = self.user_embedding(user_ids)
            item_emb = self.item_embedding(item_ids)
            return (user_emb * item_emb).sum(dim=1)
            
        def predict(self, user_ids, item_ids):
            return self.forward(user_ids, item_ids)
    
    return MatrixFactorization(num_users, num_items, embedding_dim)


def model_to_json_params(model: nn.Module) -> List[ModelParams]:
    """
    Convert PyTorch model to portable JSON format with base64 encoding.
    
    Args:
        model: PyTorch model
    
    Returns:
        List of ModelParams with base64 encoded parameters
    """
    params = []
    state_dict = model.state_dict()
    
    for name, tensor in state_dict.items():
        # Convert to float32 numpy array
        np_array = tensor.detach().cpu().numpy().astype(np.float32)
        
        # Convert to base64
        data_bytes = np_array.tobytes()
        data_b64 = base64.b64encode(data_bytes).decode('utf-8')
        
        params.append(ModelParams(
            name=name,
            shape=list(np_array.shape),
            dtype="float32",
            data=data_b64
        ))
    
    return params


def json_params_to_model(params: List[ModelParams], model: nn.Module) -> nn.Module:
    """
    Load parameters from JSON format into PyTorch model.
    
    Args:
        params: List of ModelParams
        model: PyTorch model to load into
    
    Returns:
        Model with loaded parameters
    """
    state_dict = {}
    
    for param in params:
        # Decode base64
        data_bytes = base64.b64decode(param.data)
        
        # Convert to numpy array
        np_array = np.frombuffer(data_bytes, dtype=np.float32).reshape(param.shape)
        
        # Convert to tensor
        tensor = torch.from_numpy(np_array.copy())
        state_dict[param.name] = tensor
    
    model.load_state_dict(state_dict)
    return model


def aggregate_parameters(client_params_list: List[ClientParams], global_model: nn.Module) -> nn.Module:
    """
    Perform weighted Federated Averaging (FedAvg) aggregation.
    
    Args:
        client_params_list: List of client parameters with sample counts
        global_model: Current global model
    
    Returns:
        Aggregated global model
    """
    if not client_params_list:
        return global_model
    
    # Calculate total samples
    total_samples = sum(cp.sample_count for cp in client_params_list)
    
    if total_samples == 0:
        return global_model
    
    # Initialize aggregated state dict
    aggregated_state = {}
    state_dict = global_model.state_dict()
    
    for key in state_dict.keys():
        aggregated_state[key] = torch.zeros_like(state_dict[key])
    
    # Weighted average
    for client_params in client_params_list:
        weight = client_params.sample_count / total_samples
        
        # Load client parameters into temporary model
        temp_model = type(global_model)(
            server_state.model_config['num_users'],
            server_state.model_config['num_items'],
            server_state.model_config['embedding_dim']
        )
        temp_model = json_params_to_model(client_params.params, temp_model)
        
        # Add weighted parameters
        client_state = temp_model.state_dict()
        for key in aggregated_state.keys():
            aggregated_state[key] += weight * client_state[key]
    
    # Load aggregated parameters into global model
    global_model.load_state_dict(aggregated_state)
    
    return global_model


@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "round": server_state.current_round}


@app.post("/init-model")
async def init_model(num_users: int, num_items: int, embedding_dim: int = 16):
    """
    Initialize the global model.
    
    Args:
        num_users: Number of users
        num_items: Number of items (movies)
        embedding_dim: Embedding dimension
    """
    logger.info(f"Initializing model: {num_users} users, {num_items} items, dim={embedding_dim}")
    
    model = create_matrix_factorization_model(num_users, num_items, embedding_dim)
    server_state.global_model = model
    server_state.model_config = {
        'num_users': num_users,
        'num_items': num_items,
        'embedding_dim': embedding_dim
    }
    
    return {
        "status": "initialized",
        "num_users": num_users,
        "num_items": num_items,
        "embedding_dim": embedding_dim
    }


@app.post("/register")
async def register_client(request: RegisterRequest):
    """
    Register a new client.
    
    Args:
        request: Registration request with client_id
    """
    client_id = request.client_id
    
    if client_id in server_state.clients:
        logger.warning(f"Client {client_id} already registered")
    else:
        server_state.clients[client_id] = {
            "registered_at": server_state.current_round,
            "last_seen": server_state.current_round
        }
        logger.info(f"Client {client_id} registered")
    
    return {
        "status": "registered",
        "client_id": client_id,
        "current_round": server_state.current_round
    }


@app.get("/global-params")
async def get_global_params():
    """
    Get global model parameters as torch blob (binary).
    Note: For mobile compatibility, prefer /global-params-json
    """
    if server_state.global_model is None:
        raise HTTPException(status_code=404, detail="Model not initialized")
    
    # Save as bytes (simplified - in production use torch.save())
    buffer = io.BytesIO()
    torch.save(server_state.global_model.state_dict(), buffer)
    buffer.seek(0)
    
    return JSONResponse(
        content={"message": "Use /global-params-json for portable format"},
        status_code=200
    )


@app.get("/global-params-json")
async def get_global_params_json():
    """
    Get global model parameters in portable JSON format.
    Returns base64-encoded float32 parameters.
    """
    if server_state.global_model is None:
        raise HTTPException(status_code=404, detail="Model not initialized")
    
    params = model_to_json_params(server_state.global_model)
    
    return {
        "round": server_state.current_round,
        "model_config": server_state.model_config,
        "params": [p.dict() for p in params]
    }


@app.post("/upload-params")
async def upload_params():
    """
    Upload parameters (torch blob format).
    Note: For mobile compatibility, prefer /upload-params-json
    """
    return JSONResponse(
        content={"message": "Use /upload-params-json for portable format"},
        status_code=200
    )


@app.post("/upload-params-json")
async def upload_params_json(client_params: ClientParams):
    """
    Upload client model parameters in portable JSON format.
    
    Args:
        client_params: Client parameters with sample count
    """
    logger.info(f"Received params from client {client_params.client_id} "
                f"(samples: {client_params.sample_count}, round: {server_state.current_round})")
    
    # Store uploaded parameters for current round
    server_state.uploaded_params[server_state.current_round].append(client_params)
    
    # Update client metadata
    if client_params.client_id in server_state.clients:
        server_state.clients[client_params.client_id]["last_seen"] = server_state.current_round
    
    return {
        "status": "uploaded",
        "client_id": client_params.client_id,
        "round": server_state.current_round
    }


@app.post("/aggregate")
async def aggregate():
    """
    Aggregate uploaded client parameters using weighted FedAvg.
    """
    if server_state.global_model is None:
        raise HTTPException(status_code=404, detail="Model not initialized")
    
    round_params = server_state.uploaded_params[server_state.current_round]
    
    if not round_params:
        raise HTTPException(status_code=400, detail="No parameters uploaded for current round")
    
    logger.info(f"Aggregating {len(round_params)} client updates for round {server_state.current_round}")
    
    # Perform aggregation
    server_state.global_model = aggregate_parameters(round_params, server_state.global_model)
    
    # Advance round
    server_state.current_round += 1
    
    return {
        "status": "aggregated",
        "round": server_state.current_round - 1,
        "num_clients": len(round_params),
        "total_samples": sum(cp.sample_count for cp in round_params)
    }


@app.post("/reset")
async def reset():
    """Reset server state"""
    server_state.reset()
    logger.info("Server state reset")
    return {"status": "reset"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

