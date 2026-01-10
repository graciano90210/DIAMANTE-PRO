import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'registrar_cobro_screen.dart';
import 'prestamo_detalle_screen.dart';
import '../models/prestamo_model.dart';
import '../config/api_config.dart';

class RutaDiaScreen extends StatefulWidget {
  const RutaDiaScreen({super.key});

  @override
  State<RutaDiaScreen> createState() => _RutaDiaScreenState();
}

class _RutaDiaScreenState extends State<RutaDiaScreen> {
  bool _isLoading = false;
  List<dynamic> _rutaCobro = [];
  int _totalCobros = 0;
  double _totalACobrar = 0.0;
  String _filtro = 'todos'; // todos, atrasados, al_dia

  @override
  void initState() {
    super.initState();
    _cargarRutaCobro();
  }

  Future<void> _cargarRutaCobro() async {
    setState(() => _isLoading = true);
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      final authService = Provider.of<AuthService>(context, listen: false);
      final headers = await authService.getAuthHeaders();
      
      final response = await apiService.get(
        ApiConfig.cobros, 
        headers: headers
      );
      
      setState(() {
        _rutaCobro = response['cobros'] ?? [];
        _totalCobros = response['total_cobros'] ?? 0;
        _totalACobrar = (response['total_a_cobrar'] ?? 0.0).toDouble();
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al cargar ruta: $e')),
        );
      }
    }
  }

  List<dynamic> get _cobrosFiltrados {
    if (_filtro == 'atrasados') {
      return _rutaCobro.where((c) => (c['cuotas_atrasadas'] ?? 0) > 0).toList();
    } else if (_filtro == 'al_dia') {
      return _rutaCobro.where((c) => (c['cuotas_atrasadas'] ?? 0) == 0).toList();
    }
    return _rutaCobro;
  }

  Color _getColorEstado(String? estado) {
    switch (estado) {
      case 'GRAVE':
        return Colors.red;
      case 'LEVE':
        return Colors.orange;
      default:
        return Colors.green;
    }
  }

  Future<void> _llamarCliente(String? telefono) async {
    if (telefono == null || telefono.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Cliente sin teléfono registrado')),
      );
      return;
    }

    final Uri telUri = Uri(scheme: 'tel', path: telefono);
    if (await canLaunchUrl(telUri)) {
      await launchUrl(telUri);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No se puede realizar la llamada')),
        );
      }
    }
  }

  Future<void> _abrirWhatsApp(String? whatsapp) async {
    if (whatsapp == null || whatsapp.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Cliente sin WhatsApp registrado')),
      );
      return;
    }

    // Quitar el + si existe
    String numero = whatsapp.replaceAll('+', '');
    final Uri whatsappUri = Uri.parse('https://wa.me/$numero');
    
    if (await canLaunchUrl(whatsappUri)) {
      await launchUrl(whatsappUri, mode: LaunchMode.externalApplication);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No se puede abrir WhatsApp')),
        );
      }
    }
  }

  Future<void> _abrirMapa(double? lat, double? lon) async {
    if (lat == null || lon == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Cliente sin ubicación GPS registrada')),
      );
      return;
    }

    final Uri googleMaps = Uri.parse('https://www.google.com/maps/search/?api=1&query=$lat,$lon');
    
    if (await canLaunchUrl(googleMaps)) {
      await launchUrl(googleMaps, mode: LaunchMode.externalApplication);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No se puede abrir el mapa')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final cobrosFiltrados = _cobrosFiltrados;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Ruta del Día'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _cargarRutaCobro,
          ),
        ],
      ),
      body: Column(
        children: [
          // Resumen de la Ruta
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.blue[50],
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                Column(
                  children: [
                    Text(
                      '$_totalCobros',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue,
                      ),
                    ),
                    const Text('Cobros'),
                  ],
                ),
                Container(
                  width: 1,
                  height: 40,
                  color: Colors.grey[400],
                ),
                Column(
                  children: [
                    Text(
                      '\$${_totalACobrar.toStringAsFixed(0)}',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                    const Text('Total a Cobrar'),
                  ],
                ),
                Container(
                  width: 1,
                  height: 40,
                  color: Colors.grey[400],
                ),
                Column(
                  children: [
                    Text(
                      '${_rutaCobro.where((c) => (c['cuotas_atrasadas'] ?? 0) > 0).length}',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.red,
                      ),
                    ),
                    const Text('Atrasados'),
                  ],
                ),
              ],
            ),
          ),

          // Filtros
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: ChoiceChip(
                    label: const Text('Todos'),
                    selected: _filtro == 'todos',
                    onSelected: (selected) {
                      if (selected) setState(() => _filtro = 'todos');
                    },
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ChoiceChip(
                    label: const Text('Atrasados'),
                    selected: _filtro == 'atrasados',
                    selectedColor: Colors.red[100],
                    onSelected: (selected) {
                      if (selected) setState(() => _filtro = 'atrasados');
                    },
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ChoiceChip(
                    label: const Text('Al Día'),
                    selected: _filtro == 'al_dia',
                    selectedColor: Colors.green[100],
                    onSelected: (selected) {
                      if (selected) setState(() => _filtro = 'al_dia');
                    },
                  ),
                ),
              ],
            ),
          ),

          // Lista de Cobros
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : cobrosFiltrados.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.check_circle_outline, size: 64, color: Colors.green[300]),
                            const SizedBox(height: 16),
                            Text(
                              _filtro == 'todos'
                                  ? '¡No hay cobros pendientes hoy!'
                                  : _filtro == 'atrasados'
                                      ? 'No hay cobros atrasados'
                                      : 'No hay cobros al día',
                              style: TextStyle(fontSize: 18, color: Colors.grey[600]),
                            ),
                          ],
                        ),
                      )
                    : RefreshIndicator(
                        onRefresh: _cargarRutaCobro,
                        child: ListView.builder(
                          itemCount: cobrosFiltrados.length,
                          padding: const EdgeInsets.only(bottom: 80),
                          itemBuilder: (context, index) {
                            final cobro = cobrosFiltrados[index];
                            final cliente = cobro['cliente'];
                            final estadoMora = cobro['estado_mora'];
                            final cuotasAtrasadas = cobro['cuotas_atrasadas'] ?? 0;

                            return Card(
                              margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                              child: Column(
                                children: [
                                  ListTile(
                                    leading: CircleAvatar(
                                      backgroundColor: _getColorEstado(estadoMora),
                                      child: Text(
                                        cuotasAtrasadas.toString(),
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                    title: Text(
                                      cliente['nombre'] ?? 'Sin nombre',
                                      style: const TextStyle(fontWeight: FontWeight.bold),
                                    ),
                                    subtitle: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        const SizedBox(height: 4),
                                        Row(
                                          children: [
                                            const Icon(Icons.location_on, size: 14, color: Colors.grey),
                                            const SizedBox(width: 4),
                                            Expanded(
                                              child: Text(
                                                cliente['direccion'] ?? 'Sin dirección',
                                                style: const TextStyle(fontSize: 13),
                                              ),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 2),
                                        Row(
                                          children: [
                                            const Icon(Icons.phone, size: 14, color: Colors.grey),
                                            const SizedBox(width: 4),
                                            Text(
                                              cliente['telefono'] ?? 'Sin teléfono',
                                              style: const TextStyle(fontSize: 13),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                    trailing: Column(
                                      mainAxisAlignment: MainAxisAlignment.center,
                                      crossAxisAlignment: CrossAxisAlignment.end,
                                      children: [
                                        Text(
                                          '\$${cobro['valor_cuota']?.toStringAsFixed(0) ?? '0'}',
                                          style: const TextStyle(
                                            fontSize: 18,
                                            fontWeight: FontWeight.bold,
                                            color: Colors.green,
                                          ),
                                        ),
                                        if (cuotasAtrasadas > 0)
                                          Container(
                                            margin: const EdgeInsets.only(top: 4),
                                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                            decoration: BoxDecoration(
                                              color: _getColorEstado(estadoMora),
                                              borderRadius: BorderRadius.circular(10),
                                            ),
                                            child: Text(
                                              '$cuotasAtrasadas atr.',
                                              style: const TextStyle(
                                                color: Colors.white,
                                                fontSize: 11,
                                                fontWeight: FontWeight.bold,
                                              ),
                                            ),
                                          ),
                                      ],
                                    ),
                                  ),
                                  
                                  // Botones de Acción
                                  Padding(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                                    child: Row(
                                      children: [
                                        Expanded(
                                          child: OutlinedButton.icon(
                                            onPressed: () => _llamarCliente(cliente['telefono']),
                                            icon: const Icon(Icons.phone, size: 16),
                                            label: const Text('Llamar', style: TextStyle(fontSize: 12)),
                                            style: OutlinedButton.styleFrom(
                                              padding: const EdgeInsets.symmetric(vertical: 8),
                                            ),
                                          ),
                                        ),
                                        const SizedBox(width: 4),
                                        Expanded(
                                          child: OutlinedButton.icon(
                                            onPressed: () => _abrirWhatsApp(cliente['whatsapp']),
                                            icon: const Icon(Icons.chat, size: 16),
                                            label: const Text('WhatsApp', style: TextStyle(fontSize: 12)),
                                            style: OutlinedButton.styleFrom(
                                              padding: const EdgeInsets.symmetric(vertical: 8),
                                              foregroundColor: Colors.green,
                                            ),
                                          ),
                                        ),
                                        const SizedBox(width: 4),
                                        Expanded(
                                          child: OutlinedButton.icon(
                                            onPressed: () => _abrirMapa(
                                              cliente['gps_latitud'],
                                              cliente['gps_longitud'],
                                            ),
                                            icon: const Icon(Icons.map, size: 16),
                                            label: const Text('Mapa', style: TextStyle(fontSize: 12)),
                                            style: OutlinedButton.styleFrom(
                                              padding: const EdgeInsets.symmetric(vertical: 8),
                                              foregroundColor: Colors.blue,
                                            ),
                                          ),
                                        ),
                                        const SizedBox(width: 4),
                                        Expanded(
                                          child: ElevatedButton.icon(
                                            onPressed: () {
                                              // Crear un Prestamo básico para pasar al screen de cobro
                                              final prestamo = Prestamo(
                                                id: cobro['prestamo_id'],
                                                clienteId: cliente['id'],
                                                clienteNombre: cliente['nombre'],
                                                montoPrestado: 0,
                                                montoAPagar: 0,
                                                valorCuota: cobro['valor_cuota']?.toDouble() ?? 0,
                                                numeroCuotas: 0,
                                                cuotasPagadas: 0,
                                                cuotasAtrasadas: cuotasAtrasadas,
                                                saldoActual: cobro['saldo_actual']?.toDouble() ?? 0,
                                                fechaInicio: '',
                                                diasAtraso: 0,
                                                frecuencia: '',
                                                estado: 'ACTIVO',
                                              );
                                              
                                              Navigator.push(
                                                context,
                                                MaterialPageRoute(
                                                  builder: (context) => RegistrarCobroScreen(prestamo: prestamo),
                                                ),
                                              ).then((_) => _cargarRutaCobro());
                                            },
                                            icon: const Icon(Icons.payment, size: 16),
                                            label: const Text('Cobrar', style: TextStyle(fontSize: 12)),
                                            style: ElevatedButton.styleFrom(
                                              padding: const EdgeInsets.symmetric(vertical: 8),
                                              backgroundColor: Colors.green,
                                              foregroundColor: Colors.white,
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }
}
