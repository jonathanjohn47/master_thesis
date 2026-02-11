"""
Comprehensive Analysis Script for All Experiments

Loads and analyzes results from:
- Centralized baseline
- DP sweep experiments
- Heterogeneity sweep experiments
- Generates publication-quality figures
"""

import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import glob
from typing import Dict, List, Optional
import seaborn as sns

# Set style
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('default')

plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 11


def load_baseline() -> Optional[Dict]:
    """Load centralized baseline results."""
    baseline_path = Path("results/centralized_baseline.json")
    if baseline_path.exists():
        with open(baseline_path, 'r') as f:
            return json.load(f)
    return None


def load_dp_sweep_results() -> Dict:
    """Load all DP sweep experiment results."""
    results = {}
    # Try both dim_64 and dim_16 patterns for backwards compatibility
    for dim in [64, 16]:
        pattern = f"results/dp_*_alpha_0.5_dim_{dim}_clients_100_seed_*.json"
        for filepath in glob.glob(pattern):
            with open(filepath, 'r') as f:
                data = json.load(f)
                config = data.get('config', {})
                epsilon = config.get('dp_epsilon')
                seed = config.get('seed', 42)

                if epsilon is None:
                    epsilon = float('inf')

                if epsilon not in results:
                    results[epsilon] = []

                results[epsilon].append({
                    'seed': seed,
                    'final_metrics': data.get('final_metrics', {}),
                    'rounds': data.get('rounds', [])
                })

    return results


def load_heterogeneity_results() -> Dict:
    """Load all heterogeneity sweep experiment results."""
    results = {}
    # Try both dim_64 and dim_16 patterns for backwards compatibility
    for dim in [64, 16]:
        pattern = f"results/dp_*_alpha_*_dim_{dim}_clients_100_seed_*.json"
        for filepath in glob.glob(pattern):
            with open(filepath, 'r') as f:
                data = json.load(f)
                config = data.get('config', {})
                alpha = config.get('alpha')
                epsilon = config.get('dp_epsilon')
                seed = config.get('seed', 42)

                # Only include non-DP experiments for heterogeneity analysis
                if epsilon is None or epsilon == float('inf'):
                    if alpha not in results:
                        results[alpha] = []

                    results[alpha].append({
                        'seed': seed,
                        'final_metrics': data.get('final_metrics', {}),
                        'rounds': data.get('rounds', [])
                    })

    return results


def plot_accuracy_vs_epsilon(dp_results: Dict, baseline: Optional[Dict], save_path: str = "figures/accuracy_vs_epsilon.png"):
    """Plot accuracy metrics vs DP budget (epsilon)."""
    epsilons = sorted([e for e in dp_results.keys() if e != float('inf')] + [float('inf')])
    
    ndcg_values = []
    hit_values = []
    ndcg_stds = []
    hit_stds = []
    
    for epsilon in epsilons:
        if epsilon in dp_results:
            results = dp_results[epsilon]
            ndcg_vals = [r['final_metrics'].get('NDCG@10', 0) for r in results]
            hit_vals = [r['final_metrics'].get('Hit@10', 0) for r in results]
            
            ndcg_values.append(np.mean(ndcg_vals))
            hit_values.append(np.mean(hit_vals))
            ndcg_stds.append(np.std(ndcg_vals))
            hit_stds.append(np.std(hit_vals))
        else:
            ndcg_values.append(0)
            hit_values.append(0)
            ndcg_stds.append(0)
            hit_stds.append(0)
    
    # Convert inf to string for plotting
    epsilon_labels = [str(e) if e != float('inf') else '∞' for e in epsilons]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # NDCG@10
    ax1.errorbar(range(len(epsilons)), ndcg_values, yerr=ndcg_stds, 
                 marker='o', linewidth=2, markersize=8, capsize=5, label='Federated')
    
    if baseline:
        baseline_ndcg = baseline.get('final_metrics', {}).get('NDCG@10', 0)
        ax1.axhline(y=baseline_ndcg, color='r', linestyle='--', linewidth=2, label='Centralized Baseline')
    
    ax1.set_xlabel('DP Budget (ε)')
    ax1.set_ylabel('NDCG@10')
    ax1.set_title('NDCG@10 vs DP Budget')
    ax1.set_xticks(range(len(epsilons)))
    ax1.set_xticklabels(epsilon_labels)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Hit@10
    ax2.errorbar(range(len(epsilons)), hit_values, yerr=hit_stds,
                 marker='s', linewidth=2, markersize=8, capsize=5, label='Federated', color='green')
    
    if baseline:
        baseline_hit = baseline.get('final_metrics', {}).get('Hit@10', 0)
        ax2.axhline(y=baseline_hit, color='r', linestyle='--', linewidth=2, label='Centralized Baseline')
    
    ax2.set_xlabel('DP Budget (ε)')
    ax2.set_ylabel('Hit@10')
    ax2.set_title('Hit@10 vs DP Budget')
    ax2.set_xticks(range(len(epsilons)))
    ax2.set_xticklabels(epsilon_labels)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()


