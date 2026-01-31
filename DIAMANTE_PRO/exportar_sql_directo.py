"""
Script para copiar datos usando SQL directo (no modelos)
Evita problemas de schema mismatch
"""
import sqlite3
import json

# Conectar a SQLite local
conn = sqlite3.connect('instance/diamante.db')
conn.row_factory = sqlite3.Row  # Para obtener diccionarios

# Función helper
def query_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

cursor = conn.cursor()

print("📊 Leyendo datos de SQLite...")

datos = {
    'usuarios': query_table(cursor, 'usuarios'),
    'sociedades': query_table(cursor, 'sociedades'),
    'rutas': query_table(cursor, 'rutas'),
    'clientes': query_table(cursor, 'clientes'),
    'prestamos': query_table(cursor, 'prestamos'),
    'pagos': query_table(cursor, 'pagos')
}

conn.close()

# Guardar a JSON
with open('datos_completos.json', 'w', encoding='utf-8') as f:
    json.dump(datos, f, indent=2, ensure_ascii=False)

print("✅ Datos exportados:")
for tabla, registros in datos.items():
    print(f"  - {tabla}: {len(registros)} registros")
print("\n📁 Archivo creado: datos_completos.json")
print("\nAhora puedes:")
print("1. Revisar el archivo datos_completos.json")
print("2. Crear un script de importación compatible")
