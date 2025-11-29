import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:csv/csv.dart';
import 'package:flutter/foundation.dart';
import 'package:path/path.dart' as path;

/// Metrics Collector for Federated Learning Experiments (Mobile)
/// Collects and saves all experimental metrics to JSON/CSV
class MetricsCollector {
  final String experimentId;
  late Directory resultsDir;
  
  // Store all collected metrics
  final Map<String, dynamic> experimentData;
  
  MetricsCollector({
    required this.experimentId,
  }) : experimentData = {
          'experiment_id': experimentId,
          'timestamp': DateTime.now().toIso8601String(),
          'config': <String, dynamic>{},
          'rounds': <Map<String, dynamic>>[],
          'final_metrics': <String, dynamic>{},
          'client_metrics': <Map<String, dynamic>>[],
          'mobile_metrics': <Map<String, dynamic>>[],
        };
  
  /// Initialize the results directory - saves to Downloads folder for easy access
  Future<void> initialize() async {
    // Check if running on web (not supported)
    try {
      if (kIsWeb) {
        throw UnsupportedError('Metrics collection not supported on web');
      }
    } catch (e) {
      // kIsWeb might not be available, continue anyway
    }
    
    // Try to use external storage Downloads folder (most accessible)
    try {
      final externalDir = await getExternalStorageDirectory();
      if (externalDir != null) {
        // Navigate to Downloads folder
        // Android external storage structure: /storage/emulated/0/Download
        final downloadsPath = Platform.isAndroid
            ? '/storage/emulated/0/Download/FL_Results'
            : '${externalDir.path}/Downloads/FL_Results';
        
        // Try the standard Downloads path first
        final downloadsDir = Directory(downloadsPath);
        
        // If that doesn't exist, try alternative paths
        if (!await downloadsDir.exists() && Platform.isAndroid) {
          // Alternative: Use external storage root + Download
          final altPath = path.join(externalDir.parent.path, 'Download', 'FL_Results');
          resultsDir = Directory(altPath);
        } else {
          resultsDir = downloadsDir;
        }
        
        if (!await resultsDir.exists()) {
          await resultsDir.create(recursive: true);
        }
        
        print('[METRICS_COLLECTOR] Using Downloads folder: ${resultsDir.path}');
        return;
      }
    } catch (e) {
      print('[METRICS_COLLECTOR] Warning: Downloads folder failed: $e');
    }
    
    // Fallback: Try external storage directory
    try {
      final externalDir = await getExternalStorageDirectory();
      if (externalDir != null) {
        resultsDir = Directory('${externalDir.path}/FL_Results');
        if (!await resultsDir.exists()) {
          await resultsDir.create(recursive: true);
        }
        print('[METRICS_COLLECTOR] Using external storage: ${resultsDir.path}');
        return;
      }
    } catch (e) {
      print('[METRICS_COLLECTOR] Warning: External storage failed: $e');
    }
    
    // Fallback: Application documents directory
    try {
      final appDocDir = await getApplicationDocumentsDirectory();
      resultsDir = Directory('${appDocDir.path}/FL_Results');
      
      if (!await resultsDir.exists()) {
        await resultsDir.create(recursive: true);
      }
      
      print('[METRICS_COLLECTOR] Using app documents: ${resultsDir.path}');
      return;
    } catch (e) {
      print('[METRICS_COLLECTOR] Warning: Application documents directory failed: $e');
    }
    
    // Last resort: temporary directory
    try {
      final tempDir = await getTemporaryDirectory();
      resultsDir = Directory('${tempDir.path}/FL_Results');
      if (!await resultsDir.exists()) {
        await resultsDir.create(recursive: true);
      }
      print('[METRICS_COLLECTOR] Using temporary directory: ${resultsDir.path}');
    } catch (e) {
      throw Exception('Could not initialize any storage directory: $e');
    }
  }
  
  /// Get the results directory path (for display)
  String get resultsPath => resultsDir.path;
  
