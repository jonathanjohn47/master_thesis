# Metrics Collection Guide

The mobile app now automatically collects and saves training metrics in the same format as the Python experiments.

## How It Works

1. **Automatic Collection**: When you connect to the server and run training rounds, metrics are automatically collected.

2. **Saved After Each Round**: After each training round completes, results are saved to:
   - JSON file (full detailed data)
   - CSV file (summary for easy analysis)

3. **File Location**: Results are saved in the app's documents directory:
   ```
   /data/data/com.example.federated_learning_in_mobile/app_flutter/fl_results/
   ```

## What Metrics Are Collected

### Per Training Round:
- Training loss
- Number of samples
- Training time (ms)
- Resource metrics:
  - Battery level and drain
  - Memory usage
  - CPU usage
  - Network bandwidth

### Experiment Configuration:
- Number of users and items
- Embedding dimension
- Client ID
- Device ID
- Server URL

## File Names

Files are named using the experiment ID format:
```
dp_inf_alpha_null_dim_16_clients_1_device_XXX_t1234567890.json
dp_inf_alpha_null_dim_16_clients_1_device_XXX_t1234567890_summary.csv
```

The experiment ID includes:
- DP epsilon (dp_inf = no privacy)
- Alpha (heterogeneity parameter)
- Embedding dimension
- Number of clients
- Device ID
- Timestamp

## Accessing Results

### Option 1: Using ADB (Recommended)
```bash
# Pull all results from device
adb pull /data/data/com.example.federated_learning_in_mobile/app_flutter/fl_results/ ./mobile_results/

# Or pull specific file
adb pull /data/data/com.example.federated_learning_in_mobile/app_flutter/fl_results/dp_inf_*.json
```

### Option 2: Using Android File Manager
1. Connect device via USB
2. Enable file transfer mode
3. Navigate to: Android/data/com.example.federated_learning_in_mobile/files/fl_results/
4. Copy files to your computer

### Option 3: Using the App
1. After running at least one training round
2. Click "Show Results Location" button
3. Copy the file path shown

## File Formats

### JSON Format
The JSON file contains all collected data in a structured format:
```json
{
  "experiment_id": "...",
  "timestamp": "2025-11-29T...",
  "config": {
    "num_users": 50,
    "num_items": 4032,
    ...
  },
  "rounds": [
    {
      "round": 1,
      "train_loss": 0.45,
      "resource_metrics": {
        "battery_drain": 2.5,
        "training_time_ms": 150,
        ...
      },
      ...
    }
  ],
  "client_metrics": [...],
  "mobile_metrics": [...]
}
```

### CSV Format
The CSV file is a summary table with key metrics per round:
- Round number
- Train Loss
- Training Time (MS)
- Battery Drain
- Number of Samples
- And other metrics

## Using Results for Thesis

The mobile results can be:
1. **Combined with Python results** - Same format, easy to merge
2. **Analyzed separately** - Mobile-specific resource metrics
3. **Compared** - Mobile vs Python client performance

### Analysis Example
```python
import json
import pandas as pd

# Load mobile results
with open('mobile_results/dp_inf_..._device_XXX.json') as f:
    mobile_data = json.load(f)

# Extract metrics
rounds = mobile_data['rounds']
battery_drain = [r['resource_metrics']['battery_drain'] for r in rounds]
training_times = [r['resource_metrics']['training_time_ms'] for r in rounds]

# Plot resource usage
import matplotlib.pyplot as plt
plt.plot(battery_drain, label='Battery Drain (%)')
plt.plot(training_times, label='Training Time (ms)')
plt.legend()
plt.show()
```

## Troubleshooting

**Q: Files not appearing?**
- Make sure you've run at least one training round
- Check app logs for errors
- Verify app has storage permissions

**Q: Can't access files via ADB?**
- Make sure USB debugging is enabled
- Try: `adb shell run-as com.example.federated_learning_in_mobile ls app_flutter/fl_results/`

**Q: Want to reset/clear old results?**
- Uninstall and reinstall the app (clears app data)
- Or manually delete files via ADB

## Next Steps

1. Run training rounds from mobile app
2. Collect results using ADB
3. Combine with Python experiment results
4. Analyze for your thesis!

