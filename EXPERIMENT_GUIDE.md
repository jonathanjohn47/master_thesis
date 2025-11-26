# Complete Experimentation Guide for Thesis

This guide explains how to run federated learning experiments with **Python clients** (for large-scale sweeps) and **Android devices** (for real mobile validation) together.

## Overview

Your thesis requires:
1. ✅ **Python simulation clients** - For running parameter sweeps (DP budgets, heterogeneity)
2. ✅ **2+ Android devices** - For real mobile device validation
3. ✅ **Unified server** - Both connect to the same FastAPI server

## Experiment Architecture

```
┌─────────────────────────────────────┐
│     FastAPI Server (server.py)     │
│  - Aggregates all client updates    │
│  - Tracks Python & Android clients  │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼──────┐  ┌────▼─────────────┐
│   Python    │  │   Android        │
│   Clients   │  │   Devices        │
│  (Many)     │  │  (Device 1 & 2)  │
└─────────────┘  └──────────────────┘
```

## Step-by-Step Experiment Setup

### Phase 1: Server Setup

#### 1. Start the Server

```bash
# Terminal 1: Start server
cd c:\Users\jonat\PycharmProjects\master_thesis
python server.py
```

Server will start on `http://0.0.0.0:8000`

#### 2. Make Server Accessible to Mobile Devices

**Option A: Local Network (Same WiFi)**
```bash
# Find your PC's local IP address
# Windows:
ipconfig
# Look for IPv4 Address (e.g., 192.168.1.100)

# Update server to bind to this IP, or use 0.0.0.0 (already configured)
# Mobile devices will connect to: http://192.168.1.100:8000
```

**Option B: ngrok (For External Access)**
```bash
# Install ngrok if not already installed
# Download from: https://ngrok.com/

# Create tunnel
ngrok http 8000

# Use the ngrok URL (e.g., https://abc123.ngrok.io)
# Mobile devices connect to: https://abc123.ngrok.io
```

### Phase 2: Initialize Server Model

In a new terminal, initialize the model:

```bash
# Terminal 2: Initialize model
python -c "import requests; requests.post('http://localhost:8000/init-model', params={'num_users': 943, 'num_items': 1682, 'embedding_dim': 16})"
```

Or use the interactive API docs at `http://localhost:8000/docs`

### Phase 3: Android Device Setup

#### 1. Prepare Devices

You need **at least 2 Android devices** (or emulators):

- **Device 1**: Physical Android phone OR Android Emulator
- **Device 2**: Physical Android phone OR Android Emulator

#### 2. Install the Flutter App

**On each device:**

```bash
# Build and install
cd federated_learning_in_mobile
flutter build apk
flutter install
```

Or connect device and run directly:
```bash
flutter run
```

#### 3. Configure App

1. **Device 1**:
   - Open app
   - Server URL: `http://192.168.1.100:8000` (or ngrok URL)
   - Client ID: `android_device_1`
   - Click "Connect to Server"

2. **Device 2**:
   - Open app
   - Server URL: `http://192.168.1.100:8000` (same as Device 1)
   - Client ID: `android_device_2`
   - Click "Connect to Server"

### Phase 4: Run Hybrid Experiments

#### Experiment Type 1: Baseline (Python + Android)

**Goal**: Validate Android devices work alongside Python clients

```bash
# Terminal 3: Run Python experiment with 3 clients
python run_experiment.py

# On Android devices: Click "Run Training Round" on both devices
# Wait for Python clients to complete their round
# Then run aggregation on server
```

**Procedure:**
1. Python clients train and upload (automated via `run_experiment.py`)
2. Android Device 1: Click "Run Training Round"
3. Android Device 2: Click "Run Training Round"
4. Aggregate all updates:
   ```bash
   curl -X POST http://localhost:8000/aggregate
   ```

#### Experiment Type 2: DP Budget Sweep (Python Only)

**Goal**: Answer RQ1 - Accuracy vs Privacy trade-offs

Create a new experiment script for DP sweeps:

```python
# dp_sweep_experiment.py
import requests
from client import FederatedLearningClient, ClientConfig, ...

DP_EPSILONS = [float('inf'), 8, 4, 2, 1]
NUM_ROUNDS = 10
NUM_CLIENTS = 10

for epsilon in DP_EPSILONS:
    # Calculate DP parameters (sigma, clip_norm) for target epsilon
    # Run experiment
    # Collect metrics
    # Save results
```

**Collect metrics:**
- Accuracy (NDCG@10, Hit@10) per round
- Training loss
- Final test accuracy

#### Experiment Type 3: Mobile Resource Profiling

**Goal**: Measure real mobile resource usage

1. Start resource monitoring on Android devices
2. Run training rounds
3. Collect metrics:
   - Battery drain per round
   - Memory usage
   - Training time
   - Network bandwidth

**Data Collection:**
- Note metrics from app UI
- Export logs if needed
- Document device specs

## Data Collection Strategy

### For Each Experiment, Collect:

