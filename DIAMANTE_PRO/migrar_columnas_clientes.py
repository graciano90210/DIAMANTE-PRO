import sqlite3
import os

# Ruta a la base de datos restaurada
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'diamante.db')

# Columnas que deben existir en la tabla clientes (ajusta según tu modelo actual)
COLUMNS_TO_ADD = [
    ("gps_latitud_casa", "TEXT"),
    ("gps_longitud_casa", "TEXT"),
    ("gps_latitud", "TEXT"),
    ("gps_longitud", "TEXT"),
    ("es_vip", "INTEGER DEFAULT 0"),
    ("score_crediticio", "FLOAT"),
    ("nivel_riesgo", "TEXT"),
    ("motivo_bloqueo", "TEXT"),
    ("credito_bloqueado", "INTEGER DEFAULT 0"),
    ("fecha_ultimo_calculo_score", "TEXT")
]

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

def migrate_clientes_table():
    if not os.path.exists(DB_PATH):
        print(f"❌ No se encontró la base de datos en: {DB_PATH}")
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for column, coltype in COLUMNS_TO_ADD:
        if not column_exists(cursor, "clientes", column):
            try:
                cursor.execute(f"ALTER TABLE clientes ADD COLUMN {column} {coltype}")
                print(f"✅ Columna agregada: {column} ({coltype})")
            except Exception as e:
                print(f"❌ Error al agregar columna {column}: {e}")
        else:
            print(f"✔️ Columna ya existe: {column}")
    conn.commit()
    conn.close()
    print("🚀 Migración completada. Ahora puedes reiniciar el servidor Flask.")

if __name__ == "__main__":
    migrate_clientes_table()
