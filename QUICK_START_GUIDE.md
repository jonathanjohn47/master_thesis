# 🚀 Quick Start Guide - How to Run Your Experiments

This is your **step-by-step guide** to run all thesis experiments. Follow these instructions in order.

---

## 📋 Prerequisites (Do This First!)

### 1. Check Your Dataset
Make sure `ratings.csv` (MovieLens 100K dataset) is in your project root:
```powershell
ls ratings.csv
```

If missing, download it from: https://grouplens.org/datasets/movielens/100k/

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Verify Python Scripts Exist
Check that these key files exist:
```powershell
ls centralized_baseline.py
ls dp_sweep_experiment.py
ls heterogeneity_sweep_experiment.py
ls comprehensive_analysis.py
ls server.py
```

---

## 🎯 Quick Start (Simplest Way)

### Option A: Run ALL Experiments at Once

This is the **easiest** way - one command runs everything:

```powershell
# Terminal 1: Start the server (leave this running)
python server.py

# Terminal 2: Run all experiments
python run_all_experiments.py
```

**What happens:**
1. ✅ Centralized baseline (10 mins)
2. ✅ DP sweep experiments (2-4 hours) - 15 configs × 3 seeds
3. ✅ Heterogeneity sweep (1-2 hours) - 9 configs × 3 seeds
4. ✅ Comprehensive analysis (1 min) - generates all figures

**Total time: 4-8 hours** (depending on your hardware)

**When it's done:**
- All results saved in `results/` folder
- All figures saved in `figures/` folder
- Summary table: `figures/summary_table.csv`

---

## 🔧 Option B: Run Step-by-Step (More Control)

If you want to run experiments one at a time:

### Step 1: Centralized Baseline (No Server Needed)

```powershell
python centralized_baseline.py
```

**Time:** ~5-10 minutes  
**Output:** `results/centralized_baseline.json`  
**What it does:** Trains model on all data (non-federated baseline)

---

### Step 2: Start the Server (Required for Steps 3-4)

Open a **new terminal** and leave it running:

```powershell
python server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!** The server must stay running for federated experiments.

---

### Step 3: DP Sweep Experiments

In your **original terminal**:

```powershell
python dp_sweep_experiment.py
```

**Time:** ~2-4 hours  
**Output:** Multiple JSON files in `results/` folder:
- `dp_inf_alpha_0.5_dim_16_clients_100_seed_42.json`
- `dp_8_alpha_0.5_dim_16_clients_100_seed_42.json`
- `dp_4_alpha_0.5_dim_16_clients_100_seed_42.json`
- `dp_2_alpha_0.5_dim_16_clients_100_seed_42.json`
- `dp_1_alpha_0.5_dim_16_clients_100_seed_42.json`
- (Same for seeds 123 and 456)

**What it does:** Tests different privacy budgets (ε = ∞, 8, 4, 2, 1)

**Answers Research Question 1:** "How does accuracy degrade with stronger privacy?"

---

### Step 4: Heterogeneity Sweep Experiments

```powershell
python heterogeneity_sweep_experiment.py
```

**Time:** ~1-2 hours  
**Output:** Multiple JSON files for different α values (0.1, 0.5, 1.0)

**What it does:** Tests different data distributions (heterogeneity levels)

**Answers Research Question 3:** "How does data heterogeneity affect performance?"

---

### Step 5: Generate Figures and Analysis

```powershell
python comprehensive_analysis.py
```

**Time:** ~1 minute  
**Output:** Figures in `figures/` folder:
- `accuracy_vs_epsilon.png` - Shows privacy-accuracy trade-off
- `accuracy_loss_vs_epsilon.png` - Shows % accuracy loss vs baseline
- `accuracy_vs_alpha.png` - Shows heterogeneity impact
- `summary_table.csv` - All results in table format

---

## 📊 What You Get After Running Experiments

### Results Folder Structure:
```
results/
├── centralized_baseline.json                    # Baseline metrics
├── dp_inf_alpha_0.5_dim_16_clients_100_seed_*.json   # No DP
├── dp_8_alpha_0.5_dim_16_clients_100_seed_*.json     # ε = 8
├── dp_4_alpha_0.5_dim_16_clients_100_seed_*.json     # ε = 4
├── dp_2_alpha_0.5_dim_16_clients_100_seed_*.json     # ε = 2
├── dp_1_alpha_0.5_dim_16_clients_100_seed_*.json     # ε = 1
├── dp_inf_alpha_0.1_dim_16_clients_100_seed_*.json   # High heterogeneity
└── dp_inf_alpha_1.0_dim_16_clients_100_seed_*.json   # Low heterogeneity
```

### Figures Folder Structure:
```
figures/
├── accuracy_vs_epsilon.png          # Main RQ1 figure
├── accuracy_loss_vs_epsilon.png     # Shows % loss
├── accuracy_vs_alpha.png            # Main RQ3 figure
└── summary_table.csv                # All metrics in table
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: Server Not Running
```
[ERROR] Server is not running!
```
**Solution:** Open a new terminal and run:
```powershell
python server.py
```
Leave it running while experiments execute.

