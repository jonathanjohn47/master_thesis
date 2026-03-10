// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:federated_learning_in_mobile/main.dart';

void main() {
  testWidgets('App launches and shows dashboard controls', (
    WidgetTester tester,
  ) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const FederatedLearningApp());

    // Verify that the app shows the server URL field
    expect(find.text('Federated Client'), findsOneWidget);
    expect(find.text('SERVER URL'), findsOneWidget);
    expect(find.text('CONNECT TO SERVER'), findsOneWidget);
    expect(
      find.text('Demo Mode: Train and Show Recommendations'),
      findsOneWidget,
    );
    expect(find.byIcon(Icons.movie), findsOneWidget);
  });
}
