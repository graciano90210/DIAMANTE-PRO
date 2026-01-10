import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/prestamo_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../config/api_config.dart';

class PrestamoDetalleScreen extends StatefulWidget {
  final Prestamo prestamo;

  const PrestamoDetalleScreen({super.key, required this.prestamo});

  @override
  State<PrestamoDetalleScreen> createState() => _PrestamoDetalleScreenState();
}

class _PrestamoDetalleScreenState extends State<PrestamoDetalleScreen> {
  bool _isLoading = false;
  List<dynamic> _historialPagos = [];

  @override
  void initState() {
    super.initState();
    _cargarHistorialPagos();
  }

  Future<void> _cargarHistorialPagos() async {
    setState(() => _isLoading = true);
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      final authService = Provider.of<AuthService>(context, listen: false);
      final headers = await authService.getAuthHeaders();

      final response = await apiService.getList(
        '${ApiConfig.prestamos}/${widget.prestamo.id}/pagos',
        headers: headers,
      );
      setState(() {
        _historialPagos = response;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al cargar historial: $e')),
        );
      }
    }
  }

  Color _getEstadoColor() {
    if (widget.prestamo.estaPagado) return Colors.green;
    if (widget.prestamo.moraGrave) return Colors.red;
    if (widget.prestamo.estaMora) return Colors.orange;
    return Colors.blue;
  }

  String _getEstadoTexto() {
    if (widget.prestamo.estaPagado) return 'PAGADO';
    if (widget.prestamo.moraGrave) return 'MORA GRAVE';
    if (widget.prestamo.estaMora) return 'ATRASADO';
    return 'AL DÍA';
  }

  @override
  Widget build(BuildContext context) {
    final porcentaje = widget.prestamo.porcentajePagado;

    return Scaffold(
      appBar: AppBar(
        title: Text('Préstamo #${widget.prestamo.id}'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _cargarHistorialPagos,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _cargarHistorialPagos,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Información del Cliente
              Card(
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Colors.blue,
                    child: Text(
                      widget.prestamo.clienteNombre[0].toUpperCase(),
                      style: const TextStyle(color: Colors.white),
                    ),
                  ),
                  title: Text(
                    widget.prestamo.clienteNombre,
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                  ),
                  subtitle: Text('Cliente #${widget.prestamo.clienteId}'),
                  trailing: Chip(
                    label: Text(_getEstadoTexto()),
                    backgroundColor: _getEstadoColor(),
                    labelStyle: const TextStyle(color: Colors.white, fontSize: 12),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Progreso de Pago
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Progreso de Pago',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                          Text(
                            '${porcentaje.toStringAsFixed(1)}%',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: _getEstadoColor(),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: LinearProgressIndicator(
                          value: porcentaje / 100,
                          minHeight: 20,
                          backgroundColor: Colors.grey[300],
                          valueColor: AlwaysStoppedAnimation(_getEstadoColor()),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Cuotas pagadas: ${widget.prestamo.cuotasPagadas}/${widget.prestamo.numeroCuotas}',
                        style: TextStyle(color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Información Financiera
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Información Financiera',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      const Divider(),
                      _buildInfoRow('Monto Prestado', '\$${widget.prestamo.montoPrestado.toStringAsFixed(2)}'),
                      _buildInfoRow('Total a Pagar', '\$${widget.prestamo.montoAPagar.toStringAsFixed(2)}'),
                      _buildInfoRow('Valor Cuota', '\$${widget.prestamo.valorCuota.toStringAsFixed(2)}'),
                      _buildInfoRow('Saldo Actual', '\$${widget.prestamo.saldoActual.toStringAsFixed(2)}', 
                        isHighlight: true, color: Colors.red),
                      _buildInfoRow('Frecuencia', widget.prestamo.frecuencia),
                      _buildInfoRow('Cuotas Atrasadas', '${widget.prestamo.cuotasAtrasadas}',
                        color: widget.prestamo.cuotasAtrasadas > 0 ? Colors.red : Colors.green),
                      if (widget.prestamo.diasAtraso > 0)
                        _buildInfoRow('Días de Atraso', '${widget.prestamo.diasAtraso}', color: Colors.red),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Información de Fechas
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Fechas',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      const Divider(),
                      _buildInfoRow('Fecha de Inicio', widget.prestamo.fechaInicio),
                      if (widget.prestamo.fechaUltimoPago != null)
                        _buildInfoRow('Último Pago', widget.prestamo.fechaUltimoPago!),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Historial de Pagos
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Historial de Pagos',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                          Text(
                            '${_historialPagos.length} pagos',
                            style: TextStyle(color: Colors.grey[600]),
                          ),
                        ],
                      ),
                      const Divider(),
                      if (_isLoading)
                        const Center(child: CircularProgressIndicator())
                      else if (_historialPagos.isEmpty)
                        const Padding(
                          padding: EdgeInsets.all(16),
                          child: Center(child: Text('No hay pagos registrados')),
                        )
                      else
                        ListView.separated(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          itemCount: _historialPagos.length,
                          separatorBuilder: (context, index) => const Divider(),
                          itemBuilder: (context, index) {
                            final pago = _historialPagos[index];
                            return ListTile(
                              contentPadding: EdgeInsets.zero,
                              leading: CircleAvatar(
                                backgroundColor: Colors.green,
                                child: Text('${index + 1}'),
                              ),
                              title: Text(
                                '\$${pago['monto_pagado']?.toStringAsFixed(2) ?? '0.00'}',
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                              subtitle: Text(pago['fecha_pago'] ?? ''),
                              trailing: pago['observaciones'] != null && pago['observaciones'].isNotEmpty
                                  ? const Icon(Icons.note, size: 16)
                                  : null,
                            );
                          },
                        ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: widget.prestamo.estaPagado
          ? null
          : FloatingActionButton.extended(
              onPressed: () {
                Navigator.pushNamed(
                  context,
                  '/registrar-cobro',
                  arguments: widget.prestamo,
                ).then((_) => _cargarHistorialPagos());
              },
              icon: const Icon(Icons.payment),
              label: const Text('Registrar Cobro'),
            ),
    );
  }

  Widget _buildInfoRow(String label, String value, {bool isHighlight = false, Color? color}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              color: Colors.grey[700],
              fontSize: isHighlight ? 15 : 14,
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontWeight: isHighlight ? FontWeight.bold : FontWeight.w500,
              fontSize: isHighlight ? 16 : 14,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
