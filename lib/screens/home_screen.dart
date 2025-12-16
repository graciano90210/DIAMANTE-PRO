import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _isLoading = false;
  String _message = 'Bienvenido a Diamante PRO';

  // Ejemplo de cómo hacer una petición a tu API
  Future<void> _testConnection() async {
    setState(() {
      _isLoading = true;
      _message = 'Conectando con el servidor...';
    });

    try {
      final apiService = context.read<ApiService>();
      
      // Probar con POST al login (sin credenciales válidas, solo para probar CORS)
      try {
        await apiService.post('/login', body: {'usuario': 'test', 'password': 'test'});
      } catch (e) {
        // Si el error es 400 o 401, significa que el servidor SÍ respondió (CORS OK)
        if (e.toString().contains('400') || e.toString().contains('401')) {
          setState(() {
            _message = '✅ ¡Conexión exitosa!\n\nEl servidor está respondiendo correctamente.\nCORS está funcionando.';
            _isLoading = false;
          });
          return;
        }
        throw e;
      }
      
      setState(() {
        _message = '✅ ¡Conexión exitosa con Diamante PRO!';
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _message = '❌ Error de conexión\n\nEl servidor no está respondiendo o CORS no está configurado.\n\n$e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Diamante PRO'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.diamond,
                size: 100,
                color: Colors.blue,
              ),
              const SizedBox(height: 32),
              Text(
                _message,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 32),
              if (_isLoading)
                const CircularProgressIndicator()
              else
                ElevatedButton.icon(
                  onPressed: _testConnection,
                  icon: const Icon(Icons.wifi),
                  label: const Text('Probar Conexión'),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
