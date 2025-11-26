# Federated Learning Mobile Client

A Flutter-based Android application for participating in federated learning experiments for movie recommendation systems.

## Overview

This mobile client allows Android devices to participate as federated learning clients in a distributed training system. It implements:

- Matrix Factorization model in pure Dart
- Federated learning client logic
- Resource monitoring (battery, CPU, memory)
- Integration with Python FastAPI server

## Features

- ✅ Connect to federated learning server
- ✅ Download global model parameters
- ✅ Train locally on device data
- ✅ Upload model updates to server
- ✅ Resource usage monitoring
- ✅ Real-time training metrics display

## Prerequisites

1. **Flutter SDK** (3.9.2 or higher)
   ```bash
   flutter --version
   ```

2. **Android Studio** or Android SDK for development

3. **Python Server** running (see parent directory `server.py`)
   - Server should be accessible from your device
   - Use ngrok or local network IP for mobile access

## Setup Instructions

### 1. Install Dependencies

```bash
cd federated_learning_in_mobile
flutter pub get
```

### 2. Configure Server URL

1. Find your server's IP address:
   - **For local network**: Use your PC's local IP (e.g., `192.168.1.100:8000`)
   - **For ngrok**: Use the ngrok URL (e.g., `https://abc123.ngrok.io`)

2. Update the server URL in the app when you launch it, or modify the default in `lib/main.dart`:

```dart
text: 'http://YOUR_IP:8000', // Replace with your server address
```

### 3. Build and Run

#### On Android Device:
```bash
# Connect your Android device via USB with USB debugging enabled
flutter devices  # Check if device is detected
flutter run
```

#### On Android Emulator:
```bash
# Start an Android emulator from Android Studio
flutter emulators  # List available emulators
flutter run
```

## Usage

### 1. Start the Python Server

First, start your federated learning server:

```bash
# In the parent directory
python server.py
```

Or use the helper script:
```bash
python start_server.py
```

**Important**: Make sure the server is accessible from your mobile device:
- If using local network: Ensure both devices are on the same WiFi network
- Use your PC's local IP address (not `localhost`)
- Example: `http://192.168.1.100:8000`

### 2. Launch the Mobile App

1. Open the app on your Android device/emulator
2. Enter your server URL (e.g., `http://192.168.1.100:8000`)
3. Enter a unique Client ID (default is auto-generated)
4. Click "Connect to Server"

### 3. Run Training Rounds

Once connected:
1. Click "Run Training Round"
2. The app will:
   - Fetch the global model from server
   - Train locally on sample data
   - Upload updated parameters
   - Display metrics and resource usage

## Architecture

```
lib/
├── main.dart                    # Main UI and app entry point
├── models/
│   └── matrix_factorization.dart  # Matrix Factorization model (pure Dart)
├── services/
│   ├── api_client.dart         # HTTP client for server communication
│   └── fl_client.dart          # Federated learning client logic
└── utils/
    ├── model_encoder.dart      # Model parameter encoding/decoding
    └── resource_monitor.dart   # Resource usage monitoring
```

## Integration with Python Server

The mobile client communicates with the Python FastAPI server using JSON-based parameter transfer:

- **Model Parameters**: Base64-encoded Float32 arrays
- **Endpoints**: `/register`, `/global-params-json`, `/upload-params-json`
- **Wire Format**: Compatible with Python server's portable JSON format

## For Thesis Experiments

### Running Experiments with Multiple Devices

1. **Device 1**: Launch app, connect to server, set Client ID to `android_device_1`
2. **Device 2**: Launch app, connect to server, set Client ID to `android_device_2`
3. **Server**: Initialize model and run aggregation rounds

### Data Collection

The app collects and displays:
- Training metrics (loss, samples, training time)
- Resource metrics (battery level, battery drain, device info)
- Network usage (implicit in upload/download)

For detailed logging, check the app's log output or export metrics.

### Combining with Python Clients

You can run hybrid experiments:
- Multiple Python clients (for large-scale sweeps)
- 2+ Android devices (for real mobile validation)
- All connect to the same server
- Server aggregates all updates together

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to server
- **Solution**: 
  - Ensure server is running
  - Check server URL is correct (use IP, not localhost)
  - Verify both devices are on same network
  - Check firewall settings

**Problem**: Connection timeout
- **Solution**: 
  - Use ngrok for external access
  - Check server logs for errors
  - Verify server port (default: 8000)

### Model Loading Issues

**Problem**: Model parameters not loading correctly
- **Solution**: 
  - Verify Float32 encoding compatibility
  - Check server model dimensions match client expectations
  - Review model_encoder.dart for byte order (endianness)

### Resource Monitoring

**Problem**: Battery/memory metrics not accurate
- **Solution**: 
  - Resource monitoring uses platform APIs
  - For detailed profiling, use Android Profiler
  - CPU/memory monitoring may require additional permissions

## Development Notes

### Model Compatibility

The Dart Matrix Factorization model is designed to be compatible with the Python PyTorch version:
- Same embedding dimensions
- Same initialization scheme
- Same forward pass logic
- Parameter format matches server expectations

### Performance Considerations

For mobile devices:
- Model size should be small (embedding_dim ≤ 32 recommended)
- Local training epochs should be minimal (1-2 epochs)
- Batch size should be small (16-32)
- Use sample data sets for mobile devices (5-50 samples)

## Future Enhancements

- [ ] Load actual MovieLens data from device storage
- [ ] Implement DP-SGD for privacy-preserving training
- [ ] Add background training capability
- [ ] Export metrics to CSV/JSON for analysis
- [ ] Add visualization of training progress
- [ ] Implement model checkpointing

## Thesis Integration

This mobile client addresses the requirement for **physical device participation**:

1. **Real Device Validation**: Test actual mobile constraints (battery, memory, network)
2. **Resource Profiling**: Collect real-world resource usage metrics
3. **Mobile Deployment**: Demonstrate feasibility on actual Android devices
4. **Hybrid Experiments**: Combine Python simulation with real mobile devices

## License

This project is part of a Master's thesis research project.

## Contact

For questions or issues, refer to the main thesis repository.
