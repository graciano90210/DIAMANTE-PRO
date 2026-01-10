class Prestamo {
  final int id;
  final int clienteId;
  final String clienteNombre;
  final double montoPrestado;
  final double montoAPagar;
  final double valorCuota;
  final int numeroCuotas;
  final int cuotasPagadas;
  final int cuotasAtrasadas;
  final double saldoActual;
  final String fechaInicio;
  final String? fechaUltimoPago;
  final int diasAtraso;
  final String frecuencia;
  final String estado;
  final String moneda;

  Prestamo({
    required this.id,
    required this.clienteId,
    required this.clienteNombre,
    required this.montoPrestado,
    required this.montoAPagar,
    required this.valorCuota,
    required this.numeroCuotas,
    required this.cuotasPagadas,
    required this.cuotasAtrasadas,
    required this.saldoActual,
    required this.fechaInicio,
    this.fechaUltimoPago,
    required this.diasAtraso,
    required this.frecuencia,
    required this.estado,
    this.moneda = 'COP', // Valor por defecto
  });

  factory Prestamo.fromJson(Map<String, dynamic> json) {
    // Extraer datos del cliente si viene anidado
    final cliente = json['cliente'] as Map<String, dynamic>?;
    
    return Prestamo(
      id: json['id'] ?? 0,
      clienteId: cliente?['id'] ?? json['cliente_id'] ?? 0,
      clienteNombre: cliente?['nombre'] ?? json['cliente_nombre'] ?? '',
      montoPrestado: (json['monto_prestado'] as num?)?.toDouble() ?? 0.0,
      montoAPagar: (json['monto_a_pagar'] as num?)?.toDouble() ?? 0.0,
      valorCuota: (json['valor_cuota'] as num?)?.toDouble() ?? 0.0,
      numeroCuotas: json['numero_cuotas'] as int? ?? 0,
      cuotasPagadas: json['cuotas_pagadas'] as int? ?? 0,
      cuotasAtrasadas: json['cuotas_atrasadas'] as int? ?? 0,
      saldoActual: (json['saldo_actual'] as num?)?.toDouble() ?? 0.0,
      fechaInicio: json['fecha_inicio'] as String? ?? '',
      fechaUltimoPago: json['fecha_ultimo_pago'] as String?,
      diasAtraso: json['dias_atraso'] as int? ?? 0,
      frecuencia: json['frecuencia'] as String? ?? 'DIARIO',
      estado: json['estado'] as String? ?? 'ACTIVO',
      moneda: json['moneda'] as String? ?? 'COP',
    );
  }

  bool get estaAlDia => cuotasAtrasadas == 0;
  bool get estaMora => cuotasAtrasadas > 0;
  bool get moraGrave => cuotasAtrasadas > 3;
  bool get estaPagado => estado == 'PAGADO';
  
  double get porcentajePagado => (cuotasPagadas / numeroCuotas) * 100;
}
