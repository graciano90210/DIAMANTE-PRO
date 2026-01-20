import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../services/location_service.dart';
import '../config/api_config.dart';

class CrearClienteScreen extends StatefulWidget {
  const CrearClienteScreen({super.key});

  @override
  State<CrearClienteScreen> createState() => _CrearClienteScreenState();
}

class _CrearClienteScreenState extends State<CrearClienteScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nombreController = TextEditingController();
  final _documentoController = TextEditingController();
  final _telefonoController = TextEditingController();
  final _emailController = TextEditingController();
  final _direccionController = TextEditingController(); // Negocio
  final _cepNegocioController = TextEditingController();
  final _direccionCasaController = TextEditingController();
  final _cepCasaController = TextEditingController();
  
  String _tipoDocumento = 'CPF';
  DateTime? _fechaNacimiento;

  final LocationService _locationService = LocationService();
  double? _gpsLatitud;
  double? _gpsLongitud;
  
  bool _isLoading = false;
  bool _gettingLocation = false;

  @override
  void dispose() {
    _nombreController.dispose();
    _documentoController.dispose();
    _telefonoController.dispose();
    _emailController.dispose();
    _direccionController.dispose();
    _cepNegocioController.dispose();
    _direccionCasaController.dispose();
    _cepCasaController.dispose();
    super.dispose();
  }

  Future<void> _seleccionarFecha(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now().subtract(const Duration(days: 365 * 18)),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
    );
    if (picked != null && picked != _fechaNacimiento) {
      setState(() {
        _fechaNacimiento = picked;
      });
    }
  }

  Future<void> _obtenerUbicacion() async {
    setState(() => _gettingLocation = true);
    
    final position = await _locationService.getCurrentLocation();
    
    if (mounted) {
      if (position != null) {
        setState(() {
          _gpsLatitud = position.latitude;
          _gpsLongitud = position.longitude;
          _gettingLocation = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('📍 Ubicación capturada correctamente')),
        );
      } else {
        setState(() => _gettingLocation = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('❌ No se pudo obtener la ubicación')),
        );
      }
    }
  }

  Future<void> _guardarCliente() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final apiService = context.read<ApiService>();
      final authService = context.read<AuthService>();
      final headers = await authService.getAuthHeaders();

      await apiService.post(
        ApiConfig.clientes,
        headers: headers,
        body: {
          'nombre': _nombreController.text.trim(),
          'documento': _documentoController.text.trim(),
          'tipo_documento': _tipoDocumento,
          'fecha_nacimiento': _fechaNacimiento?.toIso8601String().split('T')[0],
          'email': _emailController.text.trim(),
          'telefono': _telefonoController.text.trim(),
          
          'direccion_negocio': _direccionController.text.trim(),
          'cep_negocio': _cepNegocioController.text.trim(),
          'direccion_casa': _direccionCasaController.text.trim(),
          'cep_casa': _cepCasaController.text.trim(),
          
          'gps_latitud': _gpsLatitud,
          'gps_longitud': _gpsLongitud,
        },
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Cliente creado exitosamente')),
        );
        Navigator.pop(context, true); // Retorna true para recargar lista
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
      appBar: AppBar(title: const Text('Nuevo Cliente')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              const Text('Datos Personales', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.blue)),
              const SizedBox(height: 16),
              TextFormField(
                controller: _nombreController,
                decoration: const InputDecoration(
                  labelText: 'Nombre Completo',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.person),
                ),
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    flex: 1,
                    child: DropdownButtonFormField<String>(
                      value: _tipoDocumento,
                      decoration: const InputDecoration(labelText: 'Tipo', border: OutlineInputBorder()),
                      items: ['CPF', 'CNPJ', 'RG', 'Otro'].map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
                      onChanged: (v) => setState(() => _tipoDocumento = v!),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    flex: 2,
                    child: TextFormField(
                      controller: _documentoController,
                      decoration: const InputDecoration(
                        labelText: 'Documento ID / CNPJ',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.badge),
                      ),
                      keyboardType: TextInputType.number,
                      validator: (v) => v!.isEmpty ? 'Requerido' : null,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              InkWell(
                onTap: () => _seleccionarFecha(context),
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: 'Fecha de Nacimiento',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.calendar_today),
                  ),
                  child: Text(
                    _fechaNacimiento == null
                        ? 'Seleccionar fecha'
                        : '${_fechaNacimiento!.day.toString().padLeft(2,'0')}/${_fechaNacimiento!.month.toString().padLeft(2,'0')}/${_fechaNacimiento!.year}',
                    style: TextStyle(color: _fechaNacimiento == null ? Colors.grey : Colors.black87),
                  ),
                ),
              ),
              const SizedBox(height: 16),
               TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.email),
                ),
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _telefonoController,
                decoration: const InputDecoration(
                  labelText: 'Teléfono / WhatsApp',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.phone),
                ),
                keyboardType: TextInputType.phone,
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),
              const SizedBox(height: 24),

              const Text('Dirección Casa', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.blue)),
              const SizedBox(height: 16),
              Row(
                children: [
                   Expanded(
                    flex: 2,
                    child: TextFormField(
                      controller: _direccionCasaController,
                      decoration: const InputDecoration(
                        labelText: 'Dirección Casa',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.home),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    flex: 1,
                    child: TextFormField(
                      controller: _cepCasaController,
                      decoration: const InputDecoration(labelText: 'CEP', border: OutlineInputBorder()),
                      keyboardType: TextInputType.number,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),
              const Text('Dirección Negocio', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.blue)),
              const SizedBox(height: 16),
              
              Row(
                children: [
                   Expanded(
                    flex: 2,
                    child: TextFormField(
                      controller: _direccionController,
                      decoration: const InputDecoration(
                        labelText: 'Dirección Negocio',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.store),
                      ),
                      validator: (v) => v!.isEmpty ? 'Requerido' : null,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    flex: 1,
                    child: TextFormField(
                      controller: _cepNegocioController,
                      decoration: const InputDecoration(labelText: 'CEP', border: OutlineInputBorder()),
                      keyboardType: TextInputType.number,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade400),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.location_on, color: Colors.blue),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _gpsLatitud != null
                                ? 'GPS: ${_gpsLatitud!.toStringAsFixed(6)}, ${_gpsLongitud!.toStringAsFixed(6)}'
                                : 'Sin ubicación capturada',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: _gpsLatitud != null ? Colors.black87 : Colors.grey,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton.icon(
                        onPressed: _gettingLocation ? null : _obtenerUbicacion,
                        icon: _gettingLocation 
                            ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)) 
                            : const Icon(Icons.my_location),
                        label: Text(_gettingLocation ? 'Capturando...' : 'CAPTURAR UBICACIÓN GPS'),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _guardarCliente,
                  child: _isLoading
                      ? const CircularProgressIndicator()
                      : const Text('GUARDAR CLIENTE'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