```json
{
  "experiment_id": "dp_e8_alpha0.5_round1",
  "timestamp": "2025-01-XX...",
  "config": {
    "dp_epsilon": 8,
    "alpha": 0.5,
    "num_clients": 12,
    "client_types": ["python", "python", "android", "android"],
    "embedding_dim": 16
  },
  "results": {
    "round": 1,
    "python_clients": [
      {
        "client_id": "client_0",
        "loss": 0.123,
        "samples": 250
      }
    ],
    "android_clients": [
      {
        "client_id": "android_device_1",
        "loss": 0.145,
        "samples": 10,
        "resource_metrics": {
          "battery_drain": 2.3,
          "training_time_ms": 185,
          "memory_mb": 89.5
        }
      }
    ],
    "aggregation": {
      "total_samples": 510,
      "num_clients": 4
    },
    "global_metrics": {
      "test_ndcg_10": 0.45,
      "test_hit_10": 0.32
    }
  }
}
```

### Recommended Experiment Runs

#### Week 1: Validation
- ✅ Test Python clients alone
- ✅ Test Android devices alone  
- ✅ Test Python + Android together
- ✅ Verify server aggregation works

#### Week 2-3: Parameter Sweeps (Python)
- DP budgets: ε ∈ {∞, 8, 4, 2, 1}
- Heterogeneity: α ∈ {0.1, 0.5, 1.0}
- Embedding dims: {8, 16, 32}
- 3 seeds per configuration

#### Week 4: Mobile Validation (Android)
- Baseline (no DP)
- With DP (ε = 4, 8)
- Resource profiling
- Compare 2 devices

## Analysis Workflow

### 1. Collect All Data

Create a results directory:
```
results/
├── dp_sweep/
│   ├── epsilon_inf.json
│   ├── epsilon_8.json
│   └── ...
├── heterogeneity/
│   ├── alpha_0.1.json
│   └── ...
└── mobile/
    ├── device_1_baseline.json
    ├── device_2_baseline.json
    └── ...
```

### 2. Process Results

Create analysis scripts:
```python
# analyze_results.py
import json
import pandas as pd
import matplotlib.pyplot as plt

# Load all results
# Compute statistics
# Generate plots:
#   - Accuracy vs ε
#   - Attack AUC vs ε  
#   - Resource usage (mobile)
#   - Pareto frontiers
```

### 3. Generate Thesis Figures

Required plots:
1. **Accuracy vs DP Budget (ε)** - Line plot showing NDCG@10, Hit@10
2. **Attack AUC vs ε** - Privacy evaluation
3. **Accuracy vs Heterogeneity (α)** - How data distribution affects accuracy
4. **Resource Usage (Mobile)** - Battery, memory, network
5. **Pareto Frontiers** - Accuracy vs Privacy vs Bandwidth

## Mobile Device Requirements

### Minimum Specifications
- Android 6.0+ (API 23+)
- 2GB RAM minimum
- WiFi connectivity
- USB debugging enabled (for development)

### Recommended Setup
- **Device 1**: Modern Android phone (for best performance)
- **Device 2**: Older Android phone OR emulator (for comparison)

### Device Information to Document
For your thesis, record:
- Device model and manufacturer
- Android version
- RAM capacity
- CPU specs (if available)
- Network conditions (WiFi speed)

## Troubleshooting

### Android Cannot Connect

**Problem**: Mobile app can't reach server
- ✅ Check server is running
- ✅ Verify IP address is correct (not localhost)
- ✅ Ensure same WiFi network
- ✅ Check firewall allows port 8000
- ✅ Try ngrok as alternative

### Model Parameter Mismatch

**Problem**: Parameters don't load correctly
- ✅ Verify embedding dimensions match
- ✅ Check Float32 encoding compatibility
- ✅ Review server logs for errors

### Resource Metrics Not Accurate

**Problem**: Battery/memory readings seem off
- ✅ Resource monitoring is estimated
- ✅ Use Android Profiler for detailed metrics
- ✅ Document estimation method in thesis

## Thesis Writing Integration

### Section 4.1.3: Android Mobile Client Implementation

Describe:
- Flutter/Dart implementation
- Matrix Factorization model
- Integration with server
- Resource monitoring capabilities

### Section 5.4: Mobile Resource Profiling

Present:
- Battery drain measurements
- Memory usage
- Training latency
- Network bandwidth
- Comparison: Device 1 vs Device 2

### Limitations Section

Discuss:
- Differences between simulation and real devices
- Mobile-specific constraints
- Resource monitoring accuracy

## Next Steps

1. ✅ **Test server + Android connection**
2. ✅ **Run validation experiment (Python + 2 Android devices)**
3. ✅ **Run DP budget sweeps (Python clients)**
4. ✅ **Collect mobile resource metrics**
5. ✅ **Analyze results and generate plots**
6. ✅ **Write thesis sections**

## Quick Reference

**Server Commands:**
```bash
# Start server
python server.py

# Initialize model
curl -X POST "http://localhost:8000/init-model?num_users=943&num_items=1682&embedding_dim=16"

# Aggregate
curl -X POST http://localhost:8000/aggregate

# Check health
curl http://localhost:8000/healthz
```

**Android Setup:**
```bash
cd federated_learning_in_mobile
flutter pub get
flutter run
```

**Server URL for Mobile:**
- Local: `http://YOUR_PC_IP:8000`
- ngrok: `https://YOUR_NGROK_URL`

---

**You're all set!** You now have:
- ✅ Python federated learning system
- ✅ Android mobile clients
- ✅ Unified server
- ✅ Resource monitoring
- ✅ Ready for experiments

Good luck with your thesis! 🎓

