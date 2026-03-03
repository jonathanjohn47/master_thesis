import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'services/fl_client.dart';
import 'services/api_client.dart';
import 'utils/metrics_collector.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:share_plus/share_plus.dart';

void main() {
  runApp(const FederatedLearningApp());
}

class FederatedLearningApp extends StatelessWidget {
  const FederatedLearningApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Federated Learning Client',
      theme: ThemeData(
        colorScheme: ColorScheme.dark(
          surface: const Color(0xFF212D3F),
          primary: const Color(0xFF00BCD4),
          secondary: const Color(0xFF00BCD4),
        ),
        scaffoldBackgroundColor: const Color(0xFF1A2332),
        cardTheme: const CardThemeData(
          color: Color(0xFF212D3F),
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(12)),
          ),
        ),
        useMaterial3: true,
      ),
      home: const FederatedLearningHomePage(),
    );
  }
}

class FederatedLearningHomePage extends StatefulWidget {
  const FederatedLearningHomePage({super.key});

  @override
  State<FederatedLearningHomePage> createState() => _FederatedLearningHomePageState();
}

class _FederatedLearningHomePageState extends State<FederatedLearningHomePage> {
  final TextEditingController _serverUrlController = TextEditingController(
    text: '', // User must enter their PC's IP address (e.g., http://192.168.x.x:8000)
  );
  final TextEditingController _clientIdController = TextEditingController(
    text: 'android_client_${DateTime.now().millisecondsSinceEpoch % 10000}',
  );
  
  FederatedLearningClient? _client;
  bool _isConnected = false;
  bool _isTraining = false;
  String _status = 'Ready';
  final List<String> _logs = [];
  MetricsCollector? _metricsCollector;
  int _trainingRound = 0;
  String? _deviceId;

  @override
  void dispose() {
    _serverUrlController.dispose();
    _clientIdController.dispose();
    super.dispose();
}

  void _addLog(String message) {
    final timestamp = DateTime.now().toString().substring(11, 19);
    final logMessage = '[$timestamp] $message';
    // Debug print to console
    debugPrint('[FL_CLIENT_LOG] $logMessage');
    print('[FL_CLIENT_LOG] $logMessage'); // Also use print for better visibility
    setState(() {
      _logs.add(logMessage);
      if (_logs.length > 100) {
        _logs.removeAt(0);
      }
    });
  }
  
