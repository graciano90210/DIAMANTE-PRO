import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:image_picker/image_picker.dart';
import 'package:geolocator/geolocator.dart';
import 'dart:io';
import '../models/prestamo_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../services/location_service.dart';
import '../config/api_config.dart';

class RegistrarCobroScreen extends StatefulWidget {
  final Prestamo? prestamo;

  const RegistrarCobroScreen({super.key, this.prestamo});

  @override
  State<RegistrarCobroScreen> createState() => _RegistrarCobroScreenState();
}

class _RegistrarCobroScreenState extends State<RegistrarCobroScreen> {
  final _formKey = GlobalKey<FormState>();
  final _montoController = TextEditingController();
  final _observacionesController = TextEditingController();
  
  bool _isLoading = false;
  File? _imagenRecibo;
  Prestamo? _prestamoSeleccionado;
  List<Prestamo> _prestamos = [];
  Position? _ubicacionActual;
  final LocationService _locationService = LocationService();
  bool _capturandoUbicacion = false;

  @override
  void initState() {
    super.initState();
    _prestamoSeleccionado = widget.prestamo;
    if (_prestamoSeleccionado != null) {
      _montoController.text = _prestamoSeleccionado!.valorCuota.toStringAsFixed(2);
    } else {
      _cargarPrestamos();
    }
    // Capturar ubicación automáticamente al abrir la pantalla
    _capturarUbicacion();
  }

  @override
  void dispose() {
    _montoController.dispose();
    _observacionesController.dispose();
    super.dispose();
  }

