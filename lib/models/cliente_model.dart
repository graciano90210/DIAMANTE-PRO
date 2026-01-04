class Cliente {
  final int id;
  final String nombre;
  final String? documento;
  final String telefono;
  final String? whatsapp;
  final String direccionNegocio;
  final double? gpsLatitud;
  final double? gpsLongitud;
  final bool esVip;

  Cliente({
    required this.id,
    required this.nombre,
    this.documento,
    required this.telefono,
    this.whatsapp,
    required this.direccionNegocio,
    this.gpsLatitud,
    this.gpsLongitud,
    this.esVip = false,
  });

  factory Cliente.fromJson(Map<String, dynamic> json) {
    return Cliente(
      id: json['id'],
      nombre: json['nombre'] ?? '',
      documento: json['documento'],
      telefono: json['telefono'] ?? '',
      whatsapp: json['whatsapp'],
      direccionNegocio: json['direccion_negocio'] ?? '',
      gpsLatitud: json['gps_latitud'] != null ? (json['gps_latitud'] as num).toDouble() : null,
      gpsLongitud: json['gps_longitud'] != null ? (json['gps_longitud'] as num).toDouble() : null,
      esVip: json['es_vip'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nombre': nombre,
      'documento': documento,
      'telefono': telefono,
      'whatsapp': whatsapp,
      'direccion_negocio': direccionNegocio,
      'gps_latitud': gpsLatitud,
      'gps_longitud': gpsLongitud,
      'es_vip': esVip,
    };
  }

  bool get tieneUbicacion => gpsLatitud != null && gpsLongitud != null;
}
