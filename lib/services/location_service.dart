import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';

class LocationService {
  /// Verifica si los permisos de ubicación están otorgados
  Future<bool> checkPermissions() async {
    final status = await Permission.location.status;
    return status.isGranted;
  }

  /// Solicita permisos de ubicación al usuario
  Future<bool> requestPermissions() async {
    final status = await Permission.location.request();
    return status.isGranted;
  }

  /// Obtiene la ubicación actual del dispositivo
  /// Retorna null si no se puede obtener
  Future<Position?> getCurrentLocation() async {
    try {
      // Verificar si el servicio de ubicación está habilitado
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        print('LocationService: Servicio de ubicación deshabilitado');
        return null;
      }

      // Verificar permisos
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          print('LocationService: Permisos de ubicación denegados');
          return null;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        print('LocationService: Permisos de ubicación denegados permanentemente');
        return null;
      }

      // Obtener ubicación actual
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 10),
      );

      print('LocationService: Ubicación obtenida: ${position.latitude}, ${position.longitude}');
      return position;
    } catch (e) {
      print('LocationService: Error al obtener ubicación: $e');
      return null;
    }
  }

  /// Obtiene la distancia en metros entre dos puntos
  double getDistanceBetween(
    double startLatitude,
    double startLongitude,
    double endLatitude,
    double endLongitude,
  ) {
    return Geolocator.distanceBetween(
      startLatitude,
      startLongitude,
      endLatitude,
      endLongitude,
    );
  }

  /// Formatea las coordenadas para enviar al backend
  Map<String, double> formatCoordinates(Position position) {
    return {
      'latitud': position.latitude,
      'longitud': position.longitude,
      'precision': position.accuracy,
    };
  }
}
