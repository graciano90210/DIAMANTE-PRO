"""
Script para agregar índices de rendimiento a la base de datos.
Mejora significativamente las consultas más frecuentes.

Ejecutar con: python -m migrations.add_performance_indexes
"""
import os
import sys

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def add_indexes():
    """Agregar índices para mejorar rendimiento de queries frecuentes"""
    
    app = create_app()
    
    with app.app_context():
        # Lista de índices a crear
        indexes = [
            # Préstamos - búsquedas más frecuentes
            ("idx_prestamos_estado", "prestamos", "estado"),
            ("idx_prestamos_ruta_id", "prestamos", "ruta_id"),
            ("idx_prestamos_cobrador_id", "prestamos", "cobrador_id"),
            ("idx_prestamos_cliente_id", "prestamos", "cliente_id"),
            ("idx_prestamos_fecha_inicio", "prestamos", "fecha_inicio"),
            ("idx_prestamos_estado_ruta", "prestamos", "estado, ruta_id"),
            
            # Pagos - para reportes y dashboard
            ("idx_pagos_fecha_pago", "pagos", "fecha_pago"),
            ("idx_pagos_prestamo_id", "pagos", "prestamo_id"),
            ("idx_pagos_cobrador_id", "pagos", "cobrador_id"),
            
            # Clientes - búsquedas frecuentes
            ("idx_clientes_documento", "clientes", "documento"),
            ("idx_clientes_nivel_riesgo", "clientes", "nivel_riesgo"),
            ("idx_clientes_es_vip", "clientes", "es_vip"),
            
            # Transacciones - para reportes financieros
            ("idx_transacciones_fecha", "transacciones", "fecha"),
            ("idx_transacciones_naturaleza", "transacciones", "naturaleza"),
            
            # Rutas
            ("idx_rutas_cobrador_id", "rutas", "cobrador_id"),
            ("idx_rutas_activo", "rutas", "activo"),
            
            # Usuarios
            ("idx_usuarios_usuario", "usuarios", "usuario"),
            ("idx_usuarios_rol", "usuarios", "rol"),
            ("idx_usuarios_activo", "usuarios", "activo"),
        ]
        
        created = 0
        skipped = 0
        errors = 0
        
        for idx_name, table, columns in indexes:
            try:
                # Verificar si el índice ya existe (PostgreSQL)
                check_sql = text(f"""
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = :idx_name
                """)
                result = db.session.execute(check_sql, {"idx_name": idx_name}).fetchone()
                
                if result:
                    print(f"⏭️  Índice {idx_name} ya existe, omitiendo...")
                    skipped += 1
                    continue
                    
            except Exception:
                # SQLite no tiene pg_indexes, intentar crear directamente
                pass
            
            try:
                # Crear el índice
                create_sql = text(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({columns})")
                db.session.execute(create_sql)
                db.session.commit()
                print(f"✅ Creado índice: {idx_name} en {table}({columns})")
                created += 1
                
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"⏭️  Índice {idx_name} ya existe")
                    skipped += 1
                else:
                    print(f"❌ Error creando {idx_name}: {e}")
                    errors += 1
                db.session.rollback()
        
        print(f"\n📊 Resumen: {created} creados, {skipped} omitidos, {errors} errores")
        return created, skipped, errors


if __name__ == '__main__':
    print("🚀 Agregando índices de rendimiento...")
    print("=" * 50)
    add_indexes()
    print("=" * 50)
    print("✅ Proceso completado")
