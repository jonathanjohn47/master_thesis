import 'package:flutter_test/flutter_test.dart';

import 'package:federated_learning_in_mobile/models/matrix_factorization.dart';
import 'package:federated_learning_in_mobile/services/fl_client.dart';
import 'package:federated_learning_in_mobile/services/recommendation_service.dart';

void main() {
  test('RecommendationService returns titles and explanation text', () {
    final client = FederatedLearningClient(
      clientId: 'test-client',
      serverUrl: 'http://localhost:8000',
      numUsers: 3,
      numItems: 5,
      embeddingDim: 4,
    );

    client.model = MatrixFactorization(
      numUsers: client.numUsers,
      numItems: client.numItems,
      embeddingDim: client.embeddingDim,
    );

    client.loadLocalData([
      [0, 1, 1.0],
      [0, 3, 1.0],
    ]);

    const service = RecommendationService();
    final results = service.topNRecommendations(
      client: client,
      userId: 0,
      topN: 3,
      movieTitles: const {0: 'Toy Story (1995)', 2: 'Four Rooms (1995)'},
      excludeSeenItems: false,
    );

    expect(results.length, 3);
    expect(results.first.title.isNotEmpty, isTrue);
    expect(results.first.explanation.contains('Predicted score'), isTrue);
  });
}
