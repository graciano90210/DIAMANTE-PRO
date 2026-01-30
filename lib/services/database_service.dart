import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/cliente_model.dart';
import '../models/prestamo_model.dart';
// import 'dart:io';

class DatabaseService {
  static final DatabaseService instance = DatabaseService._init();
  static Database? _database;
  
  // Memoria para Web
  final List<Cliente> _clientesMemory = [];
  final List<Prestamo> _prestamosMemory = [];
  final List<Map<String, dynamic>> _pagosPendientesMemory = [];
  final Map<String, String> _configMemory = {};

  DatabaseService._init();

  Future<Database> get database async {
    // if (kIsWeb) {
    //   throw Exception('DB not supported on Web');
    // }
    if (_database != null) return _database!;
    _database = await _initDB('diamante_pro.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(
      path,
      version: 2,
      onCreate: _createDB,
      onUpgrade: _onUpgrade,
    );
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      // Agregar columna moneda a prestamos si venimos de v1
      await db.execute('ALTER TABLE prestamos ADD COLUMN moneda TEXT DEFAULT "COP"');
    }
  }

  Future<void> _createDB(Database db, int version) async {
    const idType = 'INTEGER PRIMARY KEY';
    const textType = 'TEXT NOT NULL';
    const textTypeNullable = 'TEXT';
    const integerType = 'INTEGER NOT NULL';
    const realType = 'REAL NOT NULL';
    const boolType = 'INTEGER NOT NULL';

    // Tabla de clientes
    await db.execute('''
      CREATE TABLE clientes (
        id $idType,
        nombre $textType,
        documento $textTypeNullable,
        telefono $textTypeNullable,
        whatsapp $textTypeNullable,
        direccion_negocio $textTypeNullable,
        gps_latitud $textTypeNullable,
        gps_longitud $textTypeNullable,
        es_vip $boolType,
        sincronizado $boolType,
        updated_at $textType
      )
    ''');

    // Tabla de préstamos
    await db.execute('''
      CREATE TABLE prestamos (
        id $idType,
        cliente_id $integerType,
        cliente_nombre $textType,
        monto_prestado $realType,
        monto_a_pagar $realType,
        saldo_actual $realType,
        valor_cuota $realType,
        frecuencia $textType,
        numero_cuotas $integerType,
        cuotas_pagadas $integerType,
        cuotas_atrasadas $integerType,
        fecha_inicio $textType,
        fecha_ultimo_pago $textTypeNullable,
        estado $textType,
        moneda $textType,
        sincronizado $boolType,
        updated_at $textType
      )
    ''');

    // Tabla de pagos pendientes de sincronización
    await db.execute('''
      CREATE TABLE pagos_pendientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prestamo_id $integerType,
        cliente_nombre $textType,
        monto $realType,
        fecha $textType,
        observaciones $textTypeNullable,
        cobrador_id $integerType,
        foto_path $textTypeNullable,
        gps_latitud $textTypeNullable,
        gps_longitud $textTypeNullable,
        sincronizado $boolType,
        created_at $textType
      )
    ''');

    // Tabla de configuración
    await db.execute('''
      CREATE TABLE configuracion (
        clave $textType UNIQUE,
        valor $textType,
        updated_at $textType
      )
    ''');
  }

  // ==================== CLIENTES ====================
  
  Future<void> insertCliente(Cliente cliente) async {
    if (kIsWeb) {
      _clientesMemory.removeWhere((c) => c.id == cliente.id);
      _clientesMemory.add(cliente);
      return;
    }
    
    final db = await instance.database;
    await db.insert(
      'clientes',
      {
        'id': cliente.id,
        'nombre': cliente.nombre,
        'documento': cliente.documento,
        'telefono': cliente.telefono,
        'whatsapp': cliente.whatsapp,
        'direccion_negocio': cliente.direccionNegocio,
        'gps_latitud': cliente.gpsLatitud,
        'gps_longitud': cliente.gpsLongitud,
        'es_vip': cliente.esVip ? 1 : 0,
        'sincronizado': 1,
        'updated_at': DateTime.now().toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<void> insertClientes(List<Cliente> clientes) async {
    if (kIsWeb) {
      for (var cliente in clientes) {
        _clientesMemory.removeWhere((c) => c.id == cliente.id);
      }
      _clientesMemory.addAll(clientes);
      return;
    }

    final db = await instance.database;
    final batch = db.batch();

    for (var cliente in clientes) {
      batch.insert(
        'clientes',
        {
          'id': cliente.id,
          'nombre': cliente.nombre,
          'documento': cliente.documento,
          'telefono': cliente.telefono,
          'whatsapp': cliente.whatsapp,
          'direccion_negocio': cliente.direccionNegocio,
          'gps_latitud': cliente.gpsLatitud,
          'gps_longitud': cliente.gpsLongitud,
          'es_vip': cliente.esVip ? 1 : 0,
          'sincronizado': 1,
          'updated_at': DateTime.now().toIso8601String(),
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }

    await batch.commit(noResult: true);
  }

  Future<List<Cliente>> getClientes() async {
    if (kIsWeb) {
      return List.from(_clientesMemory)..sort((a, b) => a.nombre.compareTo(b.nombre));
    }

    final db = await instance.database;
    final maps = await db.query('clientes', orderBy: 'nombre ASC');

    return List.generate(maps.length, (i) {
      return Cliente.fromJson({
        'id': maps[i]['id'],
        'nombre': maps[i]['nombre'],
        'documento': maps[i]['documento'],
        'telefono': maps[i]['telefono'],
        'whatsapp': maps[i]['whatsapp'],
        'direccion_negocio': maps[i]['direccion_negocio'],
        'gps_latitud': maps[i]['gps_latitud'],
        'gps_longitud': maps[i]['gps_longitud'],
        'es_vip': maps[i]['es_vip'] == 1,
      });
    });
  }

  Future<void> deleteAllClientes() async {
    if (kIsWeb) {
      _clientesMemory.clear();
      return;
    }

    final db = await instance.database;
    await db.delete('clientes');
  }

  // ==================== PRÉSTAMOS ====================

  Future<void> insertPrestamo(Prestamo prestamo) async {
    if (kIsWeb) {
      _prestamosMemory.removeWhere((p) => p.id == prestamo.id);
      _prestamosMemory.add(prestamo);
      return;
    }

    final db = await instance.database;
    await db.insert(
      'prestamos',
      {
        'id': prestamo.id,
        'cliente_id': prestamo.clienteId,
        'cliente_nombre': prestamo.clienteNombre,
        'monto_prestado': prestamo.montoPrestado,
        'monto_a_pagar': prestamo.montoAPagar,
        'saldo_actual': prestamo.saldoActual,
        'valor_cuota': prestamo.valorCuota,
        'frecuencia': prestamo.frecuencia,
        'numero_cuotas': prestamo.numeroCuotas,
        'cuotas_pagadas': prestamo.cuotasPagadas,
        'cuotas_atrasadas': prestamo.cuotasAtrasadas,
        'fecha_inicio': prestamo.fechaInicio,
        'fecha_ultimo_pago': prestamo.fechaUltimoPago,
        'estado': prestamo.estado,
        'moneda': prestamo.moneda,
        'sincronizado': 1,
        'updated_at': DateTime.now().toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<void> insertPrestamos(List<Prestamo> prestamos) async {
    if (kIsWeb) {
      for (var prestamo in prestamos) {
        _prestamosMemory.removeWhere((p) => p.id == prestamo.id);
      }
      _prestamosMemory.addAll(prestamos);
      return;
    }

    final db = await instance.database;
    final batch = db.batch();

    for (var prestamo in prestamos) {
      batch.insert(
        'prestamos',
        {
          'id': prestamo.id,
          'cliente_id': prestamo.clienteId,
          'cliente_nombre': prestamo.clienteNombre,
          'monto_prestado': prestamo.montoPrestado,
          'monto_a_pagar': prestamo.montoAPagar,
          'saldo_actual': prestamo.saldoActual,
          'valor_cuota': prestamo.valorCuota,
          'frecuencia': prestamo.frecuencia,
          'numero_cuotas': prestamo.numeroCuotas,
          'cuotas_pagadas': prestamo.cuotasPagadas,
          'cuotas_atrasadas': prestamo.cuotasAtrasadas,
          'fecha_inicio': prestamo.fechaInicio,
          'fecha_ultimo_pago': prestamo.fechaUltimoPago,
          'estado': prestamo.estado,
          'moneda': prestamo.moneda,
          'sincronizado': 1,
          'updated_at': DateTime.now().toIso8601String(),
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }

    await batch.commit(noResult: true);
  }

  Future<List<Prestamo>> getPrestamos() async {
    if (kIsWeb) {
      return _prestamosMemory
          .where((p) => p.estado == 'ACTIVO')
          .toList()
          ..sort((a, b) => b.fechaInicio.compareTo(a.fechaInicio));
    }

    final db = await instance.database;
    final maps = await db.query(
      'prestamos',
      where: 'estado = ?',
      whereArgs: ['ACTIVO'],
      orderBy: 'fecha_inicio DESC',
    );

    return List.generate(maps.length, (i) {
      return Prestamo.fromJson({
        'id': maps[i]['id'],
        'cliente': {
          'id': maps[i]['cliente_id'],
          'nombre': maps[i]['cliente_nombre'],
        },
        'monto_prestado': maps[i]['monto_prestado'],
        'monto_a_pagar': maps[i]['monto_a_pagar'],
        'saldo_actual': maps[i]['saldo_actual'],
        'valor_cuota': maps[i]['valor_cuota'],
        'frecuencia': maps[i]['frecuencia'],
        'numero_cuotas': maps[i]['numero_cuotas'],
        'cuotas_pagadas': maps[i]['cuotas_pagadas'],
        'cuotas_atrasadas': maps[i]['cuotas_atrasadas'],
        'fecha_inicio': maps[i]['fecha_inicio'],
        'fecha_ultimo_pago': maps[i]['fecha_ultimo_pago'],
        'estado': maps[i]['estado'],
        'moneda': maps[i]['moneda'] ?? 'COP',
        'dias_atraso': 0,
      });
    });
  }

  Future<void> updatePrestamoSaldo(
    int prestamoId,
    double nuevoSaldo,
    int cuotasPagadas,
    int cuotasAtrasadas,
  ) async {
    if (kIsWeb) {
      final index = _prestamosMemory.indexWhere((p) => p.id == prestamoId);
      if (index != -1) {
        // En memoria no podemos actualizar campos final fácilmente sin copyWith
        // Pero como esto se sincroniza casi inmediatamente con el servidor, 
        // podemos esperar a la recarga de datos.
      }
      return;
    }

    final db = await instance.database;
    await db.update(
      'prestamos',
      {
        'saldo_actual': nuevoSaldo,
        'cuotas_pagadas': cuotasPagadas,
        'cuotas_atrasadas': cuotasAtrasadas,
        'fecha_ultimo_pago': DateTime.now().toIso8601String(),
        'sincronizado': 0,
        'updated_at': DateTime.now().toIso8601String(),
      },
      where: 'id = ?',
      whereArgs: [prestamoId],
    );
  }

  Future<void> deleteAllPrestamos() async {
    if (kIsWeb) {
      _prestamosMemory.clear();
      return;
    }

    final db = await instance.database;
    await db.delete('prestamos');
  }

  // ==================== PAGOS PENDIENTES ====================

  Future<int> insertPagoPendiente(Map<String, dynamic> pago) async {
    if (kIsWeb) {
      pago['id'] = DateTime.now().millisecondsSinceEpoch;
      pago['sincronizado'] = 0;
      _pagosPendientesMemory.add(pago);
      return pago['id'];
    }

    final db = await instance.database;
    return await db.insert('pagos_pendientes', {
      ...pago,
      'sincronizado': 0,
      'created_at': DateTime.now().toIso8601String(),
    });
  }

  Future<List<Map<String, dynamic>>> getPagosPendientes() async {
    if (kIsWeb) {
      return _pagosPendientesMemory.where((p) => p['sincronizado'] == 0).toList();
    }

    final db = await instance.database;
    return await db.query(
      'pagos_pendientes',
      where: 'sincronizado = ?',
      whereArgs: [0],
      orderBy: 'created_at ASC',
    );
  }

  Future<void> marcarPagoComoSincronizado(int id) async {
    if (kIsWeb) {
      final index = _pagosPendientesMemory.indexWhere((p) => p['id'] == id);
      if (index != -1) {
        _pagosPendientesMemory[index]['sincronizado'] = 1;
      }
      return;
    }

    final db = await instance.database;
    await db.update(
      'pagos_pendientes',
      {'sincronizado': 1},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<void> deletePagosPendientes() async {
    if (kIsWeb) {
      _pagosPendientesMemory.removeWhere((p) => p['sincronizado'] == 1);
      return;
    }

    final db = await instance.database;
    await db.delete(
      'pagos_pendientes',
      where: 'sincronizado = ?',
      whereArgs: [1],
    );
  }

  // ==================== CONFIGURACIÓN ====================

  Future<void> setConfig(String clave, String valor) async {
    if (kIsWeb) {
      _configMemory[clave] = valor;
      return;
    }

    final db = await instance.database;
    await db.insert(
      'configuracion',
      {
        'clave': clave,
        'valor': valor,
        'updated_at': DateTime.now().toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<String?> getConfig(String clave) async {
    if (kIsWeb) {
      return _configMemory[clave];
    }

    final db = await instance.database;
    final maps = await db.query(
      'configuracion',
      where: 'clave = ?',
      whereArgs: [clave],
    );

    if (maps.isNotEmpty) {
      return maps.first['valor'] as String;
    }
    return null;
  }

  // ==================== UTILIDADES ====================

  Future<void> close() async {
    if (kIsWeb) return;
    final db = await instance.database;
    db.close();
  }

  Future<void> clearAll() async {
    if (kIsWeb) {
      _clientesMemory.clear();
      _prestamosMemory.clear();
      _pagosPendientesMemory.clear();
      return;
    }

    final db = await instance.database;
    await db.delete('clientes');
    await db.delete('prestamos');
    await db.delete('pagos_pendientes');
  }
}
