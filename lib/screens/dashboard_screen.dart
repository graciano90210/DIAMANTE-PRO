import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import '../providers/auth_provider.dart';
import '../services/sync_service.dart';
import 'clientes_screen.dart';
import 'prestamos_screen.dart';
import 'cobros_screen.dart';
import 'ruta_dia_screen.dart';
import 'login_screen.dart';
import 'registrar_gasto_screen.dart';
import '../main.dart'; // Importamos las constantes globales

// Estilo de sombra brillante (Neon Glow)
List<BoxShadow> kNeonShadow = [
  BoxShadow(
    color: kNeonCyan.withOpacity(0.3),
    blurRadius: 8,
    spreadRadius: 1,
    offset: const Offset(0, 2),
  ),
];

// Estilo de texto para títulos
const TextStyle kHeadingStyle = TextStyle(
  fontSize: 22,
  fontWeight: FontWeight.bold,
  color: kTextWhite,
  letterSpacing: 1.2,
);

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
      final response = await syncService.getEstadisticas();
      
      if (mounted) {
        setState(() {
          _stats = response;
          _isLoading = false;
        });
      }
      
      if (syncService.isOnline) {
        syncService.syncAll().catchError((e) {
          debugPrint('⚠️ Error en sincronización de fondo: $e');
        });
      }
    } catch (e) {
      debugPrint('❌ Error al cargar dashboard: $e');
      if (mounted) setState(() => _isLoading = false);
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
  
  String _getFormattedDateShort() {
    final now = DateTime.now();
    final weekDays = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
    final months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    return '${weekDays[now.weekday - 1]}, ${now.day} ${months[now.month - 1]}';
  }

  @override
  Widget build(BuildContext context) {
    // Valores del endpoint /dashboard_stats
    final totalClientes = ((_stats?['total_clientes'] ?? 0) as num).toInt();
    final totalCobrar = ((_stats?['total_cobrar'] ?? 0) as num).toDouble();
    final recaudadoHoy = ((_stats?['recaudado_hoy'] ?? 0) as num).toDouble();
    final gastosHoy = ((_stats?['gastos_hoy'] ?? 0) as num).toDouble();
    final netoHoy = ((_stats?['neto_hoy'] ?? 0) as num).toDouble();

    // Calcula efectividad de cobro
    final efectividadPercentage = totalCobrar > 0 ? (recaudadoHoy / totalCobrar) : 0.0;


    return Scaffold(
      backgroundColor: kBgDark,
      // Usamos un Container como fondo para dar un degradado sutil
      body: Container(
        decoration: const BoxDecoration(
            gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [kBgDark, Color(0xFF121212)])),
        child: SafeArea(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // --- HEADER PERSONALIZADO ---
              Padding(
                padding: const EdgeInsets.all(20.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    IconButton(
                      icon: const Icon(FontAwesomeIcons.barsStaggered, color: kTextWhite),
                      onPressed: () =>  _showCustomDrawer(context), // Implementaremos un drawer personalizado o modal
                    ),
                    const Icon(FontAwesomeIcons.gem, color: kNeonCyan, size: 30), // Logo Diamante Brillante
                    const Icon(FontAwesomeIcons.solidBell, color: kTextWhite),
                  ],
                ),
              ),

              // --- SECCIÓN DE ACCESOS RÁPIDOS FUTURISTAS ---
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 20.0),
                child: Text('Accesos Rápidos', style: kHeadingStyle),
              ),
              const SizedBox(height: 15),
              SizedBox(
                height: 100, // Altura fija para el scroll horizontal
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.only(left: 20),
                  children: [
                    TechActionCard(
                      icon: FontAwesomeIcons.users, 
                      label: 'Clientes', 
                      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ClientesScreen()))
                    ),
                    TechActionCard(
                      icon: FontAwesomeIcons.handHoldingDollar, 
                      label: 'Créditos', 
                      isPrimary: true, 
                      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const PrestamosScreen()))
                    ), // Destacado
                    TechActionCard(
                      icon: FontAwesomeIcons.moneyBillTrendUp, 
                      label: 'Cobrar', 
                      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const CobrosScreen()))
                    ),
                     TechActionCard(
                      icon: FontAwesomeIcons.cartShopping, 
                      label: 'Gastos', 
                      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const RegistrarGastoScreen()))
                    ),
                    TechActionCard(
                      icon: FontAwesomeIcons.route, 
                      label: 'Ruta', 
                      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const RutaDiaScreen()))
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 25),

              // --- SECCIÓN DEL DASHBOARD (Resumen) ---
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20.0),
                child: Row(
                   mainAxisAlignment: MainAxisAlignment.spaceBetween,
                   children: [
                     const Text('Resumen de Hoy', style: kHeadingStyle),
                      Text(_getFormattedDateShort(), style: const TextStyle(color: kNeonCyan)),
                   ]
                ),
              ),
              const SizedBox(height: 15),

              // Expanded para que el resto ocupe el espacio sobrante
              Expanded(
                child: RefreshIndicator(
                  color: kNeonCyan,
                  backgroundColor: kCardDark,
                  onRefresh: _loadDashboard,
                  child: ListView(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    children: [
                      // --- TARJETA PRINCIPAL (Cobranza) ---
                      TechDataCard(
                        title: 'Cobranza del Día',
                        totalValue: totalCobrar,
                        currentValue: recaudadoHoy,
                        icon: FontAwesomeIcons.sackDollar,
                        isHighlight: true,
                      ),
                      const SizedBox(height: 15),

                      // --- NUEVA TARJETA DE GASTOS ---
                      TechDataCard(
                        title: 'Gastos del Día',
                        totalValue: gastosHoy > 0 ? gastosHoy : 1, // Para evitar división por cero
                        currentValue: gastosHoy,
                        icon: FontAwesomeIcons.moneyBillWave,
                        isHighlight: false,
                      ),
                      const SizedBox(height: 15),

                      // --- NUEVA TARJETA DE NETO ---
                      TechDataCard(
                        title: 'Neto del Día',
                        totalValue: netoHoy.abs() > 0 ? netoHoy.abs() : 1, // Para evitar división por cero
                        currentValue: netoHoy,
                        icon: FontAwesomeIcons.wallet,
                        isHighlight: false,
                      ),
                      const SizedBox(height: 15),

                      // --- TARJETAS SECUNDARIAS EN FILA ---
                      Row(
                        children: [
                          Expanded(
                            child: TechDataCardSmall(
                              title: 'Clientes Visitados',
                              value: '$clientesVisitados/${clientesVisitados + clientesPendientes}',
                              percentage: visitadosPercentage,
                              icon: FontAwesomeIcons.route,
                            ),
                          ),
                          const SizedBox(width: 15),
                          Expanded(
                            child: TechDataCardSmall(
                              title: 'Efectividad Cobro',
                              value: '${(efectividadPercentage * 100).toStringAsFixed(1)}%',
                              percentage: efectividadPercentage,
                              icon: FontAwesomeIcons.bullseye,
                              colorAccent: Colors.purpleAccent,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 20),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
        // Un BottomNavigationBar moderno y oscuro para cerrar con broche de oro
      bottomNavigationBar: BottomNavigationBar(
        backgroundColor: kBgDark,
        selectedItemColor: kNeonCyan,
        unselectedItemColor: kTextGrey,
        type: BottomNavigationBarType.fixed,
        currentIndex: 0, 
        onTap: (index) {
          // Implement navigation logic if needed
        },
        items: const [
          BottomNavigationBarItem(icon: Icon(FontAwesomeIcons.house), label: ''),
          BottomNavigationBarItem(icon: Icon(FontAwesomeIcons.listUl), label: ''),
          BottomNavigationBarItem(icon: Icon(Icons.add_circle_outline, size: 40, color: kNeonCyan), label: ''), // Botón central destacado
          BottomNavigationBarItem(icon: Icon(FontAwesomeIcons.solidCreditCard), label: ''),
          BottomNavigationBarItem(icon: Icon(FontAwesomeIcons.gear), label: ''),
        ],
      ),
    );
  }

  void _showCustomDrawer(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        decoration: const BoxDecoration(
          color: kCardDark,
          borderRadius: BorderRadius.vertical(top: Radius.circular(25))
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 20),
            Container(height: 4, width: 40, decoration: BoxDecoration(color: kTextGrey, borderRadius: BorderRadius.circular(2))),
            const SizedBox(height: 20),
            ListTile(
              leading: const Icon(Icons.logout, color: Colors.redAccent),
              title: const Text('Cerrar Sesión', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                _handleLogout();
              },
            ),
            const SizedBox(height: 40),
          ],
        ),
      )
    );
  }
}

