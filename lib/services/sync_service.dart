import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';
import 'database_service.dart';
import 'api_service.dart';
import 'auth_service.dart';
import '../models/cliente_model.dart';
import '../models/prestamo_model.dart';
import '../config/api_config.dart';

class SyncService extends ChangeNotifier {
  final DatabaseService _dbService = DatabaseService.instance;
  final ApiService _apiService;
  final AuthService _authService;
  final Connectivity _connectivity = Connectivity();

  bool _isOnline = true;
  bool _isSyncing = false;
  DateTime? _lastSyncTime;
  StreamSubscription? _connectivitySubscription;

  SyncService(this._apiService, this._authService) {
    _initConnectivity();
    _listenToConnectivity();
  }

  bool get isOnline => _isOnline;
  bool get isSyncing => _isSyncing;
  DateTime? get lastSyncTime => _lastSyncTime;

  // Inicializar estado de conectividad
  Future<void> _initConnectivity() async {
    try {
      final result = await _connectivity.checkConnectivity();
      _updateConnectionStatus(result);
    } catch (e) {
      print('Error checking connectivity: $e');
      _isOnline = false;
    }
  }

  // Escuchar cambios de conectividad
  void _listenToConnectivity() {
    _connectivitySubscription = _connectivity.onConnectivityChanged.listen(
      (ConnectivityResult result) {
        _updateConnectionStatus(result);
        
        // Si recuperamos conexión, sincronizar automáticamente
        if (_isOnline && !_isSyncing) {
          syncAll();
        }
      },
    );
  }

  void _updateConnectionStatus(ConnectivityResult result) {
    final wasOnline = _isOnline;
    _isOnline = result != ConnectivityResult.none;
    
    if (wasOnline != _isOnline) {
      print('📡 Estado de conexión: ${_isOnline ? "ONLINE" : "OFFLINE"}');
      notifyListeners();
    }
  }

  // ==================== SINCRONIZACIÓN COMPLETA ====================

  Future<void> syncAll() async {
    if (_isSyncing) {
      print('⚠️ Sincronización ya en progreso');
      return;
    }

    if (!_isOnline) {
      print('⚠️ Sin conexión - omitiendo sincronización');
      return;
    }

    _isSyncing = true;
    notifyListeners();

    try {
      print('🔄 Iniciando sincronización completa...');

      // 1. Primero enviar pagos pendientes
      await _syncPagosPendientes();

      // 2. Luego descargar datos actualizados
      await _syncClientes();
      await _syncPrestamos();

      _lastSyncTime = DateTime.now();
      await _dbService.setConfig('last_sync', _lastSyncTime!.toIso8601String());

      print('✅ Sincronización completada');
    } catch (e) {
      print('❌ Error en sincronización: $e');
      rethrow;
    } finally {
      _isSyncing = false;
      notifyListeners();
    }
  }

  // ==================== SINCRONIZAR CLIENTES ====================

  Future<void> _syncClientes() async {
    try {
      print('📥 Descargando clientes...');
      final headers = await _authService.getAuthHeaders();
      final response = await _apiService.getList(
        ApiConfig.clientes,
        headers: headers,
      );

      final clientes = response.map((json) => Cliente.fromJson(json)).toList();

      // Guardar en BD local
      await _dbService.deleteAllClientes();
      await _dbService.insertClientes(clientes);

      print('✅ ${clientes.length} clientes sincronizados');
    } catch (e) {
      print('❌ Error sincronizando clientes: $e');
      rethrow;
    }
  }

  // ==================== SINCRONIZAR PRÉSTAMOS ====================

  Future<void> _syncPrestamos() async {
    try {
      print('📥 Descargando préstamos...');
      final headers = await _authService.getAuthHeaders();
      final response = await _apiService.getList(
        ApiConfig.prestamos,
        headers: headers,
      );

      final prestamos = response.map((json) => Prestamo.fromJson(json)).toList();

      // Guardar en BD local
      await _dbService.deleteAllPrestamos();
      await _dbService.insertPrestamos(prestamos);

      print('✅ ${prestamos.length} préstamos sincronizados');
    } catch (e) {
      print('❌ Error sincronizando préstamos: $e');
      rethrow;
    }
  }

  // ==================== SINCRONIZAR PAGOS PENDIENTES ====================

  Future<void> _syncPagosPendientes() async {
    try {
      final pagosPendientes = await _dbService.getPagosPendientes();

      if (pagosPendientes.isEmpty) {
        print('✅ No hay pagos pendientes para sincronizar');
        return;
      }

      print('📤 Enviando ${pagosPendientes.length} pagos pendientes...');

      final headers = await _authService.getAuthHeaders();
      int exitosos = 0;

      for (var pago in pagosPendientes) {
        try {
          await _apiService.post(
            ApiConfig.nuevoCobro,
            body: {
              'prestamo_id': pago['prestamo_id'],
              'monto': pago['monto'],
              'observaciones': pago['observaciones'],
            },
            headers: headers,
          );

          // Marcar como sincronizado
          await _dbService.marcarPagoComoSincronizado(pago['id'] as int);
          exitosos++;
        } catch (e) {
          print('❌ Error enviando pago ${pago['id']}: $e');
          // Continuar con los demás pagos
        }
      }

      print('✅ $exitosos de ${pagosPendientes.length} pagos sincronizados');

      // Limpiar pagos ya sincronizados
      await _dbService.deletePagosPendientes();
    } catch (e) {
      print('❌ Error sincronizando pagos: $e');
      rethrow;
    }
  }

  // ==================== OBTENER DATOS (CON FALLBACK A BD LOCAL) ====================

