"""
Analysis script for federated learning experiment results.
Generates statistics, visualizations, and summaries for thesis analysis.
"""

import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving files
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# Set style for thesis-quality plots
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except OSError:
    try:
        plt.style.use('seaborn-darkgrid')
    except OSError:
        plt.style.use('default')
        print("Warning: Using default matplotlib style")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12

def load_experiment_results(json_path: str):
    """Load experiment results from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)

def analyze_convergence(data):
    """Analyze model convergence over rounds."""
    rounds = [r['round'] for r in data['rounds']]
    train_losses = [r['train_loss'] for r in data['rounds']]
    test_metrics = [r['test_metrics'] for r in data['rounds']]
    
    return {
        'rounds': rounds,
        'train_losses': train_losses,
        'test_metrics': test_metrics
    }

def plot_convergence(data, save_path='figures/convergence.png'):
    """Plot training loss and test metrics over rounds."""
    analysis = analyze_convergence(data)
    rounds = analysis['rounds']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Training Loss
    axes[0, 0].plot(rounds, analysis['train_losses'], 'b-o', linewidth=2, markersize=8)
    axes[0, 0].set_xlabel('Training Round')
    axes[0, 0].set_ylabel('Training Loss')
    axes[0, 0].set_title('Training Loss Convergence')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Hit@10
    hit10 = [m.get('Hit@10', 0) for m in analysis['test_metrics']]
    axes[0, 1].plot(rounds, hit10, 'g-s', linewidth=2, markersize=8)
    axes[0, 1].set_xlabel('Training Round')
    axes[0, 1].set_ylabel('Hit@10')
    axes[0, 1].set_title('Hit@10 Over Rounds')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Accuracy
    accuracy = [m.get('accuracy', 0) for m in analysis['test_metrics']]
    axes[1, 0].plot(rounds, accuracy, 'r-^', linewidth=2, markersize=8)
    axes[1, 0].set_xlabel('Training Round')
    axes[1, 0].set_ylabel('Accuracy')
    axes[1, 0].set_title('Test Accuracy Over Rounds')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: MSE
    mse = [m.get('mse', 0) for m in analysis['test_metrics']]
    axes[1, 1].plot(rounds, mse, 'm-d', linewidth=2, markersize=8)
    axes[1, 1].set_xlabel('Training Round')
    axes[1, 1].set_ylabel('MSE')
    axes[1, 1].set_title('Mean Squared Error Over Rounds')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

def plot_recommendation_metrics(data, save_path='figures/recommendation_metrics.png'):
    """Plot recommendation system metrics."""
    analysis = analyze_convergence(data)
    rounds = analysis['rounds']
    test_metrics = analysis['test_metrics']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    hit10 = [m.get('Hit@10', 0) * 100 for m in test_metrics]
    precision = [m.get('Precision@10', 0) * 100 for m in test_metrics]
    recall = [m.get('Recall@10', 0) * 100 for m in test_metrics]
    
    ax.plot(rounds, hit10, 'o-', label='Hit@10', linewidth=2, markersize=8)
    ax.plot(rounds, precision, 's-', label='Precision@10', linewidth=2, markersize=8)
    ax.plot(rounds, recall, '^-', label='Recall@10', linewidth=2, markersize=8)
    
    ax.set_xlabel('Training Round', fontsize=14)
    ax.set_ylabel('Metric Value (%)', fontsize=14)
    ax.set_title('Recommendation Metrics Over Training Rounds', fontsize=16)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

def analyze_client_distribution(data):
    """Analyze client data distribution."""
    client_metrics = data.get('client_metrics', [])
    samples_per_client = [c.get('samples', 0) for c in client_metrics]
    
    return {
        'total_clients': len(client_metrics),
        'total_samples': sum(samples_per_client),
        'avg_samples': np.mean(samples_per_client),
        'std_samples': np.std(samples_per_client),
        'min_samples': np.min(samples_per_client),
        'max_samples': np.max(samples_per_client),
        'samples_distribution': samples_per_client
    }

def plot_client_distribution(data, save_path='figures/client_distribution.png'):
    """Plot distribution of samples per client."""
    dist_analysis = analyze_client_distribution(data)
    samples = dist_analysis['samples_distribution']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram
    ax1.hist(samples, bins=20, edgecolor='black', alpha=0.7, color='skyblue')
    ax1.axvline(dist_analysis['avg_samples'], color='red', linestyle='--', 
                linewidth=2, label=f"Mean: {dist_analysis['avg_samples']:.1f}")
    ax1.set_xlabel('Samples per Client', fontsize=14)
    ax1.set_ylabel('Number of Clients', fontsize=14)
    ax1.set_title('Distribution of Samples per Client', fontsize=16)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Box plot
    ax2.boxplot(samples, vert=True)
    ax2.set_ylabel('Samples per Client', fontsize=14)
    ax2.set_title('Samples per Client (Box Plot)', fontsize=16)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

def plot_per_round_aggregation(data, save_path='figures/aggregation_stats.png'):
    """Plot aggregation statistics per round."""
    rounds = [r['round'] for r in data['rounds']]
    num_clients = [r.get('aggregation', {}).get('num_clients', 0) for r in data['rounds']]
    total_samples = [r.get('aggregation', {}).get('total_samples', 0) for r in data['rounds']]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Number of clients per round
    ax1.plot(rounds, num_clients, 'o-', linewidth=2, markersize=8, color='purple')
    ax1.set_xlabel('Training Round', fontsize=14)
    ax1.set_ylabel('Number of Clients', fontsize=14)
    ax1.set_title('Client Participation Per Round', fontsize=16)
    ax1.grid(True, alpha=0.3)
    
    # Total samples per round
    ax2.plot(rounds, total_samples, 's-', linewidth=2, markersize=8, color='orange')
    ax2.set_xlabel('Training Round', fontsize=14)
    ax2.set_ylabel('Total Samples', fontsize=14)
    ax2.set_title('Total Samples Aggregated Per Round', fontsize=16)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

def generate_summary_statistics(data):
    """Generate summary statistics for thesis."""
    analysis = analyze_convergence(data)
    final_metrics = data.get('final_metrics', {})
    
    print("\n" + "="*60)
    print("EXPERIMENT SUMMARY STATISTICS")
    print("="*60)
    print(f"\nExperiment ID: {data.get('experiment_id', 'N/A')}")
    print(f"Timestamp: {data.get('timestamp', 'N/A')}")
    print(f"\nConfiguration:")
    config = data.get('config', {})
    print(f"  - Clients: {config.get('num_clients', 'N/A')}")
    print(f"  - Rounds: {config.get('num_rounds', 'N/A')}")
    print(f"  - Alpha (heterogeneity): {config.get('alpha', 'N/A')}")
    print(f"  - Embedding Dim: {config.get('embedding_dim', 'N/A')}")
    print(f"  - Learning Rate: {config.get('learning_rate', 'N/A')}")
    print(f"  - Batch Size: {config.get('batch_size', 'N/A')}")
    print(f"  - Local Epochs: {config.get('local_epochs', 'N/A')}")
    print(f"  - DP Epsilon: {config.get('dp_epsilon', 'N/A')} ({'Disabled' if not config.get('use_dp', False) else 'Enabled'})")
    
    print(f"\nTraining Convergence:")
    print(f"  - Initial Loss: {analysis['train_losses'][0]:.4f}")
    print(f"  - Final Loss: {analysis['train_losses'][-1]:.4f}")
    print(f"  - Loss Improvement: {analysis['train_losses'][0] - analysis['train_losses'][-1]:.4f}")
    if analysis['train_losses'][0] > 0:
        print(f"  - Loss Reduction: {(1 - analysis['train_losses'][-1]/analysis['train_losses'][0])*100:.2f}%")
    
    print(f"\nFinal Test Metrics:")
    print(f"  - Accuracy: {final_metrics.get('accuracy', 0):.4f} ({final_metrics.get('accuracy', 0)*100:.2f}%)")
    print(f"  - MSE: {final_metrics.get('mse', 0):.4f}")
    print(f"  - MAE: {final_metrics.get('mae', 0):.4f}")
    print(f"  - Hit@10: {final_metrics.get('Hit@10', 0):.4f} ({final_metrics.get('Hit@10', 0)*100:.2f}%)")
    print(f"  - Precision@10: {final_metrics.get('Precision@10', 0):.4f}")
    print(f"  - Recall@10: {final_metrics.get('Recall@10', 0):.4f}")
    print(f"  - NDCG@10: {final_metrics.get('NDCG@10', 0):.4f}")
    print(f"  - Test Samples: {final_metrics.get('samples', 'N/A')}")
    
    dist_analysis = analyze_client_distribution(data)
    print(f"\nClient Distribution:")
    print(f"  - Total Clients: {dist_analysis['total_clients']}")
    print(f"  - Total Samples: {dist_analysis['total_samples']}")
    print(f"  - Avg Samples/Client: {dist_analysis['avg_samples']:.1f}")
    print(f"  - Std Dev: {dist_analysis['std_samples']:.1f}")
    print(f"  - Min: {dist_analysis['min_samples']}")
    print(f"  - Max: {dist_analysis['max_samples']}")
    
    # Aggregation stats
    rounds = data.get('rounds', [])
    if rounds:
        avg_clients_per_round = np.mean([r.get('aggregation', {}).get('num_clients', 0) for r in rounds])
        avg_samples_per_round = np.mean([r.get('aggregation', {}).get('total_samples', 0) for r in rounds])
        print(f"\nAggregation Statistics (per round):")
        print(f"  - Avg Clients per Round: {avg_clients_per_round:.1f}")
        print(f"  - Avg Samples per Round: {avg_samples_per_round:.1f}")
    
    print("\n" + "="*60)

def compare_multiple_experiments(json_files: list, save_path='figures/comparison.png'):
    """Compare multiple experiments (e.g., different alpha, epsilon values)."""
    if len(json_files) < 2:
        print("Need at least 2 experiments to compare")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    for json_file in json_files:
        data = load_experiment_results(json_file)
        analysis = analyze_convergence(data)
        rounds = analysis['rounds']
        
        # Extract experiment identifier from filename or config
        exp_id = data.get('experiment_id', Path(json_file).stem)
        label = exp_id.split('_')[-3:]  # Get key parts
        label = '_'.join(label)
        
        # Plot 1: Training Loss
        axes[0, 0].plot(rounds, analysis['train_losses'], 'o-', linewidth=2, markersize=6, label=label)
        
        # Plot 2: Hit@10
        hit10 = [m.get('Hit@10', 0) for m in analysis['test_metrics']]
        axes[0, 1].plot(rounds, hit10, 's-', linewidth=2, markersize=6, label=label)
        
        # Plot 3: Accuracy
        accuracy = [m.get('accuracy', 0) for m in analysis['test_metrics']]
        axes[1, 0].plot(rounds, accuracy, '^-', linewidth=2, markersize=6, label=label)
        
        # Plot 4: Final metrics comparison
        final = data.get('final_metrics', {})
        axes[1, 1].bar(f"{label}\nHit@10", final.get('Hit@10', 0), alpha=0.7)
    
    axes[0, 0].set_xlabel('Training Round')
    axes[0, 0].set_ylabel('Training Loss')
    axes[0, 0].set_title('Training Loss Comparison')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].set_xlabel('Training Round')
    axes[0, 1].set_ylabel('Hit@10')
    axes[0, 1].set_title('Hit@10 Comparison')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[1, 0].set_xlabel('Training Round')
    axes[1, 0].set_ylabel('Accuracy')
    axes[1, 0].set_title('Accuracy Comparison')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].set_ylabel('Hit@10')
    axes[1, 1].set_title('Final Hit@10 Comparison')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

def main():
    # Default results file
    default_file = "results/dp_inf_alpha_0.5_dim_16_clients_50_seed_42.json"
    
    # Allow command-line argument for custom file
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
    else:
        results_file = default_file
    
    if not Path(results_file).exists():
        print(f"Error: Results file not found: {results_file}")
        print(f"\nAvailable files in 'results/' directory:")
        results_dir = Path("results")
        if results_dir.exists():
            json_files = list(results_dir.glob("*.json"))
            for f in json_files:
                print(f"  - {f}")
        return
    
    print(f"\n{'='*60}")
    print(f"FEDERATED LEARNING EXPERIMENT ANALYSIS")
    print(f"{'='*60}")
    print(f"\nLoading results from: {results_file}")
    data = load_experiment_results(results_file)
    print(f"[OK] Results loaded successfully!")
    
    # Generate summary
    generate_summary_statistics(data)
    
    # Create visualizations
    print("\nGenerating visualizations...")
    plot_convergence(data)
    plot_recommendation_metrics(data)
    plot_client_distribution(data)
    plot_per_round_aggregation(data)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    print("\nGenerated visualizations:")
    print("  ✓ figures/convergence.png")
    print("  ✓ figures/recommendation_metrics.png")
    print("  ✓ figures/client_distribution.png")
    print("  ✓ figures/aggregation_stats.png")
    print("\nCheck the 'figures/' folder for all plots.")
    print("="*60)
    
    # Try to load CSV summary if available
    csv_file = results_file.replace('.json', '_summary.csv')
    if Path(csv_file).exists():
        df_summary = pd.read_csv(csv_file)
        print(f"\nCSV Summary loaded: {len(df_summary)} rows")
        print("\nFirst few rows:")
        print(df_summary.head().to_string())
    else:
        print(f"\nCSV summary not found: {csv_file}")

if __name__ == "__main__":
    main()

