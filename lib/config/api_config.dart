class ApiConfig {
  // URL de tu backend con la ruta de la API
  static const String baseUrl = 'http://localhost:5001/api/v1';
  
  // Endpoints
  static const String login = '/login';
  static const String clientes = '/clientes';
  static const String prestamos = '/prestamos';
  static const String cobros = '/cobros';
  static const String rutas = '/rutas';
  
  // Timeout para peticiones
  static const Duration timeout = Duration(seconds: 30);
  
  // Headers comunes
  static Map<String, String> get defaultHeaders => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  
  static Map<String, String> getAuthHeaders(String token) => {
    ...defaultHeaders,
    'Authorization': 'Bearer $token',
  };
}
