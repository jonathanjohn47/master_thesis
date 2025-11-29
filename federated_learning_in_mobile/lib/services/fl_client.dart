import '../models/matrix_factorization.dart';
import '../utils/model_encoder.dart';
import '../utils/resource_monitor.dart';
import 'api_client.dart';

/// Federated Learning Client for mobile devices
class FederatedLearningClient {
  final ApiClient apiClient;
  final ResourceMonitor resourceMonitor;
  
  MatrixFactorization? model;
  String clientId;
  String serverUrl;
  
  int numUsers;
  int numItems;
  int embeddingDim;
  
  // Training configuration
  double learningRate = 0.01;
  int localEpochs = 1;
  int batchSize = 32;
  
  // Local training data: List of (user_id, item_id, rating) tuples
  List<List<dynamic>> localData = [];
  
  FederatedLearningClient({
    required this.clientId,
    required this.serverUrl,
    required this.numUsers,
    required this.numItems,
    this.embeddingDim = 16,
  })  : apiClient = ApiClient(serverUrl: serverUrl),
        resourceMonitor = ResourceMonitor();
  
  /// Initialize client (check server, register, initialize monitoring)
  Future<void> initialize() async {
    print('[FL_CLIENT] Initializing client: $clientId');
    try {
      // Check server health
      print('[FL_CLIENT] Checking server health...');
      await apiClient.healthCheck();
      print('[FL_CLIENT] Server health check passed');
      
      // Register with server
      print('[FL_CLIENT] Registering client...');
      await apiClient.register(clientId);
      print('[FL_CLIENT] Client registered successfully');
      
      // Initialize resource monitoring
      print('[FL_CLIENT] Initializing resource monitoring...');
      await resourceMonitor.initialize();
      print('[FL_CLIENT] Resource monitoring initialized');
    } catch (e, stackTrace) {
      print('[FL_CLIENT_ERROR] Initialization failed: $e');
      print('[FL_CLIENT_ERROR] Stack trace: $stackTrace');
      rethrow;
    }
  }
  
  /// Load local training data
  void loadLocalData(List<List<dynamic>> data) {
    localData = data; // data: [[user_id, item_id, rating], ...]
  }
  
  /// Fetch global model from server
  Future<void> fetchGlobalModel() async {
    print('[FL_CLIENT] Fetching global model...');
    try {
      final response = await apiClient.fetchGlobalParams();
      
      // Extract model config
      final modelConfig = response['model_config'] as Map<String, dynamic>;
      numUsers = modelConfig['num_users'] as int;
      numItems = modelConfig['num_items'] as int;
      embeddingDim = modelConfig['embedding_dim'] as int;
      print('[FL_CLIENT] Model config: numUsers=$numUsers, numItems=$numItems, embeddingDim=$embeddingDim');
      
      // Decode parameters
      final paramsJson = response['params'] as List;
      print('[FL_CLIENT] Decoding ${paramsJson.length} parameter tensors...');
      final stateDict = ModelEncoder.jsonParamsToModel(
        paramsJson.map((p) => p as Map<String, dynamic>).toList(),
      );
      print('[FL_CLIENT] Parameters decoded successfully');
      
      // Create and load model
      print('[FL_CLIENT] Creating model instance...');
      model = MatrixFactorization(
        numUsers: numUsers,
        numItems: numItems,
        embeddingDim: embeddingDim,
      );
      model!.loadStateDict(stateDict);
      print('[FL_CLIENT] Model loaded successfully');
    } catch (e, stackTrace) {
      print('[FL_CLIENT_ERROR] Fetch global model failed: $e');
      print('[FL_CLIENT_ERROR] Stack trace: $stackTrace');
      rethrow;
    }
  }
  
