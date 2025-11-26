# 🔧 Quick Fix: Connection Error

## The Problem

Error: `Connection refused` when trying to connect from mobile app.

**Root Cause**: You're using `localhost:8000`, which doesn't work on mobile devices.

## ✅ The Solution

Use your **PC's IP address** instead of `localhost`.

### Your PC's IP Address: `192.168.29.146`

## Steps to Fix

### 1. Update Server URL in Mobile App

In the mobile app, change:
- ❌ **Wrong**: `http://localhost:8000`
- ✅ **Correct**: `http://192.168.29.146:8000`

### 2. Verify Server is Running

Check Terminal where you ran `python server.py` - you should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Ensure Both Devices on Same WiFi

- ✅ PC and Android device must be on the **same WiFi network**
- ❌ Mobile data won't work

### 4. Check Windows Firewall (if still having issues)

If connection still fails, allow port 8000 in Windows Firewall:

**PowerShell (Run as Administrator):**
```powershell
New-NetFirewallRule -DisplayName "Federated Learning Server" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

Or manually:
1. Open Windows Defender Firewall
2. Advanced Settings
3. Inbound Rules → New Rule
4. Port → TCP → Port 8000
5. Allow Connection

## Test Connection

### From Mobile Browser (Quick Test)

1. Open browser on your Android device
2. Go to: `http://192.168.29.146:8000/healthz`
3. Should see: `{"status":"healthy","round":0}`

If this works, the app will work too!

### From Mobile App

1. Server URL: `http://192.168.29.146:8000`
2. Client ID: `android_device_1` (or any unique name)
3. Click "Connect to Server"
4. Should see "Connected" status ✅

## Troubleshooting

### Still Getting Connection Refused?

1. **Check Server is Running**
   ```bash
   # On PC, test server locally
   curl http://localhost:8000/healthz
   ```

2. **Verify IP Address**
   ```bash
   # On PC, get current IP
   ipconfig | findstr IPv4
   ```
   Make sure it matches what you're using in the app!

3. **Check Same Network**
   - PC WiFi: Check network name
   - Android WiFi: Must be same network name

4. **Test from Device Browser**
   - If browser can't reach `http://192.168.29.146:8000/healthz`, the app won't either
   - This helps isolate if it's a network/firewall issue

### Alternative: Use ngrok

If local network doesn't work, use ngrok:

1. **Install ngrok**: https://ngrok.com/download
2. **Run tunnel**:
   ```bash
   ngrok http 8000
   ```
3. **Use ngrok URL** in app (e.g., `https://abc123.ngrok.io`)

## Quick Checklist

- [ ] Server running (`python server.py`)
- [ ] Using PC IP (`192.168.29.146:8000`) NOT localhost
- [ ] Both devices on same WiFi
- [ ] Firewall allows port 8000
- [ ] Can access `http://192.168.29.146:8000/healthz` from device browser

## Updated App Features

The app has been updated to:
- ✅ Warn you if you use `localhost`
- ✅ Show helpful hints about finding your IP
- ✅ Better error messages

---

**Your Server URL should be**: `http://192.168.29.146:8000`

Try connecting again with this URL! 🚀

