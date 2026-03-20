import 'dart:io';

import 'package:integration_test/integration_test_driver_extended.dart';

const String _outputDirectoryPath = 'artifacts/integration_screenshots';

Future<void> main() async {
  final outputDirectory = Directory(_outputDirectoryPath);
  await outputDirectory.create(recursive: true);

  await integrationDriver(onScreenshot: _saveScreenshot);
}

Future<bool> _saveScreenshot(
  String screenshotName,
  List<int> screenshotBytes, [
  Map<String, Object?>? args,
]) async {
  final screenshotFile = File('$_outputDirectoryPath/$screenshotName.png');
  await screenshotFile.parent.create(recursive: true);
  await screenshotFile.writeAsBytes(screenshotBytes);
  stdout.writeln('Saved screenshot to ${screenshotFile.path}');
  return true;
}

