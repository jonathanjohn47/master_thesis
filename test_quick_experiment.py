"""
Quick Test Experiment

Run a minimal test to verify the experiment pipeline works.
Only runs 1 seed for 1 configuration.
"""

import json
import time
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main experiment runner
import run_complete_experiment as exp

def main():
    print("=" * 70)
    print("QUICK TEST EXPERIMENT")
    print("Running 1 configuration with 1 seed to verify setup")
    print("=" * 70)

    # Temporarily modify the configuration for testing
    original_epsilons = exp.DP_EPSILONS
    original_alphas = exp.ALPHA_VALUES
    original_seeds = exp.SEEDS

    # Override with minimal config
    exp.DP_EPSILONS = [float('inf')]  # Just test without DP
    exp.ALPHA_VALUES = [0.5]           # Just test default alpha
    exp.SEEDS = [42]                    # Just test one seed
    exp.NUM_ROUNDS = 2                  # Reduce rounds for speed

    print("\nTest configuration:")
    print(f"  DP Epsilons: {exp.DP_EPSILONS}")
    print(f"  Alpha values: {exp.ALPHA_VALUES}")
    print(f"  Seeds: {exp.SEEDS}")
    print(f"  Rounds: {exp.NUM_ROUNDS}")
    print()

    try:
        # Run the main experiment
        exp.main()

        print("\n" + "=" * 70)
        print("✅ TEST PASSED!")
        print("=" * 70)
        print("\nThe experiment pipeline is working correctly.")
        print("You can now run the full experiment suite with:")
        print("  python run_complete_experiment.py")

    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ TEST FAILED!")
        print("=" * 70)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Restore original values
        exp.DP_EPSILONS = original_epsilons
        exp.ALPHA_VALUES = original_alphas
        exp.SEEDS = original_seeds

if __name__ == "__main__":
    main()