  Future<void> _cargarPrestamos() async {
    setState(() => _isLoading = true);
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      final authService = Provider.of<AuthService>(context, listen: false);
      final headers = await authService.getAuthHeaders();
      
      final response = await apiService.getList(
        ApiConfig.prestamos,
        headers: headers,
      );
      setState(() {
        _prestamos = response.map((json) => Prestamo.fromJson(json)).toList();
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al cargar préstamos: $e')),
        );
      }
    }
  }

  Future<void> _capturarUbicacion() async {
    setState(() => _capturandoUbicacion = true);
    try {
      final position = await _locationService.getCurrentLocation();
      setState(() {
        _ubicacionActual = position;
        _capturandoUbicacion = false;
      });
      
      if (position != null && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✓ Ubicación capturada'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      setState(() => _capturandoUbicacion = false);
      print('Error al capturar ubicación: $e');
    }
  }

  Future<void> _tomarFoto() async {
    try {
      final ImagePicker picker = ImagePicker();
      final XFile? image = await picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (image != null) {
        setState(() {
          _imagenRecibo = File(image.path);
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al tomar foto: $e')),
        );
      }
    }
  }

  Future<void> _seleccionarFoto() async {
    try {
      final ImagePicker picker = ImagePicker();
      final XFile? image = await picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (image != null) {
        setState(() {
          _imagenRecibo = File(image.path);
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al seleccionar foto: $e')),
        );
      }
    }
  }

  Future<void> _registrarCobro() async {
    if (!_formKey.currentState!.validate()) return;
    if (_prestamoSeleccionado == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Selecciona un préstamo')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      
      final data = {
        'prestamo_id': _prestamoSeleccionado!.id,
        'monto_pagado': double.parse(_montoController.text),
        'observaciones': _observacionesController.text,
      };

      // Agregar GPS si está disponible
      if (_ubicacionActual != null) {
        data['gps_latitud'] = _ubicacionActual!.latitude.toString();
        data['gps_longitud'] = _ubicacionActual!.longitude.toString();
      }

      // TODO: Subir imagen del recibo si existe
      // if (_imagenRecibo != null) { ... }

      await apiService.post(ApiConfig.nuevoCobro, body: data);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Cobro registrado exitosamente'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al registrar cobro: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Registrar Cobro'),
        actions: [
          // Indicador de GPS
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: _capturandoUbicacion
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : IconButton(
                    icon: Icon(
                      _ubicacionActual != null
                          ? Icons.location_on
                          : Icons.location_off,
                      color: _ubicacionActual != null ? Colors.green : Colors.red,
                    ),
                    onPressed: _capturarUbicacion,
                    tooltip: _ubicacionActual != null
                        ? 'Ubicación capturada'
                        : 'Capturar ubicación',
                  ),
          ),
        ],
      ),
      body: _isLoading && _prestamos.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Indicador de GPS
                    if (_ubicacionActual != null)
                      Card(
                        color: Colors.green[50],
                        child: ListTile(
                          leading: const Icon(Icons.location_on, color: Colors.green),
                          title: const Text('Ubicación capturada'),
                          subtitle: Text(
                            'Lat: ${_ubicacionActual!.latitude.toStringAsFixed(6)}, '
                            'Lon: ${_ubicacionActual!.longitude.toStringAsFixed(6)}',
                            style: const TextStyle(fontSize: 12),
                          ),
                          trailing: IconButton(
                            icon: const Icon(Icons.refresh),
                            onPressed: _capturarUbicacion,
                            tooltip: 'Actualizar ubicación',
                          ),
                        ),
                      ),
                    if (_ubicacionActual == null && !_capturandoUbicacion)
                      Card(
                        color: Colors.orange[50],
                        child: ListTile(
                          leading: const Icon(Icons.location_off, color: Colors.orange),
                          title: const Text('Sin ubicación'),
                          subtitle: const Text('No se pudo capturar la ubicación'),
                          trailing: TextButton(
                            onPressed: _capturarUbicacion,
                            child: const Text('Reintentar'),
                          ),
                        ),
                      ),
                    const SizedBox(height: 16),
                    
                    // Selector de Préstamo
                    if (widget.prestamo == null) ...[
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Seleccionar Préstamo',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 12),
                              DropdownButtonFormField<Prestamo>(
                                initialValue: _prestamoSeleccionado,
                                decoration: const InputDecoration(
                                  border: OutlineInputBorder(),
                                  labelText: 'Préstamo',
                                ),
                                items: _prestamos.map((prestamo) {
                                  return DropdownMenuItem(
                                    value: prestamo,
                                    child: Text(
                                      '${prestamo.clienteNombre} - \$${prestamo.saldoActual.toStringAsFixed(2)}',
                                    ),
                                  );
                                }).toList(),
                                onChanged: (prestamo) {
                                  setState(() {
                                    _prestamoSeleccionado = prestamo;
                                    if (prestamo != null) {
                                      _montoController.text =
                                          prestamo.valorCuota.toStringAsFixed(2);
                                    }
                                  });
                                },
                                validator: (value) {
                                  if (value == null) {
                                    return 'Selecciona un préstamo';
                                  }
                                  return null;
                                },
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // Información del Préstamo
                    if (_prestamoSeleccionado != null) ...[
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    _prestamoSeleccionado!.clienteNombre,
                                    style: const TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  if (_prestamoSeleccionado!.cuotasAtrasadas > 0)
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 8,
                                        vertical: 4,
                                      ),
                                      decoration: BoxDecoration(
                                        color: Colors.red,
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      child: Text(
                                        '${_prestamoSeleccionado!.cuotasAtrasadas} atr.',
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontSize: 12,
                                        ),
                                      ),
                                    ),
                                ],
                              ),
                              const Divider(),
                              _buildInfoRow('Saldo Actual',
                                  '\$${_prestamoSeleccionado!.saldoActual.toStringAsFixed(2)}'),
                              _buildInfoRow('Valor Cuota',
                                  '\$${_prestamoSeleccionado!.valorCuota.toStringAsFixed(2)}'),
                              _buildInfoRow(
                                  'Cuotas Pagadas',
                                  '${_prestamoSeleccionado!.cuotasPagadas}/${_prestamoSeleccionado!.numeroCuotas}'),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // Monto del Cobro
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Información del Cobro',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextFormField(
                              controller: _montoController,
                              decoration: const InputDecoration(
                                border: OutlineInputBorder(),
                                labelText: 'Monto a Cobrar',
                                prefixText: '\$ ',
                                suffixIcon: Icon(Icons.attach_money),
                              ),
                              keyboardType: const TextInputType.numberWithOptions(
                                decimal: true,
                              ),
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Ingresa el monto';
                                }
                                final monto = double.tryParse(value);
                                if (monto == null || monto <= 0) {
                                  return 'Ingresa un monto válido';
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 12),
                            TextFormField(
                              controller: _observacionesController,
                              decoration: const InputDecoration(
                                border: OutlineInputBorder(),
                                labelText: 'Observaciones (opcional)',
                                hintText: 'Ej: Pago completo, abono, etc.',
                              ),
                              maxLines: 3,
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Foto del Recibo
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Foto del Recibo (opcional)',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 12),
                            if (_imagenRecibo != null) ...[
                              ClipRRect(
                                borderRadius: BorderRadius.circular(8),
                                child: Image.file(
                                  _imagenRecibo!,
                                  height: 200,
                                  width: double.infinity,
                                  fit: BoxFit.cover,
                                ),
                              ),
                              const SizedBox(height: 12),
                              Row(
                                children: [
                                  Expanded(
                                    child: OutlinedButton.icon(
                                      onPressed: () {
                                        setState(() => _imagenRecibo = null);
                                      },
                                      icon: const Icon(Icons.delete),
                                      label: const Text('Eliminar'),
                                      style: OutlinedButton.styleFrom(
                                        foregroundColor: Colors.red,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: OutlinedButton.icon(
                                      onPressed: _tomarFoto,
                                      icon: const Icon(Icons.camera_alt),
                                      label: const Text('Otra foto'),
                                    ),
                                  ),
                                ],
                              ),
                            ] else ...[
                              Row(
                                children: [
                                  Expanded(
                                    child: ElevatedButton.icon(
                                      onPressed: _tomarFoto,
                                      icon: const Icon(Icons.camera_alt),
                                      label: const Text('Tomar Foto'),
                                      style: ElevatedButton.styleFrom(
                                        padding: const EdgeInsets.all(16),
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: OutlinedButton.icon(
                                      onPressed: _seleccionarFoto,
                                      icon: const Icon(Icons.photo_library),
                                      label: const Text('Galería'),
                                      style: OutlinedButton.styleFrom(
                                        padding: const EdgeInsets.all(16),
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Botón Registrar
                    ElevatedButton(
                      onPressed: _isLoading ? null : _registrarCobro,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.all(16),
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                      ),
                      child: _isLoading
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor:
                                    AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : const Text(
                              'REGISTRAR COBRO',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                    ),
                  ],
                ),
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
          Text(
            label,
            style: TextStyle(color: Colors.grey[700]),
          ),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }
}
