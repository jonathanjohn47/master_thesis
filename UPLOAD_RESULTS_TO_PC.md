# 📤 Upload Results to PC - Quick Guide

## ✅ What Changed

Your Android app now **automatically saves results directly to your PC** instead of only storing them on the emulator/device. No more searching through emulator files!

---

## 🚀 How It Works

### Automatic Upload (Default)
Results are **automatically uploaded to your PC** after each training round:
- ✅ After Round 1 → Uploaded to PC
- ✅ After Round 2 → Uploaded to PC
- ✅ After Round 10 → Uploaded to PC + Success dialog shown

### Manual Upload
You can also manually upload results anytime:
1. Click the **"Upload to PC"** button
2. Wait for confirmation
3. Results are saved to your PC

---

## 📁 Where Results Are Saved on Your PC

**Location:** `mobile_results/` folder in your project directory

**Files created:**
- `{experiment_id}.json` - Full experiment data (JSON format)
- `{experiment_id}_summary.csv` - Summary table (CSV format)

**Example:**
```
C:\Users\jonat\PycharmProjects\master_thesis\
  └── mobile_results\
      ├── android_device_1_20250101_120000.json
      ├── android_device_1_20250101_120000_summary.csv
      ├── android_device_2_20250101_120500.json
      └── android_device_2_20250101_120500_summary.csv
```

---

## 📋 Step-by-Step Instructions

### Step 1: Start Server on Your PC
```powershell
python server.py
```
Keep this running!

### Step 2: Initialize Model
```powershell
python init_server_model.py
```

### Step 3: Run Training on Android Device
1. Open Flutter app on Android emulator/device
2. Enter server URL (your PC's IP: `http://192.168.x.x:8000`)
3. Click **"Connect to Server"**
4. Click **"Run Training Round"** (10 times for 10 rounds)
5. After each round, check the logs - you'll see:
   ```
   ✓ Results uploaded successfully!
     Saved on PC: Results saved to mobile_results
     JSON: mobile_results/android_device_1_20250101_120000.json
     CSV: mobile_results/android_device_1_20250101_120000_summary.csv
   ```

### Step 4: Check Results on Your PC
```powershell
# View all mobile results
dir mobile_results\*.json

# View summary CSV
dir mobile_results\*_summary.csv
```

### Step 5: Analyze Results
```powershell
# Analyze combined Python + Android results
python analyze_combined_results.py
```

---

## 🔍 Verify Upload Success

### In Android App:
- Check the logs in the app - you'll see "✓ Results uploaded successfully!"
- The status will show "Results uploaded to PC"
- After 10 rounds, a success dialog appears showing file paths

### On Your PC:
1. **Check terminal/console** where `server.py` is running:
   ```
   INFO: Saved mobile results: mobile_results\android_device_1_20250101_120000.json
   INFO: Saved CSV summary: mobile_results\android_device_1_20250101_120000_summary.csv
   ```

2. **Check the folder:**
   ```powershell
   cd mobile_results
   dir
   ```

3. **Open a file to verify:**
   ```powershell
   notepad android_device_1_20250101_120000.json
   ```

---

## 🛠️ Troubleshooting

### "Upload failed: Connection refused"
**Problem:** Cannot connect to server

**Solution:**
1. ✅ Make sure `server.py` is running on your PC
2. ✅ Check server URL is correct (use your PC's IP, not localhost)
3. ✅ Verify both devices are on the same Wi-Fi network
4. ✅ Check Windows Firewall isn't blocking port 8000

### "Upload failed: 404 Not Found"
**Problem:** Server endpoint not found

**Solution:**
1. ✅ Make sure you're using the latest `server.py` with `/upload-mobile-results` endpoint
2. ✅ Restart the server if you just updated it

### "No results to upload"
**Problem:** No training rounds completed yet

**Solution:**
1. ✅ Run at least one training round first
2. ✅ Check that `_metricsCollector` is initialized

### Results not appearing on PC
**Problem:** Files aren't showing up in `mobile_results/` folder

**Solution:**
1. ✅ Check server terminal for error messages
2. ✅ Verify folder permissions (should create automatically)
3. ✅ Check if files were saved with a different name
4. ✅ Use "Upload to PC" button to manually retry upload

---

## 💡 Tips

1. **After Each Round:**
   - Results are automatically uploaded
   - You can see the upload status in app logs
   - No manual action needed!

2. **After All 10 Rounds:**
   - A success dialog appears automatically
   - Shows exact file paths on your PC
   - You can immediately access the files

3. **Multiple Devices:**
   - Each device gets a unique experiment ID
   - Files are saved with different names
   - Easy to distinguish Device 1 vs Device 2 results

4. **Combine Results:**
   - Once both devices finish, run `analyze_combined_results.py`
   - This compares Python + Android results
   - Generates comparison plots

---

## 📊 File Format

### JSON File Structure:
```json
{
  "experiment_id": "android_device_1_20250101_120000",
  "config": {
    "client_id": "android_client_1234",
    "num_users": 50,
    "num_items": 4032,
    "embedding_dim": 16
  },
  "rounds": [
    {
      "round": 1,
      "train_loss": 0.5234,
      "test_metrics": {
        "accuracy": 0.75,
        "Hit@10": 0.32
      },
      "resource_metrics": {
        "training_time_ms": 1234,
        "battery_drain": 0.5
      }
    },
    ...
  ],
  "final_metrics": { ... }
}
```

### CSV File Structure:
| Round | Train_Loss | NDCG@10 | Hit@10 | Precision@10 | Recall@10 | MSE | MAE | Accuracy | Num_Clients | Total_Samples | Training_Time_MS | Battery_Drain |
|-------|------------|---------|--------|--------------|-----------|-----|-----|----------|-------------|---------------|------------------|---------------|
| 1     | 0.5234     | ...     | ...    | ...          | ...       | ... | ... | 0.75     | 1          | 10            | 1234             | 0.5           |

---

## ✅ Success Checklist

After running experiments, verify:

- [ ] Server is running (`python server.py`)
- [ ] At least 10 training rounds completed
- [ ] App logs show "✓ Results uploaded successfully!"
- [ ] Files exist in `mobile_results/` folder on PC
- [ ] Can open and read JSON files
- [ ] CSV summary files are readable
- [ ] Both devices have uploaded their results
- [ ] Ready to run `analyze_combined_results.py`

---

## 🎯 Next Steps

Once results are on your PC:

1. **Verify all results:**
   ```powershell
   dir mobile_results\*.json
   ```

2. **Run combined analysis:**
   ```powershell
   python analyze_combined_results.py
   ```

3. **Generate thesis figures:**
   - Check `figures/` folder
   - Use plots in your thesis

4. **Start writing results section:**
   - Include convergence plots
   - Discuss mobile vs simulated performance
   - Analyze resource consumption

---

**You're all set! Results are now automatically saved to your PC. No more searching through emulator files! 🎉**

