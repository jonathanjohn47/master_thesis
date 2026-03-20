import 'package:flutter/material.dart';

import '../services/fl_client.dart';
import '../services/movie_title_service.dart';
import '../services/recommendation_service.dart';

class RecommendationsPage extends StatefulWidget {
  final FederatedLearningClient client;

  const RecommendationsPage({super.key, required this.client});

  @override
  State<RecommendationsPage> createState() => _RecommendationsPageState();
}

class _RecommendationsPageState extends State<RecommendationsPage> {
  final RecommendationService _recommendationService =
      const RecommendationService();
  final MovieTitleService _movieTitleService = const MovieTitleService();

  List<int> _candidateUsers = const <int>[];
  List<MovieRecommendation> _recommendations = const <MovieRecommendation>[];
  Map<int, String> _movieTitles = const <int, String>{};
  int? _selectedUserId;
  int _topN = 10;
  bool _excludeSeenItems = true;
  bool _isLoadingTitles = true;
  final Set<int> _submittingSeenItems = <int>{};
  String? _error;

  @override
  void initState() {
    super.initState();
    _initialize();
  }

  Future<void> _initialize() async {
    try {
      final titles = await _movieTitleService.loadTitles();
      if (!mounted) {
        return;
      }
      _movieTitles = titles;
    } catch (_) {
      // Fallback is handled in RecommendationService with Movie #id labels.
      _movieTitles = const <int, String>{};
    }

    _candidateUsers = _recommendationService.getCandidateUsers(widget.client);
    if (_candidateUsers.isNotEmpty) {
      _selectedUserId = _candidateUsers.first;
      _refreshRecommendations();
    } else {
      _error =
          'No users available. Connect and run at least one training round first.';
    }

    if (mounted) {
      setState(() {
        _isLoadingTitles = false;
      });
    }
  }

  void _refreshRecommendations() {
    if (_selectedUserId == null) {
      return;
    }

    try {
      final results = _recommendationService.topNRecommendations(
        client: widget.client,
        userId: _selectedUserId!,
        topN: _topN,
        movieTitles: _movieTitles,
        excludeSeenItems: _excludeSeenItems,
      );

      setState(() {
        _error = null;
        _recommendations = results;
      });
    } catch (e) {
      setState(() {
        _recommendations = const <MovieRecommendation>[];
        _error = 'Failed to generate recommendations: $e';
      });
    }
  }

  Future<void> _markAsSeen(MovieRecommendation rec, int index) async {
    final userId = _selectedUserId;
    if (userId == null ||
        rec.isSeen ||
        _submittingSeenItems.contains(rec.itemId)) {
      return;
    }

    setState(() {
      _submittingSeenItems.add(rec.itemId);
      _recommendations[index] = rec.copyWith(
        isSeen: true,
        explanation:
            'Predicted score ${rec.score.toStringAsFixed(4)} - Seen before',
      );
    });

    try {
      await widget.client.markRecommendationSeen(
        userId: userId,
        itemId: rec.itemId,
        rating: 1.0,
      );

      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Marked "${rec.title}" as seen')));
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _recommendations[index] = rec;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to send seen event: $e'),
          backgroundColor: Colors.redAccent,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _submittingSeenItems.remove(rec.itemId);
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Movie Recommendations'),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: _refreshRecommendations,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildControls(),
            const SizedBox(height: 12),
            if (_isLoadingTitles)
              const Text('Loading movie titles...')
            else if (_error != null)
              Text(_error!, style: const TextStyle(color: Colors.redAccent))
            else
              Text(
                'Showing ${_recommendations.length} recommendations for user $_selectedUserId',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            const SizedBox(height: 12),
            Expanded(
              child: _recommendations.isEmpty
                  ? const Center(child: Text('No recommendations yet'))
                  : ListView.separated(
                      itemCount: _recommendations.length,
                      separatorBuilder: (_, __) => const Divider(height: 1),
                      itemBuilder: (context, index) {
                        final rec = _recommendations[index];
                        final isSubmitting = _submittingSeenItems.contains(
                          rec.itemId,
                        );
                        return Padding(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 10,
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              CircleAvatar(child: Text('${index + 1}')),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Text(
                                      rec.title,
                                      style: Theme.of(context)
                                          .textTheme
                                          .titleMedium,
                                    ),
                                    const SizedBox(height: 4),
                                    Text(rec.explanation),
                                  ],
                                ),
                              ),
                              const SizedBox(width: 10),
                              Column(
                                mainAxisSize: MainAxisSize.min,
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 2,
                                    ),
                                    decoration: BoxDecoration(
                                      color: rec.isSeen
                                          ? Colors.orange.withValues(alpha: 0.15)
                                          : Colors.green.withValues(alpha: 0.15),
                                      borderRadius: BorderRadius.circular(8),
                                      border: Border.all(
                                        color: rec.isSeen
                                            ? Colors.orange
                                            : Colors.green,
                                      ),
                                    ),
                                    child: Text(
                                      rec.isSeen ? 'Seen' : 'Unseen',
                                      style: TextStyle(
                                        color: rec.isSeen
                                            ? Colors.orange
                                            : Colors.green,
                                        fontSize: 11,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(height: 6),
                                  FilledButton.tonal(
                                    style: FilledButton.styleFrom(
                                      minimumSize: const Size(0, 28),
                                      tapTargetSize:
                                          MaterialTapTargetSize.shrinkWrap,
                                      visualDensity: VisualDensity.compact,
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 10,
                                        vertical: 6,
                                      ),
                                    ),
                                    onPressed: (rec.isSeen || isSubmitting)
                                        ? null
                                        : () => _markAsSeen(rec, index),
                                    child: isSubmitting
                                        ? const SizedBox(
                                            height: 12,
                                            width: 12,
                                            child: CircularProgressIndicator(
                                              strokeWidth: 2,
                                            ),
                                          )
                                        : Text(rec.isSeen ? 'Seen' : 'Mark seen'),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildControls() {
    final dropdownItems = _candidateUsers
        .map(
          (userId) =>
              DropdownMenuItem<int>(value: userId, child: Text('User $userId')),
        )
        .toList();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Row(
              children: [
                const Text('User:'),
                const SizedBox(width: 12),
                Expanded(
                  child: DropdownButton<int>(
                    value: _selectedUserId,
                    isExpanded: true,
                    items: dropdownItems,
                    onChanged: (value) {
                      if (value == null) {
                        return;
                      }
                      setState(() {
                        _selectedUserId = value;
                      });
                      _refreshRecommendations();
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                const Text('Top N:'),
                Expanded(
                  child: Slider(
                    min: 5,
                    max: 30,
                    divisions: 5,
                    value: _topN.toDouble(),
                    label: _topN.toString(),
                    onChanged: (value) {
                      setState(() {
                        _topN = value.round();
                      });
                    },
                    onChangeEnd: (_) => _refreshRecommendations(),
                  ),
                ),
                Text(_topN.toString()),
              ],
            ),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Exclude seen items'),
              value: _excludeSeenItems,
              onChanged: (value) {
                setState(() {
                  _excludeSeenItems = value;
                });
                _refreshRecommendations();
              },
            ),
          ],
        ),
      ),
    );
  }
}
