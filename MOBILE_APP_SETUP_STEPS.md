# Step-by-Step Guide: Running Mobile App and Connecting to Server

## Prerequisites
- Flutter installed and working
- Python server code ready
- Android device connected OR Android emulator running
- Both PC and mobile device on the same Wi-Fi network

---

## PART 1: Start the Python Server (on your PC)

### Step 1.1: Open a terminal/command prompt
- On Windows: Press `Win + R`, type `cmd`, press Enter
- Or use PowerShell

### Step 1.2: Navigate to your project folder
```powershell
cd C:\Users\jonat\PycharmProjects\master_thesis
```

### Step 1.3: Start the server
```powershell
python server.py
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**IMPORTANT:** Keep this terminal window open! The server must keep running.

---

## PART 2: Initialize the Server Model

### Step 2.1: Open a NEW terminal window
- Don't close the server terminal!
- Open a second terminal/PowerShell window

### Step 2.2: Navigate to project folder (same as before)
```powershell
cd C:\Users\jonat\PycharmProjects\master_thesis
```

### Step 2.3: Initialize the model
```powershell
python init_server_model.py
```

**Expected output:**
```
============================================================
Federated Learning Server Model Initialization
============================================================

[OK] Server is running

Initializing model on server at http://localhost:8000...
Parameters: 50 users, 4032 items, embedding_dim=16
[OK] Model initialized successfully!
Response: {'status': 'initialized', 'num_users': 50, 'num_items': 4032, 'embedding_dim': 16}

============================================================
[OK] Ready! You can now connect Android devices or Python clients.
============================================================
```

**IMPORTANT:** If you see errors, make sure the server from Part 1 is still running!

---

## PART 3: Find Your PC's IP Address

### Step 3.1: In a NEW terminal (or same one from Step 2)
```powershell
ipconfig
```

### Step 3.2: Look for "IPv4 Address"
You'll see something like:
```
Wireless LAN adapter Wi-Fi:

   IPv4 Address. . . . . . . . . . : 192.168.29.146
```

**Write down this IP address!** You'll need it for the mobile app.

**Common IP addresses:**
- `192.168.x.x` (most common for home Wi-Fi)
- `10.0.x.x` (some networks)
- `172.16.x.x` (some networks)

---

## PART 4: Set Up Android Device/Emulator

### Option A: Physical Android Device

#### Step 4A.1: Enable USB Debugging
1. On your phone: Go to **Settings** → **About Phone**
2. Tap **Build Number** 7 times (you'll see "You are now a developer")
3. Go back to **Settings** → **Developer Options**
4. Enable **USB Debugging**
5. Connect phone to PC via USB cable

#### Step 4A.2: Verify device is connected
```powershell
adb devices
```

**Expected output:**
```
List of devices attached
ABC123XYZ    device
```

If you see "unauthorized", check your phone and accept the USB debugging prompt.

---

### Option B: Android Emulator

#### Step 4B.1: Start Android Studio
1. Open Android Studio
2. Click **Device Manager** (phone icon in toolbar)
3. Click **Play** button on an emulator (or create a new one)
4. Wait for emulator to boot

#### Step 4B.2: Verify emulator is connected
```powershell
adb devices
```

**Expected output:**
```
List of devices attached
emulator-5554    device
```

---

## PART 5: Run the Flutter App

### Step 5.1: Install dependencies (if not done already)
```powershell
cd C:\Users\jonat\PycharmProjects\master_thesis\federated_learning_in_mobile
flutter pub get
```

**Expected output:**
```
Running "flutter pub get" in federated_learning_in_mobile...
Resolving dependencies...
Got dependencies!
```

### Step 5.2: Check device is available
```powershell
flutter devices
```

**Expected output:**
```
2 connected devices:

sdk gphone64 arm64 (mobile) • emulator-5554 • android-arm64  • Android 13 (API 33)
Windows (desktop)           • windows       • windows-x64    • Microsoft Windows
```

### Step 5.3: Run the app
```powershell
flutter run
```

**What happens:**
- Flutter will build the app (first time takes 2-5 minutes)
- App will install on your device/emulator
- App will launch automatically

**Expected output:**
```
Launching lib\main.dart on sdk gphone64 arm64 in debug mode...
Building APK...
Running Gradle task 'assembleDebug'...
✓ Built build\app\outputs\flutter-apk\app-debug.apk
Installing build\app\outputs\flutter-apk\app.apk...
Flutter run key commands.
r Hot reload.
R Hot restart.
q Quit; Q Quit (force quit).
```

---

## PART 6: Connect App to Server

### Step 6.1: On your mobile app screen

You should see:
- **Server URL** text field (empty)
- **Client ID** text field (has some random ID)
- **Connect to Server** button

### Step 6.2: Enter your server URL

In the **Server URL** field, type:
```
http://YOUR_PC_IP:8000
```

**Replace `YOUR_PC_IP` with the IP address from Step 3!**

**Example:**
```
http://192.168.29.146:8000
```

**IMPORTANT:**
- ✅ Use your PC's IP address (from `ipconfig`)
- ❌ Do NOT use `localhost` or `127.0.0.1`
- ❌ Do NOT use `0.0.0.0`
- ✅ Make sure to include `http://` at the start
- ✅ Make sure to include `:8000` at the end

