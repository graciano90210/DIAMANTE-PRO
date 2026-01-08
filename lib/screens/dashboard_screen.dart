import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../services/sync_service.dart';
import 'clientes_screen.dart';
import 'prestamos_screen.dart';
import 'cobros_screen.dart';
import 'ruta_dia_screen.dart';
import 'login_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _stats;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    setState(() => _isLoading = true);
    
    try {
      final syncService = context.read<SyncService>();
      
      print('🔍 Cargando estadísticas del cobrador...');
      
      // Usar SyncService en lugar de API directamente
      final response = await syncService.getEstadisticas();
      
      print('✅ Respuesta recibida: $response');
      
      setState(() {
        _stats = response;
        _isLoading = false;
      });
      
      print('📊 Stats guardados: $_stats');
      
      // Sincronizar en segundo plano si hay conexión
      if (syncService.isOnline) {
        syncService.syncAll().catchError((e) {
          print('⚠️ Error en sincronización de fondo: $e');
        });
      }
    } catch (e) {
      print('❌ Error al cargar dashboard: $e');
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  Future<void> _handleLogout() async {
    final authProvider = context.read<AuthProvider>();
    await authProvider.logout();
    
    if (mounted) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const LoginScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final syncService = context.watch<SyncService>();
    
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            const Text('Dashboard'),
            const SizedBox(width: 8),
            // Indicador de conexión
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: syncService.isOnline ? Colors.green : Colors.grey,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    syncService.isOnline ? Icons.cloud_done : Icons.cloud_off,
                    size: 16,
                    color: Colors.white,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    syncService.isOnline ? 'ONLINE' : 'OFFLINE',
                    style: const TextStyle(
                      fontSize: 12,
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            if (syncService.isSyncing)
              const Padding(
                padding: EdgeInsets.only(left: 8),
                child: SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                  ),
                ),
              ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _loadDashboard,
          ),
          IconButton(
            icon: const Icon(Icons.sync),
            onPressed: syncService.isSyncing 
                ? null 
                : () {
                    syncService.syncAll().then((_) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Sincronización completada')),
                      );
                      _loadDashboard();
                    }).catchError((e) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Error: $e')),
                      );
                    });
                  },
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _handleLogout,
          ),
        ],
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  const Icon(
                    Icons.diamond,
                    size: 50,
                    color: Colors.white,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    authProvider.currentUser?.name ?? 'Usuario',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    authProvider.currentUser?.email ?? '',
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
            ListTile(
              leading: const Icon(Icons.dashboard),
              title: const Text('Dashboard'),
              onTap: () {
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.people),
              title: const Text('Clientes'),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const ClientesScreen()),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.attach_money),
              title: const Text('Préstamos'),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const PrestamosScreen()),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.route),
              title: const Text('Ruta del Día'),
              trailing: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.orange,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  _stats != null ? (_stats!['por_cobrar_hoy'] ?? 0).toString() : '0',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const RutaDiaScreen()),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.payment),
              title: const Text('Registrar Cobro'),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const CobrosScreen()),
                );
              },
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text('Cerrar Sesión'),
              onTap: _handleLogout,
            ),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadDashboard,
              child: _buildDashboard(),
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const RutaDiaScreen()),
          );
        },
        icon: const Icon(Icons.route),
        label: const Text('Ruta del Día'),
        backgroundColor: Colors.orange,
      ),
    );
  }

  Widget _buildDashboard() {
    if (_stats == null) {
      return const Center(
        child: Text('No hay datos disponibles'),
      );
    }

    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Resumen General',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 16),
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            children: [
              _buildStatCard(
                'Préstamos Activos',
                '${_stats!['total_prestamos'] ?? 0}',
                Icons.assignment,
                Colors.blue,
              ),
              _buildStatCard(
                'Total Cartera',
                '\$${(_stats!['total_cartera'] ?? 0).toStringAsFixed(2)}',
                Icons.account_balance_wallet,
                Colors.green,
              ),
              _buildStatCard(
                'Cobrado Hoy',
                '\$${(_stats!['cobrado_hoy'] ?? 0).toStringAsFixed(2)}',
                Icons.check_circle,
                Colors.teal,
              ),
              _buildStatCard(
                'Por Cobrar Hoy',
                '\$${(_stats!['por_cobrar_hoy'] ?? 0).toStringAsFixed(2)}',
                Icons.schedule,
                Colors.orange,
              ),
              _buildStatCard(
                'Al Día',
                '${_stats!['prestamos_al_dia'] ?? 0}',
                Icons.check,
                Colors.green,
              ),
              _buildStatCard(
                'Atrasados',
                '${_stats!['prestamos_atrasados'] ?? 0}',
                Icons.warning,
                Colors.red,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 40, color: color),
            const SizedBox(height: 12),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