  /// Train model locally using local data
  Future<Map<String, dynamic>> trainLocal() async {
    print('[FL_CLIENT] Starting local training...');
    if (model == null) {
      print('[FL_CLIENT_ERROR] Model not initialized');
      throw StateError('Model not initialized. Call fetchGlobalModel() first.');
    }
    
    if (localData.isEmpty) {
      print('[FL_CLIENT] No local data available, returning empty metrics');
      return {
        'loss': 0.0,
        'samples': 0,
        'epochs': 0,
      };
    }
    
    print('[FL_CLIENT] Training with ${localData.length} samples, $localEpochs epochs, batch size $batchSize');
    
    final startTime = DateTime.now();
    double totalLoss = 0.0;
    int numBatches = 0;
    
    // Simple SGD training (one epoch for mobile efficiency)
    for (int epoch = 0; epoch < localEpochs; epoch++) {
      // Shuffle data
      localData.shuffle();
      
      // Process in batches
      for (int i = 0; i < localData.length; i += batchSize) {
        final batchEnd = (i + batchSize < localData.length) ? i + batchSize : localData.length;
        final batch = localData.sublist(i, batchEnd);
        
        // Compute gradients (simplified - full implementation would use proper backprop)
        double batchLoss = 0.0;
        
        // Initialize gradients
        final userGrad = List.generate(
          numUsers,
          (_) => List.filled(embeddingDim, 0.0),
        );
        final itemGrad = List.generate(
          numItems,
          (_) => List.filled(embeddingDim, 0.0),
        );
        
        // Compute gradients for batch
        for (var sample in batch) {
          final userId = sample[0] as int;
          final itemId = sample[1] as int;
          final rating = (sample[2] as num).toDouble();
          
          // Validate IDs are in range before accessing embeddings
          if (userId < 0 || userId >= numUsers || itemId < 0 || itemId >= numItems) {
            print('[FL_CLIENT_ERROR] Invalid IDs in sample: user=$userId (valid: 0-${numUsers-1}), item=$itemId (valid: 0-${numItems-1})');
            continue; // Skip invalid samples
          }
          
          // Forward pass
          final prediction = model!.predict(userId, itemId);
          final error = prediction - rating;
          batchLoss += error * error;
          
          // Backward pass (simplified gradient)
          final userEmb = model!.userEmbeddings[userId];
          final itemEmb = model!.itemEmbeddings[itemId];
          
          for (int j = 0; j < embeddingDim; j++) {
            userGrad[userId][j] += error * itemEmb[j];
            itemGrad[itemId][j] += error * userEmb[j];
          }
        }
        
        // Average gradients
        final actualBatchSize = batch.length;
        for (int u = 0; u < numUsers; u++) {
          for (int j = 0; j < embeddingDim; j++) {
            userGrad[u][j] /= actualBatchSize;
          }
        }
        for (int i = 0; i < numItems; i++) {
          for (int j = 0; j < embeddingDim; j++) {
            itemGrad[i][j] /= actualBatchSize;
          }
        }
        
        // Update parameters
        model!.updateParameters(userGrad, itemGrad, learningRate);
        
        totalLoss += batchLoss / actualBatchSize;
        numBatches++;
      }
    }
    
    final trainingTime = DateTime.now().difference(startTime).inMilliseconds;
    final avgLoss = numBatches > 0 ? totalLoss / numBatches : 0.0;
    
    print('[FL_CLIENT] Training complete: loss=$avgLoss, samples=${localData.length}, time=${trainingTime}ms');
    
    return {
      'loss': avgLoss,
      'samples': localData.length,
      'epochs': localEpochs,
      'training_time_ms': trainingTime,
    };
  }
  
  /// Upload local model parameters to server
  Future<Map<String, dynamic>> uploadParams() async {
    print('[FL_CLIENT] Uploading parameters...');
    if (model == null) {
      print('[FL_CLIENT_ERROR] Model not initialized');
      throw StateError('Model not initialized');
    }
    
    print('[FL_CLIENT] Getting model state dict...');
    final stateDict = model!.getStateDict();
    print('[FL_CLIENT] Encoding parameters to JSON...');
    final paramsJson = ModelEncoder.modelToJsonParams(stateDict);
    print('[FL_CLIENT] Encoded ${paramsJson.length} parameter tensors');
    
    // Get resource metrics
    print('[FL_CLIENT] Getting resource metrics...');
    final metrics = await resourceMonitor.getMetrics();
    print('[FL_CLIENT] Resource metrics: $metrics');
    
    print('[FL_CLIENT] Uploading to server...');
    final response = await apiClient.uploadParams(
      clientId: clientId,
      params: paramsJson,
      sampleCount: localData.length,
    );
    print('[FL_CLIENT] Upload successful');
    
    return {
      ...response,
      'resource_metrics': metrics,
    };
  }
  
  /// Execute one complete federated learning round
  Future<Map<String, dynamic>> runTrainingRound() async {
    print('[FL_CLIENT] ========== Starting training round ==========');
    try {
      // 1. Fetch global model (will throw if not initialized)
      print('[FL_CLIENT] Step 1/3: Fetching global model...');
      await fetchGlobalModel();
      
      // 2. Train locally
      print('[FL_CLIENT] Step 2/3: Training locally...');
      final trainMetrics = await trainLocal();
      
      // 3. Upload parameters
      print('[FL_CLIENT] Step 3/3: Uploading parameters...');
      final uploadMetrics = await uploadParams();
      
      print('[FL_CLIENT] ========== Training round complete ==========');
      return {
        'train': trainMetrics,
        'upload': uploadMetrics,
      };
    } catch (e, stackTrace) {
      print('[FL_CLIENT_ERROR] Training round failed: $e');
      print('[FL_CLIENT_ERROR] Stack trace: $stackTrace');
      rethrow;
    }
  }
}

