import sqlite3
import os

db_path = os.path.join('DIAMANTE_PRO', 'instance', 'diamante.db')

# Columnas requeridas por el modelo actual
columns = [
    ("gps_latitud_casa", "FLOAT"),
    ("gps_longitud_casa", "FLOAT"),
    ("tipo_negocio", "VARCHAR(50)")
]

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        for col, coltype in columns:
            if not column_exists(cursor, "clientes", col):
                print(f"Agregando columna: {col} ...")
                cursor.execute(f"ALTER TABLE clientes ADD COLUMN {col} {coltype}")
        conn.commit()
        print("✅ Migración completada. Todas las columnas requeridas existen.")
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
    finally:
        conn.close()
else:
    print(f"❌ No se encontró la base de datos en: {db_path}")
