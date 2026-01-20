class Cliente {
  final int id;
  final String nombre;
  final String? documento;
  final String tipoDocumento;
  final DateTime? fechaNacimiento;
  final String telefono;
  final String? email;
  final String? whatsapp;
  final String direccionNegocio;
  final String? cepNegocio;
  final String? direccionCasa;
  final String? cepCasa;
  final double? gpsLatitud;
  final double? gpsLongitud;
  final bool esVip;

  Cliente({
    required this.id,
    required this.nombre,
    this.documento,
    this.tipoDocumento = 'CPF',
    this.fechaNacimiento,
    required this.telefono,
    this.email,
    this.whatsapp,
    required this.direccionNegocio,
    this.cepNegocio,
    this.direccionCasa,
    this.cepCasa,
    this.gpsLatitud,
    this.gpsLongitud,
    this.esVip = false,
  });

  factory Cliente.fromJson(Map<String, dynamic> json) {
    return Cliente(
      id: json['id'],
      nombre: json['nombre'] ?? '',
      documento: json['documento'],
      tipoDocumento: json['tipo_documento'] ?? 'CPF',
      fechaNacimiento: json['fecha_nacimiento'] != null ? DateTime.tryParse(json['fecha_nacimiento']) : null,
      telefono: json['telefono'] ?? '',
      email: json['email'],
      whatsapp: json['whatsapp'],
      direccionNegocio: json['direccion_negocio'] ?? '',
      cepNegocio: json['cep_negocio'],
      direccionCasa: json['direccion_casa'],
      cepCasa: json['cep_casa'],
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
      'tipo_documento': tipoDocumento,
      'fecha_nacimiento': fechaNacimiento?.toIso8601String().split('T')[0],
      'telefono': telefono,
      'email': email,
      'whatsapp': whatsapp,
      'direccion_negocio': direccionNegocio,
      'cep_negocio': cepNegocio,
      'direccion_casa': direccionCasa,
      'cep_casa': cepCasa,
      'direccion': direccionNegocio, // Alias para compatibilidad con backend POST
      'gps_latitud': gpsLatitud,
      'gps_longitud': gpsLongitud,
      'es_vip': esVip,
    };
  }

  bool get tieneUbicacion => gpsLatitud != null && gpsLongitud != null;
}
