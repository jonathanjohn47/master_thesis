import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'package:federated_learning_in_mobile/main.dart' as app;

const String _serverUrl = String.fromEnvironment(
  'FL_TEST_SERVER_URL',
  defaultValue: 'http://10.0.2.2:8000',
);

void main() {
  final IntegrationTestWidgetsFlutterBinding binding =
      IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() async {
    if (Platform.isAndroid) {
      await binding.convertFlutterSurfaceToImage();
    }
  });

  testWidgets('runs 10 rounds and captures milestone screenshots', (
    WidgetTester tester,
  ) async {
    app.main();
    await tester.pumpAndSettle();

    expect(find.text('Federated Client'), findsOneWidget);
    expect(find.text('CONNECT TO SERVER'), findsOneWidget);
    await _takeScreenshot(binding, tester, 'initial_state_connection_screen');

    await _enterServerUrl(tester, _serverUrl);
    await _enterClientId(tester, 'integration_rounds_client');

    await tester.tap(find.text('CONNECT TO SERVER'));
    final connected = await _waitForText(
      tester,
      find.textContaining('Status: Connected'),
      timeout: const Duration(seconds: 35),
    );
    expect(connected, isTrue, reason: 'App did not connect to server');

    await tester.tap(find.text('Run 10 Rounds'));
    final startFinder = find.widgetWithText(ElevatedButton, 'Start');
    final startDialogVisible = await _waitForText(
      tester,
      startFinder,
      timeout: const Duration(seconds: 10),
    );
    expect(startDialogVisible, isTrue, reason: '10-round confirmation dialog missing');

    await tester.tap(startFinder);
    await tester.pumpAndSettle();

    final trainingStarted = await _waitForText(
      tester,
      find.textContaining('Status: Training Round 1'),
      timeout: const Duration(seconds: 20),
    );
    expect(trainingStarted, isTrue, reason: 'Round 1 did not start');
    await _takeScreenshot(binding, tester, 'round_1_started');

    final tenthRoundReached = await _waitForText(
      tester,
      find.text('=== Round 10/10 ==='),
      timeout: const Duration(minutes: 6),
    );
    expect(tenthRoundReached, isTrue, reason: 'Round 10 marker not found in logs');

    final trainingStopped = await _waitForText(
      tester,
      find.text('Training...'),
      timeout: const Duration(minutes: 2),
      expectMissing: true,
    );
    expect(trainingStopped, isTrue, reason: 'Training indicator never disappeared');

    // Return to top to capture final post-training status.
    await tester.drag(find.byType(Scrollable).first, const Offset(0, 1200));
    await tester.pumpAndSettle();
    await _takeScreenshot(binding, tester, 'round_10_completed');

    await tester.scrollUntilVisible(
      find.text('LIVE LOGS'),
      350,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.pumpAndSettle();
    await _takeScreenshot(binding, tester, 'logs_progress_metrics');
  });
}

Future<void> _enterServerUrl(WidgetTester tester, String url) async {
  final serverUrlField = find.byType(TextField).first;
  await tester.tap(serverUrlField);
  await tester.pumpAndSettle();
  await tester.enterText(serverUrlField, url);
  await tester.pumpAndSettle();
}

Future<void> _enterClientId(WidgetTester tester, String clientId) async {
  final clientIdField = find.byType(TextField).at(1);
  await tester.tap(clientIdField);
  await tester.pumpAndSettle();
  await tester.enterText(clientIdField, clientId);
  await tester.pumpAndSettle();
}

Future<bool> _waitForText(
  WidgetTester tester,
  Finder finder, {
  required Duration timeout,
  bool expectMissing = false,
}) async {
  final maxIterations = timeout.inMilliseconds ~/ 250;
  for (int i = 0; i < maxIterations; i++) {
    await tester.pump(const Duration(milliseconds: 250));
    final present = finder.evaluate().isNotEmpty;
    if (!expectMissing && present) {
      return true;
    }
    if (expectMissing && !present) {
      return true;
    }
  }
  return false;
}

Future<void> _takeScreenshot(
  IntegrationTestWidgetsFlutterBinding binding,
  WidgetTester tester,
  String name,
) async {
  await tester.pump(const Duration(milliseconds: 300));
  await tester.pumpAndSettle();
  await binding.takeScreenshot(name);
}