---

### Issue 2: Out of Memory
**Symptoms:** Script crashes, computer freezes

**Solution:** Edit the experiment scripts to reduce:
- `num_clients = 50` (instead of 100)
- `batch_size = 32` (instead of 64)

---

### Issue 3: Taking Too Long
**Solution:** Reduce the number of seeds in experiment scripts:

Edit `dp_sweep_experiment.py` and `heterogeneity_sweep_experiment.py`:
```python
# Change this line:
SEEDS = [42, 123, 456]

# To this:
SEEDS = [42]  # Just one seed
```

This reduces experiment time by 3x (but gives less statistical confidence).

---

### Issue 4: ratings.csv Not Found
```
[ERROR] ratings.csv not found!
```

**Solution:** Download MovieLens 100K dataset:
1. Go to: https://grouplens.org/datasets/movielens/100k/
2. Download `ml-100k.zip`
3. Extract and copy `u.data` to your project folder
4. Rename it to `ratings.csv`

Or use this command (if you have the file elsewhere):
```powershell
cp path\to\ml-100k\u.data ratings.csv
```

---

## 🎓 What Each Experiment Answers

| Experiment | Research Question | Key Metric |
|------------|------------------|------------|
| **Centralized Baseline** | N/A (baseline) | NDCG@10, Hit@10 |
| **DP Sweep** | RQ1: Privacy-Accuracy Trade-off | Accuracy vs ε |
| **Heterogeneity Sweep** | RQ3: Data Distribution Impact | Accuracy vs α |
| **Comprehensive Analysis** | All | Generates thesis figures |

---

## 📈 Expected Results Preview

After experiments complete, you should see:

### 1. Accuracy vs Privacy (ε)
- **ε = ∞ (no privacy):** ~90% accuracy (close to baseline)
- **ε = 8:** ~88% accuracy
- **ε = 4:** ~85% accuracy
- **ε = 2:** ~80% accuracy
- **ε = 1:** ~70% accuracy

**Thesis claim:** "We achieve ≤5% accuracy loss with ε ≥ 4"

### 2. Accuracy vs Heterogeneity (α)
- **α = 0.1 (very heterogeneous):** Lower accuracy
- **α = 0.5 (moderate):** Medium accuracy
- **α = 1.0 (more uniform):** Higher accuracy

**Thesis claim:** "Data heterogeneity significantly impacts federated learning performance"

---

## 🚀 Next Steps After Experiments

### 1. Review Results
```powershell
# Open figures folder
explorer figures\

# View summary table
cat figures\summary_table.csv
```

### 2. Verify Results Make Sense
- Check that accuracy decreases as ε decreases (stronger privacy)
- Check that all seeds show similar trends
- Compare federated results with baseline

### 3. Start Writing Thesis Results Section
Use the generated figures in your thesis:
- Figure 1: Accuracy vs ε (privacy trade-off)
- Figure 2: Accuracy loss vs ε (% degradation)
- Figure 3: Accuracy vs α (heterogeneity impact)
- Table 1: Summary statistics

---

## 📞 Still Stuck?

If you encounter issues:

1. **Check terminal output** - error messages tell you what's wrong
2. **Verify prerequisites** - Is `ratings.csv` present? Is server running?
3. **Review experiment scripts** - Check configuration parameters
4. **Check server logs** - Look at the server terminal for errors
5. **Read detailed guides**:
   - `EXPERIMENT_RUNNER_GUIDE.md` - Comprehensive guide
   - `EXPERIMENT_GUIDE.md` - Detailed experiment setup
   - `BEGINNER_GUIDE_TO_THESIS.md` - Explains concepts

---

## ⏱️ Time Budget Planning

If you have limited time:

### Minimal Setup (1-2 hours):
```powershell
# Run with just 1 seed and fewer configs
python centralized_baseline.py
python comprehensive_analysis.py
```

### Quick Validation (3-4 hours):
```powershell
# Edit scripts to use SEEDS = [42]
python run_all_experiments.py
```

### Full Experiments (4-8 hours):
```powershell
# Use default settings (3 seeds)
python run_all_experiments.py
```

---

## 🎉 Success Criteria

You know experiments are complete when:

✅ All JSON files exist in `results/` folder  
✅ All figures exist in `figures/` folder  
✅ `summary_table.csv` is generated  
✅ Figures show expected trends (accuracy ↓ as privacy ↑)  
✅ No error messages in terminal output  

**Congratulations! You're ready to write your thesis results section! 🎓**

