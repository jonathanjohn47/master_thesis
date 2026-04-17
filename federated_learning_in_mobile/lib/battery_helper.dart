import 'dart:io';
import 'package:battery_plus/battery_plus.dart';

final Battery _battery = Battery();

Future<int> getSafeBatteryLevel() async {
  // iOS simulator → always fail → skip
  if (Platform.isIOS) return -1;

  try {
    return await _battery.batteryLevel;
  } catch (e) {
    return -1;
  }
}