"""
Compare Experiment Results

This script compares newly generated results with published results
to verify reproducibility.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List


def load_experiment_results(results_dir: str = "results") -> Dict:
    """Load all experiment results from JSON files."""
    results = {}
    results_path = Path(results_dir)

    if not results_path.exists():
        print(f"Results directory not found: {results_dir}")
        return results

    for json_file in results_path.glob("*.json"):
        if json_file.name == "attack_evaluation_summary.json":
            continue  # Skip attack summary for now

        with open(json_file) as f:
            data = json.load(f)
            results[json_file.stem] = data

    return results


def extract_metrics(results: Dict) -> Dict:
    """Extract key metrics from experiment results."""
    metrics = {}

    # Group by configuration
    configurations = {}

    for exp_id, data in results.items():
        if exp_id == "centralized_baseline":
            metrics["centralized"] = {
                "NDCG@10": data.get("final_metrics", {}).get("NDCG@10", 0),
                "Hit@10": data.get("final_metrics", {}).get("Hit@10", 0),
            }
            continue

        # Parse experiment ID: dp_X_alpha_Y_dim_Z_clients_N_seed_S
        # Remove the seed part to group configurations
        parts = exp_id.split("_seed_")
        if len(parts) == 2:
            config_key = parts[0]
        else:
            # Fallback: remove last part if it looks like a number
            parts = exp_id.split("_")
            if parts[-1].isdigit():
                config_key = "_".join(parts[:-2])  # Remove "seed_XXX"
            else:
                config_key = exp_id

        if config_key not in configurations:
            configurations[config_key] = []

        configurations[config_key].append({
            "NDCG@10": data.get("final_metrics", {}).get("NDCG@10", 0),
            "Hit@10": data.get("final_metrics", {}).get("Hit@10", 0),
        })

    # Compute statistics across seeds
    for config_key, runs in configurations.items():
        ndcg_values = [r["NDCG@10"] for r in runs]
        hit_values = [r["Hit@10"] for r in runs]

        metrics[config_key] = {
            "NDCG@10": {
                "mean": np.mean(ndcg_values),
                "std": np.std(ndcg_values),
                "values": ndcg_values
            },
            "Hit@10": {
                "mean": np.mean(hit_values),
                "std": np.std(hit_values),
                "values": hit_values
            },
            "num_runs": len(runs)
        }

    return metrics


def compare_metrics(published: Dict, new: Dict, tolerance: float = 0.02):
    """Compare published results with new results."""
    print("=" * 80)
    print("RESULTS COMPARISON")
    print("=" * 80)

    all_configs = set(published.keys()) | set(new.keys())

    differences = []

    for config in sorted(all_configs):
        print(f"\n{config}:")
        print("-" * 80)

        if config not in published:
            print("  ⚠️  NOT FOUND in published results")
            continue

        if config not in new:
            print("  ⚠️  NOT FOUND in new results")
            continue

        pub = published[config]
        new_res = new[config]

        # Compare NDCG@10
        if isinstance(pub, dict) and "NDCG@10" in pub:
            if isinstance(pub["NDCG@10"], dict):
                pub_ndcg = pub["NDCG@10"]["mean"]
                new_ndcg = new_res["NDCG@10"]["mean"]
                diff_ndcg = abs(pub_ndcg - new_ndcg)

                status = "✅" if diff_ndcg < tolerance else "⚠️"
                print(f"  NDCG@10: Published={pub_ndcg:.4f}±{pub['NDCG@10']['std']:.4f}, "
                      f"New={new_ndcg:.4f}±{new_res['NDCG@10']['std']:.4f}, "
                      f"Diff={diff_ndcg:.4f} {status}")

                if diff_ndcg >= tolerance:
                    differences.append((config, "NDCG@10", diff_ndcg))
            else:
                pub_ndcg = pub["NDCG@10"]
                new_ndcg = new_res["NDCG@10"]
                diff_ndcg = abs(pub_ndcg - new_ndcg)

                status = "✅" if diff_ndcg < tolerance else "⚠️"
                print(f"  NDCG@10: Published={pub_ndcg:.4f}, New={new_ndcg:.4f}, "
                      f"Diff={diff_ndcg:.4f} {status}")

                if diff_ndcg >= tolerance:
                    differences.append((config, "NDCG@10", diff_ndcg))

        # Compare Hit@10
        if isinstance(pub, dict) and "Hit@10" in pub:
            if isinstance(pub["Hit@10"], dict):
                pub_hit = pub["Hit@10"]["mean"]
                new_hit = new_res["Hit@10"]["mean"]
                diff_hit = abs(pub_hit - new_hit)

                status = "✅" if diff_hit < tolerance else "⚠️"
                print(f"  Hit@10:  Published={pub_hit:.4f}±{pub['Hit@10']['std']:.4f}, "
                      f"New={new_hit:.4f}±{new_res['Hit@10']['std']:.4f}, "
                      f"Diff={diff_hit:.4f} {status}")

                if diff_hit >= tolerance:
                    differences.append((config, "Hit@10", diff_hit))
            else:
                pub_hit = pub["Hit@10"]
                new_hit = new_res["Hit@10"]
                diff_hit = abs(pub_hit - new_hit)

                status = "✅" if diff_hit < tolerance else "⚠️"
                print(f"  Hit@10:  Published={pub_hit:.4f}, New={new_hit:.4f}, "
                      f"Diff={diff_hit:.4f} {status}")

                if diff_hit >= tolerance:
                    differences.append((config, "Hit@10", diff_hit))

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if not differences:
        print("\n✅ All results match published values within tolerance!")
        print(f"   Tolerance: ±{tolerance:.4f}")
    else:
        print(f"\n⚠️  Found {len(differences)} significant differences:")
        for config, metric, diff in differences:
            print(f"   - {config} ({metric}): diff = {diff:.4f}")
        print(f"\n   Tolerance: ±{tolerance:.4f}")
        print("\n   Note: Some variation is expected due to:")
        print("   - Random initialization")
        print("   - Floating-point precision")
        print("   - Hardware differences")
        print("   - PyTorch version differences")


def main():
    # Define published results (from EXPERIMENT_STATUS.md)
    published_results = {
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

    # Load new results
    print("Loading new experiment results...")
    new_results_raw = load_experiment_results("results")
    new_results = extract_metrics(new_results_raw)

    print(f"Loaded {len(new_results)} configurations\n")

    # Compare
    compare_metrics(published_results, new_results, tolerance=0.02)


if __name__ == "__main__":
    main()

