# 📊 Experiment Flow Diagram

## Visual Guide: How Your Experiments Work

```
┌─────────────────────────────────────────────────────────────┐
│                    START: Run Experiments                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  Prerequisites Check   │
         │  • ratings.csv exists? │
         │  • Dependencies OK?    │
         └────────┬───────────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │  EXPERIMENT 1: Baseline     │
    │  • No server needed         │
    │  • Centralized training     │
    │  • Creates reference metrics│
    │  ⏱️ Time: ~10 minutes        │
    └─────────┬───────────────────┘
              │
              ▼
    ┌─────────────────────────────┐
    │  Start Server (Terminal 1)  │
    │  python server.py           │
    │  🔄 Leave Running           │
    └─────────┬───────────────────┘
              │
              ▼
    ┌─────────────────────────────────────────┐
    │  EXPERIMENT 2: DP Sweep                 │
    │  • Tests privacy budgets (ε)            │
    │  • ε = ∞, 8, 4, 2, 1                    │
    │  • 3 seeds each (42, 123, 456)          │
    │  • Total: 15 experiment runs            │
    │  ⏱️ Time: ~2-4 hours                     │
    │  📊 Answers RQ1: Privacy vs Accuracy    │
    └─────────┬───────────────────────────────┘
              │
              ▼
    ┌─────────────────────────────────────────┐
    │  EXPERIMENT 3: Heterogeneity Sweep      │
    │  • Tests data distributions (α)         │
    │  • α = 0.1, 0.5, 1.0                    │
    │  • 3 seeds each (42, 123, 456)          │
    │  • Total: 9 experiment runs             │
    │  ⏱️ Time: ~1-2 hours                     │
    │  📊 Answers RQ3: Heterogeneity Impact   │
    └─────────┬───────────────────────────────┘
              │
              ▼
    ┌─────────────────────────────────────────┐
    │  EXPERIMENT 4: Analysis                 │
    │  • Load all results                     │
    │  • Generate figures                     │
    │  • Create summary tables                │
    │  ⏱️ Time: ~1 minute                      │
    │  📊 Output: Publication-ready figures   │
    └─────────┬───────────────────────────────┘
              │
              ▼
    ┌─────────────────────────────┐
    │  ✅ COMPLETE!               │
    │  • All results saved        │
    │  • All figures generated    │
    │  • Ready for thesis writing │
    └─────────────────────────────┘
```

---

## Detailed Flow: What Happens in Each Experiment

### 🔵 Experiment 1: Centralized Baseline

```
Input: ratings.csv (MovieLens 100K dataset)
  │
  ├─► Split data into train/test (80/20)
  │
  ├─► Train model on ALL data (no federated learning)
  │   • 10 rounds of training
  │   • Embedding dim: 16
  │   • Batch size: 64
  │
  ├─► Evaluate on test set
  │   • Calculate NDCG@10
  │   • Calculate Hit@10
  │   • Calculate training loss
  │
  └─► Save results
      Output: results/centralized_baseline.json
```

**Why this matters:** This is your "best case" scenario. All federated experiments are compared to this baseline.

---

### 🟢 Experiment 2: DP Sweep (Privacy Budget Testing)

```
For each ε in [∞, 8, 4, 2, 1]:
  │
  For each seed in [42, 123, 456]:
    │
    ├─► Initialize server with global model
    │
    ├─► Create 100 simulated clients
    │   • Each client gets subset of data
    │   • Data distributed using Dirichlet(α=0.5)
    │
    ├─► For 10 rounds:
    │   │
    │   ├─► Each client trains locally
    │   │   • On their own data
    │   │   • With DP noise (σ based on ε)
    │   │   • Gradient clipping (C = 1.0)
    │   │
    │   ├─► Clients send updates to server
    │   │
    │   ├─► Server aggregates updates
    │   │   • FedAvg: weighted average
    │   │   • Based on client data sizes
    │   │
    │   └─► Evaluate global model
    │       • NDCG@10, Hit@10
    │       • Training loss
    │
    └─► Save results
        Output: results/dp_{ε}_alpha_0.5_dim_16_clients_100_seed_{seed}.json
```