// Widget para los botones de acceso rápido superiores
class TechActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  final bool isPrimary;

  const TechActionCard({
    super.key,
    required this.icon,
    required this.label,
    required this.onTap,
    this.isPrimary = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(right: 15),
        padding: const EdgeInsets.all(15),
        width: 110,
        decoration: BoxDecoration(
          // Si es primario, el fondo es cian, si no, es oscuro
          color: isPrimary ? kNeonCyan.withOpacity(0.2) : kCardDark,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
              color: isPrimary ? kNeonCyan : Colors.transparent, width: 1.5),
          boxShadow: isPrimary ? kNeonShadow : [],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: isPrimary ? kNeonCyan : kTextWhite, size: 28),
            const SizedBox(height: 8),
            Text(
              label,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: isPrimary ? kNeonCyan : kTextGrey,
                fontSize: 12,
                fontWeight: isPrimary ? FontWeight.bold : FontWeight.normal
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Widget para la tarjeta grande principal
class TechDataCard extends StatelessWidget {
  final String title;
  final double totalValue;
  final double currentValue;
  final IconData icon;
  final bool isHighlight;

  const TechDataCard({
    super.key,
    required this.title,
    required this.totalValue,
    required this.currentValue,
    required this.icon,
    this.isHighlight = false,
  });

  @override
  Widget build(BuildContext context) {
    // --- CORRECCIÓN LÓGICA MATEMÁTICA ---
    // Si el total es 0, el porcentaje es 0. Evitamos división por cero.
    double percentage = totalValue == 0 ? 0.0 : (currentValue / totalValue);
    // Aseguramos que no pase de 1.0 (100%)
    if (percentage > 1.0) percentage = 1.0;


    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: kCardDark,
        borderRadius: BorderRadius.circular(25),
        // Sombra neón solo si está destacada
        boxShadow: isHighlight ? kNeonShadow : [],
        border: isHighlight ? Border.all(color: kNeonCyan.withOpacity(0.5)) : null,
      ),
      child: Row(
        children: [
          // Columna de textos
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(icon, color: kTextGrey, size: 18),
                    const SizedBox(width: 8),
                    Text(title, style: const TextStyle(color: kTextGrey)),
                  ],
                ),
                const SizedBox(height: 10),
                // Muestra el valor monetario
                Text(
                  '\$${totalValue.toStringAsFixed(2)}',
                  style: kHeadingStyle.copyWith(fontSize: 28, color: isHighlight ? kNeonCyan : kTextWhite),
                ),
                const SizedBox(height: 5),
                Text(
                  'Cobrado: \$${currentValue.toStringAsFixed(2)}',
                   style: const TextStyle(color: kTextGrey, fontSize: 12),
                )
              ],
            ),
          ),
          // Gráfico Circular (Indicator)
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                height: 80,
                width: 80,
                child: CircularProgressIndicator(
                  // Usamos el porcentaje corregido
                  value: percentage,
                  backgroundColor: kBgDark,
                  color: isHighlight ? kNeonCyan : Colors.purpleAccent,
                  strokeWidth: 8,
                ),
              ),
              Text(
                // Muestra el porcentaje sin decimales
                '${(percentage * 100).toStringAsFixed(0)}%',
                style: const TextStyle(color: kTextWhite, fontWeight: FontWeight.bold),
              )
            ],
          )
        ],
      ),
    );
  }
}

// Widget para las tarjetas secundarias más pequeñas
class TechDataCardSmall extends StatelessWidget {
  final String title;
  final String value;
  final double percentage;
  final IconData icon;
  final Color colorAccent;

  const TechDataCardSmall({
    super.key,
    required this.title,
    required this.value,
    required this.percentage,
    required this.icon,
    this.colorAccent = kNeonCyan, // Por defecto cian, pero se puede cambiar
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: kCardDark,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Icon(icon, color: colorAccent, size: 20),
               // Pequeño indicador circular arriba a la derecha
               SizedBox(
                height: 25,
                width: 25,
                child: CircularProgressIndicator(
                  value: percentage,
                  backgroundColor: kBgDark,
                  color: colorAccent,
                  strokeWidth: 3,
                ),
              ),
            ],
          ),
          const SizedBox(height: 15),
          Text(value, style: kHeadingStyle),
          const SizedBox(height: 5),
          Text(title, style: const TextStyle(color: kTextGrey, fontSize: 12)),
        ],
      ),
    );
  }
}
