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
                        return ListTile(
                          leading: CircleAvatar(child: Text('${index + 1}')),
                          title: Text(rec.title),
                          subtitle: Text(rec.explanation),
                          trailing: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
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
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
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
