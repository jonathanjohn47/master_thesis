# 🚀 Complete Experiment Runner Guide

This guide explains how to run all experiments to complete your thesis work.

## 📋 Prerequisites

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Dataset**: Ensure `ratings.csv` (MovieLens 100K) is in the project root

3. **Server**: For federated learning experiments, you'll need the server running

## 🎯 Quick Start (All Experiments)

### Option 1: Run Everything Automatically

```bash
# Terminal 1: Start the server
python server.py

# Terminal 2: Run all experiments
python run_all_experiments.py
```

This will run:
1. Centralized baseline (no server needed)
2. DP sweep experiments (requires server)
3. Heterogeneity sweep experiments (requires server)
4. Comprehensive analysis

**Estimated Time**: 4-8 hours (depending on your hardware)

### Option 2: Run Experiments Individually

If you want more control, run each step separately:

#### Step 1: Centralized Baseline
```bash
python centralized_baseline.py
```
**Time**: ~5-10 minutes
**Output**: `results/centralized_baseline.json`

#### Step 2: DP Sweep Experiments
```bash
# Make sure server is running first!
python server.py  # In another terminal

# Then run DP sweep
python dp_sweep_experiment.py
```
**Time**: ~2-4 hours (15 experiments × 3 seeds)
**Output**: `results/dp_*_alpha_0.5_dim_16_clients_100_seed_*.json`

#### Step 3: Heterogeneity Sweep Experiments
```bash
# Server should still be running
python heterogeneity_sweep_experiment.py
```
**Time**: ~1-2 hours (9 experiments × 3 seeds)
**Output**: `results/dp_*_alpha_*_dim_16_clients_100_seed_*.json`

#### Step 4: Comprehensive Analysis
```bash
python comprehensive_analysis.py
```
**Time**: ~1 minute
**Output**: 
- `figures/accuracy_vs_epsilon.png`
- `figures/accuracy_loss_vs_epsilon.png`
- `figures/accuracy_vs_alpha.png`
- `figures/summary_table.csv`

## 📊 What Each Experiment Does

### 1. Centralized Baseline
- Trains a model on all data (no federated learning)
- Establishes baseline accuracy metrics
- Required for measuring "≤5% accuracy loss" target

### 2. DP Sweep Experiments
- Runs federated learning with different DP budgets: ε ∈ {∞, 8, 4, 2, 1}
- Each epsilon tested with 3 different seeds (for statistical significance)
- Answers **RQ1**: How does accuracy degrade with privacy?

### 3. Heterogeneity Sweep Experiments
- Runs federated learning with different data distributions: α ∈ {0.1, 0.5, 1.0}
- Each alpha tested with 3 different seeds
- Answers **RQ3**: How does data heterogeneity affect performance?

### 4. Comprehensive Analysis
- Loads all experiment results
- Generates publication-quality figures
- Creates summary tables
- Compares federated results with baseline

## 🔧 Advanced Options

### Run with Custom Options

```bash
# Skip certain steps
python run_all_experiments.py --skip-baseline  # If already run
python run_all_experiments.py --skip-dp        # Skip DP sweep
python run_all_experiments.py --skip-heterogeneity  # Skip heterogeneity
python run_all_experiments.py --skip-analysis  # Skip analysis

# Check server before federated experiments
python run_all_experiments.py --server-check
```

### Modify Experiment Parameters

Edit the experiment scripts to change:
- Number of clients
- Number of rounds
- Learning rate
- Batch size
- etc.

## 📁 Output Structure

After running all experiments, you'll have:

```
results/
├── centralized_baseline.json
├── dp_inf_alpha_0.5_dim_16_clients_100_seed_42.json
├── dp_8_alpha_0.5_dim_16_clients_100_seed_42.json
├── dp_4_alpha_0.5_dim_16_clients_100_seed_42.json
├── dp_2_alpha_0.5_dim_16_clients_100_seed_42.json
├── dp_1_alpha_0.5_dim_16_clients_100_seed_42.json
├── ... (more with seeds 123, 456)
├── dp_inf_alpha_0.1_dim_16_clients_100_seed_42.json
├── dp_inf_alpha_1.0_dim_16_clients_100_seed_42.json
└── ... (more with seeds 123, 456)

figures/
├── accuracy_vs_epsilon.png
├── accuracy_loss_vs_epsilon.png
├── accuracy_vs_alpha.png
└── summary_table.csv
```

## ⚠️ Troubleshooting

### Server Not Running
```
[ERROR] Server is not running!
```
**Solution**: Start server in a separate terminal: `python server.py`

### Out of Memory
If you run out of memory with 100 clients:
- Reduce `num_clients` in experiment scripts
- Reduce `batch_size`
- Close other applications

### Experiments Taking Too Long
- Reduce number of seeds (use only `[42]` instead of `[42, 123, 456]`)
- Reduce number of rounds (use 5 instead of 10)
- Reduce number of epsilon values

### Missing Results
- Check that `ratings.csv` exists
- Verify server is running for federated experiments
- Check `results/` directory permissions

## 📈 Expected Results

After completing all experiments, you should have:

1. **Baseline Metrics**: 
   - NDCG@10, Hit@10 from centralized training
   - Used as reference for accuracy loss calculation

2. **DP Sweep Results**:
   - Accuracy metrics for each ε value
   - Statistical significance (mean ± std across seeds)
   - Comparison with baseline (accuracy loss %)

3. **Heterogeneity Results**:
   - Performance across different α values
   - Shows impact of data distribution

4. **Publication-Quality Figures**:
   - Accuracy vs ε plots
   - Accuracy loss vs ε plots
   - Accuracy vs α plots
   - Summary tables

## 🎓 Next Steps After Experiments

1. **Review Results**:
   - Check all figures in `figures/`
   - Review summary table
   - Verify results make sense

2. **Write Thesis**:
   - Use figures in Results section
   - Reference experiment configurations
   - Discuss findings and trade-offs

3. **Optional: Attack Evaluation**:
   - Run attack evaluation if needed (RQ2)
   - See `scripts/attack_evaluation.py` for implementation
   - May require additional setup

## 💡 Tips

1. **Run Baseline First**: Always run centralized baseline before federated experiments
2. **Monitor Server**: Keep server terminal visible to see logs
3. **Save Progress**: Results are saved incrementally, so you can stop and resume
4. **Check Disk Space**: Experiments generate many JSON files (~10-50MB total)
5. **Use Screen/Tmux**: For long-running experiments on remote servers

## 📞 Support

If you encounter issues:
1. Check error messages in terminal output
2. Verify all prerequisites are met
3. Review experiment scripts for configuration
4. Check server logs for federated learning issues

---

**Good luck with your experiments! 🎉**