**Why this matters:** Shows the privacy-accuracy trade-off. Answers "Can we protect privacy without losing too much accuracy?"

---

### 🟡 Experiment 3: Heterogeneity Sweep (Data Distribution Testing)

```
For each α in [0.1, 0.5, 1.0]:
  │
  For each seed in [42, 123, 456]:
    │
    ├─► Initialize server with global model
    │
    ├─► Create 100 simulated clients
    │   • Each client gets subset of data
    │   • Data distributed using Dirichlet(α)
    │   • α = 0.1: Very heterogeneous (some clients very different)
    │   • α = 0.5: Moderate heterogeneity
    │   • α = 1.0: More uniform distribution
    │
    ├─► For 10 rounds:
    │   │
    │   ├─► Each client trains locally
    │   │   • On their own data
    │   │   • No DP (ε = ∞) to isolate heterogeneity effect
    │   │
    │   ├─► Clients send updates to server
    │   │
    │   ├─► Server aggregates updates
    │   │   • FedAvg: weighted average
    │   │
    │   └─► Evaluate global model
    │       • NDCG@10, Hit@10
    │       • Training loss
    │
    └─► Save results
        Output: results/dp_inf_alpha_{α}_dim_16_clients_100_seed_{seed}.json
```

**Why this matters:** Shows how data distribution affects federated learning. Answers "Does it matter if clients have very different data?"

---

### 🟣 Experiment 4: Comprehensive Analysis

```
Input: All result JSON files from Experiments 1-3
  │
  ├─► Load centralized baseline metrics
  │
  ├─► Load all DP sweep results
  │   • Group by ε value
  │   • Calculate mean ± std across seeds
  │
  ├─► Load all heterogeneity results
  │   • Group by α value
  │   • Calculate mean ± std across seeds
  │
  ├─► Generate Figure 1: Accuracy vs ε
  │   • X-axis: Privacy budget (ε)
  │   • Y-axis: NDCG@10 and Hit@10
  │   • Shows privacy-accuracy trade-off
  │
  ├─► Generate Figure 2: Accuracy Loss vs ε
  │   • X-axis: Privacy budget (ε)
  │   • Y-axis: % accuracy loss vs baseline
  │   • Highlights "≤5% loss" threshold
  │
  ├─► Generate Figure 3: Accuracy vs α
  │   • X-axis: Heterogeneity (α)
  │   • Y-axis: NDCG@10 and Hit@10
  │   • Shows heterogeneity impact
  │
  └─► Generate Summary Table
      • All metrics in CSV format
      • Mean ± std for each configuration
      Output: figures/*.png, figures/summary_table.csv
```

**Why this matters:** Creates publication-ready figures for your thesis. All your hard work visualized!

---

## Data Flow Diagram

