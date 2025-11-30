"""
RDP (Renyi Differential Privacy) Accountant for DP-SGD.

This module provides privacy accounting for federated learning with DP-SGD.
It computes the privacy budget (epsilon) consumed given the noise multiplier,
clipping norm, number of rounds, and other parameters.
"""

import numpy as np
from typing import Tuple, Optional
import math


class RDPAccountant:
    """
    RDP Accountant for tracking privacy budget in federated learning.
    
    Implements the RDP composition theorem to compute (ε, δ)-DP guarantees.
    """
    
    def __init__(self, delta: float = 1e-5):
        """
        Initialize RDP accountant.
        
        Args:
            delta: Delta parameter for (ε, δ)-DP (default: 1e-5)
        """
        self.delta = delta
        self.orders = np.array([1 + x / 10.0 for x in range(1, 100)] + list(range(12, 65)))
    
    def compute_rdp(self, sigma: float, alpha: float) -> float:
        """
        Compute RDP for Gaussian mechanism.
        
        Args:
            sigma: Noise multiplier
            alpha: Renyi order (alpha)
        
        Returns:
            RDP value
        """
        if sigma == 0:
            return float('inf')
        
        # RDP for Gaussian mechanism: alpha / (2 * sigma^2)
        return alpha / (2 * sigma ** 2)
    
    def compute_epsilon(self, 
                       sigma: float, 
                       num_rounds: int,
                       samples_per_round: int,
                       batch_size: int,
                       clip_norm: float = 1.0) -> Tuple[float, float]:
        """
        Compute epsilon (privacy budget) for federated learning with DP-SGD.
        
        Args:
            sigma: Noise multiplier
            num_rounds: Number of federated learning rounds
            samples_per_round: Average number of samples per client per round
            batch_size: Batch size for local training
            clip_norm: Gradient clipping norm
        
        Returns:
            Tuple of (epsilon, best_alpha) - epsilon value and the Renyi order that minimizes it
        """
        if sigma == 0 or sigma == float('inf'):
            return (float('inf'), 0.0)
        
        # Number of steps per round (approximate)
        steps_per_round = max(1, samples_per_round // batch_size)
        total_steps = num_rounds * steps_per_round
        
        # Compute RDP for each order
        epsilons = []
        for alpha in self.orders:
            # RDP per step
            rdp_per_step = self.compute_rdp(sigma, alpha)
            
            # Compose over total steps
            total_rdp = total_steps * rdp_per_step
            
            # Convert RDP to (ε, δ)-DP
            epsilon = total_rdp + np.log(1 / self.delta) / (alpha - 1)
            epsilons.append(epsilon)
        
        # Find minimum epsilon (best privacy guarantee)
        min_epsilon = min(epsilons)
        best_alpha_idx = np.argmin(epsilons)
        best_alpha = self.orders[best_alpha_idx]
        
        return (min_epsilon, best_alpha)
    
    def compute_sigma_for_epsilon(self,
                                  target_epsilon: float,
                                  num_rounds: int,
                                  samples_per_round: int,
                                  batch_size: int,
                                  clip_norm: float = 1.0,
                                  sigma_min: float = 0.1,
                                  sigma_max: float = 10.0,
                                  tolerance: float = 0.1) -> Optional[float]:
        """
        Find noise multiplier (sigma) that achieves target epsilon.
        
        Uses binary search to find the sigma value that gives the desired epsilon.
        
        Args:
            target_epsilon: Target privacy budget
            num_rounds: Number of federated learning rounds
            samples_per_round: Average number of samples per client per round
            batch_size: Batch size for local training
            clip_norm: Gradient clipping norm
            sigma_min: Minimum sigma to search
            sigma_max: Maximum sigma to search
            tolerance: Tolerance for epsilon match
        
        Returns:
            Sigma value that achieves target epsilon, or None if not found
        """
        if target_epsilon == float('inf'):
            return 0.0
        
        # Binary search for sigma
        low, high = sigma_min, sigma_max
        
        for _ in range(50):  # Max 50 iterations
            mid = (low + high) / 2
            epsilon, _ = self.compute_epsilon(mid, num_rounds, samples_per_round, batch_size, clip_norm)
            
            if abs(epsilon - target_epsilon) < tolerance:
                return mid
            
            if epsilon > target_epsilon:
                # Need more noise (higher sigma)
                low = mid
            else:
                # Can use less noise (lower sigma)
                high = mid
        
        # Return the best approximation
        final_sigma = (low + high) / 2
        final_epsilon, _ = self.compute_epsilon(final_sigma, num_rounds, samples_per_round, batch_size, clip_norm)
        
        if abs(final_epsilon - target_epsilon) < tolerance * 2:
            return final_sigma
        
        return None


def compute_sigma_for_target_epsilon(target_epsilon: float,
                                    num_rounds: int = 10,
                                    samples_per_client: int = 100,
                                    batch_size: int = 32,
                                    clip_norm: float = 1.0,
                                    delta: float = 1e-5) -> Optional[float]:
    """
    Convenience function to compute sigma for target epsilon.
    
    Args:
        target_epsilon: Target privacy budget
        num_rounds: Number of federated learning rounds
        samples_per_client: Average samples per client
        batch_size: Batch size
        clip_norm: Gradient clipping norm
        delta: Delta for (ε, δ)-DP
    
    Returns:
        Recommended sigma value
    """
    accountant = RDPAccountant(delta=delta)
    return accountant.compute_sigma_for_epsilon(
        target_epsilon=target_epsilon,
        num_rounds=num_rounds,
        samples_per_round=samples_per_client,
        batch_size=batch_size,
        clip_norm=clip_norm
    )


def compute_epsilon_for_sigma(sigma: float,
                              num_rounds: int = 10,
                              samples_per_client: int = 100,
                              batch_size: int = 32,
                              clip_norm: float = 1.0,
                              delta: float = 1e-5) -> Tuple[float, float]:
    """
    Convenience function to compute epsilon for given sigma.
    
    Args:
        sigma: Noise multiplier
        num_rounds: Number of federated learning rounds
        samples_per_client: Average samples per client
        batch_size: Batch size
        clip_norm: Gradient clipping norm
        delta: Delta for (ε, δ)-DP
    
    Returns:
        Tuple of (epsilon, best_alpha)
    """
    accountant = RDPAccountant(delta=delta)
    return accountant.compute_epsilon(
        sigma=sigma,
        num_rounds=num_rounds,
        samples_per_round=samples_per_client,
        batch_size=batch_size,
        clip_norm=clip_norm
    )

