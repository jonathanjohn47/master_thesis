"""
Master Experiment Runner

Orchestrates all experiments in the correct order:
1. Centralized baseline
2. DP sweep experiments
3. Heterogeneity sweep experiments
4. Comprehensive analysis

Usage:
    python run_all_experiments.py [--skip-baseline] [--skip-dp] [--skip-heterogeneity] [--skip-analysis]
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd: list, description: str):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n[OK] {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] {description} failed with exit code {e.returncode}")
        return False
    except KeyboardInterrupt:
        print(f"\n[INTERRUPTED] {description} was interrupted by user")
        return False


def check_server_running():
    """Check if server is running (for federated experiments)."""
    import requests
    try:
        response = requests.get("http://localhost:8000/healthz", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    parser = argparse.ArgumentParser(description="Run all thesis experiments")
    parser.add_argument("--skip-baseline", action="store_true", help="Skip centralized baseline")
    parser.add_argument("--skip-dp", action="store_true", help="Skip DP sweep experiments")
    parser.add_argument("--skip-heterogeneity", action="store_true", help="Skip heterogeneity sweep")
    parser.add_argument("--skip-analysis", action="store_true", help="Skip comprehensive analysis")
    parser.add_argument("--server-check", action="store_true", help="Check if server is running before federated experiments")
    
    args = parser.parse_args()
    
    print("="*60)
    print("Master Experiment Runner")
    print("="*60)
    print("\nThis script will run all experiments in sequence:")
    print("  1. Centralized baseline")
    print("  2. DP sweep experiments (requires server)")
    print("  3. Heterogeneity sweep experiments (requires server)")
    print("  4. Comprehensive analysis")
    print("\nNote: Steps 2-3 require the server to be running.")
    print("      Start the server in a separate terminal: python server.py")
    print("="*60)
    
    # Check prerequisites
    if not Path("ratings.csv").exists():
        print("\n[ERROR] ratings.csv not found!")
        print("Please ensure the MovieLens 100K dataset is in the current directory.")
        sys.exit(1)
    
    results = {
        'baseline': False,
        'dp_sweep': False,
        'heterogeneity': False,
        'analysis': False
    }
    
    # Step 1: Centralized baseline
    if not args.skip_baseline:
        if run_command(
            [sys.executable, "centralized_baseline.py"],
            "Centralized Baseline Experiment"
        ):
            results['baseline'] = True
            time.sleep(2)
    else:
        print("\n[Skipping] Centralized baseline")
    
    # Step 2: DP sweep (requires server)
    if not args.skip_dp:
        if args.server_check:
            if not check_server_running():
                print("\n[ERROR] Server is not running!")
                print("Please start the server first: python server.py")
                print("Then run this script again, or use --skip-dp to skip this step.")
                sys.exit(1)
        
        print("\n[INFO] Starting DP sweep experiments...")
        print("       This will take a while (15+ experiments × 3 seeds each)")
        
        if run_command(
            [sys.executable, "dp_sweep_experiment.py"],
            "DP Budget Sweep Experiments"
        ):
            results['dp_sweep'] = True
            time.sleep(2)
    else:
        print("\n[Skipping] DP sweep experiments")
    
    # Step 3: Heterogeneity sweep (requires server)
    if not args.skip_heterogeneity:
        if args.server_check:
            if not check_server_running():
                print("\n[ERROR] Server is not running!")
                print("Please start the server first: python server.py")
                print("Then run this script again, or use --skip-heterogeneity to skip this step.")
                sys.exit(1)
        
        print("\n[INFO] Starting heterogeneity sweep experiments...")
        print("       This will take a while (3 alpha values × 3 seeds each)")
        
        if run_command(
            [sys.executable, "heterogeneity_sweep_experiment.py"],
            "Heterogeneity Sweep Experiments"
        ):
            results['heterogeneity'] = True
            time.sleep(2)
    else:
        print("\n[Skipping] Heterogeneity sweep experiments")
    
    # Step 4: Comprehensive analysis
    if not args.skip_analysis:
        if run_command(
            [sys.executable, "comprehensive_analysis.py"],
            "Comprehensive Analysis"
        ):
            results['analysis'] = True
    else:
        print("\n[Skipping] Comprehensive analysis")
    
    # Summary
    print("\n" + "="*60)
    print("Experiment Summary")
    print("="*60)
    print(f"  Centralized Baseline: {'✓' if results['baseline'] else '✗'}")
    print(f"  DP Sweep: {'✓' if results['dp_sweep'] else '✗'}")
    print(f"  Heterogeneity Sweep: {'✓' if results['heterogeneity'] else '✗'}")
    print(f"  Analysis: {'✓' if results['analysis'] else '✗'}")
    print("="*60)
    
    if all(results.values()):
        print("\n🎉 All experiments completed successfully!")
        print("\nNext steps:")
        print("  1. Review generated figures in figures/")
        print("  2. Check summary table: figures/summary_table.csv")
        print("  3. Start writing your thesis results section")
    else:
        print("\n⚠️  Some experiments were skipped or failed.")
        print("   Review the output above for details.")


if __name__ == "__main__":
    main()