```
┌─────────────┐
│ ratings.csv │  (MovieLens 100K dataset)
└──────┬──────┘
       │
       ├───────────────────────────────────────────┐
       │                                           │
       ▼                                           ▼
┌──────────────┐                          ┌────────────────┐
│ Centralized  │                          │   Federated    │
│   Training   │                          │    Learning    │
│  (Baseline)  │                          │  (Experiments) │
└──────┬───────┘                          └────────┬───────┘
       │                                           │
       ▼                                           ▼
┌──────────────────────┐              ┌─────────────────────────┐
│ Baseline Metrics     │              │ Split across clients:   │
│ • NDCG@10: ~0.XX     │              │                         │
│ • Hit@10: ~0.XX      │              │ Client 1: [data subset] │
│ • Loss: ~X.XX        │              │ Client 2: [data subset] │
└──────┬───────────────┘              │ ...                     │
       │                               │ Client 100: [data]      │
       │                               └────────┬────────────────┘
       │                                        │
       │                                        ▼
       │                               ┌─────────────────────┐
       │                               │ Federated Training: │
       │                               │                     │
       │                               │ Round 1 → Model v1  │
       │                               │ Round 2 → Model v2  │
       │                               │ ...                 │
       │                               │ Round 10 → Final    │
       │                               └────────┬────────────┘
       │                                        │
       │                                        ▼
       │                               ┌──────────────────────┐
       │                               │ Federated Metrics:   │
       │                               │ • NDCG@10: ~0.XX     │
       │                               │ • Hit@10: ~0.XX      │
       │                               │ • Loss: ~X.XX        │
       │                               └────────┬─────────────┘
       │                                        │
       └────────────────┬───────────────────────┘
                        │
                        ▼
            ┌─────────────────────┐
            │ Comprehensive       │
            │ Analysis            │
            │                     │
            │ • Compare results   │
            │ • Calculate % loss  │
            │ • Generate figures  │
            └─────────┬───────────┘
                      │
                      ▼
            ┌───────────────────────┐
            │ Publication Figures:  │
            │                       │
            │ 📊 accuracy_vs_epsilon │
            │ 📊 accuracy_loss       │
            │ 📊 accuracy_vs_alpha   │
            │ 📋 summary_table.csv   │
            └───────────────────────┘
```

---

## Timeline Visualization

```
Hour 0                                                    Hour 8
│                                                            │
├─ Baseline ─┤                                              │
│  (10 min)  │                                              │
│            │                                              │
│            ├──────── DP Sweep ────────┤                   │
│            │      (2-4 hours)         │                   │
│            │   15 experiments ×       │                   │
│            │   3 seeds each           │                   │
│            │                          │                   │
│            │                          ├─ Heterogeneity ──┤│
│            │                          │   (1-2 hours)    ││
│            │                          │  9 experiments × ││
│            │                          │  3 seeds each    ││
│            │                          │                  ││
│            │                          │                  ├┤ Analysis
│            │                          │                  ││ (1 min)
│            │                          │                  ││
└────────────┴──────────────────────────┴──────────────────┴┴─
  Baseline      DP Sweep Testing         Het. Testing      Done
```

---

## File Output Structure

```
master_thesis/
│
├── results/                                    # All experimental data
│   ├── centralized_baseline.json              # Baseline metrics
│   │
│   ├── dp_inf_alpha_0.5_..._seed_42.json     # No DP, seed 42
│   ├── dp_inf_alpha_0.5_..._seed_123.json    # No DP, seed 123
│   ├── dp_inf_alpha_0.5_..._seed_456.json    # No DP, seed 456
│   │
│   ├── dp_8_alpha_0.5_..._seed_42.json       # ε=8, seed 42
│   ├── dp_8_alpha_0.5_..._seed_123.json      # ε=8, seed 123
│   ├── dp_8_alpha_0.5_..._seed_456.json      # ε=8, seed 456
│   │
│   ├── dp_4_alpha_0.5_..._seed_42.json       # ε=4, all seeds
│   ├── dp_2_alpha_0.5_..._seed_42.json       # ε=2, all seeds
│   ├── dp_1_alpha_0.5_..._seed_42.json       # ε=1, all seeds
│   │
│   ├── dp_inf_alpha_0.1_..._seed_42.json     # High heterogeneity
│   └── dp_inf_alpha_1.0_..._seed_42.json     # Low heterogeneity
│
└── figures/                                    # Thesis figures
    ├── accuracy_vs_epsilon.png                # Main RQ1 figure
    ├── accuracy_loss_vs_epsilon.png           # % loss visualization
    ├── accuracy_vs_alpha.png                  # Main RQ3 figure
    └── summary_table.csv                      # All metrics table
```

---

## Expected Output Preview

### Figure 1: Accuracy vs Privacy Budget (ε)

