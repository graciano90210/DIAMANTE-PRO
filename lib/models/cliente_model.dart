class Cliente {
  final int id;
  final String nombre;
  final String telefono;
  final String? whatsapp;
  final String direccion;
  final String? cedula;
  final bool activo;

  Cliente({
    required this.id,
    required this.nombre,
    required this.telefono,
    this.whatsapp,
    required this.direccion,
    this.cedula,
    required this.activo,
  });

  factory Cliente.fromJson(Map<String, dynamic> json) {
    return Cliente(
      id: json['id'],
      nombre: json['nombre'] ?? '',
      telefono: json['telefono'] ?? '',
      whatsapp: json['whatsapp'],
      direccion: json['direccion'] ?? '',
      cedula: json['cedula'],
      activo: json['activo'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nombre': nombre,
      'telefono': telefono,
      'whatsapp': whatsapp,
      'direccion': direccion,
      'cedula': cedula,
      'activo': activo,
    };
  }
}
