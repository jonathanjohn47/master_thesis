"""
Comprehensive Results Verification Report

This script generates a detailed comparison report between
existing results and published results in EXPERIMENT_STATUS.md
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List
from datetime import datetime


def load_experiment_results(results_dir: str = "results") -> Dict:
    """Load all experiment results from JSON files."""
    results = {}
    results_path = Path(results_dir)

    for json_file in results_path.glob("*.json"):
        if json_file.name == "attack_evaluation_summary.json":
            continue

        with open(json_file) as f:
            data = json.load(f)
            results[json_file.stem] = data

    return results


def extract_all_metrics(results: Dict) -> Dict:
    """Extract comprehensive metrics from experiment results."""
    metrics = {}

    # Group by configuration
    configurations = {}

    for exp_id, data in results.items():
        if exp_id == "centralized_baseline":
            metrics["centralized"] = {
                "NDCG@10": data.get("final_metrics", {}).get("NDCG@10", 0),
                "Hit@10": data.get("final_metrics", {}).get("Hit@10", 0),
                "MSE": data.get("final_metrics", {}).get("MSE", 0),
                "MAE": data.get("final_metrics", {}).get("MAE", 0),
            }
            continue

        # Parse experiment ID
        parts = exp_id.split("_seed_")
        if len(parts) == 2:
            config_key = parts[0]
            seed = int(parts[1])
        else:
            continue

        if config_key not in configurations:
            configurations[config_key] = []

        configurations[config_key].append({
            "seed": seed,
            "NDCG@10": data.get("final_metrics", {}).get("NDCG@10", 0),
            "Hit@10": data.get("final_metrics", {}).get("Hit@10", 0),
            "MSE": data.get("final_metrics", {}).get("MSE", 0),
            "MAE": data.get("final_metrics", {}).get("MAE", 0),
            "final_loss": data.get("final_metrics", {}).get("training_loss", 0),
        })

    # Compute statistics across seeds
    for config_key, runs in configurations.items():
        ndcg_values = [r["NDCG@10"] for r in runs]
        hit_values = [r["Hit@10"] for r in runs]
        mse_values = [r["MSE"] for r in runs]
        mae_values = [r["MAE"] for r in runs]

        metrics[config_key] = {
            "NDCG@10": {
                "mean": np.mean(ndcg_values),
                "std": np.std(ndcg_values),
                "min": np.min(ndcg_values),
                "max": np.max(ndcg_values),
                "values": ndcg_values
            },
            "Hit@10": {
                "mean": np.mean(hit_values),
                "std": np.std(hit_values),
                "min": np.min(hit_values),
                "max": np.max(hit_values),
                "values": hit_values
            },
            "MSE": {
                "mean": np.mean(mse_values),
                "std": np.std(mse_values),
            },
            "MAE": {
                "mean": np.mean(mae_values),
                "std": np.std(mae_values),
            },
            "num_runs": len(runs),
            "seeds": [r["seed"] for r in runs]
        }

    return metrics


def generate_report():
    """Generate comprehensive verification report."""
    print("=" * 80)
    print("EXPERIMENT RESULTS VERIFICATION REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Published results from EXPERIMENT_STATUS.md
    published = {
        "centralized": {
            "NDCG@10": 0.2250,
            "Hit@10": 0.3800
        },
        "dp_inf_alpha_0.5_dim_64_clients_100": {
            "NDCG@10": {"mean": 0.0539, "std": 0.0108},
            "Hit@10": {"mean": 0.0633, "std": 0.0205}
        },
        "dp_8_alpha_0.5_dim_64_clients_100": {
            "NDCG@10": {"mean": 0.0534, "std": 0.0131},
            "Hit@10": {"mean": 0.0600, "std": 0.0082}
        },
        "dp_4_alpha_0.5_dim_64_clients_100": {
            "NDCG@10": {"mean": 0.0479, "std": 0.0091},
            "Hit@10": {"mean": 0.0600, "std": 0.0082}
        },
        "dp_2_alpha_0.5_dim_64_clients_100": {
            "NDCG@10": {"mean": 0.0456, "std": 0.0095},
            "Hit@10": {"mean": 0.0567, "std": 0.0094}
        },
        "dp_1_alpha_0.5_dim_64_clients_100": {
            "NDCG@10": {"mean": 0.0467, "std": 0.0121},
            "Hit@10": {"mean": 0.0533, "std": 0.0047}
        },
        "dp_inf_alpha_0.1_dim_64_clients_100": {
            "NDCG@10": {"mean": 0.0538, "std": 0.0108},
            "Hit@10": {"mean": 0.0633, "std": 0.0205}
        },
        "dp_inf_alpha_1.0_dim_64_clients_100": {
            "NDCG@10": {"mean": 0.0539, "std": 0.0108},
            "Hit@10": {"mean": 0.0633, "std": 0.0205}
        }
    }

    # Load current results
    print("\nLoading experiment results from results/...")
    current_results_raw = load_experiment_results("results")
    current_results = extract_all_metrics(current_results_raw)
    print(f"Loaded {len(current_results)} configurations")

    # Section 1: DP Sweep Results (RQ1)
    print("\n" + "=" * 80)
    print("SECTION 1: DP SWEEP RESULTS (RQ1: Accuracy-Privacy Trade-offs)")
    print("=" * 80)
    print("\nConfiguration: 100 clients, 10 rounds, 3 local epochs, α=0.5")
    print("\n{:<20} {:<25} {:<25} {:<10}".format(
        "DP Budget (ε)", "NDCG@10", "Hit@10", "Status"))
    print("-" * 80)

    dp_configs = [
        ("inf", "dp_inf_alpha_0.5_dim_64_clients_100"),
        ("8", "dp_8_alpha_0.5_dim_64_clients_100"),
        ("4", "dp_4_alpha_0.5_dim_64_clients_100"),
        ("2", "dp_2_alpha_0.5_dim_64_clients_100"),
        ("1", "dp_1_alpha_0.5_dim_64_clients_100"),
    ]

    all_match = True
    for epsilon, config_key in dp_configs:
        if config_key in current_results and config_key in published:
            curr = current_results[config_key]
            pub = published[config_key]

            curr_ndcg = curr["NDCG@10"]["mean"]
            pub_ndcg = pub["NDCG@10"]["mean"]
            curr_hit = curr["Hit@10"]["mean"]
            pub_hit = pub["Hit@10"]["mean"]

            ndcg_match = abs(curr_ndcg - pub_ndcg) < 0.0001
            hit_match = abs(curr_hit - pub_hit) < 0.0001

            status = "✅" if (ndcg_match and hit_match) else "⚠️"
            if not (ndcg_match and hit_match):
                all_match = False

            print("{:<20} {:.4f} ± {:.4f}        {:.4f} ± {:.4f}        {}".format(
                epsilon, curr_ndcg, curr["NDCG@10"]["std"],
                curr_hit, curr["Hit@10"]["std"], status))

    # Section 2: Heterogeneity Sweep Results (RQ3)
    print("\n" + "=" * 80)
    print("SECTION 2: HETEROGENEITY SWEEP RESULTS (RQ3: Data Distribution Impact)")
    print("=" * 80)
    print("\nConfiguration: 100 clients, 10 rounds, no DP")
    print("\n{:<20} {:<25} {:<25} {:<10}".format(
        "Alpha (heterogeneity)", "NDCG@10", "Hit@10", "Status"))
    print("-" * 80)

    hetero_configs = [
        ("0.1", "dp_inf_alpha_0.1_dim_64_clients_100"),
        ("0.5", "dp_inf_alpha_0.5_dim_64_clients_100"),
        ("1.0", "dp_inf_alpha_1.0_dim_64_clients_100"),
    ]

    for alpha, config_key in hetero_configs:
        if config_key in current_results and config_key in published:
            curr = current_results[config_key]
            pub = published[config_key]

            curr_ndcg = curr["NDCG@10"]["mean"]
            pub_ndcg = pub["NDCG@10"]["mean"]
            curr_hit = curr["Hit@10"]["mean"]
            pub_hit = pub["Hit@10"]["mean"]

            ndcg_match = abs(curr_ndcg - pub_ndcg) < 0.0001
            hit_match = abs(curr_hit - pub_hit) < 0.0001

            status = "✅" if (ndcg_match and hit_match) else "⚠️"
            if not (ndcg_match and hit_match):
                all_match = False

            print("{:<20} {:.4f} ± {:.4f}        {:.4f} ± {:.4f}        {}".format(
                alpha, curr_ndcg, curr["NDCG@10"]["std"],
                curr_hit, curr["Hit@10"]["std"], status))

    # Section 3: Centralized Baseline
    print("\n" + "=" * 80)
    print("SECTION 3: CENTRALIZED BASELINE")
    print("=" * 80)

    if "centralized" in current_results:
        curr = current_results["centralized"]
        pub = published["centralized"]

        print(f"\nNDCG@10: {curr['NDCG@10']:.4f} (Published: {pub['NDCG@10']:.4f})")
        print(f"Hit@10:  {curr['Hit@10']:.4f} (Published: {pub['Hit@10']:.4f})")

        ndcg_match = abs(curr['NDCG@10'] - pub['NDCG@10']) < 0.0001
        hit_match = abs(curr['Hit@10'] - pub['Hit@10']) < 0.0001

        if ndcg_match and hit_match:
            print("\nStatus: ✅ Matches published baseline")
        else:
            print("\nStatus: ⚠️ Differs from published baseline")
            all_match = False

    # Section 4: Attack Evaluation
    print("\n" + "=" * 80)
    print("SECTION 4: PRIVACY ATTACK EVALUATION (RQ2)")
    print("=" * 80)

    attack_file = Path("results/attack_evaluation_summary.json")
    if attack_file.exists():
        with open(attack_file) as f:
            attacks = json.load(f)

        print("\n{:<15} {:<12} {:<15} {:<20}".format(
            "DP Budget (ε)", "MIA AUC", "MIA Accuracy", "Inversion Top-K"))
        print("-" * 80)

        for eps in ["inf", "8", "4", "2", "1"]:
            if eps in attacks:
                mia = attacks[eps].get("mia", {})
                inv = attacks[eps].get("inversion", {})
                print("{:<15} {:.4f}       {:.4f}          {:.4f}".format(
                    eps, mia.get("auc", 0), mia.get("accuracy", 0),
                    inv.get("top_k_accuracy", 0)))
    else:
        print("\n⚠️  Attack evaluation results not found")

    # Final Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    print(f"\nTotal configurations verified: {len(published)}")
    print(f"Configurations found: {len(current_results)}")

    if all_match:
        print("\n✅ ALL RESULTS MATCH PUBLISHED VALUES!")
        print("\nConclusion: The experiments are reproducible and the results")
        print("in the results/ directory match exactly with those published")
        print("in EXPERIMENT_STATUS.md")
    else:
        print("\n⚠️  Some results differ from published values")
        print("\nThis could be due to:")
        print("  - Results from a different run")
        print("  - Updated experiment configuration")
        print("  - Random seed variation")

    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)

    if all_match:
        print("\nThe existing results are valid and match published values.")
        print("No need to re-run experiments unless:")
        print("  1. You want to verify reproducibility with different seeds")
        print("  2. You want to test with different configurations")
        print("  3. You want to update the published results")
        print("\nTo re-run all experiments:")
        print("  python run_complete_experiment.py")
        print("\nEstimated time: ~60 minutes")
    else:
        print("\nConsider re-running experiments to verify reproducibility:")
        print("  python run_complete_experiment.py")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    generate_report()

