# 📚 Experiment Documentation Index

## 🎯 Quick Navigation

### New to Running Experiments?
**→ Start with [START_HERE.md](START_HERE.md)** ⭐

This is the simplest guide with just two commands to run everything.

---

## 📖 All Documentation Files

### 1. **START_HERE.md** ⚡
- **Level:** Beginner
- **Length:** 2 minutes
- **Purpose:** Absolute minimal guide
- **Contains:** Just the two commands you need
- **Best for:** First-time users who want to start immediately

### 2. **QUICK_START_GUIDE.md** 📘
- **Level:** Intermediate
- **Length:** 10 minutes
- **Purpose:** Comprehensive step-by-step guide
- **Contains:**
  - Detailed prerequisites
  - Step-by-step instructions (Option A & B)
  - What each experiment does
  - Expected results
  - Troubleshooting solutions
  - Time estimates and planning
- **Best for:** Understanding what's happening, solving problems

### 3. **COMMAND_REFERENCE.md** 💻
- **Level:** All levels
- **Length:** 1 minute (quick lookup)
- **Purpose:** Copy-paste command reference
- **Contains:**
  - Main experiment commands
  - Individual experiment commands
  - Advanced options
  - Debugging commands
  - Cleanup commands
  - Common workflows
- **Best for:** Quick reference when you need a specific command

### 4. **EXPERIMENT_FLOW_DIAGRAM.md** 📊
- **Level:** All levels
- **Length:** 5 minutes
- **Purpose:** Visual explanation
- **Contains:**
  - Flow diagrams
  - Timeline visualization
  - Data flow diagrams
  - File structure diagrams
  - Expected output previews
- **Best for:** Understanding the big picture and what happens when

### 5. **EXPERIMENT_RUNNER_GUIDE.md** 📗 (Existing)
- **Level:** Intermediate to Advanced
- **Length:** 15 minutes
- **Purpose:** Detailed experiment runner documentation
- **Contains:**
  - Prerequisites
  - Quick start options
  - What each experiment does
  - Advanced options
  - Troubleshooting
  - Expected results
- **Best for:** Deep understanding of the experiment runner

### 6. **EXPERIMENT_GUIDE.md** 📕 (Existing)
- **Level:** Advanced
- **Length:** 20 minutes
- **Purpose:** Complete experimentation guide
- **Contains:**
  - Experiment architecture
  - Server setup
  - Android device setup
  - Hybrid experiments
  - Data collection strategy
- **Best for:** Understanding the complete system architecture

### 7. **BEGINNER_GUIDE_TO_THESIS.md** 🎓 (Existing)
- **Level:** Beginner
- **Length:** 10 minutes
- **Purpose:** Explains concepts and what results mean
- **Contains:**
  - What you've accomplished
  - What is federated learning
  - How to analyze results
  - What each metric means
- **Best for:** Understanding concepts if you're new to ML/FL

---

## 🎯 Choose Your Path

### Path 1: "I Want to Run Everything NOW!"
1. Read **START_HERE.md** (2 min)
2. Run the two commands
3. Wait 4-8 hours
4. Done! ✅

### Path 2: "I Want to Understand First"
1. Read **QUICK_START_GUIDE.md** (10 min)
2. Read **EXPERIMENT_FLOW_DIAGRAM.md** (5 min)
3. Run the experiments
4. Refer to **COMMAND_REFERENCE.md** as needed

### Path 3: "I Want Deep Understanding"
1. Read **BEGINNER_GUIDE_TO_THESIS.md** (10 min)
2. Read **EXPERIMENT_GUIDE.md** (20 min)
3. Read **EXPERIMENT_RUNNER_GUIDE.md** (15 min)
4. Read **EXPERIMENT_FLOW_DIAGRAM.md** (5 min)
5. Run the experiments
6. Keep **COMMAND_REFERENCE.md** handy

### Path 4: "Something's Not Working!"
1. Check error message in terminal
2. Look up solution in **QUICK_START_GUIDE.md** → Troubleshooting section
3. Check **COMMAND_REFERENCE.md** → Debugging commands
4. Review **EXPERIMENT_RUNNER_GUIDE.md** → Troubleshooting section

---

## 🔧 Key Files You'll Use

### Scripts to Run:
- `server.py` - Starts the federated learning server
- `run_all_experiments.py` - Runs all experiments automatically
- `centralized_baseline.py` - Baseline experiment (standalone)
- `dp_sweep_experiment.py` - Privacy budget sweep (requires server)
- `heterogeneity_sweep_experiment.py` - Heterogeneity sweep (requires server)
- `comprehensive_analysis.py` - Generates figures and tables

### Data Files:
- `ratings.csv` - MovieLens 100K dataset (required)
- `requirements.txt` - Python dependencies

### Output Folders:
- `results/` - JSON files with experiment metrics
- `figures/` - PNG images and CSV tables for thesis

---

## ✅ Pre-Flight Checklist

Before running experiments, verify:
- [ ] `ratings.csv` exists in project folder
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] All key scripts exist (see list above)
- [ ] ~1 GB free disk space
- [ ] ~8 GB RAM available
- [ ] 4-8 hours available for experiments to run

