import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';

class ApiService {
  // Método GET que retorna Map
  Future<Map<String, dynamic>> get(
    String endpoint, {
    Map<String, String>? headers,
  }) async {
    try {
      final url = Uri.parse('${ApiConfig.baseUrl}$endpoint');
      final response = await http.get(
        url,
        headers: headers ?? ApiConfig.defaultHeaders,
      ).timeout(ApiConfig.timeout);

      return _handleResponse(response);
    } catch (e) {
      throw Exception('Error en petición GET: $e');
    }
  }

  // Método GET que retorna List
  Future<List<dynamic>> getList(
    String endpoint, {
    Map<String, String>? headers,
  }) async {
    try {
      final url = Uri.parse('${ApiConfig.baseUrl}$endpoint');
      final response = await http.get(
        url,
        headers: headers ?? ApiConfig.defaultHeaders,
      ).timeout(ApiConfig.timeout);

      return _handleListResponse(response);
    } catch (e) {
      throw Exception('Error en petición GET: $e');
    }
  }

  // Método POST
  Future<Map<String, dynamic>> post(
    String endpoint, {
    Map<String, dynamic>? body,
    Map<String, String>? headers,
  }) async {
    try {
      final url = Uri.parse('${ApiConfig.baseUrl}$endpoint');
      final response = await http.post(
        url,
        headers: headers ?? ApiConfig.defaultHeaders,
        body: json.encode(body ?? {}),
      ).timeout(ApiConfig.timeout);

      return _handleResponse(response);
    } catch (e) {
      throw Exception('Error en petición POST: $e');
    }
  }

  // Método PUT
  Future<Map<String, dynamic>> put(
    String endpoint, {
    Map<String, dynamic>? body,
    Map<String, String>? headers,
  }) async {
    try {
      final url = Uri.parse('${ApiConfig.baseUrl}$endpoint');
      final response = await http.put(
        url,
        headers: headers ?? ApiConfig.defaultHeaders,
        body: json.encode(body ?? {}),
      ).timeout(ApiConfig.timeout);

      return _handleResponse(response);
    } catch (e) {
      throw Exception('Error en petición PUT: $e');
    }
  }

  // Método DELETE
  Future<Map<String, dynamic>> delete(
    String endpoint, {
    Map<String, String>? headers,
  }) async {
    try {
      final url = Uri.parse('${ApiConfig.baseUrl}$endpoint');
      final response = await http.delete(
        url,
        headers: headers ?? ApiConfig.defaultHeaders,
      ).timeout(ApiConfig.timeout);

      return _handleResponse(response);
    } catch (e) {
      throw Exception('Error en petición DELETE: $e');
    }
  }

  // Manejo de respuestas Map
  Map<String, dynamic> _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      final decoded = json.decode(response.body);
      if (decoded is Map<String, dynamic>) {
        return decoded;
      } else {
        throw Exception('Se esperaba un objeto pero se recibió: ${decoded.runtimeType}');
      }
    } else {
      throw Exception(
        'Error ${response.statusCode}: ${response.body}',
      );
    }
  }

  // Manejo de respuestas List
  List<dynamic> _handleListResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      final decoded = json.decode(response.body);
      if (decoded is List) {
        return decoded;
      } else {
        throw Exception('Se esperaba una lista pero se recibió: ${decoded.runtimeType}');
      }
    } else {
      throw Exception(
        'Error ${response.statusCode}: ${response.body}',
      );
    }
  }
}
