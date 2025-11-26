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
    // Check server health
    await apiClient.healthCheck();
    
    // Register with server
    await apiClient.register(clientId);
    
    // Initialize resource monitoring
    await resourceMonitor.initialize();
  }
  
  /// Load local training data
  void loadLocalData(List<List<dynamic>> data) {
    localData = data; // data: [[user_id, item_id, rating], ...]
  }
  
  /// Fetch global model from server
  Future<void> fetchGlobalModel() async {
    final response = await apiClient.fetchGlobalParams();
    
    // Extract model config
    final modelConfig = response['model_config'] as Map<String, dynamic>;
    numUsers = modelConfig['num_users'] as int;
    numItems = modelConfig['num_items'] as int;
    embeddingDim = modelConfig['embedding_dim'] as int;
    
    // Decode parameters
    final paramsJson = response['params'] as List;
    final stateDict = ModelEncoder.jsonParamsToModel(
      paramsJson.map((p) => p as Map<String, dynamic>).toList(),
    );
    
    // Create and load model
    model = MatrixFactorization(
      numUsers: numUsers,
      numItems: numItems,
      embeddingDim: embeddingDim,
    );
    model!.loadStateDict(stateDict);
  }
  
  /// Train model locally using local data
  Future<Map<String, dynamic>> trainLocal() async {
    if (model == null) {
      throw StateError('Model not initialized. Call fetchGlobalModel() first.');
    }
    
    if (localData.isEmpty) {
      return {
        'loss': 0.0,
        'samples': 0,
        'epochs': 0,
      };
    }
    
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
    
    return {
      'loss': avgLoss,
      'samples': localData.length,
      'epochs': localEpochs,
      'training_time_ms': trainingTime,
    };
  }
  
  /// Upload local model parameters to server
  Future<Map<String, dynamic>> uploadParams() async {
    if (model == null) {
      throw StateError('Model not initialized');
    }
    
    final stateDict = model!.getStateDict();
    final paramsJson = ModelEncoder.modelToJsonParams(stateDict);
    
    // Get resource metrics
    final metrics = await resourceMonitor.getMetrics();
    
    final response = await apiClient.uploadParams(
      clientId: clientId,
      params: paramsJson,
      sampleCount: localData.length,
    );
    
    return {
      ...response,
      'resource_metrics': metrics,
    };
  }
  
  /// Execute one complete federated learning round
  Future<Map<String, dynamic>> runTrainingRound() async {
    // 1. Fetch global model (will throw if not initialized)
    await fetchGlobalModel();
    
    // 2. Train locally
    final trainMetrics = await trainLocal();
    
    // 3. Upload parameters
    final uploadMetrics = await uploadParams();
    
    return {
      'train': trainMetrics,
      'upload': uploadMetrics,
    };
  }
}