### Step 6.3: Click "Connect to Server"

**What should happen:**
- Button shows "Training..." (briefly)
- Status changes to "Connected" (green dot)
- Logs show: "Server health check passed"
- Logs show: "Client registered: android_client_XXXXX"

**If connection fails, see Troubleshooting below!**

---

## PART 7: Run Training Round

### Step 7.1: After successful connection

You'll see:
- Status: "Connected" (green)
- **Run Training Round** button (now clickable)

### Step 7.2: Click "Run Training Round"

**What happens:**
- Button shows "Training..." with spinner
- Logs show progress:
  - "Fetching global model..."
  - "Global model fetched. Model: 50 users, 4032 items"
  - "Generating sample data..."
  - "Starting training round..."
  - Training completes

### Step 7.3: Check results

After training completes:
- Status: "Training complete"
- **Training Metrics** card appears with:
  - Loss: X.XXXX
  - Samples: X
  - Training Time: XXX ms
- **Resource Metrics** card shows:
  - Battery Level: XX%
  - Battery Drain: X.X%
- **Logs** show: "Results saved: JSON: ..., CSV: ..."

---

## PART 8: View Results

### Step 8.1: Click "Show Results Location" button

This shows you where files are saved on your device.

### Step 8.2: Copy files to your PC

**If using physical device or emulator:**

```powershell
# Pull all results
adb pull /data/data/com.example.federated_learning_in_mobile/app_flutter/fl_results/ ./mobile_results/

# Or pull specific files
adb pull /data/data/com.example.federated_learning_in_mobile/app_flutter/fl_results/*.json ./mobile_results/
adb pull /data/data/com.example.federated_learning_in_mobile/app_flutter/fl_results/*.csv ./mobile_results/
```

**Check the files:**
```powershell
dir mobile_results
```

You should see `.json` and `.csv` files!

---

## Troubleshooting

### ❌ "Connection refused" error

**Problem:** App can't reach server

**Solutions:**
1. ✅ Check server is running (Part 1)
2. ✅ Check IP address is correct (use `ipconfig`)
3. ✅ Check both devices are on same Wi-Fi
4. ✅ Try disabling Windows Firewall temporarily
5. ✅ Check server shows: `Uvicorn running on http://0.0.0.0:8000`

### ❌ "Invalid server address" error

**Problem:** Wrong URL format

**Solutions:**
1. ✅ Must start with `http://`
2. ✅ Must end with `:8000`
3. ✅ Use IP address, NOT `localhost`
4. ✅ No trailing slash: `http://192.168.x.x:8000` (not `http://192.168.x.x:8000/`)

### ❌ "Model not initialized" error

**Problem:** Server model not set up

**Solutions:**
1. ✅ Run `python init_server_model.py` (Part 2)
2. ✅ Check server terminal shows model initialized
3. ✅ Try again after initialization

### ❌ App won't build/run

**Problem:** Flutter setup issues

**Solutions:**
1. ✅ Run `flutter doctor` to check setup
2. ✅ Run `flutter pub get` to install dependencies
3. ✅ Make sure device is connected: `adb devices`
4. ✅ Try cleaning: `flutter clean` then `flutter run`

### ❌ "Invalid user_id or item_id" error

**Problem:** Model dimensions mismatch

**Solutions:**
1. ✅ Make sure you ran `init_server_model.py` after server started
2. ✅ Server should show: `50 users, 4032 items`
3. ✅ App should fetch model before training (automatic)

### ❌ Can't find results files

**Problem:** Files not saved

**Solutions:**
1. ✅ Check logs show "Results saved: ..."
2. ✅ Make sure you ran at least one training round
3. ✅ Try "Show Results Location" button in app
4. ✅ Check app has storage permissions

---

## Quick Checklist

Before starting:
- [ ] Server is running (`python server.py`)
- [ ] Model is initialized (`python init_server_model.py`)
- [ ] PC IP address noted (from `ipconfig`)
- [ ] Android device/emulator connected
- [ ] Device shows in `adb devices`
- [ ] Flutter dependencies installed (`flutter pub get`)

In the app:
- [ ] Server URL entered: `http://YOUR_IP:8000`
- [ ] "Connect to Server" clicked
- [ ] Status shows "Connected" (green)
- [ ] "Run Training Round" clicked
- [ ] Training completes successfully
- [ ] Results saved message appears

After training:
- [ ] Click "Show Results Location"
- [ ] Copy files using `adb pull`
- [ ] Verify JSON and CSV files exist

---

## Summary

**The flow:**
1. **PC Terminal 1:** `python server.py` (keep running!)
2. **PC Terminal 2:** `python init_server_model.py`
3. **PC:** Note IP address from `ipconfig`
4. **Mobile:** Run `flutter run`
5. **App:** Enter `http://YOUR_IP:8000`
6. **App:** Click "Connect to Server"
7. **App:** Click "Run Training Round"
8. **PC:** Pull results with `adb pull`

That's it! 🎉

