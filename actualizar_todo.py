import os
from sqlalchemy import text
from app import create_app, db

app = create_app()

def columna_existe(table, column):
    """Verifica si una columna ya existe en la base de datos"""
    try:
        # Consulta compatible con SQLite y PostgreSQL para verificar columnas
        with db.engine.connect() as conn:
            # Intentamos seleccionar la columna. Si falla, no existe.
            conn.execute(text(f"SELECT {column} FROM {table} LIMIT 1"))
        return True
    except Exception:
        return False

with app.app_context():
    print("💎 INICIANDO ACTUALIZACIÓN DE DIAMANTE PRO 💎")
    
    # 1. Crear tablas nuevas (Activos, Aportes, etc.)
    print("---------------------------------------------")
    print("1️⃣  Verificando tablas nuevas...")
    db.create_all()
    print("✅  Tablas aseguradas (AportesCapital, Activos, etc.)")

    # 2. Actualizar Tabla PRÉSTAMOS (Agregar ruta_id)
    print("---------------------------------------------")
    print("2️⃣  Actualizando tabla 'prestamos'...")
    if not columna_existe('prestamos', 'ruta_id'):
        try:
            with db.engine.connect() as conn:
                # Agregamos la columna permitiendo NULL inicialmente para no romper datos viejos
                conn.execute(text("ALTER TABLE prestamos ADD COLUMN ruta_id INTEGER"))
                conn.commit()
            print("✅  Columna 'ruta_id' agregada exitosamente.")
        except Exception as e:
            print(f"❌  Error agregando ruta_id: {e}")
    else:
        print("ℹ️  La columna 'ruta_id' ya existía.")

    # 3. Actualizar Tabla SOCIEDADES (Agregar socios 2 y 3)
    print("---------------------------------------------")
    print("3️⃣  Actualizando tabla 'sociedades'...")
    nuevas_columnas_sociedad = [
        ("nombre_socio_2", "VARCHAR(100)"),
        ("telefono_socio_2", "VARCHAR(20)"),
        ("porcentaje_socio_2", "FLOAT DEFAULT 0"),
        ("nombre_socio_3", "VARCHAR(100)"),
        ("telefono_socio_3", "VARCHAR(20)"),
        ("porcentaje_socio_3", "FLOAT DEFAULT 0")
    ]

    for col_nombre, col_tipo in nuevas_columnas_sociedad:
        if not columna_existe('sociedades', col_nombre):
            try:
                with db.engine.connect() as conn:
                    conn.execute(text(f"ALTER TABLE sociedades ADD COLUMN {col_nombre} {col_tipo}"))
                    conn.commit()
                print(f"✅  Columna '{col_nombre}' agregada.")
            except Exception as e:
                print(f"⚠️  No se pudo agregar {col_nombre}: {e}")
        else:
             print(f"ℹ️  Columna '{col_nombre}' ya existe.")

    print("---------------------------------------------")
    print("✨ ¡ACTUALIZACIÓN COMPLETADA, MI AMOR! ✨")
    print("Ahora tu base de datos está lista para las nuevas funciones.")