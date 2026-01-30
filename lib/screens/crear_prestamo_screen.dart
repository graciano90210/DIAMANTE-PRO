import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../config/api_config.dart';
import '../models/cliente_model.dart';

class CrearPrestamoScreen extends StatefulWidget {
  final Cliente cliente;

  const CrearPrestamoScreen({super.key, required this.cliente});

  @override
  State<CrearPrestamoScreen> createState() => _CrearPrestamoScreenState();
}

class _CrearPrestamoScreenState extends State<CrearPrestamoScreen> {
  final _formKey = GlobalKey<FormState>();
  final _montoController = TextEditingController();
  final _interesController = TextEditingController(text: '20');
  final _cuotasController = TextEditingController(text: '24');
  
  bool _isLoading = false;
  List<dynamic> _rutas = [];
  int? _rutaSeleccionadaId;
  String _frecuencia = 'DIARIO';

  @override
  void initState() {
    super.initState();
    _cargarRutas();
  }

  Future<void> _cargarRutas() async {
    try {
      final apiService = context.read<ApiService>();
      final authService = context.read<AuthService>();
      final headers = await authService.getAuthHeaders();
      
      final response = await apiService.getList(
        ApiConfig.rutas,
        headers: headers,
      );
      
      if (mounted) {
        setState(() {
          _rutas = response;
          if (_rutas.isNotEmpty) {
            _rutaSeleccionadaId = _rutas[0]['id'];
          }
        });
      }
    } catch (e) {
      print('Error cargando rutas: $e');
    }
  }

  void _calcularProyeccion() {
    // Solo para mostrar info al usuario (opcional)
    setState(() {});
  }

  double get _monto => double.tryParse(_montoController.text) ?? 0;
  double get _interes => double.tryParse(_interesController.text) ?? 20;
  int get _cuotas => int.tryParse(_cuotasController.text) ?? 1;

  double get _totalPagar => _monto * (1 + (_interes / 100));
  double get _valorCuota => _totalPagar / _cuotas;

  Future<void> _crearPrestamo() async {
    if (!_formKey.currentState!.validate()) return;
    if (_rutaSeleccionadaId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No hay rutas disponibles para el cobrador')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final apiService = context.read<ApiService>();
      final authService = context.read<AuthService>();
      final headers = await authService.getAuthHeaders();

      await apiService.post(
        ApiConfig.prestamos,
        headers: headers,
        body: {
          'cliente_id': widget.cliente.id,
          'monto': _monto,
          'interes': _interes,
          'cuotas': _cuotas,
          'frecuencia': _frecuencia,
          'ruta_id': _rutaSeleccionadaId,
        },
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Préstamo creado exitosamente')),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nuevo Préstamo')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Info Cliente
              Card(
                color: Colors.blue.shade50,
                child: ListTile(
                  leading: const Icon(Icons.person, color: Colors.blue),
                  title: Text(widget.cliente.nombre, style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(widget.cliente.documento ?? 'Sin documento'),
                ),
              ),
              const SizedBox(height: 20),
              
              // Campos
              Row(
                children: [
                   Expanded(
                    child: TextFormField(
                      controller: _montoController,
                      decoration: const InputDecoration(
                        labelText: 'Monto a Prestar',
                        prefixText: '\$',
                        border: OutlineInputBorder(),
                      ),
                      keyboardType: TextInputType.number,
                      onChanged: (_) => _calcularProyeccion(),
                      validator: (v) => v!.isEmpty ? 'Requerido' : null,
                    ),
                  ),
                  const SizedBox(width: 16),
                  SizedBox(
                    width: 100,
                    child: TextFormField(
                      controller: _interesController,
                      decoration: const InputDecoration(
                        labelText: 'Interés %',
                        border: OutlineInputBorder(),
                      ),
                      keyboardType: TextInputType.number,
                      onChanged: (_) => _calcularProyeccion(),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _cuotasController,
                      decoration: const InputDecoration(
                        labelText: 'N° Cuotas',
                        border: OutlineInputBorder(),
                      ),
                      keyboardType: TextInputType.number,
                      onChanged: (_) => _calcularProyeccion(),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      initialValue: _frecuencia,
                      decoration: const InputDecoration(
                        labelText: 'Frecuencia',
                        border: OutlineInputBorder(),
                      ),
                      items: ['DIARIO', 'SEMANAL', 'QUINCENAL', 'MENSUAL']
                          .map((f) => DropdownMenuItem(value: f, child: Text(f)))
                          .toList(),
                      onChanged: (v) => setState(() => _frecuencia = v!),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              
              if (_rutas.isNotEmpty)
                DropdownButtonFormField<int>(
                  initialValue: _rutaSeleccionadaId,
                  decoration: const InputDecoration(
                    labelText: 'Asignar a Ruta',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.map),
                  ),
                  items: _rutas.map((r) => DropdownMenuItem<int>(
                    value: r['id'],
                    child: Text(r['nombre']),
                  )).toList(),
                  onChanged: (v) => setState(() => _rutaSeleccionadaId = v),
                )
              else
                const Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Text('Cargando rutas...', style: TextStyle(color: Colors.grey)),
                ),

              const SizedBox(height: 30),
              
              // RESUMEN
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: Column(
                  children: [
                    const Text('RESUMEN DEL PRÉSTAMO', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.grey)),
                    const Divider(),
                    _ResumenRow(label: 'Monto Prestado:', value: '\$${_monto.toStringAsFixed(2)}'),
                    _ResumenRow(label: 'Total a Pagar:', value: '\$${_totalPagar.toStringAsFixed(2)}', isBold: true),
                    const SizedBox(height: 8),
                    _ResumenRow(label: 'Valor Cuota:', value: '\$${_valorCuota.toStringAsFixed(2)}', color: Colors.blue),
                  ],
                ),
              ),

              const SizedBox(height: 30),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _crearPrestamo,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                  ),
                  child: _isLoading
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text('CREAR PRÉSTAMO', style: TextStyle(fontWeight: FontWeight.bold)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ResumenRow extends StatelessWidget {
  final String label;
  final String value;
  final bool isBold;
  final Color? color;

  const _ResumenRow({required this.label, required this.value, this.isBold = false, this.color});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            value,
            style: TextStyle(
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
              fontSize: isBold ? 18 : 16,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
