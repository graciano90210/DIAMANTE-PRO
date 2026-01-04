import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/prestamo_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'prestamo_detalle_screen.dart';

class PrestamosScreen extends StatefulWidget {
  const PrestamosScreen({super.key});

  @override
  State<PrestamosScreen> createState() => _PrestamosScreenState();
}

class _PrestamosScreenState extends State<PrestamosScreen> {
  List<Prestamo> _prestamos = [];
  bool _isLoading = true;
  String _filtro = 'todos'; // todos, al_dia, atrasados

  @override
  void initState() {
    super.initState();
    _loadPrestamos();
  }

  Future<void> _loadPrestamos() async {
    setState(() => _isLoading = true);

    try {
      final apiService = context.read<ApiService>();
      final authService = context.read<AuthService>();
      final headers = await authService.getAuthHeaders();

      final response = await apiService.getList('/api/v1/cobrador/prestamos', headers: headers);

      setState(() {
        _prestamos = response.map((json) => Prestamo.fromJson(json)).toList();
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

  List<Prestamo> get _filteredPrestamos {
    switch (_filtro) {
      case 'al_dia':
        return _prestamos.where((p) => p.estaAlDia).toList();
      case 'atrasados':
        return _prestamos.where((p) => p.estaMora).toList();
      default:
        return _prestamos;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Préstamos'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadPrestamos,
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
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
                    label: const Text('Al Día'),
                    selected: _filtro == 'al_dia',
                    onSelected: (selected) {
                      if (selected) setState(() => _filtro = 'al_dia');
                    },
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ChoiceChip(
                    label: const Text('Atrasados'),
                    selected: _filtro == 'atrasados',
                    onSelected: (selected) {
                      if (selected) setState(() => _filtro = 'atrasados');
                    },
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _filteredPrestamos.isEmpty
                    ? const Center(child: Text('No hay préstamos'))
                    : ListView.builder(
                        itemCount: _filteredPrestamos.length,
                        itemBuilder: (context, index) {
                          final prestamo = _filteredPrestamos[index];
                          return Card(
                            margin: const EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 8,
                            ),
                            child: ListTile(
                              leading: CircleAvatar(
                                backgroundColor: prestamo.moraGrave
                                    ? Colors.red
                                    : prestamo.estaMora
                                        ? Colors.orange
                                        : Colors.green,
                                child: Text(
                                  prestamo.cuotasAtrasadas.toString(),
                                  style: const TextStyle(color: Colors.white),
                                ),
                              ),
                              title: Text(
                                prestamo.clienteNombre,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const SizedBox(height: 4),
                                  Text('Monto: \$${prestamo.montoPrestado.toStringAsFixed(2)}'),
                                  Text(
                                      'Cuota: \$${prestamo.valorCuota.toStringAsFixed(2)}'),
                                  Text(
                                      'Saldo: \$${prestamo.saldoActual.toStringAsFixed(2)}'),
                                  Text(
                                      'Cuotas pagadas: ${prestamo.cuotasPagadas}/${prestamo.numeroCuotas}'),
                                ],
                              ),
                              trailing: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  if (prestamo.cuotasAtrasadas > 0)
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 8,
                                        vertical: 4,
                                      ),
                                      decoration: BoxDecoration(
                                        color: prestamo.moraGrave
                                            ? Colors.red
                                            : Colors.orange,
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      child: Text(
                                        '${prestamo.cuotasAtrasadas} atr.',
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontSize: 12,
                                        ),
                                      ),
                                    ),
                                ],
                              ),
                              onTap: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) => PrestamoDetalleScreen(
                                      prestamo: prestamo,
                                    ),
                                  ),
                                );
                              },
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
