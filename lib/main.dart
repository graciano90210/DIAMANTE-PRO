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

// --- 1. CONSTANTES DE DISEÑO DIAMANTE PRO (igual que la web) ---
const Color kBgDark = Color(0xFF0D1117);      // Fondo principal oscuro
const Color kCardDark = Color(0xFF161B22);    // Color de tarjetas
const Color kInputBg = Color(0xFF0D1926);     // Fondo de inputs (azul oscuro)
const Color kPrimaryGreen = Color(0xFF00D67F); // Verde header/botones
const Color kNeonCyan = Color(0xFF00D67F);    // Alias para compatibilidad
const Color kNeonGreen = Color(0xFF00D67F);   // Verde para acciones
const Color kNeonRed = Color(0xFFFF4757);     // Rojo para errores
const Color kTextWhite = Colors.white;
const Color kTextGrey = Color(0xFF8B949E);

// --- 2. DEFINICIÓN DEL TEMA GLOBAL (igual que la web) ---
final ThemeData kDarkTechTheme = ThemeData.dark().copyWith(
  scaffoldBackgroundColor: kBgDark,
  primaryColor: kPrimaryGreen,
  cardColor: kCardDark,
  colorScheme: const ColorScheme.dark(
    primary: kPrimaryGreen,
    secondary: kPrimaryGreen,
    surface: kCardDark,
    error: kNeonRed,
  ),

  // AppBar verde como la web
  appBarTheme: const AppBarTheme(
    backgroundColor: kPrimaryGreen,
    elevation: 0,
    centerTitle: false,
    titleTextStyle: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
    iconTheme: IconThemeData(color: Colors.white),
  ),

  // Textos
  textTheme: const TextTheme(
    bodyLarge: TextStyle(color: kTextWhite),
    bodyMedium: TextStyle(color: kTextWhite),
    bodySmall: TextStyle(color: kTextGrey),
    titleLarge: TextStyle(color: kTextWhite, fontWeight: FontWeight.bold),
    titleMedium: TextStyle(color: kTextWhite, fontWeight: FontWeight.bold),
    labelLarge: TextStyle(color: kTextGrey),
  ),

  // Inputs con fondo azul oscuro como la web
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    fillColor: kInputBg,
    labelStyle: const TextStyle(color: kTextGrey),
    hintStyle: TextStyle(color: kTextGrey.withOpacity(0.6)),
    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
      borderSide: BorderSide.none,
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
      borderSide: BorderSide.none,
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
      borderSide: const BorderSide(color: kPrimaryGreen, width: 2),
    ),
    errorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
      borderSide: const BorderSide(color: kNeonRed, width: 1),
    ),
  ),

  // Botones verdes como la web
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: kPrimaryGreen,
      foregroundColor: Colors.white,
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
      elevation: 0,
    ),
  ),

  textButtonTheme: TextButtonThemeData(
    style: TextButton.styleFrom(foregroundColor: kPrimaryGreen),
  ),

  floatingActionButtonTheme: const FloatingActionButtonThemeData(
    backgroundColor: kPrimaryGreen,
    foregroundColor: Colors.white,
  ),

  iconTheme: const IconThemeData(color: kPrimaryGreen),

  bottomNavigationBarTheme: const BottomNavigationBarThemeData(
    backgroundColor: kBgDark,
    selectedItemColor: kPrimaryGreen,
    unselectedItemColor: kTextGrey,
    elevation: 0,
  ),

  cardTheme: CardTheme(
    color: kCardDark,
    elevation: 0,
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
  ),

  dialogTheme: DialogTheme(
    backgroundColor: kCardDark,
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
  ),
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
