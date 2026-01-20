import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:provider/provider.dart';
import '../models/cliente_model.dart';
import '../models/prestamo_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../config/api_config.dart';
import 'crear_prestamo_screen.dart';
import 'prestamo_detalle_screen.dart';

class ClienteDetalleScreen extends StatefulWidget {
  final Cliente cliente;

  const ClienteDetalleScreen({super.key, required this.cliente});

  @override
  State<ClienteDetalleScreen> createState() => _ClienteDetalleScreenState();
}

class _ClienteDetalleScreenState extends State<ClienteDetalleScreen> {
  List<Prestamo> _prestamos = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _cargarPrestamos();
  }

  Future<void> _cargarPrestamos() async {
    setState(() => _isLoading = true);
    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      final apiService = Provider.of<ApiService>(context, listen: false);
      final headers = await authService.getAuthHeaders();

      final response = await apiService.getList(
        '${ApiConfig.prestamos}?cliente_id=${widget.cliente.id}',
        headers: headers,
      );

      setState(() {
        _prestamos = response.map((data) => Prestamo.fromJson(data)).toList();
        _isLoading = false;
      });
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        // Silently fail or show simple error?
        // Usually better to show empty list if error or empty
        print('Error cargando préstamos: $e');
      }
    }
  }

  Future<void> _makePhoneCall(String phoneNumber) async {
    final Uri launchUri = Uri(
      scheme: 'tel',
      path: phoneNumber,
    );
    if (await canLaunchUrl(launchUri)) {
      await launchUrl(launchUri);
    }
  }

  Future<void> _openWhatsApp(String phoneNumber) async {
    final cleanNumber = phoneNumber.replaceAll(RegExp(r'\D'), '');
    final Uri launchUri = Uri.parse(
      'https://wa.me/$cleanNumber',
    );
    if (await canLaunchUrl(launchUri)) {
      await launchUrl(launchUri, mode: LaunchMode.externalApplication);
    }
  }

  Future<void> _openMap(double lat, double lng) async {
    final Uri googleMapsUrl = Uri.parse(
        'https://www.google.com/maps/search/?api=1&query=$lat,$lng');
    if (await canLaunchUrl(googleMapsUrl)) {
      await launchUrl(googleMapsUrl, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.cliente.nombre),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _cargarPrestamos,
          )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Header con Logo/Avatar
            CircleAvatar(
              radius: 40,
              backgroundColor: Colors.blue.shade100,
              child: Text(
                widget.cliente.nombre[0].toUpperCase(),
                style: const TextStyle(fontSize: 40, color: Colors.blue),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              widget.cliente.nombre,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            if (widget.cliente.esVip)
              Container(
                margin: const EdgeInsets.only(top: 8),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.amber,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Text(
                  '⭐ CLIENTE VIP',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            const SizedBox(height: 24),

            // Botón Crear Préstamo
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                icon: const Icon(Icons.monetization_on),
                label: const Text('NUEVO PRÉSTAMO'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                ),
                onPressed: () async {
                  await Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => CrearPrestamoScreen(cliente: widget.cliente),
                    ),
                  );
                  _cargarPrestamos();
                },
              ),
            ),
            const SizedBox(height: 24),

            if (_prestamos.isNotEmpty)
              _ResumenFinancieroCard(
                prestado: _prestamos.fold(0, (sum, p) => sum + p.montoPrestado),
                pagado: _prestamos.fold(0, (sum, p) => sum + (p.montoAPagar - p.saldoActual)),
                pendiente: _prestamos.fold(0, (sum, p) => sum + p.saldoActual),
              ),
            const SizedBox(height: 24),

             // Lista de Préstamos Activos
            if (_isLoading)
               const Center(child: CircularProgressIndicator())
            else if (_prestamos.isNotEmpty) ...[
               const Align(
                 alignment: Alignment.centerLeft,
                 child: Text(
                   'Préstamos Activos',
                   style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                 ),
               ),
               const SizedBox(height: 8),
               ..._prestamos.map((prestamo) => Card(
                 child: ListTile(
                   title: Text('Préstamo #${prestamo.id}'),
                   subtitle: Text('Saldo: ${prestamo.moneda} ${prestamo.saldoActual}'),
                   trailing: const Icon(Icons.arrow_forward_ios),
                   onTap: () async {
                     await Navigator.push(
                       context,
                       MaterialPageRoute(
                         builder: (_) => PrestamoDetalleScreen(prestamo: prestamo),
                       ),
                     );
                     _cargarPrestamos();
                   },
                 ),
               )),
               const SizedBox(height: 24),
            ],

            // Botones de Acción Rápida
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _ActionButton(
                  icon: Icons.phone,
                  label: 'Llamar',
                  color: Colors.green,
                  onTap: () => _makePhoneCall(widget.cliente.telefono),
                ),
                if (widget.cliente.whatsapp != null)
                  _ActionButton(
                    icon: Icons.message,
                    label: 'WhatsApp',
                    color: Colors.teal,
                    onTap: () => _openWhatsApp(widget.cliente.whatsapp!),
                  ),
                if (widget.cliente.tieneUbicacion)
                  _ActionButton(
                    icon: Icons.map,
                    label: 'Mapa',
                    color: Colors.orange,
                    onTap: () => _openMap(
                      widget.cliente.gpsLatitud!,
                      widget.cliente.gpsLongitud!,
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 32),

            // Información Detallada
            _InfoCard(
              title: 'Información de Contacto',
              children: [
                _InfoRow(icon: Icons.phone, label: 'Teléfono', value: widget.cliente.telefono),
                if (widget.cliente.documento != null)
                  _InfoRow(icon: Icons.badge, label: 'Documento', value: widget.cliente.documento!),
                _InfoRow(icon: Icons.store, label: 'Dirección Negocio', value: widget.cliente.direccionNegocio),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(30),
          child: Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 30),
          ),
        ),
        const SizedBox(height: 8),
        Text(label, style: TextStyle(color: color, fontWeight: FontWeight.bold)),
      ],
    );
  }
}

class _InfoCard extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _InfoCard({required this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey,
              ),
            ),
            const Divider(),
            ...children,
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        children: [
          Icon(icon, color: Colors.blueGrey, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
                Text(value, style: const TextStyle(fontSize: 16)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
class _ResumenFinancieroCard extends StatelessWidget {
  final double prestado;
  final double pagado;
  final double pendiente;

  const _ResumenFinancieroCard({
    required this.prestado,
    required this.pagado,
    required this.pendiente,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      color: Colors.blue.shade50,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const Text(
              'Resumen Financiero Activo',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Colors.blue),
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _StatItem(label: 'Prestado', value: prestado, color: Colors.blue),
                _StatItem(label: 'Pagado', value: pagado, color: Colors.green),
                _StatItem(label: 'Deben', value: pendiente, color: Colors.red),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String label;
  final double value;
  final Color color;

  const _StatItem({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
        Text(
          '\$${value.toStringAsFixed(0)}',
          style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: color),
        ),
      ],
    );
  }
}
