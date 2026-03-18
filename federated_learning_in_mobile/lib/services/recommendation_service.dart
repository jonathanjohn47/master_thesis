import 'dart:math';

import 'fl_client.dart';

class MovieRecommendation {
  final int itemId;
  final String title;
  final double score;
  final bool isSeen;
  final String explanation;

  const MovieRecommendation({
    required this.itemId,
    required this.title,
    required this.score,
    required this.isSeen,
    required this.explanation,
  });

  MovieRecommendation copyWith({
    int? itemId,
    String? title,
    double? score,
    bool? isSeen,
    String? explanation,
  }) {
    return MovieRecommendation(
      itemId: itemId ?? this.itemId,
      title: title ?? this.title,
      score: score ?? this.score,
      isSeen: isSeen ?? this.isSeen,
      explanation: explanation ?? this.explanation,
    );
  }
}

class RecommendationService {
  const RecommendationService();

  List<int> getCandidateUsers(FederatedLearningClient client) {
    final ids =
        client.localData
            .map((sample) => sample[0])
            .whereType<int>()
            .where((id) => id >= 0 && id < client.numUsers)
            .toSet()
            .toList()
          ..sort();

    if (ids.isNotEmpty) {
      return ids;
    }

    if (client.numUsers > 0) {
      return [0];
    }

    return <int>[];
  }

  List<MovieRecommendation> topNRecommendations({
    required FederatedLearningClient client,
    required int userId,
    required int topN,
    Map<int, String> movieTitles = const <int, String>{},
    bool excludeSeenItems = true,
  }) {
    if (client.model == null) {
      throw StateError('Model is not loaded.');
    }
    if (client.numItems <= 0 || client.numUsers <= 0) {
      return const <MovieRecommendation>[];
    }
    if (userId < 0 || userId >= client.numUsers) {
      throw ArgumentError('Invalid user id: $userId');
    }

    final seenItems = <int>{};
    for (final sample in client.localData) {
      if (sample.length < 2) {
        continue;
      }
      final sampleUserId = sample[0];
      final sampleItemId = sample[1];
      if (sampleUserId is int &&
          sampleItemId is int &&
          sampleUserId == userId) {
        seenItems.add(sampleItemId);
      }
    }

    final recommendations = <MovieRecommendation>[];
    for (int itemId = 0; itemId < client.numItems; itemId++) {
      final isSeen = seenItems.contains(itemId);
      if (excludeSeenItems && isSeen) {
        continue;
      }

      final score = client.model!.predict(userId, itemId);
      final movieTitle = movieTitles[itemId] ?? 'Movie #$itemId';
      final seenLabel = isSeen ? 'Seen before' : 'New for this user';
      final explanation =
          'Predicted score ${score.toStringAsFixed(4)} - $seenLabel';

      recommendations.add(
        MovieRecommendation(
          itemId: itemId,
          title: movieTitle,
          score: score,
          isSeen: isSeen,
          explanation: explanation,
        ),
      );
    }

    recommendations.sort((a, b) => b.score.compareTo(a.score));
    return recommendations.take(max(0, topN)).toList(growable: false);
  }
}
