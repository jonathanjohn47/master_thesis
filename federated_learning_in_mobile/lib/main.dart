import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'services/fl_client.dart';
import 'services/api_client.dart';

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
  
  @override
  void dispose() {
    _serverUrlController.dispose();
    _clientIdController.dispose();
    super.dispose();
  }
  
  void _addLog(String message) {
    setState(() {
      _logs.insert(0, '${DateTime.now().toString().substring(11, 19)}: $message');
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
    
    // Warn if using localhost
    if (serverUrl.contains('localhost') || serverUrl.contains('127.0.0.1')) {
      _showError('localhost/127.0.0.1 will not work from mobile device!\n\nUse your PC\'s IP address instead (e.g., http://192.168.1.100:8000)\n\nRun "ipconfig" on your PC to find your IP');
      return;
    }
    
    // Validate URL format
    if (!serverUrl.startsWith('http://') && !serverUrl.startsWith('https://')) {
      _showError('Server URL must start with http:// or https://');
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
      
      setState(() {
        _isConnected = true;
        _status = 'Connected';
        _isTraining = false;
      });
      
      _addLog('Client registered: ${_clientIdController.text}');
      
      // Try to fetch initial model (optional - model might not be initialized yet)
      try {
        await _client!.fetchGlobalModel();
        _addLog('Global model fetched');
      } catch (e) {
        _addLog('Model not initialized yet. Initialize model on server first.');
        _addLog('You can still connect and fetch model later when starting training.');
      }
      
    } catch (e) {
      setState(() {
        _status = 'Connection failed';
        _isTraining = false;
      });
      _addLog('Error: $e');
      _showError('Failed to connect: $e');
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
      // Load some sample data (in real app, this would come from device)
      // For demo, create minimal sample data
      if (_client!.localData.isEmpty) {
        // Generate sample data based on model dimensions
        final sampleData = <List<dynamic>>[];
        final random = DateTime.now().millisecondsSinceEpoch;
        for (int i = 0; i < 10; i++) {
          sampleData.add([
            (random + i) % _client!.numUsers,
            (random + i * 2) % _client!.numItems,
            1.0, // Binarized rating
          ]);
        }
        _client!.loadLocalData(sampleData);
        _addLog('Loaded ${sampleData.length} sample interactions');
      }
      
      _addLog('Starting training round...');
      
      // Run training round
      final metrics = await _client!.runTrainingRound();
      
      setState(() {
        _lastMetrics = metrics;
        _resourceMetrics = metrics['upload']?['resource_metrics'];
        _status = 'Training complete';
        _isTraining = false;
      });
      
      _addLog('Training round complete');
      _addLog('Loss: ${metrics['train']?['loss']?.toStringAsFixed(4) ?? "N/A"}');
      
    } catch (e) {
      setState(() {
        _status = 'Training failed';
        _isTraining = false;
      });
      _addLog('Training error: $e');
      _showError('Training failed: $e');
    }
  }
  
  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
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
