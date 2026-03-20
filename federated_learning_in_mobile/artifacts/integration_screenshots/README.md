# Integration screenshots

This folder is populated by the screenshot integration test.

Expected output files after a successful run:

- `01_dashboard_overview.png`
- `02_dashboard_logs.png`
- `03_recommendations.png`

Run the screenshot flow from the app root with:

```bash
flutter drive \
  --driver=test_driver/integration_test.dart \
  --target=integration_test/app_screenshots_test.dart \
  -d "iPhone 16e"
```

The test overwrites the PNG files on each run so the latest captures are always easy to find.

