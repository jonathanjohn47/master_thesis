"""
Combined analysis script for Python and Android experiment results.
Compares simulated clients vs real mobile devices.
"""

import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import glob

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

def load_all_results():
    """Load both Python and Android results."""
    python_results = []
    android_results = []
    
    # Load Python results
    python_files = glob.glob("results/*.json")
    for f in python_files:
        try:
            with open(f, 'r') as file:
                data = json.load(file)
                data['source'] = 'python'
                data['file'] = f
                python_results.append(data)
        except Exception as e:
            print(f"Error loading {f}: {e}")
    
    # Load Android results
    android_files = glob.glob("mobile_results/*.json")
    for f in android_files:
        try:
            with open(f, 'r') as file:
                data = json.load(file)
                data['source'] = 'android'
                data['file'] = f
                android_results.append(data)
        except Exception as e:
            print(f"Error loading {f}: {e}")
    
    return python_results, android_results

def compare_convergence(python_results, android_results, save_path='figures/combined_convergence.png'):
    """Compare convergence between Python and Android clients."""
    if not python_results or not android_results:
        print("Need both Python and Android results for comparison")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Python results
    for py_data in python_results:
        rounds = [r['round'] for r in py_data.get('rounds', [])]
        train_losses = [r['train_loss'] for r in py_data.get('rounds', [])]
        hit10 = [r['test_metrics'].get('Hit@10', 0) for r in py_data.get('rounds', [])]
        accuracy = [r['test_metrics'].get('accuracy', 0) for r in py_data.get('rounds', [])]
        
        exp_id = py_data.get('experiment_id', 'Python')
        axes[0, 0].plot(rounds, train_losses, 'b-o', label=f'{exp_id}', linewidth=2, markersize=6)
        axes[0, 1].plot(rounds, hit10, 'b-s', label=f'{exp_id}', linewidth=2, markersize=6)
        axes[1, 0].plot(rounds, accuracy, 'b-^', label=f'{exp_id}', linewidth=2, markersize=6)
    
    # Android results (aggregate across devices)
    android_rounds = []
    android_losses = []
    android_hit10 = []
    android_accuracy = []
    
    for android_data in android_results:
        for r in android_data.get('rounds', []):
            round_num = r.get('round', 0)
            if round_num not in android_rounds:
                android_rounds.append(round_num)
                android_losses.append(r.get('train_loss', 0))
                android_hit10.append(r.get('test_metrics', {}).get('Hit@10', 0))
                android_accuracy.append(r.get('test_metrics', {}).get('accuracy', 0))
    
    if android_rounds:
        android_rounds, android_losses = zip(*sorted(zip(android_rounds, android_losses)))
        _, android_hit10 = zip(*sorted(zip(android_rounds, android_hit10)))
        _, android_accuracy = zip(*sorted(zip(android_rounds, android_accuracy)))
        
        axes[0, 0].plot(android_rounds, android_losses, 'r--o', label='Android (Avg)', linewidth=2, markersize=8)
        axes[0, 1].plot(android_rounds, android_hit10, 'r--s', label='Android (Avg)', linewidth=2, markersize=8)
        axes[1, 0].plot(android_rounds, android_accuracy, 'r--^', label='Android (Avg)', linewidth=2, markersize=8)
    
    axes[0, 0].set_xlabel('Training Round')
    axes[0, 0].set_ylabel('Training Loss')
    axes[0, 0].set_title('Training Loss: Python vs Android')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].set_xlabel('Training Round')
    axes[0, 1].set_ylabel('Hit@10')
    axes[0, 1].set_title('Hit@10: Python vs Android')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[1, 0].set_xlabel('Training Round')
    axes[1, 0].set_ylabel('Accuracy')
    axes[1, 0].set_title('Accuracy: Python vs Android')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Resource metrics (Android only)
    android_times = []
    android_battery = []
    for android_data in android_results:
        for r in android_data.get('rounds', []):
            res_metrics = r.get('resource_metrics', {})
            if res_metrics:
                android_times.append(res_metrics.get('training_time_ms', 0))
                android_battery.append(res_metrics.get('battery_drain', 0))
    
    if android_times:
        axes[1, 1].bar(range(len(android_times)), android_times, alpha=0.7, color='orange')
        axes[1, 1].set_xlabel('Round')
        axes[1, 1].set_ylabel('Training Time (ms)')
        axes[1, 1].set_title('Android Training Time Per Round')
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

