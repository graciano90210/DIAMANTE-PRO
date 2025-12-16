class ApiConfig {
  // URL de tu backend en Heroku (URL directa)
  static const String baseUrl = 'https://diamante-pro-1951dcdb66df.herokuapp.com/api/v1';
  
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
