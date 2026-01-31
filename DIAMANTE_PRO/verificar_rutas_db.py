import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('instance/diamante.db')
cursor = conn.cursor()

# Ver todas las rutas
cursor.execute("SELECT id, nombre, activo, cobrador_id, sociedad_id FROM rutas")
rutas = cursor.fetchall()

print(f"\n📋 Total de rutas en la BD: {len(rutas)}\n")

for ruta in rutas:
    id_ruta, nombre, activo, cobrador_id, sociedad_id = ruta
    estado = "✅ ACTIVA" if activo else "❌ INACTIVA"
    tipo = f"Sociedad ID: {sociedad_id}" if sociedad_id else "PROPIO"
    print(f"{id_ruta}. {nombre} - {estado}")
    print(f"   Cobrador ID: {cobrador_id} - {tipo}\n")

conn.close()