def analyze_resource_consumption(android_results, save_path='figures/resource_consumption.png'):
    """Analyze resource consumption on Android devices."""
    if not android_results:
        print("No Android results to analyze")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    all_times = []
    all_battery = []
    all_memory = []
    device_labels = []
    
    for idx, android_data in enumerate(android_results):
        device_id = android_data.get('experiment_id', f'Device_{idx}').split('_')[-2] if '_' in android_data.get('experiment_id', '') else f'Device_{idx}'
        times = []
        battery = []
        memory = []
        
        for r in android_data.get('rounds', []):
            res_metrics = r.get('resource_metrics', {})
            if res_metrics:
                times.append(res_metrics.get('training_time_ms', 0))
                battery.append(res_metrics.get('battery_drain', 0))
                memory.append(res_metrics.get('memory_mb', 0))
        
        if times:
            all_times.extend(times)
            all_battery.extend(battery)
            all_memory.extend(memory)
            device_labels.extend([device_id] * len(times))
            
            rounds = list(range(1, len(times) + 1))
            axes[0, 0].plot(rounds, times, 'o-', label=device_id, linewidth=2, markersize=6)
            axes[0, 1].plot(rounds, battery, 's-', label=device_id, linewidth=2, markersize=6)
            if memory and any(m > 0 for m in memory):
                axes[1, 0].plot(rounds, memory, '^-', label=device_id, linewidth=2, markersize=6)
    
    axes[0, 0].set_xlabel('Training Round')
    axes[0, 0].set_ylabel('Training Time (ms)')
    axes[0, 0].set_title('Training Time per Round (Android)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].set_xlabel('Training Round')
    axes[0, 1].set_ylabel('Battery Drain (%)')
    axes[0, 1].set_title('Battery Drain per Round (Android)')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    if memory and any(m > 0 for m in memory):
        axes[1, 0].set_xlabel('Training Round')
        axes[1, 0].set_ylabel('Memory Usage (MB)')
        axes[1, 0].set_title('Memory Usage per Round (Android)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    
    # Summary statistics
    if all_times:
        avg_time = np.mean(all_times)
        avg_battery = np.mean(all_battery) if all_battery else 0
        axes[1, 1].axis('off')
        summary_text = f"""
Resource Consumption Summary (Android):
        
Average Training Time: {avg_time:.1f} ms
Average Battery Drain: {avg_battery:.2f} %
Total Devices: {len(android_results)}
Total Rounds: {len(all_times)}
        """
        axes[1, 1].text(0.1, 0.5, summary_text, fontsize=12, 
                        verticalalignment='center', family='monospace')
    
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

def generate_combined_summary(python_results, android_results):
    """Generate combined summary statistics."""
    print("\n" + "="*60)
    print("COMBINED RESULTS SUMMARY")
    print("="*60)
    
    print(f"\nPython Experiments: {len(python_results)}")
    for py_data in python_results:
        config = py_data.get('config', {})
        final = py_data.get('final_metrics', {})
        print(f"  - {py_data.get('experiment_id', 'Unknown')}")
        print(f"    Clients: {config.get('num_clients', 'N/A')}, "
              f"Rounds: {config.get('num_rounds', 'N/A')}")
        print(f"    Final Accuracy: {final.get('accuracy', 0):.4f}, "
              f"Hit@10: {final.get('Hit@10', 0):.4f}")
    
    print(f"\nAndroid Experiments: {len(android_results)}")
    for android_data in android_results:
        config = android_data.get('config', {})
        final = android_data.get('final_metrics', {})
        print(f"  - {android_data.get('experiment_id', 'Unknown')}")
        print(f"    Rounds: {len(android_data.get('rounds', []))}")
        if final:
            print(f"    Final Accuracy: {final.get('accuracy', 0):.4f}, "
                  f"Hit@10: {final.get('Hit@10', 0):.4f}")
        
        # Resource summary
        res_metrics = []
        for r in android_data.get('rounds', []):
            res = r.get('resource_metrics', {})
            if res:
                res_metrics.append(res)
        
        if res_metrics:
            avg_time = np.mean([r.get('training_time_ms', 0) for r in res_metrics])
            avg_battery = np.mean([r.get('battery_drain', 0) for r in res_metrics])
            print(f"    Avg Training Time: {avg_time:.1f} ms")
            print(f"    Avg Battery Drain: {avg_battery:.2f} %")
    
    print("\n" + "="*60)

def main():
    print("\n" + "="*60)
    print("COMBINED ANALYSIS: Python + Android Results")
    print("="*60)
    
    python_results, android_results = load_all_results()
    
    print(f"\nLoaded:")
    print(f"  - Python results: {len(python_results)}")
    print(f"  - Android results: {len(android_results)}")
    
    if not python_results and not android_results:
        print("\nError: No results found!")
        print("  - Python results should be in: results/*.json")
        print("  - Android results should be in: mobile_results/*.json")
        return
    
    # Generate summary
    generate_combined_summary(python_results, android_results)
    
    # Generate visualizations
    print("\nGenerating combined visualizations...")
    
    if python_results and android_results:
        compare_convergence(python_results, android_results)
    
    if android_results:
        analyze_resource_consumption(android_results)
    
    print("\n" + "="*60)
    print("COMBINED ANALYSIS COMPLETE!")
    print("="*60)
    print("\nGenerated visualizations:")
    if python_results and android_results:
        print("  ✓ figures/combined_convergence.png")
    if android_results:
        print("  ✓ figures/resource_consumption.png")
    print("\nCheck the 'figures/' folder for all plots.")

if __name__ == "__main__":
    main()

