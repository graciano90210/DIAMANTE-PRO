import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import '../models/cliente_model.dart';
import '../models/prestamo_model.dart';
import 'dart:io';

class DatabaseService {
  static final DatabaseService instance = DatabaseService._init();
  static Database? _database;

  DatabaseService._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('diamante_pro.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(
      path,
      version: 1,
      onCreate: _createDB,
    );
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
    final db = await instance.database;
    await db.delete('clientes');
  }

  // ==================== PRÉSTAMOS ====================

  Future<void> insertPrestamo(Prestamo prestamo) async {
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
        'sincronizado': 1,
        'updated_at': DateTime.now().toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<void> insertPrestamos(List<Prestamo> prestamos) async {
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
          'sincronizado': 1,
          'updated_at': DateTime.now().toIso8601String(),
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }

    await batch.commit(noResult: true);
  }

  Future<List<Prestamo>> getPrestamos() async {
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
    final db = await instance.database;
    await db.delete('prestamos');
  }

  // ==================== PAGOS PENDIENTES ====================

  Future<int> insertPagoPendiente(Map<String, dynamic> pago) async {
    final db = await instance.database;
    return await db.insert('pagos_pendientes', {
      ...pago,
      'sincronizado': 0,
      'created_at': DateTime.now().toIso8601String(),
    });
  }

  Future<List<Map<String, dynamic>>> getPagosPendientes() async {
    final db = await instance.database;
    return await db.query(
      'pagos_pendientes',
      where: 'sincronizado = ?',
      whereArgs: [0],
      orderBy: 'created_at ASC',
    );
  }

  Future<void> marcarPagoComoSincronizado(int id) async {
    final db = await instance.database;
    await db.update(
      'pagos_pendientes',
      {'sincronizado': 1},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<void> deletePagosPendientes() async {
    final db = await instance.database;
    await db.delete(
      'pagos_pendientes',
      where: 'sincronizado = ?',
      whereArgs: [1],
    );
  }

  // ==================== CONFIGURACIÓN ====================

  Future<void> setConfig(String clave, String valor) async {
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
    final db = await instance.database;
    db.close();
  }

  Future<void> clearAll() async {
    final db = await instance.database;
    await db.delete('clientes');
    await db.delete('prestamos');
    await db.delete('pagos_pendientes');
  }
}
