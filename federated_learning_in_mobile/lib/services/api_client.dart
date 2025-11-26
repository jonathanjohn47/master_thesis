import 'dart:convert';
import 'package:http/http.dart' as http;

/// API client for communicating with the federated learning server
class ApiClient {
  final String _baseUrl;
  
  ApiClient({required String serverUrl}) 
      : _baseUrl = serverUrl.endsWith('/') 
          ? serverUrl.substring(0, serverUrl.length - 1) 
          : serverUrl;
  
  /// Get normalized base URL (without trailing slash)
  String get baseUrl => _baseUrl;
  
  /// Check if server is available
  Future<Map<String, dynamic>> healthCheck() async {
    final url = Uri.parse('$_baseUrl/healthz');
    final response = await http.get(url);
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('Server health check failed: ${response.statusCode}');
    }
  }
  
  /// Register client with server
  Future<Map<String, dynamic>> register(String clientId) async {
    final url = Uri.parse('$_baseUrl/register');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'client_id': clientId}),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('Registration failed: ${response.statusCode} - ${response.body}');
    }
  }
  
  /// Fetch global model parameters from server
  Future<Map<String, dynamic>> fetchGlobalParams() async {
    final url = Uri.parse('$_baseUrl/global-params-json');
    final response = await http.get(url);
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return data;
    } else if (response.statusCode == 404) {
      // Model not initialized on server
      throw Exception('Model not initialized on server. Please initialize the model first:\n\n'
          'Run on your PC: curl -X POST "$_baseUrl/init-model?num_users=943&num_items=1682&embedding_dim=16"\n\n'
          'Or use the API docs at: $_baseUrl/docs');
    } else {
      throw Exception('Failed to fetch global params: ${response.statusCode} - ${response.body}');
    }
  }
  
  /// Upload client model parameters to server
  Future<Map<String, dynamic>> uploadParams({
    required String clientId,
    required List<Map<String, dynamic>> params,
    required int sampleCount,
  }) async {
    final url = Uri.parse('$_baseUrl/upload-params-json');
    final payload = {
      'client_id': clientId,
      'params': params,
      'sample_count': sampleCount,
    };
    
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('Upload failed: ${response.statusCode} - ${response.body}');
    }
  }
  
  /// Upload resource metrics (CPU, memory, battery, etc.)
  Future<void> uploadResourceMetrics({
    required String clientId,
    required Map<String, dynamic> metrics,
  }) async {
    // This endpoint should be added to server.py
    // For now, we'll include it in upload-params or create a separate endpoint
    // Implementation depends on server capability
  }
}