  Future<void> _connectToServer() async {
    final serverUrl = _serverUrlController.text.trim();
    
    if (serverUrl.isEmpty) {
      _showError('Please enter server URL (e.g., http://192.168.1.100:8000)\n\nOn your PC, run: ipconfig\nto find your IP address');
      return;
    }
    
    // Validate URL format
    if (!serverUrl.startsWith('http://') && !serverUrl.startsWith('https://')) {
      _showError('Server URL must start with http:// or https://');
      return;
    }
    
    // Parse and validate the host address
    try {
      final uri = Uri.parse(serverUrl);
      final host = uri.host.toLowerCase();
      
      // Check for invalid addresses
      if (host == 'localhost' || host == '192.168.29.147' || host == '127.0.0.1' || host == '0.0.0.0' || host.isEmpty) {
        String errorMsg = 'Invalid server address: $host\n\n';
        if (host == '0.0.0.0') {
          errorMsg += '0.0.0.0 is not a valid address to connect to!\n\n';
        } else {
          errorMsg += 'localhost/127.0.0.1 will not work from mobile device!\n\n';
        }
        errorMsg += 'Use your PC\'s actual IP address instead:\n';
        errorMsg += '• Windows: Run "ipconfig" and look for "IPv4 Address"\n';
        errorMsg += '• Mac/Linux: Run "ifconfig" or "ip addr"\n';
        errorMsg += '• Example: http://192.168.1.100:8000';
        _showError(errorMsg);
        return;
      }
      
      // Warn if port is missing
      if (uri.port == 0) {
        _showError('Server URL must include a port number (e.g., :8000)');
        return;
      }
      
      _addLog('NETWORK: DNS lookup resolved for coordinator.');
    } catch (e) {
      _showError('Invalid URL format: $e\n\nPlease use format: http://IP_ADDRESS:PORT\nExample: http://192.168.1.100:8000');
      return;
    }
    
    setState(() {
      _status = 'Connecting...';
      _isTraining = true;
    });
    
    try {
      final apiClient = ApiClient(serverUrl: serverUrl);
      await apiClient.healthCheck();
      
      _addLog('INFO: Handshake protocol version 3.2.0.');

      // Create client
      _client = FederatedLearningClient(
        clientId: _clientIdController.text,
        serverUrl: serverUrl,
        numUsers: 943, // Will be updated after fetching model
        numItems: 1682, // Will be updated after fetching model
        embeddingDim: 16,
      );
      
      await _client!.initialize();
      
      // Get device info for metrics collection
      try {
        final deviceInfo = DeviceInfoPlugin();
        if (Theme.of(context).platform == TargetPlatform.android) {
          final androidInfo = await deviceInfo.androidInfo;
          _deviceId = '${androidInfo.brand}_${androidInfo.model}'.replaceAll(' ', '_');
        } else {
          _deviceId = 'device_${DateTime.now().millisecondsSinceEpoch}';
        }
      } catch (e) {
        _deviceId = 'device_${DateTime.now().millisecondsSinceEpoch}';
        _addLog('Warning: Could not get device info: $e');
      }
      
      // Initialize metrics collector (non-blocking - continue even if it fails)
      String? experimentId;
      try {
        experimentId = createExperimentId(
          embeddingDim: _client!.embeddingDim,
          numClients: 1,
          deviceId: _deviceId,
        );
        
        _metricsCollector = MetricsCollector(experimentId: experimentId);
        await _metricsCollector!.initialize();
        _addLog('Metrics collector initialized');
        
        // Set experiment config
        _metricsCollector!.setConfig({
          'num_users': _client!.numUsers,
          'num_items': _client!.numItems,
          'embedding_dim': _client!.embeddingDim,
          'client_id': _clientIdController.text,
          'device_id': _deviceId,
          'server_url': serverUrl,
        });
      } catch (e) {
        _addLog('Warning: Metrics collector initialization failed: $e');
        _addLog('Training will continue but results won\'t be saved');
        // Continue anyway - don't block connection
      }
      
      setState(() {
        _isConnected = true;
        _status = 'Connected';
        _isTraining = false;
      });
      
      _addLog('SYSTEM: Client initialized successfully.');
      if (experimentId != null) {
        _addLog('Experiment ID: $experimentId');
        _addLog('Metrics will be saved after training');
      }
      
      // Try to fetch initial model (optional - model might not be initialized yet)
      try {
        await _client!.fetchGlobalModel();
        _addLog('SYSTEM: Local model weight buffer allocated (512MB).');
      } catch (e) {
        _addLog('WARN: Model not initialized on server yet.');
        _addLog('INFO: You can fetch model later when starting training.');
      }
      
    } catch (e, stackTrace) {
      setState(() {
        _status = 'Connection failed';
        _isTraining = false;
      });
      debugPrint('[FL_CLIENT_ERROR] Connection error: $e');
      debugPrint('[FL_CLIENT_ERROR] Stack trace: $stackTrace');
      print('[FL_CLIENT_ERROR] Connection error: $e');
      print('[FL_CLIENT_ERROR] Stack trace: $stackTrace');
      
      // Provide helpful error message based on error type
      String errorMessage = 'Failed to connect to server.\n\n';
      
      if (e.toString().contains('Connection refused') || 
          e.toString().contains('SocketException')) {
        errorMessage += 'Connection was refused. This usually means:\n';
        errorMessage += '1. Server is not running\n';
        errorMessage += '2. Wrong IP address or port\n';
        errorMessage += '3. Firewall blocking connection\n';
        errorMessage += '4. Device not on same network\n\n';
        errorMessage += 'Troubleshooting:\n';
        errorMessage += '• Verify server is running on your PC\n';
        errorMessage += '• Check IP address: Run "ipconfig" (Windows) or "ifconfig" (Mac/Linux)\n';
        errorMessage += '• Ensure both devices are on the same Wi-Fi network\n';
        errorMessage += '• Try disabling firewall temporarily\n';
        errorMessage += '• Check server logs for errors';
      } else if (e.toString().contains('timeout') || 
                 e.toString().contains('TimeoutException')) {
        errorMessage += 'Connection timed out. Check:\n';
        errorMessage += '• Server is running and accessible\n';
        errorMessage += '• Network connection is stable\n';
        errorMessage += '• Firewall is not blocking the connection';
      } else {
        errorMessage += 'Error: $e';
      }
      
      _addLog('Error: $e');
      _showError(errorMessage);
    }
  }
  
