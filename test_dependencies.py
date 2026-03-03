"""
Test Single Experiment

Run a single experiment to verify the setup works before running all experiments.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check imports
print("Checking dependencies...")
try:
    import torch
    print(f"✓ PyTorch {torch.__version__}")
except ImportError:
    print("✗ PyTorch not found - run: pip install torch")
    sys.exit(1)

try:
    import pandas
    print(f"✓ Pandas {pandas.__version__}")
except ImportError:
    print("✗ Pandas not found - run: pip install pandas")
    sys.exit(1)

try:
    import numpy
    print(f"✓ NumPy {numpy.__version__}")
except ImportError:
    print("✗ NumPy not found - run: pip install numpy")
    sys.exit(1)

try:
    from scripts.recommendation_metrics import evaluate_recommendations_simple
    print("✓ recommendation_metrics module")
except ImportError as e:
    print(f"✗ recommendation_metrics not found: {e}")
    sys.exit(1)

try:
    from scripts.rdp_accountant import compute_sigma_for_target_epsilon
    print("✓ rdp_accountant module")
except ImportError as e:
    print(f"✗ rdp_accountant not found: {e}")
    sys.exit(1)

try:
    from scripts.attack_evaluation import MembershipInferenceAttack
    print("✓ attack_evaluation module")
except ImportError as e:
    print(f"✗ attack_evaluation not found: {e}")
    sys.exit(1)

print("\n✅ All dependencies found!")
print("\nReady to run experiments. Use:")
print("  python run_complete_experiment.py")

