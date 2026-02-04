"""
Script de Migración Completa - Diamante PRO
Ejecuta todas las migraciones pendientes:
1. Crea índices de rendimiento
2. Crea tabla de Socios
3. Migra datos legacy a nueva estructura
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Sociedad, Socio

def run_migrations():
    """Ejecuta todas las migraciones"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("DIAMANTE PRO - SISTEMA DE MIGRACIONES")
        print("=" * 60)
        
        # 1. Crear todas las tablas (incluyendo la nueva tabla 'socios')
        print("\n[1/3] Creando tablas nuevas...")
        try:
            db.create_all()
            print("✅ Tablas creadas/verificadas correctamente")
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
            return False
        
        # 2. Crear índices de rendimiento
        print("\n[2/3] Creando índices de rendimiento...")
        indices = [
            ("idx_prestamos_estado", "prestamos", "estado"),
            ("idx_prestamos_ruta", "prestamos", "ruta_id"),
            ("idx_prestamos_cliente", "prestamos", "cliente_id"),
            ("idx_prestamos_cobrador", "prestamos", "cobrador_id"),
            ("idx_prestamos_fecha", "prestamos", "fecha_inicio"),
            ("idx_pagos_prestamo", "pagos", "prestamo_id"),
            ("idx_pagos_fecha", "pagos", "fecha_pago"),
            ("idx_pagos_cobrador", "pagos", "cobrador_id"),
            ("idx_clientes_cedula", "clientes", "cedula"),
            ("idx_clientes_ruta", "clientes", "ruta_id"),
            ("idx_socios_sociedad", "socios", "sociedad_id"),
            ("idx_socios_activo", "socios", "activo"),
        ]
        
        for idx_name, table, column in indices:
            try:
                db.session.execute(db.text(
                    f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({column})"
                ))
                print(f"  ✅ Índice {idx_name}")
            except Exception as e:
                print(f"  ⚠️ Índice {idx_name}: {e}")
        
        db.session.commit()
        print("✅ Índices creados/verificados")
        
        # 3. Migrar datos legacy de socios
        print("\n[3/3] Migrando datos de socios legacy...")
        try:
            sociedades = Sociedad.query.all()
            migrados = 0
            
            if not sociedades:
                print("  ℹ️ No hay sociedades para migrar")
            
            for sociedad in sociedades:
                try:
                    # Verificar si ya tiene socios migrados
                    socios_existentes = Socio.query.filter_by(sociedad_id=sociedad.id).count()
                    if socios_existentes > 0:
                        print(f"  ⏭️ Sociedad '{sociedad.nombre}' ya tiene socios migrados")
                        continue
                    
                    # Migrar socio 1 (legacy)
                    nombre_s1 = getattr(sociedad, 'nombre_socio', None)
                    if nombre_s1:
                        socio1 = Socio(
                            sociedad_id=sociedad.id,
                            nombre=nombre_s1,
                            telefono=getattr(sociedad, 'telefono_socio', None),
                            porcentaje=float(getattr(sociedad, 'porcentaje_socio', 0) or 0),
                            tipo_socio='INVERSIONISTA',
                            activo=True
                        )
                        db.session.add(socio1)
                        migrados += 1
                        print(f"    ✅ Socio 1: {nombre_s1}")
                    
                    # Migrar socio 2 (legacy)
                    nombre_s2 = getattr(sociedad, 'nombre_socio_2', None)
                    if nombre_s2:
                        socio2 = Socio(
                            sociedad_id=sociedad.id,
                            nombre=nombre_s2,
                            telefono=getattr(sociedad, 'telefono_socio_2', None),
                            porcentaje=float(getattr(sociedad, 'porcentaje_socio_2', 0) or 0),
                            tipo_socio='INVERSIONISTA',
                            activo=True
                        )
                        db.session.add(socio2)
                        migrados += 1
                        print(f"    ✅ Socio 2: {nombre_s2}")
                    
                    # Migrar socio 3 (legacy)
                    nombre_s3 = getattr(sociedad, 'nombre_socio_3', None)
                    if nombre_s3:
                        socio3 = Socio(
                            sociedad_id=sociedad.id,
                            nombre=nombre_s3,
                            telefono=getattr(sociedad, 'telefono_socio_3', None),
                            porcentaje=float(getattr(sociedad, 'porcentaje_socio_3', 0) or 0),
                            tipo_socio='INVERSIONISTA',
                            activo=True
                        )
                        db.session.add(socio3)
                        migrados += 1
                        print(f"    ✅ Socio 3: {nombre_s3}")
                        
                except Exception as e_socio:
                    print(f"  ⚠️ Error en sociedad {sociedad.id}: {e_socio}")
                    continue
            
            db.session.commit()
            print(f"✅ {migrados} socios migrados desde estructura legacy")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error migrando socios: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        
        # Resumen
        total_sociedades = Sociedad.query.count()
        total_socios = Socio.query.count()
        print(f"\n📊 Resumen:")
        print(f"   - Sociedades: {total_sociedades}")
        print(f"   - Socios: {total_socios}")
        
        return True


if __name__ == '__main__':
    success = run_migrations()
    sys.exit(0 if success else 1)
