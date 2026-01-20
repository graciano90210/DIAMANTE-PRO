class ApiConfig {
  // URL de tu backend con la ruta de la API
  static const String baseUrl = 'https://diamante-pro-1951dcdb66df.herokuapp.com/api/v1'; // Producción
  // static const String baseUrl = 'http://localhost:5001/api/v1'; // Local Windows/Web
  // static const String baseUrl = 'http://10.0.2.2:5001/api/v1'; // Local Android Emulator
  
  // Endpoints
  static const String login = '/login';
  static const String clientes = '/cobrador/clientes';
  static const String prestamos = '/cobrador/prestamos';
  static const String cobros = '/cobrador/ruta-cobro';
  static const String registrarPago = '/cobrador/registrar-pago';
  static const String estadisticas = '/cobrador/estadisticas';
  static const String rutas = '/cobrador/rutas';
  static const String nuevoCobro = '/cobrador/registrar-pago';
  static const String gastos = '/cobrador/gastos';
  
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
