# 📝 Command Reference - Quick Copy-Paste Guide

## 🚀 Main Commands (What You Need)

### Run All Experiments (Simplest)
```powershell
# Terminal 1: Start server
python server.py

# Terminal 2: Run everything
python run_all_experiments.py
```

---

## 🔧 Individual Experiment Commands

### 1. Centralized Baseline Only
```powershell
python centralized_baseline.py
```
⏱️ Time: ~10 minutes | 💾 Output: `results/centralized_baseline.json`

### 2. DP Sweep Only (needs server)
```powershell
# Terminal 1:
python server.py

# Terminal 2:
python dp_sweep_experiment.py
```
⏱️ Time: ~2-4 hours | 💾 Output: Multiple JSON files in `results/`

### 3. Heterogeneity Sweep Only (needs server)
```powershell
# Terminal 1:
python server.py

# Terminal 2:
python heterogeneity_sweep_experiment.py
```
⏱️ Time: ~1-2 hours | 💾 Output: Multiple JSON files in `results/`

### 4. Generate Figures Only
```powershell
python comprehensive_analysis.py
```
⏱️ Time: ~1 minute | 💾 Output: Figures in `figures/` folder

---

## 🎯 Advanced Commands

### Skip Certain Steps
```powershell
# Skip baseline (if already run)
python run_all_experiments.py --skip-baseline

# Skip DP sweep
python run_all_experiments.py --skip-dp

# Skip heterogeneity sweep
python run_all_experiments.py --skip-heterogeneity

# Skip analysis
python run_all_experiments.py --skip-analysis
```

### Check Server Status
```powershell
# Check if server is running
python run_all_experiments.py --server-check
```

### Combine Skip Options
```powershell
# Only run analysis (skip all experiments)
python run_all_experiments.py --skip-baseline --skip-dp --skip-heterogeneity

# Only run DP sweep (skip rest)
python run_all_experiments.py --skip-baseline --skip-heterogeneity --skip-analysis
```

---

## 📊 Analysis & Viewing Results

### View Summary Statistics
```powershell
python analyze_results.py
```

### Compare Results
```powershell
python compare_results.py
```

### Generate All Figures
```powershell
python comprehensive_analysis.py
```

### View Results in Explorer
```powershell
# Open results folder
explorer results\

# Open figures folder
explorer figures\
```

### Check What Files Were Created
```powershell
# List all result files
ls results\*.json

# List all figures
ls figures\*.png

# View summary table
cat figures\summary_table.csv
```

---

## 🔍 Debugging & Troubleshooting Commands

### Check Dataset Exists
```powershell
ls ratings.csv
```

### Verify Dependencies
```powershell
pip install -r requirements.txt
```

### Check Server Health
```powershell
# Using curl (if installed)
curl http://localhost:8000/healthz

# Using PowerShell
Invoke-WebRequest -Uri http://localhost:8000/healthz
```

### Check Python Version
```powershell
python --version
```

### Check Available Memory
```powershell
# Check system memory
systeminfo | findstr /C:"Available Physical Memory"
```

### View Server Logs (if server crashes)
```powershell
# Run server with verbose output
python server.py --log-level debug
```

### Kill Server Process (if stuck)
```powershell
# Find Python processes
Get-Process python

# Kill by port (if server won't stop)
netstat -ano | findstr :8000
# Note the PID, then:
taskkill /PID <PID> /F
```

---

## 📱 Mobile/Android Commands (If Testing Mobile)

### Build Flutter App
```powershell
cd federated_learning_in_mobile
flutter build apk
```

### Install on Device
```powershell
flutter install
```

### Run on Device/Emulator
```powershell
flutter run
```

### Check Connected Devices
```powershell
flutter devices
```

---

## 🧹 Cleanup Commands

### Remove All Results (Start Fresh)
```powershell
# Remove result files
Remove-Item results\*.json

# Remove figures
Remove-Item figures\*.png
Remove-Item figures\*.csv
```

### Remove Cache Files
```powershell
# Remove Python cache
Remove-Item -Recurse __pycache__
Remove-Item -Recurse .pytest_cache
```

---

## 📦 Installation Commands

### First-Time Setup
```powershell
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import torch; import pandas; import numpy; print('All packages installed!')"
```

### Update Dependencies
```powershell
pip install --upgrade -r requirements.txt
```

---

## 💾 Backup Commands

### Backup Results
```powershell
# Create backup folder
mkdir backup_$(Get-Date -Format "yyyy-MM-dd")

# Copy results
Copy-Item results\* backup_$(Get-Date -Format "yyyy-MM-dd")\

# Copy figures
Copy-Item figures\* backup_$(Get-Date -Format "yyyy-MM-dd")\
```

### Compress Results for Sharing
```powershell
# Create zip file
Compress-Archive -Path results,figures -DestinationPath thesis_results.zip
```

---

## 🎓 Quick Copy-Paste Workflows

### Complete Fresh Run
```powershell
# 1. Clean previous results (optional)
Remove-Item results\*.json -ErrorAction SilentlyContinue
Remove-Item figures\*.png -ErrorAction SilentlyContinue

# 2. Start server (Terminal 1)
python server.py

# 3. Run all experiments (Terminal 2)
python run_all_experiments.py

# 4. View results when done
explorer figures\
```

### Re-generate Figures Only
```powershell
# If experiments are done but you want new figures
python comprehensive_analysis.py
explorer figures\
```

### Quick Test (Fast Version)
```powershell
# Run just baseline + analysis
python centralized_baseline.py
python comprehensive_analysis.py
```

---

## 🆘 Emergency Commands

### If Everything is Broken
```powershell
# 1. Kill all Python processes
Get-Process python | Stop-Process -Force

# 2. Clear cache
Remove-Item -Recurse __pycache__ -ErrorAction SilentlyContinue

# 3. Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# 4. Try again
python server.py
```

### If Server Won't Start
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# If something is using it, kill that process
taskkill /PID <PID> /F

# Then restart
python server.py
```

### If Out of Disk Space
```powershell
# Check disk space
Get-PSDrive C

# Remove old results
Remove-Item results\*.json
```

---

## 📋 Verification Checklist Commands

### Before Running Experiments
```powershell
# ✓ Dataset exists
ls ratings.csv

# ✓ Dependencies installed
pip list | findstr torch

# ✓ Scripts exist
ls *.py

# ✓ Enough disk space (need ~1GB free)
Get-PSDrive C
```

### After Running Experiments
```powershell
# ✓ Results created
ls results\*.json | Measure-Object

# ✓ Figures created
ls figures\*.png | Measure-Object

# ✓ Summary table exists
cat figures\summary_table.csv
```

---

## 🎯 Most Common Workflows

### First Time Running Everything
```powershell
pip install -r requirements.txt
python server.py  # Terminal 1
python run_all_experiments.py  # Terminal 2
```

### Re-running After Code Changes
```powershell
python server.py  # Terminal 1
python run_all_experiments.py --skip-baseline  # Terminal 2 (skip baseline if unchanged)
```

### Just Want the Figures
```powershell
python comprehensive_analysis.py
explorer figures\
```

---

**💡 Tip:** Bookmark this file for quick reference during your experiments!

