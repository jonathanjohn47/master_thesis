import 'dart:convert';
import 'dart:io';
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
    print('[API_CLIENT] Health check: GET $url');
    print('[API_CLIENT] Parsed host: ${url.host}, port: ${url.port}');
    
    // Validate host before attempting connection
    if (url.host.isEmpty || url.host == '0.0.0.0') {
      throw Exception('Invalid server address: ${url.host}. Use your PC\'s actual IP address (e.g., 192.168.1.100)');
    }
    
    try {
      final response = await http.get(url).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Connection timeout: Server did not respond within 10 seconds. Check if server is running and accessible.');
        },
      );
      print('[API_CLIENT] Health check response: ${response.statusCode}');
      print('[API_CLIENT] Health check headers: ${response.headers}');
      print('[API_CLIENT] Health check body (raw): ${response.body}');
      print('[API_CLIENT] Health check body length: ${response.body.length}');
      
      if (response.statusCode == 200) {
        try {
          final decoded = jsonDecode(response.body) as Map<String, dynamic>;
          print('[API_CLIENT] Health check parsed successfully: $decoded');
          return decoded;
        } catch (jsonError) {
          print('[API_CLIENT_ERROR] JSON decode failed: $jsonError');
          print('[API_CLIENT_ERROR] Response body that failed to parse: ${response.body}');
          throw Exception('Server returned invalid JSON. Expected JSON but got: ${response.body.substring(0, 100)}...');
        }
      } else {
        throw Exception('Server health check failed: ${response.statusCode} - ${response.body}');
      }
    } on SocketException catch (e) {
      print('[API_CLIENT_ERROR] Socket error: $e');
      throw Exception('Cannot connect to server at ${url.host}:${url.port}. '
          'Check that:\n'
          '1. Server is running\n'
          '2. IP address is correct\n'
          '3. Port is correct\n'
          '4. Both devices are on the same network');
    } catch (e, stackTrace) {
      print('[API_CLIENT_ERROR] Health check failed: $e');
      print('[API_CLIENT_ERROR] Stack trace: $stackTrace');
      rethrow;
    }
  }
  
  /// Register client with server
  Future<Map<String, dynamic>> register(String clientId) async {
    final url = Uri.parse('$_baseUrl/register');
    print('[API_CLIENT] Register: POST $url');
    print('[API_CLIENT] Register payload: client_id=$clientId');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'client_id': clientId}),
      );
      print('[API_CLIENT] Register response: ${response.statusCode}');
      print('[API_CLIENT] Register body: ${response.body}');
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception('Registration failed: ${response.statusCode} - ${response.body}');
      }
    } catch (e, stackTrace) {
      print('[API_CLIENT_ERROR] Registration failed: $e');
      print('[API_CLIENT_ERROR] Stack trace: $stackTrace');
      rethrow;
    }
  }
  
  /// Fetch global model parameters from server
  Future<Map<String, dynamic>> fetchGlobalParams() async {
    final url = Uri.parse('$_baseUrl/global-params-json');
    print('[API_CLIENT] Fetch global params: GET $url');
    try {
      final response = await http.get(url);
      print('[API_CLIENT] Fetch global params response: ${response.statusCode}');
      print('[API_CLIENT] Response body length: ${response.body.length}');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        print('[API_CLIENT] Model config: ${data['model_config']}');
        print('[API_CLIENT] Params count: ${(data['params'] as List?)?.length ?? 'N/A'}');
        return data;
      } else if (response.statusCode == 404) {
        // Model not initialized on server
        print('[API_CLIENT_ERROR] Model not initialized (404)');
        throw Exception('Model not initialized on server. Please initialize the model first:\n\n'
            'Run on your PC: curl -X POST "$_baseUrl/init-model?num_users=943&num_items=1682&embedding_dim=16"\n\n'
            'Or use the API docs at: $_baseUrl/docs');
      } else {
        throw Exception('Failed to fetch global params: ${response.statusCode} - ${response.body}');
      }
    } catch (e, stackTrace) {
      print('[API_CLIENT_ERROR] Fetch global params failed: $e');
      print('[API_CLIENT_ERROR] Stack trace: $stackTrace');
      rethrow;
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
    print('[API_CLIENT] Upload params: POST $url');
    print('[API_CLIENT] Upload payload: client_id=$clientId, sample_count=$sampleCount, params_count=${params.length}');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      );
      print('[API_CLIENT] Upload response: ${response.statusCode}');
      print('[API_CLIENT] Upload body: ${response.body}');
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception('Upload failed: ${response.statusCode} - ${response.body}');
      }
    } catch (e, stackTrace) {
      print('[API_CLIENT_ERROR] Upload failed: $e');
      print('[API_CLIENT_ERROR] Stack trace: $stackTrace');
      rethrow;
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
  
  /// Upload mobile experiment results to server (saves to PC)
  Future<Map<String, dynamic>> uploadMobileResults({
    required String experimentId,
    required Map<String, dynamic> experimentData,
  }) async {
    final url = Uri.parse('$_baseUrl/upload-mobile-results');
    final payload = {
      'experiment_id': experimentId,
      'experiment_data': experimentData,
    };
    
    print('[API_CLIENT] Upload mobile results: POST $url');
    print('[API_CLIENT] Experiment ID: $experimentId');
    
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      );
      
      print('[API_CLIENT] Upload results response: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception('Upload failed: ${response.statusCode} - ${response.body}');
      }
    } catch (e, stackTrace) {
      print('[API_CLIENT_ERROR] Upload results failed: $e');
      print('[API_CLIENT_ERROR] Stack trace: $stackTrace');
      rethrow;
    }
  }
}

