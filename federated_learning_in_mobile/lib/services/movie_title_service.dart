import 'package:flutter/services.dart' show rootBundle;

class MovieTitleService {
  const MovieTitleService();

  static const String _assetPath = 'assets/movielens_titles.csv';

  Future<Map<int, String>> loadTitles() async {
    final csvData = await rootBundle.loadString(_assetPath);
    final titles = <int, String>{};

    for (final rawLine in csvData.split('\n')) {
      final line = rawLine.trim();
      if (line.isEmpty || line.startsWith('item_id')) {
        continue;
      }

      final commaIndex = line.indexOf(',');
      if (commaIndex <= 0) {
        continue;
      }

      final idText = line.substring(0, commaIndex).trim();
      final itemId = int.tryParse(idText);
      if (itemId == null) {
        continue;
      }

      var title = line.substring(commaIndex + 1).trim();
      if (title.startsWith('"') && title.endsWith('"') && title.length >= 2) {
        title = title.substring(1, title.length - 1).replaceAll('""', '"');
      }

      titles[itemId] = title;
    }

    return titles;
  }
}