  Future<List<Cliente>> getClientes({bool forceOnline = false}) async {
    if (_isOnline && forceOnline) {
      try {
        await _syncClientes();
      } catch (e) {
        print('⚠️ Error descargando clientes online, usando caché local');
      }
    }

    return await _dbService.getClientes();
  }

  Future<List<Prestamo>> getPrestamos({bool forceOnline = false}) async {
    if (_isOnline && forceOnline) {
      try {
        await _syncPrestamos();
      } catch (e) {
        print('⚠️ Error descargando préstamos online, usando caché local');
      }
    }

    return await _dbService.getPrestamos();
  }

  // ==================== REGISTRAR PAGO (OFFLINE-FIRST) ====================

  Future<Map<String, dynamic>> registrarPago({
    required int prestamoId,
    required String clienteNombre,
    required double monto,
    required int cobradorId,
    String? observaciones,
    String? fotoPath,
    double? gpsLatitud,
    double? gpsLongitud,
  }) async {
    try {
      // Guardar en BD local primero (offline-first)
      final pagoId = await _dbService.insertPagoPendiente({
        'prestamo_id': prestamoId,
        'cliente_nombre': clienteNombre,
        'monto': monto,
        'fecha': DateTime.now().toIso8601String(),
        'observaciones': observaciones,
        'cobrador_id': cobradorId,
        'foto_path': fotoPath,
        'gps_latitud': gpsLatitud?.toString(),
        'gps_longitud': gpsLongitud?.toString(),
      });

      // Actualizar préstamo localmente
      final prestamos = await _dbService.getPrestamos();
      final prestamo = prestamos.firstWhere((p) => p.id == prestamoId);
      
      final nuevoSaldo = prestamo.saldoActual - monto;
      final cuotasPagadasNuevas = (monto / prestamo.valorCuota).floor();
      final nuevasCuotasPagadas = prestamo.cuotasPagadas + cuotasPagadasNuevas;
      final nuevasCuotasAtrasadas = prestamo.cuotasAtrasadas > 0 
          ? (prestamo.cuotasAtrasadas - cuotasPagadasNuevas).clamp(0, prestamo.cuotasAtrasadas)
          : 0;

      await _dbService.updatePrestamoSaldo(
        prestamoId,
        nuevoSaldo,
        nuevasCuotasPagadas,
        nuevasCuotasAtrasadas,
      );

      print('✅ Pago guardado localmente (ID: $pagoId)');

      // Si hay conexión, intentar sincronizar inmediatamente
      if (_isOnline) {
        try {
          final headers = await _authService.getAuthHeaders();
          final response = await _apiService.post(
            ApiConfig.nuevoCobro,
            body: {
              'prestamo_id': prestamoId,
              'monto': monto,
              'observaciones': observaciones,
            },
            headers: headers,
          );

          // Marcar como sincronizado
          await _dbService.marcarPagoComoSincronizado(pagoId);
          print('✅ Pago sincronizado inmediatamente');

          return {
            'success': true,
            'pago_id': pagoId,
            'sincronizado': true,
            'mensaje': 'Pago registrado y sincronizado',
            ...response,
          };
        } catch (e) {
          print('⚠️ Error sincronizando pago, se enviará después: $e');
          return {
            'success': true,
            'pago_id': pagoId,
            'sincronizado': false,
            'mensaje': 'Pago guardado, se sincronizará cuando haya conexión',
          };
        }
      } else {
        return {
          'success': true,
          'pago_id': pagoId,
          'sincronizado': false,
          'mensaje': 'Pago guardado sin conexión, se sincronizará después',
        };
      }
    } catch (e) {
      print('❌ Error registrando pago: $e');
      rethrow;
    }
  }

  // ==================== ESTADÍSTICAS ====================

  Future<Map<String, dynamic>> getEstadisticas() async {
    // Si hay conexión, intentar obtener del servidor
    if (_isOnline) {
      try {
        final headers = await _authService.getAuthHeaders();
        final response = await _apiService.get(
          '/dashboard_stats', // Nuevo endpoint
          headers: headers,
        );
        return {
          ...response,
          'sincronizado': true,
        };
      } catch (e) {
        print('⚠️ Error obteniendo estadísticas online: $e');
        // Fallback a cálculo local
      }
    }

    // Cálculo local (Offline)
    final prestamos = await _dbService.getPrestamos();

    final totalCartera = prestamos.fold<double>(
      0,
      (sum, p) => sum + p.saldoActual,
    );

    final capitalPrestado = prestamos.fold<double>(
      0,
      (sum, p) => sum + p.montoPrestado,
    );

    final prestamosAlDia = prestamos.where((p) => p.cuotasAtrasadas == 0).length;
    final prestamosAtrasados = prestamos.where((p) => p.cuotasAtrasadas > 0).length;
    final prestamosMoraGrave = prestamos.where((p) => p.cuotasAtrasadas > 3).length;

    // Obtener pagos pendientes de sincronización
    final pagosPendientes = await _dbService.getPagosPendientes();

    return {
      'total_prestamos': prestamos.length,
      'total_cartera': totalCartera,
      'capital_prestado': capitalPrestado,
      'prestamos_al_dia': prestamosAlDia,
      'prestamos_atrasados': prestamosAtrasados,
      'prestamos_mora_grave': prestamosMoraGrave,
      'pagos_pendientes_sync': pagosPendientes.length,
      'sincronizado': _isOnline && pagosPendientes.isEmpty,
    };
  }

  @override
  void dispose() {
    _connectivitySubscription?.cancel();
    super.dispose();
  }
}
