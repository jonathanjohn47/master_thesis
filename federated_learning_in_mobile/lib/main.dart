import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'services/fl_client.dart';
import 'services/api_client.dart';
import 'utils/metrics_collector.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:share_plus/share_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

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
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
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
  List<String> _logs = [];
  Map<String, dynamic>? _lastMetrics;
  Map<String, dynamic>? _resourceMetrics;
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
    final logMessage = '${DateTime.now().toString().substring(11, 19)}: $message';
    // Debug print to console
    debugPrint('[FL_CLIENT_LOG] $logMessage');
    print('[FL_CLIENT_LOG] $logMessage'); // Also use print for better visibility
    setState(() {
      _logs.insert(0, logMessage);
      if (_logs.length > 50) {
        _logs.removeLast();
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
      if (host == 'localhost' || host == '127.0.0.1' || host == '0.0.0.0' || host.isEmpty) {
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
      
      _addLog('Connecting to: $host:${uri.port}');
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
      
      _addLog('Server health check passed');
      
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
      
      _addLog('Client registered: ${_clientIdController.text}');
      if (experimentId != null) {
        _addLog('Experiment ID: $experimentId');
        _addLog('Metrics will be saved after training');
      }
      
      // Try to fetch initial model (optional - model might not be initialized yet)
      try {
        await _client!.fetchGlobalModel();
        _addLog('Global model fetched');
      } catch (e) {
        _addLog('Model not initialized yet. Initialize model on server first.');
        _addLog('You can still connect and fetch model later when starting training.');
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
      _status = 'Training...';
    });
    
    try {
      // First, make sure we have the global model (it updates numUsers and numItems)
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
      
      _addLog('Starting training round...');
      
      // Run training round
      final metrics = await _client!.runTrainingRound();
      
      _trainingRound++;
      
      // Collect metrics
      if (_metricsCollector != null) {
        final trainMetrics = metrics['train'] as Map<String, dynamic>? ?? {};
        final uploadMetrics = metrics['upload'] as Map<String, dynamic>? ?? {};
        final resourceMetrics = uploadMetrics['resource_metrics'] as Map<String, dynamic>? ?? {};
        
        _metricsCollector!.addRoundMetrics(
          roundNum: _trainingRound,
          trainLoss: (trainMetrics['loss'] as num?)?.toDouble() ?? 0.0,
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
        
        // Save results after each round
        try {
          final jsonPath = await _metricsCollector!.saveJson();
          final csvPath = await _metricsCollector!.saveCsvSummary();
          
          _addLog('Results saved:');
          _addLog('  JSON: ${jsonPath.split('/').last}');
          _addLog('  CSV: ${csvPath.split('/').last}');
        } catch (e) {
          _addLog('Warning: Failed to save results: $e');
        }
      }
      
      setState(() {
        _lastMetrics = metrics;
        _resourceMetrics = metrics['upload']?['resource_metrics'];
        _status = 'Training complete';
        _isTraining = false;
      });
      
      _addLog('Training round $_trainingRound complete');
      _addLog('Loss: ${metrics['train']?['loss']?.toStringAsFixed(4) ?? "N/A"}');
      
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
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('Federated Learning Client'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Connection Section
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Text(
                      'Server Configuration',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _serverUrlController,
                      decoration: const InputDecoration(
                        labelText: 'Server URL',
                        hintText: 'http://192.168.x.x:8000 (Use your PC IP, NOT localhost)',
                        helperText: 'Find your PC IP: ipconfig (Windows) or ifconfig (Mac/Linux)',
                        border: OutlineInputBorder(),
                      ),
                      enabled: !_isConnected,
                      keyboardType: TextInputType.url,
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _clientIdController,
                      decoration: const InputDecoration(
                        labelText: 'Client ID',
                        border: OutlineInputBorder(),
                      ),
                      enabled: !_isConnected,
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: _isConnected ? null : _connectToServer,
                      child: const Text('Connect to Server'),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Status Section
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 12,
                          height: 12,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: _isConnected ? Colors.green : Colors.grey,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Status: $_status',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: (_isConnected && !_isTraining) ? _runTrainingRound : null,
                      child: _isTraining
                          ? const Row(
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
                            )
                          : const Text('Run Training Round'),
                    ),
                    if (_metricsCollector != null && _trainingRound > 0) ...[
                      const SizedBox(height: 8),
                      OutlinedButton(
                        onPressed: _showResultsLocation,
                        child: const Text('Show Results Location'),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            
            // Metrics Section
            if (_lastMetrics != null) ...[
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text(
                        'Training Metrics',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      _buildMetricRow('Loss', _lastMetrics!['train']?['loss']?.toStringAsFixed(4) ?? 'N/A'),
                      _buildMetricRow('Samples', _lastMetrics!['train']?['samples']?.toString() ?? 'N/A'),
                      _buildMetricRow('Training Time', '${_lastMetrics!['train']?['training_time_ms'] ?? 0} ms'),
                    ],
                  ),
                ),
              ),
            ],
            
            // Resource Metrics
            if (_resourceMetrics != null) ...[
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text(
                        'Resource Metrics',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      _buildMetricRow('Battery Level', '${_resourceMetrics!['battery_level']}%'),
                      _buildMetricRow('Battery Drain', '${_resourceMetrics!['battery_drain']?.toStringAsFixed(1)}%'),
                      if (_resourceMetrics!['device_info'] != null)
                        _buildMetricRow('Device', '${_resourceMetrics!['device_info']?['model'] ?? 'Unknown'}'),
                    ],
                  ),
                ),
              ),
            ],
            
            // Logs Section
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Logs',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        TextButton(
                          onPressed: () {
                            setState(() {
                              _logs.clear();
                            });
                          },
                          child: const Text('Clear'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Container(
                      height: 200,
                      decoration: BoxDecoration(
                        color: Colors.grey[900],
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: ListView.builder(
                        reverse: true,
                        itemCount: _logs.length,
                        itemBuilder: (context, index) {
                          return Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 2.0),
                            child: Text(
                              _logs[index],
                              style: const TextStyle(
                                color: Colors.green,
                                fontFamily: 'monospace',
                                fontSize: 12,
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildMetricRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
          Text(value, style: const TextStyle(fontFamily: 'monospace')),
        ],
      ),
    );
  }
}