def plot_accuracy_vs_alpha(heterogeneity_results: Dict, save_path: str = "figures/accuracy_vs_alpha.png"):
    """Plot accuracy metrics vs data heterogeneity (alpha)."""
    alphas = sorted(heterogeneity_results.keys())
    
    ndcg_values = []
    hit_values = []
    ndcg_stds = []
    hit_stds = []
    
    for alpha in alphas:
        if alpha in heterogeneity_results:
            results = heterogeneity_results[alpha]
            ndcg_vals = [r['final_metrics'].get('NDCG@10', 0) for r in results]
            hit_vals = [r['final_metrics'].get('Hit@10', 0) for r in results]
            
            ndcg_values.append(np.mean(ndcg_vals))
            hit_values.append(np.mean(hit_vals))
            ndcg_stds.append(np.std(ndcg_vals))
            hit_stds.append(np.std(hit_vals))
        else:
            ndcg_values.append(0)
            hit_values.append(0)
            ndcg_stds.append(0)
            hit_stds.append(0)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # NDCG@10
    ax1.errorbar(range(len(alphas)), ndcg_values, yerr=ndcg_stds,
                 marker='o', linewidth=2, markersize=8, capsize=5, color='purple')
    ax1.set_xlabel('Data Heterogeneity (α)')
    ax1.set_ylabel('NDCG@10')
    ax1.set_title('NDCG@10 vs Data Heterogeneity')
    ax1.set_xticks(range(len(alphas)))
    ax1.set_xticklabels([str(a) for a in alphas])
    ax1.grid(True, alpha=0.3)
    
    # Hit@10
    ax2.errorbar(range(len(alphas)), hit_values, yerr=hit_stds,
                 marker='s', linewidth=2, markersize=8, capsize=5, color='orange')
    ax2.set_xlabel('Data Heterogeneity (α)')
    ax2.set_ylabel('Hit@10')
    ax2.set_title('Hit@10 vs Data Heterogeneity')
    ax2.set_xticks(range(len(alphas)))
    ax2.set_xticklabels([str(a) for a in alphas])
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()


def plot_accuracy_loss_vs_epsilon(dp_results: Dict, baseline: Optional[Dict], save_path: str = "figures/accuracy_loss_vs_epsilon.png"):
    """Plot relative accuracy loss vs DP budget."""
    if not baseline:
        print("No baseline available. Skipping accuracy loss plot.")
        return
    
    baseline_ndcg = baseline.get('final_metrics', {}).get('NDCG@10', 0)
    baseline_hit = baseline.get('final_metrics', {}).get('Hit@10', 0)
    
    if baseline_ndcg == 0 or baseline_hit == 0:
        print("Baseline metrics are zero. Skipping accuracy loss plot.")
        return
    
    epsilons = sorted([e for e in dp_results.keys() if e != float('inf')] + [float('inf')])
    
    ndcg_losses = []
    hit_losses = []
    ndcg_loss_stds = []
    hit_loss_stds = []
    
    for epsilon in epsilons:
        if epsilon in dp_results:
            results = dp_results[epsilon]
            ndcg_vals = [r['final_metrics'].get('NDCG@10', 0) for r in results]
            hit_vals = [r['final_metrics'].get('Hit@10', 0) for r in results]
            
            # Calculate relative loss
            ndcg_loss_vals = [((baseline_ndcg - val) / baseline_ndcg) * 100 for val in ndcg_vals]
            hit_loss_vals = [((baseline_hit - val) / baseline_hit) * 100 for val in hit_vals]
            
            ndcg_losses.append(np.mean(ndcg_loss_vals))
            hit_losses.append(np.mean(hit_loss_vals))
            ndcg_loss_stds.append(np.std(ndcg_loss_vals))
            hit_loss_stds.append(np.std(hit_loss_vals))
        else:
            ndcg_losses.append(0)
            hit_losses.append(0)
            ndcg_loss_stds.append(0)
            hit_loss_stds.append(0)
    
    epsilon_labels = [str(e) if e != float('inf') else '∞' for e in epsilons]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.errorbar(range(len(epsilons)), ndcg_losses, yerr=ndcg_loss_stds,
                marker='o', linewidth=2, markersize=8, capsize=5, label='NDCG@10 Loss')
    ax.errorbar(range(len(epsilons)), hit_losses, yerr=hit_loss_stds,
                marker='s', linewidth=2, markersize=8, capsize=5, label='Hit@10 Loss')
    
    # Target threshold line
    ax.axhline(y=5, color='r', linestyle='--', linewidth=2, label='Target (≤5%)')
    
    ax.set_xlabel('DP Budget (ε)')
    ax.set_ylabel('Relative Accuracy Loss (%)')
    ax.set_title('Accuracy Loss vs DP Budget')
    ax.set_xticks(range(len(epsilons)))
    ax.set_xticklabels(epsilon_labels)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()