---

## 🚀 The Two Commands (Most Important!)

```powershell
# Terminal 1: Start server (leave running)
python server.py

# Terminal 2: Run all experiments
python run_all_experiments.py
```

That's it! Everything else is optional reading.

---

## 📊 What You'll Get

After running experiments:

### Figures (for thesis):
- `figures/accuracy_vs_epsilon.png` - Privacy-accuracy trade-off (RQ1)
- `figures/accuracy_loss_vs_epsilon.png` - % accuracy loss
- `figures/accuracy_vs_alpha.png` - Heterogeneity impact (RQ3)

### Data Table:
- `figures/summary_table.csv` - All metrics in one table

### Raw Results:
- `results/*.json` - 24 JSON files with detailed metrics

---

## ⏱️ Time Estimates

| Experiment | Time | Seeds | Total Runs |
|------------|------|-------|------------|
| Centralized Baseline | 10 min | 1 | 1 |
| DP Sweep | 2-4 hours | 3 | 15 |
| Heterogeneity Sweep | 1-2 hours | 3 | 9 |
| Analysis | 1 min | - | 1 |
| **Total** | **4-8 hours** | - | **26** |

---

## 🎯 Success Indicators

You'll know experiments completed successfully when:
- ✅ Terminal 2 shows: "🎉 All experiments completed successfully!"
- ✅ `results/` folder contains 24 JSON files
- ✅ `figures/` folder contains 3 PNG files + 1 CSV
- ✅ No error messages in terminals
- ✅ Figures show expected trends (accuracy decreases with stronger privacy)

---

## 🆘 Common Issues

| Issue | Quick Fix |
|-------|-----------|
| Server won't start | Check if port 8000 is in use: `netstat -ano \| findstr :8000` |
| Out of memory | Reduce `num_clients` in experiment scripts to 50 |
| Taking forever | Reduce `SEEDS` to just `[42]` in experiment scripts |
| Missing ratings.csv | Download from: https://grouplens.org/datasets/movielens/100k/ |

Full troubleshooting in **QUICK_START_GUIDE.md**.

---

## 📚 Additional Resources (Existing)

These files already existed in your project:

- `DATA_COLLECTION_GUIDE.md` - How data collection works
- `INTERPRET_YOUR_RESULTS.md` - How to interpret your results
- `EXPERIMENT_STATUS.md` - Status of experiment implementation
- `EXPERIMENTS_COMPLETE.md` - Summary of completed experiments
- `ANDROID_QUICK_START.md` - Mobile device setup guide
- `ANDROID_RESULTS_SUMMARY.md` - Mobile experiment results

---

## 💡 Pro Tips

1. **Start simple** - Just read START_HERE.md and run the commands
2. **Run overnight** - Experiments take 4-8 hours, perfect for overnight
3. **Don't close terminals** - Keep both running until complete
4. **Backup results** - Copy `results/` and `figures/` folders when done
5. **Verify figures** - Make sure plots show reasonable trends
6. **Keep references handy** - Bookmark COMMAND_REFERENCE.md

---

## 🎓 Next Steps After Experiments

1. **Verify completion**
   ```powershell
   ls results\*.json | Measure-Object  # Should show 24 files
   ls figures\*.png                     # Should show 3 files
   ```

2. **Review results**
   ```powershell
   explorer figures\                    # Open figures folder
   cat figures\summary_table.csv        # View summary table
   ```

3. **Use in thesis**
   - Insert figures into Results section
   - Copy metrics from summary table
   - Discuss trends and findings
   - Compare with baseline

---

## 📞 Need Help?

1. **Check terminal output** - Error messages tell you what's wrong
2. **Read troubleshooting** - Check QUICK_START_GUIDE.md
3. **Review commands** - Check COMMAND_REFERENCE.md
4. **Understand flow** - Read EXPERIMENT_FLOW_DIAGRAM.md
5. **Deep dive** - Read EXPERIMENT_RUNNER_GUIDE.md

---

## 🎉 You're All Set!

Everything you need is documented. Just:
1. Choose your path (above)
2. Read the relevant guide(s)
3. Run the two commands
4. Get your thesis results!

**Good luck! 🍀**

---

**Last Updated:** March 10, 2026  
**Documentation Status:** Complete ✅  
**Ready to Run:** Yes ✅

---

## 📋 Quick Reference Table

| What do you want? | Which file to read? |
|-------------------|---------------------|
| Run experiments NOW | START_HERE.md |
| Understand what's happening | QUICK_START_GUIDE.md |
| Look up a command | COMMAND_REFERENCE.md |
| See visual flow | EXPERIMENT_FLOW_DIAGRAM.md |
| Advanced options | EXPERIMENT_RUNNER_GUIDE.md |
| System architecture | EXPERIMENT_GUIDE.md |
| Understand concepts | BEGINNER_GUIDE_TO_THESIS.md |
| Fix a problem | QUICK_START_GUIDE.md → Troubleshooting |
| Interpret results | INTERPRET_YOUR_RESULTS.md |

---

**🎯 Bottom Line:** Read START_HERE.md, run two commands, get thesis results!

