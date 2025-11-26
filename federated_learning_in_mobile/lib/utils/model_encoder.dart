import 'dart:convert';
import 'package:flutter/foundation.dart';

/// Utilities for encoding/decoding model parameters to/from JSON format
/// Compatible with Python server's portable JSON format

class ModelEncoder {
  /// Convert model parameters to portable JSON format (compatible with server)
  /// Returns list of parameter dictionaries with base64-encoded data
  static List<Map<String, dynamic>> modelToJsonParams(
    Map<String, dynamic> stateDict,
  ) {
    final params = <Map<String, dynamic>>[];
    
    stateDict.forEach((name, value) {
      if (value is List<List<double>>) {
        // Convert 2D list to flat array and then to base64
        final flatList = <double>[];
        var shape = <int>[];
        
        if (value.isNotEmpty) {
          shape = [value.length, value[0].length];
          for (var row in value) {
            flatList.addAll(row);
          }
        }
        
        // Convert to Float32 bytes (4 bytes per float)
        final bytes = <int>[];
        for (var val in flatList) {
          // Convert double to Float32 bytes (simplified - actual implementation
          // should use proper Float32 encoding)
          final bytes32 = _doubleToFloat32Bytes(val);
          bytes.addAll(bytes32);
        }
        
        // Encode to base64
        final base64Data = base64Encode(bytes);
        
        params.add({
          'name': name,
          'shape': shape,
          'dtype': 'float32',
          'data': base64Data,
        });
      }
    });
    
    return params;
  }
  
  /// Convert Float32 bytes (4 bytes) from double
  static List<int> _doubleToFloat32Bytes(double value) {
    // Simplified: convert double to 4-byte representation
    // For production, use proper Float32 encoding
    final bytes = ByteData(4);
    bytes.setFloat32(0, value.toDouble(), Endian.little);
    return bytes.buffer.asUint8List().toList();
  }
  
  /// Decode JSON parameters into model state dictionary
  static Map<String, dynamic> jsonParamsToModel(List<Map<String, dynamic>> params) {
    final stateDict = <String, dynamic>{};
    
    for (var param in params) {
      final name = param['name'] as String;
      final shape = List<int>.from(param['shape'] as List);
      final dtype = param['dtype'] as String;
      final base64Data = param['data'] as String;
      
      if (dtype == 'float32') {
        // Decode base64
        final bytes = base64Decode(base64Data);
        
        // Convert bytes to Float32 values
        final values = <double>[];
        for (int i = 0; i < bytes.length; i += 4) {
          if (i + 4 <= bytes.length) {
            final byteData = ByteData.view(
              bytes.buffer,
              bytes.offsetInBytes + i,
              4,
            );
            values.add(byteData.getFloat32(0, Endian.little));
          }
        }
        
        // Reshape to 2D list
        if (shape.length == 2) {
          final matrix = <List<double>>[];
          for (int i = 0; i < shape[0]; i++) {
            final row = <double>[];
            for (int j = 0; j < shape[1]; j++) {
              final idx = i * shape[1] + j;
              if (idx < values.length) {
                row.add(values[idx]);
              }
            }
            matrix.add(row);
          }
          stateDict[name] = matrix;
        }
      }
    }
    
    return stateDict;
  }
}

