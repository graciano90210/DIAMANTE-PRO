import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:provider/provider.dart';
// IMPORTANTE: Asegúrate de importar el archivo donde definiste las constantes de color (main.dart o constants.dart)
import '../main.dart'; 
import '../providers/auth_provider.dart';
import 'dashboard_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key}); // Added super.key for consistency

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  // Controllers and State
  final _usuarioController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _usuarioController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    final username = _usuarioController.text.trim();
    final password = _passwordController.text;

    if (username.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Por favor ingresa usuario y contraseña')),
      );
      return;
    }

    setState(() => _isLoading = true);

    final authProvider = context.read<AuthProvider>();
    final success = await authProvider.login(username, password);

    if (mounted) {
      setState(() => _isLoading = false);
      if (success) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const DashboardScreen()),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authProvider.errorMessage ?? 'Error al iniciar sesión'),
            backgroundColor: kNeonRed,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // Obtenemos el tema actual para usar sus estilos
    final theme = Theme.of(context);

    return Scaffold(
      // El color de fondo ya lo pone el tema global
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 30.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // --- LOGO CON EFECTO NEÓN ---
              Container(
                padding: const EdgeInsets.all(25),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: kCardDark, // Usa la constante de color oscuro
                  boxShadow: [
                    BoxShadow(
                      color: kNeonCyan.withOpacity(0.4), // Brillo cian
                      blurRadius: 30,
                      spreadRadius: 5,
                    )
                  ],
                ),
                child: const Icon(FontAwesomeIcons.gem, size: 70, color: kNeonCyan),
              ),
              const SizedBox(height: 40),

              // --- TÍTULOS ---
              Text(
                'DIAMANTE PRO',
                style: theme.textTheme.titleLarge?.copyWith(fontSize: 32, letterSpacing: 3),
              ),
              const SizedBox(height: 10),
              Text(
                'Sistema de Cobranza v1.0.3 (Dark Tech)',
                style: theme.textTheme.bodySmall?.copyWith(fontSize: 16),
              ),
              const SizedBox(height: 60),

              // --- CAMPOS DE TEXTO (Se estilizan solos con el tema global) ---
              TextField(
                controller: _usuarioController,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(
                  labelText: 'Usuario',
                  prefixIcon: Icon(FontAwesomeIcons.userLarge),
                  hintText: 'Ingresa tu usuario',
                ),
                style: const TextStyle(color: kTextWhite), // Color del texto al escribir
              ),
              const SizedBox(height: 25),
              TextField(
                controller: _passwordController,
                obscureText: _obscurePassword,
                decoration: InputDecoration(
                  labelText: 'Contraseña',
                  prefixIcon: const Icon(FontAwesomeIcons.lock),
                  suffixIcon: IconButton(
                    icon: Icon(_obscurePassword ? FontAwesomeIcons.eye : FontAwesomeIcons.eyeSlash),
                    onPressed: () {
                      setState(() {
                         _obscurePassword = !_obscurePassword;
                      });
                    },
                  ), // Ícono para ver contraseña
                  hintText: 'Ingresa tu contraseña',
                ),
                style: const TextStyle(color: kTextWhite),
              ),
              const SizedBox(height: 50),

              // --- BOTÓN DE INICIO (Toma el estilo del tema global) ---
              SizedBox(
                width: double.infinity, // Ancho completo
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _handleLogin,
                  child: _isLoading 
                    ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: kBgDark, strokeWidth: 2))
                    : const Text('INICIAR SESIÓN'),
                ),
              ),
              const SizedBox(height: 30),
               TextButton(
                onPressed: (){}, 
                child: const Text('¿Olvidaste tu contraseña?', style: TextStyle(color: kTextGrey))
              )
            ],
          ),
        ),
      ),
    );
  }
}
