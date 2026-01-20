import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/prestamo_model.dart';
import '../services/sync_service.dart';
import '../providers/auth_provider.dart';

class CobrosScreen extends StatefulWidget {
  const CobrosScreen({super.key});

  @override
  State<CobrosScreen> createState() => _CobrosScreenState();
}

class _CobrosScreenState extends State<CobrosScreen> {
  List<Prestamo> _prestamos = [];
  Prestamo? _selectedPrestamo;
  final _montoController = TextEditingController();
  final _observacionesController = TextEditingController();
  bool _isLoading = true;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _loadPrestamos();
  }

  @override
  void dispose() {
    _montoController.dispose();
    _observacionesController.dispose();
    super.dispose();
  }

  Future<void> _loadPrestamos() async {
    setState(() => _isLoading = true);

    try {
      final syncService = context.read<SyncService>();
      final prestamos = await syncService.getPrestamos();

      setState(() {
        _prestamos = prestamos.where((p) => p.estado == 'ACTIVO').toList();
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  Future<void> _registrarCobro() async {
    if (_selectedPrestamo == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Seleccione un préstamo')),
      );
      return;
    }

    if (_montoController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Ingrese el monto')),
      );
      return;
    }

    setState(() => _isSaving = true);

    try {
      final syncService = context.read<SyncService>();
      final authProvider = context.read<AuthProvider>();

      final result = await syncService.registrarPago(
        prestamoId: _selectedPrestamo!.id,
        clienteNombre: _selectedPrestamo!.clienteNombre,
        monto: double.parse(_montoController.text),
        cobradorId: authProvider.currentUser!.id,
        observaciones: _observacionesController.text.isEmpty
            ? null
            : _observacionesController.text,
      );

      if (mounted) {
        final mensaje = result['sincronizado'] == true
            ? 'Cobro registrado y sincronizado'
            : 'Cobro guardado (se sincronizará con conexión)';

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(mensaje),
            backgroundColor: result['sincronizado'] == true ? Colors.green : Colors.orange,
            action: result['sincronizado'] != true
                ? SnackBarAction(
                    label: 'SINCRONIZAR',
                    textColor: Colors.white,
                    onPressed: () {
                      syncService.syncAll();
                    },
                  )
                : null,
          ),
        );

        // Limpiar formulario
        setState(() {
          _selectedPrestamo = null;
          _montoController.clear();
          _observacionesController.clear();
        });

        _loadPrestamos();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error al registrar cobro: $e'),
            duration: const Duration(seconds: 5),
            action: SnackBarAction(
              label: 'DETALLES',
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('Error Técnico'),
                    content: Text(e.toString()),
                    actions: [TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('OK'))],
                  ),
                );
              },
            ),
          ),
        );
      }
    } finally {
      setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Registrar Cobro'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Seleccionar Préstamo',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 16),
                  DropdownButtonFormField<Prestamo>(
                    initialValue: _selectedPrestamo,
                    decoration: InputDecoration(
                      labelText: 'Préstamo',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    items: _prestamos.map((prestamo) {
                      return DropdownMenuItem(
                        value: prestamo,
                        child: Text(
                          '${prestamo.clienteNombre} - \$${prestamo.valorCuota}',
                          overflow: TextOverflow.ellipsis,
                        ),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() {
                        _selectedPrestamo = value;
                        if (value != null) {
                          _montoController.text = value.valorCuota.toString();
                        }
                      });
                    },
                  ),
                  if (_selectedPrestamo != null) ...[
                    const SizedBox(height: 16),
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Información del Préstamo',
                              style: Theme.of(context).textTheme.titleMedium,
                            ),
                            const Divider(),
                            _buildInfoRow('Cliente:', _selectedPrestamo!.clienteNombre),
                            _buildInfoRow('Cuota sugerida:',
                                '\$${_selectedPrestamo!.valorCuota.toStringAsFixed(2)}'),
                            _buildInfoRow('Saldo pendiente:',
                                '\$${_selectedPrestamo!.saldoActual.toStringAsFixed(2)}'),
                            _buildInfoRow('Cuotas atrasadas:',
                                '${_selectedPrestamo!.cuotasAtrasadas}'),
                          ],
                        ),
                      ),
                    ),
                  ],
                  const SizedBox(height: 24),
                  Text(
                    'Datos del Cobro',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _montoController,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: 'Monto',
                      prefixText: '\$ ',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _observacionesController,
                    maxLines: 3,
                    decoration: InputDecoration(
                      labelText: 'Observaciones (opcional)',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton.icon(
                      onPressed: _isSaving ? null : _registrarCobro,
                      icon: _isSaving
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.check),
                      label: const Text('REGISTRAR COBRO'),
                      style: ElevatedButton.styleFrom(
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }
}
