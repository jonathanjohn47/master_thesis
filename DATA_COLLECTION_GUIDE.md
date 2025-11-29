# Data Collection Guide for Thesis

This guide explains how to collect, organize, and analyze data from your federated learning experiments.

## ✅ Phase 1 Complete: Data Collection Infrastructure

### What Has Been Built

1. **Recommendation Metrics Module** (`scripts/recommendation_metrics.py`)
   - ✅ NDCG@10 (Normalized Discounted Cumulative Gain)
   - ✅ Hit@10 (Hit Rate)
   - ✅ Precision@10
   - ✅ Recall@10
   - Fully compatible with your thesis requirements

2. **Metrics Collector** (`scripts/metrics_collector.py`)
   - ✅ Automatic JSON export
   - ✅ CSV summary export
   - ✅ Per-round metrics tracking
   - ✅ Client-specific metrics
   - ✅ Mobile device metrics support

3. **Updated Experiment Runner** (`run_experiment.py`)
   - ✅ Integrated metrics collection
   - ✅ Per-round evaluation
   - ✅ Automatic results saving
   - ✅ Experiment ID generation

## How Data Collection Works

### Running an Experiment

1. **Start the server:**
   ```bash
   python server.py
   ```

2. **Initialize the model:**
   ```bash
   python init_server_model.py
   ```

3. **Run experiment:**
   ```bash
   python run_experiment.py
   ```

### What Gets Collected

For each experiment, the system automatically collects:

```json
{
  "experiment_id": "dp_inf_alpha_0.5_dim_16_clients_3_seed_42",
  "timestamp": "2025-11-29T...",
  "config": {
    "num_users": 943,
    "num_items": 1682,
    "embedding_dim": 16,
    "dp_epsilon": null,
    "alpha": 0.5,
    "num_clients": 3,
    "num_rounds": 3
  },
  "rounds": [
    {
      "round": 1,
      "train_loss": 0.1234,
      "test_metrics": {
        "NDCG@10": 0.45,
        "Hit@10": 0.32,
        "Precision@10": 0.28,
        "Recall@10": 0.15,
        "mse": 0.123,
        "mae": 0.089,
        "accuracy": 0.67
      },
      "aggregation": {
        "num_clients": 3,
        "total_samples": 6901
      },
      "client_metrics": [
        {
          "client_id": "client_0",
          "loss": 0.124,
          "samples": 2300
        }
      ]
    }
  ],
  "final_metrics": {
    "NDCG@10": 0.47,
    "Hit@10": 0.35,
    ...
  }
}
```

### Output Files

After running an experiment, you get:

1. **JSON file**: `results/dp_inf_alpha_0.5_dim_16_clients_3_seed_42.json`
   - Complete detailed results
   - All rounds, all metrics
   - Full configuration

2. **CSV file**: `results/dp_inf_alpha_0.5_dim_16_clients_3_seed_42_summary.csv`
   - Quick summary for analysis
   - One row per round
   - Easy to load in Excel/Pandas

## Running Experiments for Your Thesis

### Baseline Experiment (Start Here)

```bash
# This runs with default config:
# - No DP (epsilon = inf)
# - Alpha = 0.5 (moderate heterogeneity)
# - 3 clients, 3 rounds
# - Seed = 42

python run_experiment.py
```

**Output**: `results/dp_inf_alpha_0.5_dim_16_clients_3_seed_42.json`

### DP Budget Sweep (RQ1)

You'll need to modify `run_experiment.py` or create a new script for each epsilon:

**Example: Run with DP epsilon = 8**
```python
# In run_experiment.py, change:
experiment_config["dp_epsilon"] = 8
experiment_config["use_dp"] = True
experiment_config["dp_sigma"] = 1.0  # Adjust based on epsilon
```

**Run for each ε value**: ∞, 8, 4, 2, 1

### Heterogeneity Sweep (RQ3)

Change alpha in config:
```python
experiment_config["alpha"] = 0.1  # or 0.5, 1.0
```

### Multiple Seeds

For reproducibility (3 seeds per configuration):
```python
for seed in [42, 123, 456]:
    experiment_config["seed"] = seed
    # Run experiment...
```

## Data Organization

