"""
Script para verificar y mostrar la estructura de la tabla prestamos
"""
import sqlite3

db_path = 'instance/diamante.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("📊 Estructura de la tabla prestamos:")
print("=" * 60)

cursor.execute("PRAGMA table_info(prestamos)")
columns = cursor.fetchall()

for col in columns:
    print(f"  {col[1]:25} {col[2]:15} {'NOT NULL' if col[3] else ''} {'PK' if col[5] else ''}")

print("=" * 60)

# Ver cuántos préstamos hay
cursor.execute("SELECT COUNT(*) FROM prestamos")
count = cursor.fetchone()[0]
print(f"\n📈 Total de préstamos en la base de datos: {count}")

conn.close()