def generate_summary_table(dp_results: Dict, heterogeneity_results: Dict, baseline: Optional[Dict], save_path: str = "figures/summary_table.csv"):
    """Generate summary table of all results."""
    rows = []
    
    # Baseline
    if baseline:
        rows.append({
            'Experiment': 'Centralized Baseline',
            'Epsilon': 'N/A',
            'Alpha': 'N/A',
            'NDCG@10': baseline.get('final_metrics', {}).get('NDCG@10', 0),
            'Hit@10': baseline.get('final_metrics', {}).get('Hit@10', 0),
            'Accuracy': baseline.get('final_metrics', {}).get('accuracy', 0)
        })
    
    # DP sweep results
    for epsilon in sorted(dp_results.keys()):
        results = dp_results[epsilon]
        ndcg_vals = [r['final_metrics'].get('NDCG@10', 0) for r in results]
        hit_vals = [r['final_metrics'].get('Hit@10', 0) for r in results]
        acc_vals = [r['final_metrics'].get('accuracy', 0) for r in results]
        
        rows.append({
            'Experiment': 'DP Sweep',
            'Epsilon': str(epsilon) if epsilon != float('inf') else '∞',
            'Alpha': '0.5',
            'NDCG@10': f"{np.mean(ndcg_vals):.4f} ± {np.std(ndcg_vals):.4f}",
            'Hit@10': f"{np.mean(hit_vals):.4f} ± {np.std(hit_vals):.4f}",
            'Accuracy': f"{np.mean(acc_vals):.4f} ± {np.std(acc_vals):.4f}"
        })
    
    # Heterogeneity results
    for alpha in sorted(heterogeneity_results.keys()):
        results = heterogeneity_results[alpha]
        ndcg_vals = [r['final_metrics'].get('NDCG@10', 0) for r in results]
        hit_vals = [r['final_metrics'].get('Hit@10', 0) for r in results]
        acc_vals = [r['final_metrics'].get('accuracy', 0) for r in results]
        
        rows.append({
            'Experiment': 'Heterogeneity Sweep',
            'Epsilon': '∞',
            'Alpha': str(alpha),
            'NDCG@10': f"{np.mean(ndcg_vals):.4f} ± {np.std(ndcg_vals):.4f}",
            'Hit@10': f"{np.mean(hit_vals):.4f} ± {np.std(hit_vals):.4f}",
            'Accuracy': f"{np.mean(acc_vals):.4f} ± {np.std(acc_vals):.4f}"
        })
    
    df = pd.DataFrame(rows)
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(save_path, index=False)
    print(f"Saved: {save_path}")
    
    return df