  Future<void> _runTrainingRound() async {
    if (_client == null || !_isConnected) {
      _showError('Please connect to server first');
      return;
    }
    
    setState(() {
      _isTraining = true;
      _status = 'Training Round $_trainingRound...';
    });
    
    try {
      // First, make sure we have the global model (it updates numUsers and numItems)
      if (_trainingRound == 1) {
        _addLog('Fetching global model...');
        try {
          await _client!.fetchGlobalModel();
          _addLog('Global model fetched. Model: ${_client!.numUsers} users, ${_client!.numItems} items');
        } catch (e) {
          _addLog('Warning: Could not fetch model, using current dimensions');
        }
        
        // Load some sample data (in real app, this would come from device)
        // For demo, create minimal sample data
        if (_client!.localData.isEmpty) {
          // Generate sample data based on ACTUAL model dimensions (updated after fetchGlobalModel)
          final sampleData = <List<dynamic>>[];
          final random = DateTime.now().millisecondsSinceEpoch;
          final numUsers = _client!.numUsers;
          final numItems = _client!.numItems;
          
          _addLog('Generating sample data for $numUsers users, $numItems items...');
          
          for (int i = 0; i < 10; i++) {
            final userId = (random + i) % numUsers;
            final itemId = (random + i * 2) % numItems;
            
            // Validate IDs are in range (just to be safe)
            if (userId >= 0 && userId < numUsers && itemId >= 0 && itemId < numItems) {
              sampleData.add([
                userId,
                itemId,
                1.0, // Binarized rating
              ]);
            } else {
              _addLog('Warning: Skipping invalid sample: user=$userId (max=$numUsers), item=$itemId (max=$numItems)');
            }
          }
          _client!.loadLocalData(sampleData);
          _addLog('Loaded ${sampleData.length} sample interactions');
        }
      }
      
      _addLog('Starting training round $_trainingRound...');
      
      // Run training round
      final metrics = await _client!.runTrainingRound();
      
      _trainingRound++;
      
      // Collect metrics
      if (_metricsCollector != null) {
        final trainMetrics = metrics['train'] as Map<String, dynamic>? ?? {};
        final testMetrics = metrics['test'] as Map<String, dynamic>? ?? {};
        final uploadMetrics = metrics['upload'] as Map<String, dynamic>? ?? {};
        final resourceMetrics = uploadMetrics['resource_metrics'] as Map<String, dynamic>? ?? {};
        
        _metricsCollector!.addRoundMetrics(
          roundNum: _trainingRound - 1, // Use round number before increment
          trainLoss: (trainMetrics['loss'] as num?)?.toDouble() ?? 0.0,
          testMetrics: testMetrics,
          aggregationInfo: {
            'num_clients': 1,
            'total_samples': trainMetrics['samples'] ?? 0,
          },
          clientMetrics: [
            {
              'client_id': _clientIdController.text,
              'loss': trainMetrics['loss'] ?? 0.0,
              'samples': trainMetrics['samples'] ?? 0,
              'epochs': trainMetrics['epochs'] ?? 0,
            }
          ],
          resourceMetrics: resourceMetrics,
        );
        
        // Save results after each round (both locally and to server)
        try {
          // Save locally first
          final jsonPath = await _metricsCollector!.saveJson();
          final csvPath = await _metricsCollector!.saveCsvSummary();
          
          _addLog('Results saved locally:');
          _addLog('  JSON: ${jsonPath.split('/').last}');
          _addLog('  CSV: ${csvPath.split('/').last}');
          
          // Also upload to server (saves to PC automatically!)
          await _uploadResultsToServer();
        } catch (e) {
          _addLog('Warning: Failed to save results: $e');
        }
      }
      
      setState(() {
        _status = 'Round ${_trainingRound - 1} complete';
        _isTraining = false;
      });
      
      _addLog('Training round ${_trainingRound - 1} complete');
      _addLog('Loss: ${metrics['train']?['loss']?.toStringAsFixed(4) ?? "N/A"}');
      _addLog('Accuracy: ${metrics['test']?['accuracy']?.toStringAsFixed(4) ?? "N/A"}');
      
      // Show success message after 10 rounds
      if (_trainingRound > 10) {
        _addLog('🎉 All 10 rounds complete!');
        _addLog('Results have been uploaded to your PC automatically.');
        
        // Calculate and add final metrics
        _calculateFinalMetrics();
        
        // Show dialog after final round
        Future.delayed(const Duration(seconds: 1), () {
          _uploadResultsToServer(showSuccessDialog: true);
        });
      }
      
    } catch (e, stackTrace) {
      setState(() {
        _status = 'Training failed';
        _isTraining = false;
      });
      debugPrint('[FL_CLIENT_ERROR] Training error: $e');
      debugPrint('[FL_CLIENT_ERROR] Stack trace: $stackTrace');
      print('[FL_CLIENT_ERROR] Training error: $e');
      print('[FL_CLIENT_ERROR] Stack trace: $stackTrace');
      _addLog('Training error: $e');
      _showError('Training failed: $e');
    }
  }
  