  /// Get list of all result files
  Future<List<File>> getResultFiles() async {
    try {
      if (!await resultsDir.exists()) {
        return [];
      }
      
      final files = resultsDir.listSync()
          .whereType<File>()
          .where((f) => f.path.endsWith('.json') || f.path.endsWith('.csv'))
          .toList();
      
      return files;
    } catch (e) {
      print('[METRICS_COLLECTOR] Error listing files: $e');
      return [];
    }
  }
  
  /// Set experiment configuration
  void setConfig(Map<String, dynamic> config) {
    experimentData['config'] = config;
    print('[METRICS_COLLECTOR] Set experiment config');
  }
  
  /// Add metrics for a training round
  void addRoundMetrics({
    required int roundNum,
    required double trainLoss,
    Map<String, dynamic>? testMetrics,
    Map<String, dynamic>? aggregationInfo,
    List<Map<String, dynamic>>? clientMetrics,
    Map<String, dynamic>? resourceMetrics,
  }) {
    final roundData = <String, dynamic>{
      'round': roundNum,
      'train_loss': trainLoss,
      'test_metrics': testMetrics ?? <String, dynamic>{},
      'aggregation': aggregationInfo ?? <String, dynamic>{},
      'client_metrics': clientMetrics ?? <Map<String, dynamic>>[],
      'resource_metrics': resourceMetrics ?? <String, dynamic>{},
      'timestamp': DateTime.now().toIso8601String(),
    };
    
    (experimentData['rounds'] as List).add(roundData);
    print('[METRICS_COLLECTOR] Added metrics for round $roundNum');
  }
  
  /// Add final evaluation metrics
  void addFinalMetrics(Map<String, dynamic> metrics) {
    experimentData['final_metrics'] = metrics;
    print('[METRICS_COLLECTOR] Added final metrics');
  }
  
  /// Add per-client metrics
  void addClientMetrics(String clientId, Map<String, dynamic> metrics) {
    final clientData = <String, dynamic>{
      'client_id': clientId,
      ...metrics,
      'timestamp': DateTime.now().toIso8601String(),
    };
    
    (experimentData['client_metrics'] as List).add(clientData);
  }
  
  /// Add mobile device resource metrics
  void addMobileMetrics(String deviceId, Map<String, dynamic> metrics) {
    final mobileData = <String, dynamic>{
      'device_id': deviceId,
      ...metrics,
      'timestamp': DateTime.now().toIso8601String(),
    };
    
    (experimentData['mobile_metrics'] as List).add(mobileData);
  }
  
  /// Save metrics to JSON file
  Future<String> saveJson([String? filename]) async {
    await initialize();
    
    if (filename == null) {
      filename = '$experimentId.json';
    }
    
    final file = File('${resultsDir.path}/$filename');
    
    // Convert to JSON with proper formatting
    final jsonString = JsonEncoder.withIndent('  ').convert(experimentData);
    await file.writeAsString(jsonString);
    
    print('[METRICS_COLLECTOR] Saved JSON to: ${file.path}');
    return file.path;
  }
  