```
NDCG@10
  0.30 ├─────────●─────────────────────────── Centralized Baseline
       │         ●
  0.25 ├         ●
       │          ●
  0.20 ├           ●─────●
       │                 ●
  0.15 ├                  ●
       │                   ●
  0.10 ├                    ●────●
       │                          ●
  0.05 ├                           ●
       │
  0.00 └─────┬─────┬─────┬─────┬─────┬─────
             ∞     8     4     2     1      ε (Privacy Budget)
             
       ← Less Privacy | More Privacy →
```

### Figure 2: Accuracy Loss vs Privacy Budget

```
Loss %
    0% ├─●──────────────────────── No loss (ε=∞)
       │
    5% ├──────●───●──────────────── ≤5% loss threshold
       │          ●
   10% ├           ●
       │            ●
   15% ├             ●
       │
   20% ├──────────────●──────────── Strong privacy (ε=1)
       │
       └─────┬─────┬─────┬─────┬─────
             ∞     8     4     2     1      ε
```

### Figure 3: Accuracy vs Heterogeneity (α)

```
NDCG@10
  0.30 ├──────────────────────────●
       │                         ●
  0.25 ├                       ●
       │                     ●
  0.20 ├                   ●
       │                 ●
  0.15 ├               ●
       │             ●
  0.10 ├           ●
       │         ●
  0.05 ├───────●
       │
       └─────┬──────┬──────┬──────
            0.1    0.5    1.0      α (Heterogeneity)
            
       ← More Heterogeneous | More Uniform →
```

---

## Success Indicators

### ✅ Experiments Running Correctly

```
Terminal 1 (Server):
  INFO: Uvicorn running on http://0.0.0.0:8000
  INFO: Client connected: client_0
  INFO: Client connected: client_1
  ...
  INFO: Aggregating 100 client updates
  INFO: Round 1 complete

Terminal 2 (Experiments):
  [OK] Centralized Baseline completed successfully
  
  [INFO] Starting DP sweep experiments...
  [1/15] Running: ε=∞, α=0.5, seed=42
  Round 1/10: loss=0.XX, ndcg=0.XX
  ...
  [2/15] Running: ε=∞, α=0.5, seed=123
  ...
```

### ✅ Expected Final Output

```
🎉 All experiments completed successfully!

Next steps:
  1. Review generated figures in figures/
  2. Check summary table: figures/summary_table.csv
  3. Start writing your thesis results section
  
Files created:
  ✓ 24 result JSON files
  ✓ 3 figure PNG files
  ✓ 1 summary table CSV
```

---

## What Each File Contains

### results/*.json Structure
```json
{
  "experiment_id": "dp_8_alpha_0.5_...",
  "config": {
    "epsilon": 8,
    "alpha": 0.5,
    "num_clients": 100,
    "num_rounds": 10,
    "seed": 42
  },
  "metrics": {
    "round_1": {"ndcg": 0.XX, "hit": 0.XX, "loss": X.XX},
    "round_2": {"ndcg": 0.XX, "hit": 0.XX, "loss": X.XX},
    ...
    "round_10": {"ndcg": 0.XX, "hit": 0.XX, "loss": X.XX}
  },
  "final_metrics": {
    "ndcg@10": 0.XX,
    "hit@10": 0.XX,
    "final_loss": X.XX
  }
}
```

### summary_table.csv Structure
```csv
epsilon,alpha,seed,ndcg@10,hit@10,loss,accuracy_loss_%
inf,0.5,42,0.XXX,0.XXX,X.XX,0.0%
8,0.5,42,0.XXX,0.XXX,X.XX,1.5%
4,0.5,42,0.XXX,0.XXX,X.XX,3.2%
2,0.5,42,0.XXX,0.XXX,X.XX,6.8%
1,0.5,42,0.XXX,0.XXX,X.XX,15.2%
...
```

---

**💡 Use this diagram to understand what happens when you run experiments!**

