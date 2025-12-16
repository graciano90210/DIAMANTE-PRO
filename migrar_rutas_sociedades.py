"""
Script para crear las tablas de Sociedades y Rutas
Migra los datos existentes de cobrador_id a ruta_id
"""
from app import create_app, db
from app.models import Usuario, Sociedad, Ruta, Prestamo
from sqlalchemy import inspect, text

def migrar_a_rutas():
    app = create_app()
    
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            tablas_existentes = inspector.get_table_names()
            
            print("🔧 INICIANDO MIGRACIÓN A SISTEMA DE RUTAS Y SOCIEDADES\n")
            
            # 1. Crear tabla de sociedades
            if 'sociedades' not in tablas_existentes:
                print("📋 Creando tabla 'sociedades'...")
                with db.engine.connect() as conn:
                    conn.execute(text("""
                        CREATE TABLE sociedades (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre VARCHAR(100) NOT NULL,
                            nombre_socio VARCHAR(100) NOT NULL,
                            telefono_socio VARCHAR(20),
                            porcentaje_socio FLOAT DEFAULT 50.0,
                            activo BOOLEAN DEFAULT 1,
                            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                            notas VARCHAR(500)
                        )
                    """))
                    conn.commit()
                print("✅ Tabla 'sociedades' creada\n")
            else:
                print("⚠️  Tabla 'sociedades' ya existe\n")
            
            # 2. Crear tabla de rutas
            if 'rutas' not in tablas_existentes:
                print("📋 Creando tabla 'rutas'...")
                with db.engine.connect() as conn:
                    conn.execute(text("""
                        CREATE TABLE rutas (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre VARCHAR(100) NOT NULL,
                            cobrador_id INTEGER,
                            sociedad_id INTEGER,
                            activo BOOLEAN DEFAULT 1,
                            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                            descripcion VARCHAR(200),
                            FOREIGN KEY (cobrador_id) REFERENCES usuarios(id),
                            FOREIGN KEY (sociedad_id) REFERENCES sociedades(id)
                        )
                    """))
                    conn.commit()
                print("✅ Tabla 'rutas' creada\n")
            else:
                print("⚠️  Tabla 'rutas' ya existe\n")
            
            # 3. Agregar columna ruta_id a prestamos
            columnas_prestamos = [col['name'] for col in inspector.get_columns('prestamos')]
            if 'ruta_id' not in columnas_prestamos:
                print("📋 Agregando columna 'ruta_id' a tabla prestamos...")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE prestamos ADD COLUMN ruta_id INTEGER"))
                    conn.commit()
                print("✅ Columna 'ruta_id' agregada\n")
            else:
                print("⚠️  Columna 'ruta_id' ya existe en prestamos\n")
            
            # 4. Crear rutas basadas en los cobradores existentes
            print("📋 Creando rutas para cobradores existentes...\n")
            cobradores = Usuario.query.filter_by(rol='cobrador', activo=True).all()
            
            for cobrador in cobradores:
                # Verificar si ya existe una ruta para este cobrador
                ruta_existente = Ruta.query.filter_by(cobrador_id=cobrador.id).first()
                
                if not ruta_existente:
                    # Crear ruta con el nombre del cobrador
                    nueva_ruta = Ruta(
                        nombre=f"Ruta {cobrador.nombre}",
                        cobrador_id=cobrador.id,
                        sociedad_id=None,  # PROPIO por defecto
                        activo=True,
                        descripcion=f"Ruta operada por {cobrador.nombre}"
                    )
                    db.session.add(nueva_ruta)
                    db.session.flush()  # Para obtener el ID
                    
                    print(f"   ✅ Ruta creada: '{nueva_ruta.nombre}' (ID: {nueva_ruta.id}) → Cobrador: {cobrador.nombre}")
                else:
                    print(f"   ⚠️  Ruta ya existe para {cobrador.nombre}")
            
            db.session.commit()
            
            # 5. Migrar préstamos de cobrador_id a ruta_id
            print("\n📋 Migrando préstamos a las rutas...\n")
            prestamos = Prestamo.query.filter(Prestamo.ruta_id.is_(None)).all()
            
            for prestamo in prestamos:
                if prestamo.cobrador_id:
                    # Buscar la ruta del cobrador
                    ruta = Ruta.query.filter_by(cobrador_id=prestamo.cobrador_id).first()
                    if ruta:
                        prestamo.ruta_id = ruta.id
                        print(f"   ✅ Préstamo #{prestamo.id} → Ruta '{ruta.nombre}'")
            
            db.session.commit()
            
            # 6. Resumen final
            print("\n" + "="*70)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("="*70)
            
            total_sociedades = Sociedad.query.count()
            total_rutas = Ruta.query.count()
            total_prestamos = Prestamo.query.filter(Prestamo.ruta_id.isnot(None)).count()
            
            print(f"\n📊 RESUMEN:")
            print(f"   • Sociedades creadas: {total_sociedades}")
            print(f"   • Rutas creadas: {total_rutas}")
            print(f"   • Préstamos migrados: {total_prestamos}")
            
            print("\n🎯 PRÓXIMOS PASOS:")
            print("   1. Crear sociedades desde la interfaz si tienes socios")
            print("   2. Asignar rutas a sociedades según corresponda")
            print("   3. Los préstamos nuevos se crearán asociados a rutas")
            print("   4. Puedes cambiar el cobrador de una ruta sin afectar los préstamos")
            
        except Exception as e:
            print(f"\n❌ Error durante la migración: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    migrar_a_rutas()
