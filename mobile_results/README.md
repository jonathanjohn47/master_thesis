# Mobile Results Directory

This folder contains experiment results automatically saved from Android devices/emulators.

## How It Works

When you run training rounds on the mobile app:
1. Results are saved locally on the device
2. Results are **automatically uploaded** to the server
3. Server saves them here in `mobile_results/` folder on your PC

## File Format

- **JSON files**: `experiment_id.json` - Full detailed results
- **CSV files**: `experiment_id_summary.csv` - Summary table

## Location

Results are saved to:
```
C:\Users\jonat\PycharmProjects\master_thesis\mobile_results\
```

You can access them directly from your PC - no ADB or file manager needed!

## Example Files

- `dp_inf_alpha_null_dim_16_clients_1_device_XXX_t1234567890.json`
- `dp_inf_alpha_null_dim_16_clients_1_device_XXX_t1234567890_summary.csv`

## Combining with Python Results

Mobile results use the same format as Python experiment results in `results/` folder, so you can:
- Load them together for analysis
- Compare mobile vs Python client performance
- Generate combined plots and tables

## Troubleshooting

**Q: No files appearing?**
- Make sure server is running
- Check mobile app logs for upload errors
- Verify mobile app successfully connected to server

**Q: Upload failed?**
- Check server logs for errors
- Verify network connection
- Results are still saved locally on device (use ADB to pull if needed)