### Recommended Directory Structure

```
results/
├── baseline/
│   ├── dp_inf_alpha_0.5_dim_16_clients_3_seed_42.json
│   ├── dp_inf_alpha_0.5_dim_16_clients_3_seed_123.json
│   └── dp_inf_alpha_0.5_dim_16_clients_3_seed_456.json
├── dp_sweep/
│   ├── dp_8_alpha_0.5_dim_16_clients_3_seed_42.json
│   ├── dp_4_alpha_0.5_dim_16_clients_3_seed_42.json
│   └── ...
├── heterogeneity/
│   ├── dp_inf_alpha_0.1_dim_16_clients_3_seed_42.json
│   └── ...
└── mobile/
    ├── android_device_1_baseline.json
    └── android_device_2_baseline.json
```

## Collecting Mobile Device Data

### From Android App

The Flutter app displays metrics in the UI. To collect:

1. **Run training round** on Android device
2. **Note the metrics** displayed:
   - Training loss
   - Resource metrics (battery, memory, time)
3. **Export manually** or add export feature to app

### Manual Collection Template

Create a CSV file: `results/mobile/mobile_experiments.csv`

```csv
experiment_id,device_id,round,loss,samples,battery_drain,training_time_ms,memory_mb
baseline,android_device_1,1,0.145,10,2.3,185,89.5
baseline,android_device_2,1,0.138,10,2.1,172,87.2
```

## Analyzing Collected Data

### Quick Analysis with Python

```python
import json
import pandas as pd

# Load results
with open('results/dp_inf_alpha_0.5_dim_16_clients_3_seed_42.json') as f:
    data = json.load(f)

# Extract metrics
rounds = data['rounds']
final_ndcg = data['final_metrics']['NDCG@10']

print(f"Final NDCG@10: {final_ndcg}")
```

### Using CSV Files

```python
import pandas as pd

# Load CSV summary
df = pd.read_csv('results/dp_inf_alpha_0.5_dim_16_clients_3_seed_42_summary.csv')

# Analyze
print(df[['Round', 'NDCG@10', 'Hit@10']])
print(f"Best NDCG@10: {df['NDCG@10'].max()}")
```

## Next Steps

### Immediate (Do Now)

1. ✅ **Test data collection:**
   ```bash
   python run_experiment.py
   ```
   Check that `results/` directory is created with JSON and CSV files.

2. ✅ **Verify metrics:**
   - Open the JSON file
   - Check that NDCG@10, Hit@10 are computed
   - Verify per-round metrics are saved

### This Week

1. **Run baseline experiment** (3 seeds)
2. **Run one DP sweep** (epsilon = 8, test it works)
3. **Collect mobile data** (2 Android devices)

### Next Phase

1. Create experiment runner script for automated sweeps
2. Build analysis and visualization scripts
3. Generate thesis figures

## Data Collection Checklist

Before starting experiments, ensure:

- [ ] Server can start and initialize model
- [ ] Python clients can connect and train
- [ ] Android devices can connect
- [ ] Results directory is created
- [ ] JSON/CSV files are saved
- [ ] Metrics include NDCG@10, Hit@10
- [ ] Per-round metrics are tracked

## Example: Complete Experiment Session

```bash
# Terminal 1: Start server
python server.py

# Terminal 2: Initialize model
python init_server_model.py

# Terminal 3: Run experiment
python run_experiment.py

# After experiment completes:
# - Check results/dp_inf_alpha_0.5_dim_16_clients_3_seed_42.json
# - Check results/dp_inf_alpha_0.5_dim_16_clients_3_seed_42_summary.csv
# - Verify all metrics are present
```

## Troubleshooting

**Problem**: Metrics not saving
- ✅ Check `results/` directory exists
- ✅ Verify file permissions
- ✅ Check experiment completes without errors

**Problem**: Missing NDCG@10/Hit@10
- ✅ Check recommendation_metrics.py is imported
- ✅ Verify test data is not empty
- ✅ Check evaluation function is called

**Problem**: CSV file is empty
- ✅ Verify at least one round completed
- ✅ Check JSON file has data first

---

**You're ready to start collecting data!** 🎉

Run your first experiment and check the `results/` directory for saved metrics.

