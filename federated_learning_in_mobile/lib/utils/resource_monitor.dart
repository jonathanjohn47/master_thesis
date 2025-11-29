import 'dart:io';
import 'package:battery_plus/battery_plus.dart';
import 'package:device_info_plus/device_info_plus.dart';

/// Resource monitoring utilities for mobile devices
/// Tracks CPU, memory, battery, and network usage

class ResourceMonitor {
  final Battery _battery = Battery();
  final DeviceInfoPlugin _deviceInfo = DeviceInfoPlugin();
  
  int? _initialBatteryLevel;
  DateTime? _startTime;
  int? _startMemory;
  
  /// Initialize monitoring (record initial state)
  Future<void> initialize() async {
    print('[RESOURCE_MONITOR] Initializing resource monitoring...');
    try {
      _startTime = DateTime.now();
      _initialBatteryLevel = await _battery.batteryLevel;
      print('[RESOURCE_MONITOR] Initial battery level: $_initialBatteryLevel%');
      print('[RESOURCE_MONITOR] Start time: $_startTime');
    } catch (e, stackTrace) {
      print('[RESOURCE_MONITOR_ERROR] Initialization failed: $e');
      print('[RESOURCE_MONITOR_ERROR] Stack trace: $stackTrace');
      rethrow;
    }
  }
  
  /// Get current battery level
  Future<int> getBatteryLevel() async {
    return await _battery.batteryLevel;
  }
  
  /// Calculate battery drain since initialization
  Future<double> getBatteryDrain() async {
    if (_initialBatteryLevel == null) {
      await initialize();
    }
    
    final currentLevel = await _battery.batteryLevel;
    return (_initialBatteryLevel! - currentLevel).toDouble();
  }
  
  /// Get device information
  Future<Map<String, dynamic>> getDeviceInfo() async {
    if (Platform.isAndroid) {
      final androidInfo = await _deviceInfo.androidInfo;
      return {
        'platform': 'Android',
        'model': androidInfo.model,
        'manufacturer': androidInfo.manufacturer,
        'version': androidInfo.version.release,
        'sdkInt': androidInfo.version.sdkInt,
      };
    } else if (Platform.isIOS) {
      final iosInfo = await _deviceInfo.iosInfo;
      return {
        'platform': 'iOS',
        'model': iosInfo.model,
        'name': iosInfo.name,
        'systemVersion': iosInfo.systemVersion,
      };
    }
    return {'platform': 'Unknown'};
  }
  
  /// Get resource metrics (for reporting)
  Future<Map<String, dynamic>> getMetrics() async {
    print('[RESOURCE_MONITOR] Getting resource metrics...');
    try {
      final batteryLevel = await getBatteryLevel();
      final batteryDrain = await getBatteryDrain();
      final deviceInfo = await getDeviceInfo();
      
      final elapsedSeconds = _startTime != null
          ? DateTime.now().difference(_startTime!).inSeconds
          : 0;
      
      final metrics = {
        'battery_level': batteryLevel,
        'battery_drain': batteryDrain,
        'elapsed_seconds': elapsedSeconds,
        'device_info': deviceInfo,
        'timestamp': DateTime.now().toIso8601String(),
        // Note: CPU and memory monitoring requires platform channels
        // For thesis, you can add estimates or use platform-specific packages
        'cpu_percent': _estimateCpuUsage(), // Placeholder
        'memory_mb': _estimateMemoryUsage(), // Placeholder
      };
      
      print('[RESOURCE_MONITOR] Metrics collected: battery=$batteryLevel%, drain=$batteryDrain%, elapsed=${elapsedSeconds}s');
      return metrics;
    } catch (e, stackTrace) {
      print('[RESOURCE_MONITOR_ERROR] Failed to get metrics: $e');
      print('[RESOURCE_MONITOR_ERROR] Stack trace: $stackTrace');
      rethrow;
    }
  }
  
  /// Estimate CPU usage (placeholder - requires platform channels for real measurement)
  double _estimateCpuUsage() {
    // For thesis, you can implement platform channels or use profiling tools
    // This is a placeholder
    return 15.0; // Estimated percentage
  }
  
  /// Estimate memory usage (placeholder)
  double _estimateMemoryUsage() {
    // Requires platform channels for accurate measurement
    // For thesis, you can add actual implementation using dart:ffi or plugins
    return 50.0; // Estimated MB
  }
  
  /// Measure network bandwidth for data transfer
  static int measureNetworkBytes(int bytesTransferred, DateTime start, DateTime end) {
    final duration = end.difference(start);
    final bytesPerSecond = duration.inMilliseconds > 0
        ? (bytesTransferred / (duration.inMilliseconds / 1000)).round()
        : 0;
    return bytesPerSecond;
  }
}

