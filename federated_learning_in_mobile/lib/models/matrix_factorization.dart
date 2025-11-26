/// Matrix Factorization model for movie recommendations
/// Pure Dart implementation compatible with PyTorch server model

class MatrixFactorization {
  final int numUsers;
  final int numItems;
  final int embeddingDim;
  
  // Embedding matrices: [num_users x embedding_dim], [num_items x embedding_dim]
  late List<List<double>> userEmbeddings;
  late List<List<double>> itemEmbeddings;
  
  MatrixFactorization({
    required this.numUsers,
    required this.numItems,
    required this.embeddingDim,
  }) {
    // Initialize embeddings with small random values
    userEmbeddings = _initializeEmbeddings(numUsers, embeddingDim);
    itemEmbeddings = _initializeEmbeddings(numItems, embeddingDim);
  }
  
  /// Initialize embedding matrix with small random values (similar to PyTorch)
  List<List<double>> _initializeEmbeddings(int size, int dim) {
    final embeddings = <List<double>>[];
    final random = DateTime.now().millisecondsSinceEpoch; // Simple seed
    
    for (int i = 0; i < size; i++) {
      final row = <double>[];
      for (int j = 0; j < dim; j++) {
        // Generate random value between -0.01 and 0.01
        final value = ((random + i * dim + j) % 2000 - 1000) / 100000.0;
        row.add(value);
      }
      embeddings.add(row);
    }
    return embeddings;
  }
  
  /// Forward pass: predict rating for user-item pair
  double predict(int userId, int itemId) {
    if (userId >= numUsers || itemId >= numItems || userId < 0 || itemId < 0) {
      throw ArgumentError('Invalid user_id or item_id');
    }
    
    final userEmb = userEmbeddings[userId];
    final itemEmb = itemEmbeddings[itemId];
    
    // Dot product: sum(user_emb[i] * item_emb[i])
    double result = 0.0;
    for (int i = 0; i < embeddingDim; i++) {
      result += userEmb[i] * itemEmb[i];
    }
    
    return result;
  }
  
  /// Predict ratings for multiple user-item pairs (batch prediction)
  List<double> predictBatch(List<int> userIds, List<int> itemIds) {
    if (userIds.length != itemIds.length) {
      throw ArgumentError('userIds and itemIds must have same length');
    }
    
    final predictions = <double>[];
    for (int i = 0; i < userIds.length; i++) {
      predictions.add(predict(userIds[i], itemIds[i]));
    }
    return predictions;
  }
  
  /// Get model state dictionary (for serialization)
  Map<String, dynamic> getStateDict() {
    return {
      'user_embedding.weight': userEmbeddings,
      'item_embedding.weight': itemEmbeddings,
    };
  }
  
  /// Load model state from dictionary (for deserialization)
  void loadStateDict(Map<String, dynamic> stateDict) {
    userEmbeddings = List<List<double>>.from(
      stateDict['user_embedding.weight'].map((row) => 
        List<double>.from(row.map((val) => val.toDouble()))
      )
    );
    itemEmbeddings = List<List<double>>.from(
      stateDict['item_embedding.weight'].map((row) => 
        List<double>.from(row.map((val) => val.toDouble()))
      )
    );
  }
  
  /// Get all trainable parameters (flattened for gradient computation)
  List<List<List<double>>> getParameters() {
    return [userEmbeddings, itemEmbeddings];
  }
  
  /// Update parameters (used during training)
  void updateParameters(List<List<double>> userGrad, List<List<double>> itemGrad, double learningRate) {
    // Gradient descent update
    for (int i = 0; i < numUsers; i++) {
      for (int j = 0; j < embeddingDim; j++) {
        userEmbeddings[i][j] -= learningRate * userGrad[i][j];
      }
    }
    
    for (int i = 0; i < numItems; i++) {
      for (int j = 0; j < embeddingDim; j++) {
        itemEmbeddings[i][j] -= learningRate * itemGrad[i][j];
      }
    }
  }
}

