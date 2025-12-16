class Prestamo {
  final int id;
  final int clienteId;
  final String clienteNombre;
  final double monto;
  final double valorCuota;
  final int numeroCuotas;
  final int cuotasPagadas;
  final int cuotasAtrasadas;
  final double saldoPendiente;
  final String fechaInicio;
  final String? fechaFinalizacion;
  final String estado;
  final String? observaciones;

  Prestamo({
    required this.id,
    required this.clienteId,
    required this.clienteNombre,
    required this.monto,
    required this.valorCuota,
    required this.numeroCuotas,
    required this.cuotasPagadas,
    required this.cuotasAtrasadas,
    required this.saldoPendiente,
    required this.fechaInicio,
    this.fechaFinalizacion,
    required this.estado,
    this.observaciones,
  });

  factory Prestamo.fromJson(Map<String, dynamic> json) {
    return Prestamo(
      id: json['id'],
      clienteId: json['cliente_id'],
      clienteNombre: json['cliente_nombre'] ?? '',
      monto: (json['monto'] ?? 0).toDouble(),
      valorCuota: (json['valor_cuota'] ?? 0).toDouble(),
      numeroCuotas: json['numero_cuotas'] ?? 0,
      cuotasPagadas: json['cuotas_pagadas'] ?? 0,
      cuotasAtrasadas: json['cuotas_atrasadas'] ?? 0,
      saldoPendiente: (json['saldo_pendiente'] ?? 0).toDouble(),
      fechaInicio: json['fecha_inicio'] ?? '',
      fechaFinalizacion: json['fecha_finalizacion'],
      estado: json['estado'] ?? 'activo',
      observaciones: json['observaciones'],
    );
  }

  bool get estaAlDia => cuotasAtrasadas == 0;
  bool get estaMora => cuotasAtrasadas > 0;
  bool get moraGrave => cuotasAtrasadas > 3;
}