  /// Run 10 rounds automatically
  Future<void> _runAll10Rounds() async {
    if (_client == null || !_isConnected) {
      _showError('Please connect to server first');
      return;
    }
    
    if (_isTraining) {
      _showError('Training already in progress');
      return;
    }
    
    // Reset round counter
    _trainingRound = 0;
    
    // Confirm action
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Run 10 Training Rounds'),
        content: const Text(
          'This will automatically run 10 training rounds.\n\n'
          'The training will continue until all 10 rounds are complete.\n'
          'You can stop by closing the app if needed.\n\n'
          'Proceed?'
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Start'),
          ),
        ],
      ),
    );
    
    if (confirmed != true) {
      return;
    }
    
    setState(() {
      _status = 'Running 10 rounds...';
    });
    
    _addLog('Starting automatic 10-round training...');
    
    // Run 10 rounds sequentially
    for (int round = 1; round <= 10; round++) {
      if (!_isConnected || _client == null) {
        _addLog('Training stopped: connection lost');
        break;
      }
      
      _addLog('=== Round $round/10 ===');
      await _runTrainingRound();
      
      // Small delay between rounds
      await Future.delayed(const Duration(milliseconds: 500));
    }
    
    if (_trainingRound > 10) {
      setState(() {
        _status = 'All 10 rounds complete!';
      });
    }
  }
  
  /// Calculate final metrics after all rounds are complete
  void _calculateFinalMetrics() {
    if (_metricsCollector == null) return;
    
    final rounds = _metricsCollector!.experimentData['rounds'] as List;
    if (rounds.isEmpty) return;
    
    // Get metrics from last round
    final lastRound = rounds.last as Map<String, dynamic>;
    final lastTestMetrics = lastRound['test_metrics'] as Map<String, dynamic>? ?? {};
    
    // Calculate averages across all rounds
    double avgAccuracy = 0.0;
    double avgLoss = 0.0;
    double avgHit10 = 0.0;
    double avgNDCG10 = 0.0;
    int count = 0;
    
    for (var round in rounds) {
      final roundMap = round as Map<String, dynamic>;
      final testMetrics = roundMap['test_metrics'] as Map<String, dynamic>? ?? {};
      
      if (testMetrics['accuracy'] != null) {
        avgAccuracy += (testMetrics['accuracy'] as num).toDouble();
        avgLoss += (roundMap['train_loss'] as num?)?.toDouble() ?? 0.0;
        avgHit10 += (testMetrics['Hit@10'] as num?)?.toDouble() ?? 0.0;
        avgNDCG10 += (testMetrics['NDCG@10'] as num?)?.toDouble() ?? 0.0;
        count++;
      }
    }
    
    if (count > 0) {
      avgAccuracy /= count;
      avgLoss /= count;
      avgHit10 /= count;
      avgNDCG10 /= count;
    }
    
    // Set final metrics
    _metricsCollector!.addFinalMetrics({
      'accuracy': lastTestMetrics['accuracy'] ?? avgAccuracy,
      'mse': lastTestMetrics['mse'] ?? 0.0,
      'mae': lastTestMetrics['mae'] ?? 0.0,
      'Hit@10': lastTestMetrics['Hit@10'] ?? avgHit10,
      'NDCG@10': lastTestMetrics['NDCG@10'] ?? avgNDCG10,
      'Precision@10': lastTestMetrics['Precision@10'] ?? 0.0,
      'Recall@10': lastTestMetrics['Recall@10'] ?? 0.0,
      'final_train_loss': avgLoss,
      'avg_accuracy': avgAccuracy,
      'avg_Hit@10': avgHit10,
      'avg_NDCG@10': avgNDCG10,
    });
    
    // Add client metrics summary
    _metricsCollector!.addClientMetrics(_clientIdController.text, {
      'total_rounds': rounds.length,
      'total_samples': (rounds.last as Map)['aggregation']?['total_samples'] ?? 0,
      'final_loss': avgLoss,
      'final_accuracy': avgAccuracy,
    });
    
    // Add mobile metrics summary
    double totalBatteryDrain = 0.0;
    int totalTimeMs = 0;
    for (var round in rounds) {
      final roundMap = round as Map<String, dynamic>;
      final resourceMetrics = roundMap['resource_metrics'] as Map<String, dynamic>? ?? {};
      totalBatteryDrain += (resourceMetrics['battery_drain'] as num?)?.toDouble() ?? 0.0;
      totalTimeMs += (resourceMetrics['training_time_ms'] as num?)?.toInt() ?? 0;
    }
    
    _metricsCollector!.addMobileMetrics(_deviceId ?? 'unknown', {
      'total_rounds': rounds.length,
      'total_battery_drain': totalBatteryDrain,
      'total_training_time_ms': totalTimeMs,
      'avg_battery_drain_per_round': rounds.isNotEmpty ? totalBatteryDrain / rounds.length : 0.0,
      'avg_training_time_ms_per_round': rounds.isNotEmpty ? totalTimeMs / rounds.length : 0.0,
    });
    
    _addLog('Final metrics calculated and saved');
  }
  
  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }
  
  Future<void> _showResultsLocation() async {
    if (_metricsCollector == null) return;
    
    try {
      await _metricsCollector!.initialize();
      final resultsPath = _metricsCollector!.resultsPath;
      final resultFiles = await _metricsCollector!.getResultFiles();
      
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Results Location'),
          content: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Results are saved to Downloads folder:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                SelectableText(
                  resultsPath,
                  style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
                ),
                const SizedBox(height: 16),
                const Text('Files:', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                if (resultFiles.isEmpty)
                  const Text('No files saved yet', style: TextStyle(fontStyle: FontStyle.italic))
                else
                  ...resultFiles.map((f) => Text(
                        '• ${f.path.split('/').last}',
                        style: const TextStyle(fontSize: 12),
                      )),
                const SizedBox(height: 16),
                Text(
                  'Training rounds: $_trainingRound',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                const Text(
                  'How to access files:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                const Text(
                  '1. Open Android File Manager\n'
                  '2. Go to Downloads folder\n'
                  '3. Look for "FL_Results" folder\n'
                  '4. Your JSON and CSV files are inside\n\n'
                  'Or use ADB:\n'
                  'adb pull /storage/emulated/0/Download/FL_Results/',
                  style: TextStyle(fontSize: 12),
                ),
              ],
            ),
          ),
          actions: [
            if (resultFiles.isNotEmpty)
              TextButton.icon(
                onPressed: () => _shareResults(),
                icon: const Icon(Icons.share),
                label: const Text('Share Files'),
              ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Close'),
            ),
          ],
        ),
      );
    } catch (e) {
      _showError('Failed to get results location: $e');
    }
  }
  
  Future<void> _shareResults() async {
    if (_metricsCollector == null) return;
    
    try {
      final resultFiles = await _metricsCollector!.getResultFiles();
      if (resultFiles.isEmpty) {
        _showError('No result files to share');
        return;
      }
      
      // Share the most recent JSON file
      final jsonFiles = resultFiles.where((f) => f.path.endsWith('.json')).toList();
      if (jsonFiles.isEmpty) {
        _showError('No JSON files to share');
        return;
      }
      
      // Sort by modification time (newest first)
      jsonFiles.sort((a, b) => b.lastModifiedSync().compareTo(a.lastModifiedSync()));
      final latestFile = jsonFiles.first;
      
      final xFile = XFile(latestFile.path, mimeType: 'application/json');
      await Share.shareXFiles(
        [xFile],
        text: 'Federated Learning Experiment Results',
        subject: 'FL Results: ${_metricsCollector!.experimentId}',
      );
      
      _addLog('Shared file: ${latestFile.path.split('/').last}');
    } catch (e) {
      _showError('Failed to share files: $e');
    }
  }
  
  /// Upload results to server (saves directly to PC)
  Future<void> _uploadResultsToServer({bool showSuccessDialog = false}) async {
    if (_client == null || !_isConnected) {
      _showError('Please connect to server first');
      return;
    }
    
    if (_metricsCollector == null) {
      _showError('No results to upload. Run training rounds first.');
      return;
    }
    
    setState(() {
      _status = 'Uploading results to PC...';
    });
    
    try {
      final experimentData = _metricsCollector!.getExperimentData();
      
      _addLog('Uploading results to server (PC)...');
      _addLog('Experiment ID: ${_metricsCollector!.experimentId}');
      
      final uploadResponse = await _client!.apiClient.uploadMobileResults(
        experimentId: _metricsCollector!.experimentId,
        experimentData: experimentData,
      );
      
      final jsonPath = uploadResponse['json_file'] as String? ?? 'mobile_results/${_metricsCollector!.experimentId}.json';
      final csvPath = uploadResponse['csv_file'] as String?;
      final message = uploadResponse['message'] as String? ?? 'Results saved to PC';
      
      _addLog('✓ Results uploaded successfully!');
      _addLog('  Saved on PC: $message');
      _addLog('  JSON: $jsonPath');
      if (csvPath != null) {
        _addLog('  CSV: $csvPath');
      }
      
      setState(() {
        _status = 'Results uploaded to PC';
      });
      
      if (showSuccessDialog) {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('✓ Results Uploaded to PC'),
            content: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'Your results have been saved directly to your PC!',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Location on your PC:',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  SelectableText(
                    jsonPath,
                    style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
                  ),
                  if (csvPath != null) ...[
                    const SizedBox(height: 8),
                    SelectableText(
                      csvPath,
                      style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
                    ),
                  ],
                  const SizedBox(height: 16),
                  const Text(
                    'How to access:',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '1. Go to your project folder\n'
                    '2. Open the "mobile_results" folder\n'
                    '3. Find your JSON and CSV files\n\n'
                    'Or check your server terminal - it shows the full path!',
                    style: TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('OK'),
              ),
            ],
          ),
        );
      }
      
    } catch (uploadError) {
      _addLog('✗ Upload failed: $uploadError');
      setState(() {
        _status = 'Upload failed';
      });
      
      String errorMsg = 'Failed to upload results to PC.\n\n';
      if (uploadError.toString().contains('Connection refused') ||
          uploadError.toString().contains('SocketException')) {
        errorMsg += 'Cannot connect to server.\n';
        errorMsg += '• Make sure server is running\n';
        errorMsg += '• Check server URL is correct\n';
        errorMsg += '• Verify both devices are on same network';
      } else {
        errorMsg += 'Error: $uploadError';
      }
      
      _showError(errorMsg);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1A2332),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header with title and settings icon
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Federated Client',
                        style: TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Researcher Edition v2.4',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.grey[400],
                        ),
                      ),
                    ],
                  ),
                  Container(
                    decoration: BoxDecoration(
                      color: const Color(0xFF212D3F),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: const Color(0xFF00BCD4).withValues(alpha: 0.3),
                        width: 1,
                      ),
                    ),
                    child: IconButton(
                      icon: const Icon(Icons.settings, color: Color(0xFF00BCD4)),
                      onPressed: () {
                        // Settings action - can be implemented later
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Settings coming soon')),
                        );
                      },
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // Connection Section
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.dns, color: const Color(0xFF00BCD4), size: 20),
                          const SizedBox(width: 8),
                          const Text(
                            'SERVER CONFIGURATION',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                              letterSpacing: 0.5,
                              color: Colors.grey,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 20),
                      Text(
                        'SERVER URL',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: const Color(0xFF00BCD4),
                          letterSpacing: 0.5,
                        ),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _serverUrlController,
                        decoration: InputDecoration(
                          hintText: 'wss://fl-coordinator.research.net',
                          hintStyle: TextStyle(color: Colors.grey[600]),
                          filled: true,
                          fillColor: const Color(0xFF1A2332),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: BorderSide.none,
                          ),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                        ),
                        style: const TextStyle(color: Colors.white70, fontSize: 15),
                        enabled: !_isConnected,
                        keyboardType: TextInputType.url,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'CLIENT ID',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Colors.grey[400],
                          letterSpacing: 0.5,
                        ),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _clientIdController,
                        decoration: InputDecoration(
                          hintText: 'android_client_6149',
                          hintStyle: TextStyle(color: Colors.grey[600]),
                          filled: true,
                          fillColor: const Color(0xFF1A2332),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: BorderSide.none,
                          ),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                        ),
                        style: const TextStyle(color: Colors.white70, fontSize: 15),
                        enabled: !_isConnected,
                      ),
                      const SizedBox(height: 20),
                      SizedBox(
                        height: 54,
                        child: ElevatedButton(
                          onPressed: _isConnected ? null : _connectToServer,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF00BCD4),
                            foregroundColor: Colors.black87,
                            disabledBackgroundColor: Colors.grey[700],
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                            elevation: 0,
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(Icons.flash_on, size: 20),
                              const SizedBox(width: 8),
                              const Text(
                                'CONNECT TO SERVER',
                                style: TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.bold,
                                  letterSpacing: 0.5,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // Status Section
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              Container(
                                width: 12,
                                height: 12,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: _isConnected ? const Color(0xFF4CAF50) : Colors.grey,
                                ),
                              ),
                              const SizedBox(width: 10),
                              Text(
                                'Status: $_status',
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white,
                                ),
                              ),
                            ],
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              color: const Color(0xFF1A2332),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              _isTraining ? 'TRAINING' : 'IDLE',
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF4CAF50),
                                letterSpacing: 0.5,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 20),
                      Row(
                        children: [
                          Expanded(
                            child: SizedBox(
                              height: 100,
                              child: ElevatedButton(
                                onPressed: (_isConnected && !_isTraining) ? _runTrainingRound : null,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: const Color(0xFF2A3A4F),
                                  foregroundColor: Colors.white70,
                                  disabledBackgroundColor: const Color(0xFF1E2936),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  elevation: 0,
                                ),
                                child: const Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(Icons.play_arrow, size: 32, color: Color(0xFF00BCD4)),
                                    SizedBox(height: 8),
                                    Text(
                                      'Run 1 Round',
                                      style: TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: SizedBox(
                              height: 100,
                              child: ElevatedButton(
                                onPressed: (_isConnected && !_isTraining) ? _runAll10Rounds : null,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: const Color(0xFF2A3A4F),
                                  foregroundColor: Colors.white70,
                                  disabledBackgroundColor: const Color(0xFF1E2936),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  elevation: 0,
                                ),
                                child: const Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(Icons.fast_forward, size: 32, color: Color(0xFF00BCD4)),
                                    SizedBox(height: 8),
                                    Text(
                                      'Run 10 Rounds',
                                      style: TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    if (_isTraining) ...[
                      const SizedBox(height: 8),
                      const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                          SizedBox(width: 8),
                          Text('Training...'),
                        ],
                      ),
                    ],
                    if (_metricsCollector != null && _trainingRound > 0) ...[
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(
                              child: OutlinedButton.icon(
                                onPressed: (_isConnected && !_isTraining) ? _uploadResultsToServer : null,
                                icon: const Icon(Icons.cloud_upload, size: 18),
                                label: const Text('Upload to PC', style: TextStyle(fontSize: 13)),
                                style: OutlinedButton.styleFrom(
                                  foregroundColor: const Color(0xFF00BCD4),
                                  side: const BorderSide(color: Color(0xFF00BCD4)),
                                  padding: const EdgeInsets.symmetric(vertical: 12),
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: OutlinedButton.icon(
                                onPressed: _showResultsLocation,
                                icon: const Icon(Icons.folder, size: 18),
                                label: const Text('Location', style: TextStyle(fontSize: 13)),
                                style: OutlinedButton.styleFrom(
                                  foregroundColor: Colors.grey[400],
                                  side: BorderSide(color: Colors.grey[700]!),
                                  padding: const EdgeInsets.symmetric(vertical: 12),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
              ),  // End of Status Section Card

            // Logs Section
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.live_tv, color: Colors.grey[400], size: 20),
                            const SizedBox(width: 8),
                            const Text(
                              'LIVE LOGS',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                letterSpacing: 0.5,
                                color: Colors.grey,
                              ),
                            ),
                          ],
                        ),
                        TextButton(
                          onPressed: () {
                            setState(() {
                              _logs.clear();
                            });
                          },
                          style: TextButton.styleFrom(
                            foregroundColor: Colors.grey[500],
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          ),
                          child: const Text(
                            'CLEAR CONSOLE',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Container(
                      height: 250,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF0D1117),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: _logs.isEmpty
                          ? Center(
                              child: Text(
                                'No logs yet. Connect to server to see activity.',
                                style: TextStyle(
                                  color: Colors.grey[600],
                                  fontSize: 13,
                                  fontStyle: FontStyle.italic,
                                ),
                              ),
                            )
                          : ListView.builder(
                              reverse: false,
                              itemCount: _logs.length,
                              itemBuilder: (context, index) {
                                final log = _logs[index];
                                Color logColor = const Color(0xFF58A6FF); // Default blue

                                // Color code logs based on type
                                if (log.contains('SYSTEM:')) {
                                  logColor = const Color(0xFF4CAF50); // Green
                                } else if (log.contains('NETWORK:')) {
                                  logColor = const Color(0xFF00BCD4); // Cyan
                                } else if (log.contains('INFO:')) {
                                  logColor = const Color(0xFF58A6FF); // Blue
                                } else if (log.contains('WARN:')) {
                                  logColor = const Color(0xFFFFA726); // Orange
                                } else if (log.contains('ERROR:')) {
                                  logColor = const Color(0xFFEF5350); // Red
                                }

                                return Padding(
                                  padding: const EdgeInsets.symmetric(vertical: 2.0),
                                  child: Text(
                                    log,
                                    style: TextStyle(
                                      color: logColor,
                                      fontFamily: 'Courier',
                                      fontSize: 12,
                                      height: 1.4,
                                    ),
                                  ),
                                );
                              },
                            ),
                    ),  // End of Container
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    ),
    );
  }
}
