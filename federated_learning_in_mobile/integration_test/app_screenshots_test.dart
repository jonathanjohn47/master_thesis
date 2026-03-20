import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'package:federated_learning_in_mobile/main.dart' as app;

const String _liveServerUrl = String.fromEnvironment(
  'FL_TEST_SERVER_URL',
  defaultValue: '',
);

void main() {
  final IntegrationTestWidgetsFlutterBinding binding =
      IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() async {
    if (Platform.isAndroid) {
      await binding.convertFlutterSurfaceToImage();
    }
  });

  testWidgets('launches app and captures screenshots across app situations', (
    WidgetTester tester,
  ) async {
    app.main();
    await tester.pumpAndSettle();

    expect(find.text('Federated Client'), findsOneWidget);
    expect(find.text('SERVER CONFIGURATION'), findsOneWidget);

    expect(
      _liveServerUrl.isNotEmpty,
      isTrue,
      reason:
          'Provide the server URL with --dart-define=FL_TEST_SERVER_URL=http://<HOST_IP>:8080',
    );

    await _enterServerUrl(tester, _liveServerUrl);
    await _enterClientId(tester, 'integration_screenshots_client');
    await tester.tap(find.text('CONNECT TO SERVER'));

    final connected = await _pumpUntilFound(
      tester,
      find.textContaining('Status: Connected'),
      timeout: const Duration(seconds: 30),
      throwOnTimeout: false,
    );
    expect(connected, isTrue, reason: 'App did not reach Connected state');

    await _assertNoVisibleErrorSnackbar(tester);
    await _takeScreenshot(binding, tester, '01_connected_dashboard');

    await tester.tap(find.byIcon(Icons.movie));
    await tester.pumpAndSettle();
    expect(find.text('Movie Recommendations'), findsOneWidget);
    await _assertNoVisibleErrorSnackbar(tester);
    await _takeScreenshot(binding, tester, '02_recommendations_live');

    await tester.pageBack();
    await tester.pumpAndSettle();
    expect(find.text('Federated Client'), findsOneWidget);

    await tester.scrollUntilVisible(
      find.text('LIVE LOGS'),
      350,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.pumpAndSettle();
    await _assertNoVisibleErrorSnackbar(tester);
    await _takeScreenshot(binding, tester, '03_dashboard_logs_connected');
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

Future<bool> _pumpUntilFound(
  WidgetTester tester,
  Finder finder, {
  required Duration timeout,
  bool throwOnTimeout = true,
}) async {
  final maxIterations = timeout.inMilliseconds ~/ 250;
  for (int i = 0; i < maxIterations; i++) {
    await tester.pump(const Duration(milliseconds: 250));
    if (finder.evaluate().isNotEmpty) {
      return true;
    }
  }
  if (throwOnTimeout) {
    throw TestFailure('Timed out waiting for $finder');
  }
  return false;
}

Future<void> _assertNoVisibleErrorSnackbar(WidgetTester tester) async {
  await tester.pump();
  expect(find.byType(SnackBar), findsNothing);
}

Future<void> _takeScreenshot(
  IntegrationTestWidgetsFlutterBinding binding,
  WidgetTester tester,
  String name,
) async {
  await tester.pump(const Duration(milliseconds: 250));
  await tester.pumpAndSettle();
  await binding.takeScreenshot(name);
}