def plot_convergence(dp_results: Dict, save_path: str = "figures/convergence.png"):
    """Plot training convergence curves for different DP budgets."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    epsilons = sorted([e for e in dp_results.keys() if e != float('inf')] + [float('inf')])

    for idx, epsilon in enumerate(epsilons):
        if epsilon not in dp_results:
            continue
        results = dp_results[epsilon]
        # Average across seeds
        all_losses = []
        all_ndcg = []
        for r in results:
            losses = [rd.get('train_loss', 0) for rd in r['rounds']]
            ndcg = [rd.get('test_metrics', {}).get('NDCG@10', 0) for rd in r['rounds']]
            all_losses.append(losses)
            all_ndcg.append(ndcg)

        if not all_losses:
            continue

        max_len = max(len(l) for l in all_losses)
        avg_losses = np.mean([l + [l[-1]]*(max_len-len(l)) for l in all_losses], axis=0)
        avg_ndcg = np.mean([n + [n[-1]]*(max_len-len(n)) for n in all_ndcg], axis=0)
        rounds = list(range(1, len(avg_losses) + 1))

        label = f'ε={epsilon}' if epsilon != float('inf') else 'ε=∞ (no DP)'
        color = colors[idx % len(colors)]

        ax1.plot(rounds, avg_losses, marker='o', markersize=4, linewidth=2, label=label, color=color)
        ax2.plot(rounds, avg_ndcg, marker='s', markersize=4, linewidth=2, label=label, color=color)

    ax1.set_xlabel('Round')
    ax1.set_ylabel('Training Loss')
    ax1.set_title('Training Loss Convergence')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    ax2.set_xlabel('Round')
    ax2.set_ylabel('NDCG@10')
    ax2.set_title('NDCG@10 Convergence')
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()


def plot_attack_results(save_path: str = "figures/attack_evaluation.png"):
    """Plot attack evaluation results across DP budgets."""
    attack_path = Path("results/attack_evaluation_summary.json")
    if not attack_path.exists():
        print("No attack evaluation results found. Skipping attack plot.")
        return

    with open(attack_path) as f:
        attack_data = json.load(f)

    if not attack_data:
        return

    epsilons = []
    mia_aucs = []
    mia_accs = []
    inv_accs = []

    for eps_str in sorted(attack_data.keys(), key=lambda x: float(x) if x != 'inf' else float('inf')):
        epsilons.append('∞' if eps_str == 'inf' else eps_str)
        mia = attack_data[eps_str].get('mia', {})
        inv = attack_data[eps_str].get('inversion', {})
        mia_aucs.append(mia.get('auc', 0))
        mia_accs.append(mia.get('accuracy', 0))
        inv_accs.append(inv.get('top_k_accuracy', 0))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    x = range(len(epsilons))
    ax1.bar([i - 0.2 for i in x], mia_aucs, 0.4, label='MIA AUC', color='#d62728', alpha=0.8)
    ax1.bar([i + 0.2 for i in x], mia_accs, 0.4, label='MIA Accuracy', color='#ff7f0e', alpha=0.8)
    ax1.axhline(y=0.5, color='gray', linestyle='--', linewidth=1, label='Random Baseline')
    ax1.set_xlabel('DP Budget (ε)')
    ax1.set_ylabel('Score')
    ax1.set_title('Membership Inference Attack')
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(epsilons)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')

    ax2.bar(x, inv_accs, 0.5, color='#9467bd', alpha=0.8)
    ax2.set_xlabel('DP Budget (ε)')
    ax2.set_ylabel('Top-K Accuracy')
    ax2.set_title('Model Inversion Attack')
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(epsilons)
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()


def main():
    """Main analysis function"""
    print("="*60)
    print("Comprehensive Experiment Analysis")
    print("="*60)

    # Load results
    print("\nLoading results...")
    baseline = load_baseline()
    dp_results = load_dp_sweep_results()
    heterogeneity_results = load_heterogeneity_results()

    print(f"  Baseline: {'Found' if baseline else 'Not found'}")
    print(f"  DP sweep experiments: {len(dp_results)} epsilon values")
    print(f"  Heterogeneity experiments: {len(heterogeneity_results)} alpha values")

    # Generate plots
    print("\nGenerating plots...")

    if dp_results:
        plot_accuracy_vs_epsilon(dp_results, baseline)
        plot_accuracy_loss_vs_epsilon(dp_results, baseline)
        plot_convergence(dp_results)

    if heterogeneity_results:
        plot_accuracy_vs_alpha(heterogeneity_results)

    # Attack evaluation plot
    plot_attack_results()

    # Generate summary table
    print("\nGenerating summary table...")
    summary_df = generate_summary_table(dp_results, heterogeneity_results, baseline)

    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60)
    print("\nGenerated files:")
    print("  - figures/accuracy_vs_epsilon.png")
    print("  - figures/accuracy_loss_vs_epsilon.png")
    print("  - figures/accuracy_vs_alpha.png")
    print("  - figures/convergence.png")
    print("  - figures/attack_evaluation.png")
    print("  - figures/summary_table.csv")
    print("\nSummary Table:")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()

