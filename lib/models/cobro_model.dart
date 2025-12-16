class Cobro {
  final int? id;
  final int prestamoId;
  final String clienteNombre;
  final double monto;
  final String fecha;
  final String? observaciones;
  final int cobradorId;

  Cobro({
    this.id,
    required this.prestamoId,
    required this.clienteNombre,
    required this.monto,
    required this.fecha,
    this.observaciones,
    required this.cobradorId,
  });

  factory Cobro.fromJson(Map<String, dynamic> json) {
    return Cobro(
      id: json['id'],
      prestamoId: json['prestamo_id'],
      clienteNombre: json['cliente_nombre'] ?? '',
      monto: (json['monto'] ?? 0).toDouble(),
      fecha: json['fecha'] ?? '',
      observaciones: json['observaciones'],
      cobradorId: json['cobrador_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'prestamo_id': prestamoId,
      'monto': monto,
      'fecha': fecha,
      'observaciones': observaciones,
    };
  }
}
