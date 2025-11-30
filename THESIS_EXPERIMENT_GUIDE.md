# 📊 Thesis Experiment Guide

## 🎯 Experiment Requirements

Your professor requires:
- **2 physical Android devices/emulators** (minimum)
- **50 simulated Python clients** (minimum)
- **10 training rounds** (minimum)
- **Total: 52 clients** participating in federated learning

---

## 📋 Experiment Setup

### Current Configuration in `run_experiment.py`:

```python
num_clients = 50        # Simulated Python clients
num_rounds = 10         # Training rounds
alpha = 0.5            # Data heterogeneity (non-IID)
embedding_dim = 16     # Model embedding dimension
```

**Total Clients**: 50 (simulated) + 2 (Android) = **52 clients**

---

## 🚀 How to Run Experiments

### Step 1: Start the Server

```powershell
python server.py
```

Keep this running in a terminal. The server will:
- Accept connections from all clients
- Aggregate parameters from all 52 clients
- Track participation per round

### Step 2: Initialize Server Model

```powershell
python init_server_model.py
```

This initializes the model with correct dimensions (50 users, 4032 items).

### Step 3: Run Simulated Clients (50 clients)

In a **new terminal**:

```powershell
python run_experiment.py
```

This will:
- Create 50 simulated Python clients
- Split training data non-IID across them
- Run 10 training rounds
- Each client trains locally and uploads parameters
- Server aggregates all parameters

**Expected output:**
```
=== Round 1/10 ===
Training 50 simulated clients...
  Client 0: loss=0.1234, samples=250
  Client 1: loss=0.1456, samples=180
  ...
  Client 49: loss=0.1321, samples=220
Completed: 50/50 simulated clients trained
Note: Android devices should also participate in this round

Waiting 5 seconds for Android devices to complete training...
Aggregating parameters from all clients (simulated + Android)...
  Total clients aggregated: 52
  Total samples: 12500
```

### Step 4: Connect Android Devices (2 devices)

**On each Android device/emulator:**

1. Open the Flutter app
2. Enter server IP address (your PC's IP)
3. Click "Connect to Server"
4. Click "Run Training Round" **10 times** (one per round)

**Important**: 
- Run training rounds **synchronously** with the Python script
- When Python script shows "Waiting 5 seconds for Android devices", that's your window to run a round on Android
- Or run Android rounds **before** starting the Python script, then Python will aggregate everything

---

## 📊 Data Collection

### Python Results (50 clients)
- Saved to: `results/experiment_id.json`
- Contains: All 50 simulated client metrics, per-round results, final evaluation

### Android Results (2 devices)
- Saved to: `mobile_results/experiment_id.json` (automatically uploaded to PC)
- Contains: Device-specific metrics, resource usage, training times

### Combined Analysis
Both use the same format, so you can:
- Load all JSON files together
- Compare simulated vs real device performance
- Analyze resource consumption on mobile
- Generate combined plots and tables

---

## ⏱️ Timing Strategy

### Option 1: Sequential (Recommended)
1. Start server
2. Initialize model
3. **Run Android rounds first** (2 devices × 10 rounds)
4. **Then run Python script** (50 clients × 10 rounds)
5. Python script will aggregate everything together

### Option 2: Synchronized
1. Start server
2. Initialize model
3. **Start Python script** (runs 50 clients)
4. **During each round**, when Python shows "Waiting 5 seconds", run Android round
5. Python aggregates all 52 clients together

### Option 3: Parallel (Advanced)
1. Start server
2. Initialize model
3. **Run Python script** in one terminal
4. **Run Android rounds** simultaneously (they'll queue on server)
5. After all clients finish, manually trigger aggregation:
   ```powershell
   curl -X POST http://localhost:8000/aggregate
   ```

---

## 📈 Expected Results

### Per Round:
- **52 clients** participate (50 simulated + 2 Android)
- **~12,500 total samples** (depends on data split)
- **Aggregated model** improves over rounds
- **Metrics tracked**: NDCG@10, Hit@10, Precision, Recall, MSE, MAE, Accuracy

### Final Results:
- **10 rounds** of training
- **Final model evaluation** on test set
- **Comprehensive metrics** for thesis analysis
- **Resource metrics** from Android devices (battery, CPU, memory)

---

## 📁 Output Files

### Python Script Output:
```
results/
└── dp_inf_alpha_0.5_dim_16_clients_50_seed_42.json
└── dp_inf_alpha_0.5_dim_16_clients_50_seed_42_summary.csv
```

### Android Device Output:
```
mobile_results/
├── dp_inf_alpha_null_dim_16_clients_1_device_XXX_t1234567890.json
├── dp_inf_alpha_null_dim_16_clients_1_device_XXX_t1234567890_summary.csv
├── dp_inf_alpha_null_dim_16_clients_1_device_YYY_t1234567891.json
└── dp_inf_alpha_null_dim_16_clients_1_device_YYY_t1234567891_summary.csv
```

---

## ✅ Verification Checklist

Before starting experiments:

- [ ] Server is running (`python server.py`)
- [ ] Model is initialized (`python init_server_model.py`)
- [ ] `ratings.csv` exists in project directory
- [ ] 2 Android devices/emulators ready
- [ ] Android apps can connect to server
- [ ] Network connectivity verified

During experiments:

- [ ] Python script shows 50 clients training
- [ ] Android devices show successful training
- [ ] Server logs show all clients registering
- [ ] Aggregation shows 52 total clients
- [ ] Results files are being created

After experiments:

- [ ] Check `results/` folder for Python results
- [ ] Check `mobile_results/` folder for Android results
- [ ] Verify 10 rounds completed
- [ ] Verify final metrics are recorded
- [ ] All JSON and CSV files present

---

## 🔬 For Thesis Analysis

### Minimum Data Collected:
- ✅ 50 simulated clients
- ✅ 2 Android devices
- ✅ 10 training rounds
- ✅ Per-round metrics
- ✅ Final evaluation metrics
- ✅ Resource consumption (Android)

### Analysis You Can Do:
1. **Convergence**: How model improves over 10 rounds
2. **Scalability**: Performance with 52 clients
3. **Mobile vs Simulated**: Compare Android vs Python client metrics
4. **Resource Efficiency**: Battery, CPU, memory usage on mobile
5. **Non-IID Effects**: Impact of α=0.5 on performance
6. **Aggregation Quality**: How well FedAvg works with mixed clients

---

## 🆘 Troubleshooting

### "Not enough clients aggregated"
- Make sure Android devices are running rounds
- Check server logs for client registrations
- Verify all 50 Python clients completed training

### "Server timeout"
- Increase timeout in `run_experiment.py` (line 212)
- Check network connectivity
- Reduce number of clients if needed (but minimum is 50)

### "Android devices not connecting"
- Verify server IP address
- Check server is running
- Verify network security config on Android

### "Results missing"
- Check `results/` folder for Python results
- Check `mobile_results/` folder for Android results
- Verify server received uploads (check server logs)

---

## 📝 Notes

- **Minimum requirements**: 50 simulated + 2 Android = 52 clients, 10 rounds
- **Data format**: All results use same JSON structure for easy combination
- **Resource metrics**: Only Android devices provide battery/CPU/memory data
- **Synchronization**: Android and Python clients can run independently; server aggregates all

---

Good luck with your thesis experiments! 🎓

