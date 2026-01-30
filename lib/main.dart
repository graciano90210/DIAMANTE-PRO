import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/login_screen.dart';
import 'screens/dashboard_screen.dart';
import 'screens/registrar_cobro_screen.dart';
import 'services/api_service.dart';
import 'services/auth_service.dart';
import 'services/sync_service.dart';
import 'providers/auth_provider.dart';
import 'models/prestamo_model.dart';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:sqflite_common_ffi_web/sqflite_ffi_web.dart';

// --- 1. CONSTANTES DE DISEÑO TECH ---
// (Pégalas al principio del archivo, fuera de main())
const Color kBgDark = Color(0xFF0A0E21);   // Fondo principal casi negro
const Color kCardDark = Color(0xFF1D1E33); // Color de tarjetas y campos
const Color kNeonCyan = Color(0xFF00E5FF); // Azul eléctrico principal
const Color kNeonGreen = Color(0xFF00FF99); // Verde neón para acciones positivas
const Color kNeonRed = Color(0xFFFF3366);   // Rojo neón para gastos/errores
const Color kTextWhite = Colors.white;
const Color kTextGrey = Color(0xFF8D8E98);

// --- 2. DEFINICIÓN DEL TEMA GLOBAL ---
// (Pégalo justo debajo de las constantes)
final ThemeData kDarkTechTheme = ThemeData.dark().copyWith(
  // Colores base
  scaffoldBackgroundColor: kBgDark,
  primaryColor: kNeonCyan,
  cardColor: kCardDark, // Para alertas y menús

  // Barra superior (AppBar)
  appBarTheme: const AppBarTheme(
    backgroundColor: kBgDark,
    elevation: 0, // Sin sombra para un look plano y moderno
    centerTitle: true,
    titleTextStyle: TextStyle(color: kTextWhite, fontSize: 20, fontWeight: FontWeight.bold, letterSpacing: 1),
    iconTheme: IconThemeData(color: kNeonCyan), // Íconos de atrás/menú en cian
  ),

  // Textos
  textTheme: const TextTheme(
    bodyMedium: TextStyle(color: kTextWhite), // Texto normal
    bodySmall: TextStyle(color: kTextGrey),   // Subtítulos
    titleLarge: TextStyle(color: kNeonCyan, fontWeight: FontWeight.bold), // Títulos grandes
    titleMedium: TextStyle(color: kTextWhite, fontWeight: FontWeight.bold), // Títulos de tarjetas
  ),

  // Campos de texto (Inputs) - ¡Esto hará que se vean increíbles!
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    fillColor: kCardDark, // Fondo oscuro
    labelStyle: const TextStyle(color: kTextGrey),
    hintStyle: TextStyle(color: kTextGrey.withOpacity(0.5)),
    contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(15),
      borderSide: BorderSide.none, // Sin borde cuando no está en foco
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(15),
      borderSide: BorderSide(color: kCardDark.withOpacity(0.5)),
    ),
    focusedBorder: OutlineInputBorder( // Borde brillante al tocar
      borderRadius: BorderRadius.circular(15),
      borderSide: const BorderSide(color: kNeonCyan, width: 2),
    ),
    prefixIconColor: kTextGrey,
    suffixIconColor: kNeonCyan,
  ),

  // Botones principales (ElevatedButton)
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: kNeonCyan, // Color de fondo cian
      foregroundColor: kBgDark,   // Texto oscuro para contraste
      padding: const EdgeInsets.symmetric(vertical: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
      textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, letterSpacing: 1),
      elevation: 5,
      shadowColor: kNeonCyan.withOpacity(0.4), // Sombra con color neón
    ),
  ),

  // Íconos generales
  iconTheme: const IconThemeData(color: kNeonCyan),
  
  // Menú inferior
  bottomNavigationBarTheme: const BottomNavigationBarThemeData(
    backgroundColor: kBgDark,
    selectedItemColor: kNeonCyan,
    unselectedItemColor: kTextGrey,
    elevation: 0,
  ), dialogTheme: const DialogThemeData(backgroundColor: kCardDark),
);

void main() {
  if (kIsWeb) {
    // Initialize FFI for Web
    databaseFactory = databaseFactoryFfiWeb;
  } else if (Platform.isWindows || Platform.isLinux) {
    // Initialize FFI
    sqfliteFfiInit();
    
    // Change the default factory
    databaseFactory = databaseFactoryFfi;
  }

  runApp(const DiamantePro());
}

class DiamantePro extends StatelessWidget {
  const DiamantePro({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<ApiService>(
          create: (_) => ApiService(),
        ),
        ProxyProvider<ApiService, AuthService>(
          update: (_, apiService, __) => AuthService(apiService),
        ),
        ChangeNotifierProxyProvider2<ApiService, AuthService, SyncService>(
          create: (context) => SyncService(
            context.read<ApiService>(),
            context.read<AuthService>(),
          ),
          update: (_, apiService, authService, previous) =>
              previous ?? SyncService(apiService, authService),
        ),
        ChangeNotifierProxyProvider<AuthService, AuthProvider>(
          create: (context) => AuthProvider(context.read<AuthService>()),
          update: (_, authService, previous) =>
              previous ?? AuthProvider(authService),
        ),
      ],
      child: MaterialApp(
        title: 'Diamante PRO',
        debugShowCheckedModeBanner: false,
        theme: kDarkTechTheme,
        home: const AuthCheck(),
        routes: {
          '/registrar-cobro': (context) {
            final prestamo = ModalRoute.of(context)?.settings.arguments as Prestamo?;
            return RegistrarCobroScreen(prestamo: prestamo);
          },
          '/dashboard': (context) => const DashboardScreen(),
        },
      ),
    );
  }
}

class AuthCheck extends StatelessWidget {
  const AuthCheck({super.key});

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<bool>(
      future: context.read<AuthProvider>().checkSession(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }

        if (snapshot.data == true) {
          return const DashboardScreen();
        }

        return const LoginScreen();
      },
    );
  }
}
