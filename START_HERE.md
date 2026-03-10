# ⚡ QUICK START - Read This First!

> **TL;DR:** Run two commands in two terminals. Wait 4-8 hours. Get your thesis results.

---

## 🎯 The Absolute Minimum You Need to Know

### 1. What This Does
Runs federated learning experiments to test:
- **Privacy vs Accuracy** (How much accuracy do you lose with stronger privacy?)
- **Data Distribution** (How does non-uniform data affect performance?)

### 2. What You Get
- **Figures** for your thesis (3 PNG files)
- **Data** for your results section (CSV table)
- **Proof** that your approach works

### 3. How Long It Takes
- **4-8 hours** total (run overnight)
- You can walk away - it's fully automated

---

## 🚀 Two Commands to Run Everything

### Terminal 1: Start the Server
```powershell
cd C:\Users\jonat\OneDrive\Documents\GitHub\master_thesis
python server.py
```
✅ **Leave this running** (don't close this terminal)

### Terminal 2: Run All Experiments
```powershell
cd C:\Users\jonat\OneDrive\Documents\GitHub\master_thesis
python run_all_experiments.py
```
✅ **This will run for 4-8 hours** (you can minimize and do other things)

---

## ✅ You're Done When...

You see this message in Terminal 2:
```
🎉 All experiments completed successfully!

Next steps:
  1. Review generated figures in figures/
  2. Check summary table: figures/summary_table.csv
  3. Start writing your thesis results section
```

Then:
1. Open the `figures/` folder
2. Use the 3 PNG images in your thesis
3. Use `summary_table.csv` for your results table

---

## 📁 Where Are My Results?

### Figures (for your thesis):
```
C:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\figures\
├── accuracy_vs_epsilon.png          ← Use for RQ1 (Privacy)
├── accuracy_loss_vs_epsilon.png     ← Use for % loss discussion
└── accuracy_vs_alpha.png            ← Use for RQ3 (Heterogeneity)
```

### Data (for your results table):
```
C:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\figures\
└── summary_table.csv                ← All metrics in one table
```

### Raw Results (if you need detailed data):
```
C:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\results\
└── *.json                           ← 24 JSON files with all metrics
```

---

## 🆘 Something Went Wrong?

### Server Won't Start?
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill the process using it
taskkill /PID <number> /F

# Try again
python server.py
```

### Out of Memory?
Edit these files:
- `dp_sweep_experiment.py`
- `heterogeneity_sweep_experiment.py`

Change this line:
```python
num_clients = 100  # Change to 50
```

### Taking Forever?
Edit the same files above and change:
```python
SEEDS = [42, 123, 456]  # Change to just [42]
```
This makes experiments 3x faster (but less statistically robust).

### Missing ratings.csv?
Download MovieLens 100K:
https://grouplens.org/datasets/movielens/100k/

Extract and copy `u.data` to your project folder as `ratings.csv`

---

## 📚 Want More Details?

Read these guides (in order of detail):
1. **QUICK_START_GUIDE.md** ← Comprehensive guide with troubleshooting
2. **COMMAND_REFERENCE.md** ← All commands you might need
3. **EXPERIMENT_FLOW_DIAGRAM.md** ← Visual explanation of what happens
4. **EXPERIMENT_RUNNER_GUIDE.md** ← Advanced options and configurations

---

## 🎓 What Happens Behind the Scenes

```
1. Centralized Baseline (10 min)
   └─► Trains model on all data
   
2. DP Sweep (2-4 hours)
   └─► Tests 5 privacy levels × 3 seeds = 15 runs
   
3. Heterogeneity Sweep (1-2 hours)
   └─► Tests 3 data distributions × 3 seeds = 9 runs
   
4. Analysis (1 min)
   └─► Generates figures and tables
   
Total: 25 experiments (24 federated + 1 baseline)
```

---

## 💡 Pro Tips

1. **Run overnight** - Start before bed, results ready in the morning
2. **Don't close terminals** - Keep both open until "🎉 completed successfully!"
3. **Check progress** - Terminal 2 shows which experiment is running
4. **Backup results** - Copy `results/` and `figures/` folders when done

---

## ✨ That's It!

Two commands. One night. Thesis results ready.

**Just run:**
```powershell
python server.py           # Terminal 1
python run_all_experiments.py  # Terminal 2
```

**Good luck! 🍀**

---

## 📞 Quick Links

- Report issues → Check terminal error messages first
- Need help → Read QUICK_START_GUIDE.md
- Command reference → See COMMAND_REFERENCE.md
- Understand flow → Read EXPERIMENT_FLOW_DIAGRAM.md

---

**Last Updated:** 2026-03-10

