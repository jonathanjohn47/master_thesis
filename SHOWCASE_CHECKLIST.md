# 🚀 SHOWCASE CHECKLIST - DO THESE STEPS NOW

## Before Showcase Starts

### ✓ Terminal 1: Verify Server is Running
```powershell
cd C:\Users\jonat\OneDrive\Documents\GitHub\master_thesis
python server.py
```
**Expected Output:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```
**ACTION**: Keep this terminal open during entire showcase!

---

### ✓ Terminal 2: Initialize Model (Run Once)
```powershell
cd C:\Users\jonat\OneDrive\Documents\GitHub\master_thesis
python init_server_model.py
```
**Expected Output:**
```
[OK] Model initialized successfully!
Response: {'status': 'initialized', ...}
```

---

### ✓ Mobile App: Prepare Flutter
```powershell
cd C:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\federated_learning_in_mobile
flutter clean
flutter pub get
flutter run
```
**Wait for**: App to appear in emulator (2-3 minutes)

---

## During Showcase

### Step 1: Show Server Running
**In Terminal 1 (server terminal)**
1. Point to the logs
2. Highlight: `Application startup complete`
3. Show: Port 8080 is listening
4. Explain: "Backend server is ready for mobile clients"

---

### Step 2: Configure Mobile App
**In Android Emulator**
1. Show the app main screen
2. Point to "Server URL" input field
3. Enter: `http://192.168.29.147:8080`
   - (Your IP is: 192.168.29.147)
4. Keep Client ID as auto-generated
5. Tap "Connect to Server" button
6. **Wait**: Should show "Connected" status

---

### Step 3: Start Training
**In Android Emulator**
1. Once "Connected" appears
2. Tap "Start Training" button
3. **Watch**:
   - Progress bar fills
   - Loss value decreases each epoch
   - Metrics update in real-time
   - Training round completes (1-3 min)

---

### Step 4: Verify Results Collected
**After training round:**
1. Open file explorer: `C:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\mobile_results\`
2. **Look for**:
   - `.json` file (full results)
   - `.csv` file (summary table)
3. Show timestamps match current time
4. Point out: "Results automatically synced to PC"

---

### Step 5: Analyze Results (Optional)
**In Terminal 3:**
```powershell
cd C:\Users\jonat\OneDrive\Documents\GitHub\master_thesis
python analyze_mobile_results.py
```
**Shows**: Summary of mobile experiments

---

## Your IP Address (For Reference)
```
192.168.29.147
```

## Server Port
```
8080
```

## Mobile App URL to Use
```
http://192.168.29.147:8080
```

---

## Timing Guide

| Step | Duration | What Happens |
|------|----------|--------------|
| Setup | 2-3 min | Server starts, model initializes, app launches |
| Connection | 30 sec | App connects to server |
| First Training | 1-3 min | Live loss curve shows convergence |
| Results Check | 1 min | Verify files in mobile_results/ folder |
| Analysis | 1-2 min | Show reproducibility |
| **Total** | **~8-10 min** | Complete demonstration |

---

## If Something Goes Wrong

### Server Won't Start
```powershell
# Kill any process on port 8080
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue | 
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

# Try again
python server.py
```

### App Won't Connect
1. **Check IP**: Run `ipconfig` in new terminal
2. **Verify IP**: Should be `192.168.29.147`
3. **In app**: Make sure URL is `http://192.168.29.147:8080`
4. **Network**: Both PC and emulator on same Wi-Fi

### Training Too Slow
- This is **normal for emulator** (it's slower than real device)
- Each round takes 1-3 minutes
- Real Android device would be 2-3x faster

### Results Not Appearing
1. Check folder exists: `mobile_results/`
2. Check server logs: Look for "Saved mobile results"
3. Wait longer: Sometimes takes a few seconds to upload

---

## Pro Tips

1. **Take a Screenshot**
   - Screenshot of loss curve during training
   - Perfect for thesis/presentation

2. **Show Logs**
   - Point to server logs showing "Received results from device"
   - Demonstrates real-time sync

3. **Explain Privacy**
   - Emphasize: Only model updates sent, not raw data
   - This is the key benefit of federated learning

4. **Highlight Metrics**
   - Point to low CPU/memory usage
   - Show it's practical for real phones

---

## You're All Set! 🎉

Everything is configured and ready:
- ✅ Server on port 8080
- ✅ Your IP: 192.168.29.147
- ✅ Mobile app configured
- ✅ Model initialized
- ✅ Results auto-collecting

Just run the steps above and follow the showcase flow!