  /// Save summary to CSV file
  Future<String> saveCsvSummary([String? filename]) async {
    await initialize();
    
    if (filename == null) {
      filename = '${experimentId}_summary.csv';
    }
    
    final file = File('${resultsDir.path}/$filename');
    
    // Create CSV rows
    final List<List<dynamic>> csvData = [];
    
    // Header
    csvData.add([
      'Round',
      'Train_Loss',
      'NDCG@10',
      'Hit@10',
      'Precision@10',
      'Recall@10',
      'MSE',
      'MAE',
      'Accuracy',
      'Num_Clients',
      'Total_Samples',
      'Training_Time_MS',
      'Battery_Drain',
    ]);
    
    // Round data
    final rounds = experimentData['rounds'] as List;
    for (final roundData in rounds) {
      final testMetrics = roundData['test_metrics'] as Map<String, dynamic>? ?? {};
      final agg = roundData['aggregation'] as Map<String, dynamic>? ?? {};
      final resourceMetrics = roundData['resource_metrics'] as Map<String, dynamic>? ?? {};
      
      csvData.add([
        roundData['round'],
        roundData['train_loss']?.toString() ?? '',
        testMetrics['NDCG@10']?.toString() ?? '',
        testMetrics['Hit@10']?.toString() ?? '',
        testMetrics['Precision@10']?.toString() ?? '',
        testMetrics['Recall@10']?.toString() ?? '',
        testMetrics['mse']?.toString() ?? '',
        testMetrics['mae']?.toString() ?? '',
        testMetrics['accuracy']?.toString() ?? '',
        agg['num_clients']?.toString() ?? '',
        agg['total_samples']?.toString() ?? '',
        resourceMetrics['training_time_ms']?.toString() ?? '',
        resourceMetrics['battery_drain']?.toString() ?? '',
      ]);
    }
    
    // Final metrics row
    final finalMetrics = experimentData['final_metrics'] as Map<String, dynamic>? ?? {};
    csvData.add([
      'FINAL',
      '',
      finalMetrics['NDCG@10']?.toString() ?? '',
      finalMetrics['Hit@10']?.toString() ?? '',
      finalMetrics['Precision@10']?.toString() ?? '',
      finalMetrics['Recall@10']?.toString() ?? '',
      finalMetrics['mse']?.toString() ?? '',
      finalMetrics['mae']?.toString() ?? '',
      finalMetrics['accuracy']?.toString() ?? '',
      '',
      '',
      '',
      '',
    ]);
    
    // Write CSV
    final csvString = const ListToCsvConverter().convert(csvData);
    await file.writeAsString(csvString);
    
    print('[METRICS_COLLECTOR] Saved CSV summary to: ${file.path}');
    return file.path;
  }
  
  /// Get summary statistics
  Map<String, dynamic> getSummary() {
    final rounds = experimentData['rounds'] as List;
    
    if (rounds.isEmpty) {
      return {'message': 'No rounds collected yet'};
    }
    
    // Extract metrics across rounds
    final trainLosses = rounds
        .map((r) => (r as Map)['train_loss'] as double?)
        .where((loss) => loss != null)
        .cast<double>()
        .toList();
    
    final ndcgScores = rounds
        .map((r) {
          final testMetrics = (r as Map)['test_metrics'] as Map?;
          return testMetrics?['NDCG@10'] as double?;
        })
        .where((score) => score != null)
        .cast<double>()
        .toList();
    
    final hitScores = rounds
        .map((r) {
          final testMetrics = (r as Map)['test_metrics'] as Map?;
          return testMetrics?['Hit@10'] as double?;
        })
        .where((score) => score != null)
        .cast<double>()
        .toList();
    
    return {
      'experiment_id': experimentId,
      'num_rounds': rounds.length,
      'final_train_loss': trainLosses.isNotEmpty ? trainLosses.last : null,
      'final_ndcg@10': ndcgScores.isNotEmpty ? ndcgScores.last : null,
      'final_hit@10': hitScores.isNotEmpty ? hitScores.last : null,
      'best_ndcg@10': ndcgScores.isNotEmpty ? ndcgScores.reduce((a, b) => a > b ? a : b) : null,
      'best_hit@10': hitScores.isNotEmpty ? hitScores.reduce((a, b) => a > b ? a : b) : null,
      'config': experimentData['config'],
    };
  }
}

/// Create standardized experiment ID
String createExperimentId({
  double? dpEpsilon,
  double? alpha,
  int embeddingDim = 16,
  int numClients = 3,
  int? seed,
  String? deviceId,
}) {
  final parts = <String>[];
  
  if (dpEpsilon == null) {
    parts.add('dp_inf');
  } else {
    parts.add('dp_$dpEpsilon');
  }
  
  if (alpha != null) {
    parts.add('alpha_$alpha');
  }
  
  parts.add('dim_$embeddingDim');
  parts.add('clients_$numClients');
  
  if (seed != null) {
    parts.add('seed_$seed');
  }
  
  if (deviceId != null) {
    // Clean device ID for filename
    final cleanId = deviceId.replaceAll(RegExp(r'[^\w-]'), '_');
    parts.add('device_$cleanId');
  }
  
  // Add timestamp for uniqueness
  final timestamp = DateTime.now().millisecondsSinceEpoch;
  parts.add('t$timestamp');
  
  return parts.join('_');
}

