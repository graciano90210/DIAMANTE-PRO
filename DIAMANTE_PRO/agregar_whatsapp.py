"""
Script para agregar campos de WhatsApp a la tabla de clientes
"""
import sqlite3
import os

# Ruta a la base de datos
db_path = os.path.join('instance', 'diamante.db')

if not os.path.exists(db_path):
    print(f"❌ No se encontró la base de datos en: {db_path}")
    exit(1)

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🔧 Actualizando base de datos...")

# Agregar columnas si no existen
try:
    cursor.execute("""
        ALTER TABLE clientes 
        ADD COLUMN whatsapp_codigo_pais VARCHAR(5) DEFAULT '57'
    """)
    print("✅ Columna 'whatsapp_codigo_pais' agregada")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("⚠️  Columna 'whatsapp_codigo_pais' ya existe")
    else:
        print(f"❌ Error: {e}")

try:
    cursor.execute("""
        ALTER TABLE clientes 
        ADD COLUMN whatsapp_numero VARCHAR(20)
    """)
    print("✅ Columna 'whatsapp_numero' agregada")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("⚠️  Columna 'whatsapp_numero' ya existe")
    else:
        print(f"❌ Error: {e}")

# Migrar datos existentes: copiar teléfono a whatsapp_numero donde esté vacío
try:
    cursor.execute("""
        UPDATE clientes 
        SET whatsapp_numero = telefono, 
            whatsapp_codigo_pais = '57'
        WHERE whatsapp_numero IS NULL OR whatsapp_numero = ''
    """)
    conn.commit()
    print(f"✅ Datos migrados: teléfonos copiados a WhatsApp (código país: +57)")
except Exception as e:
    print(f"❌ Error al migrar datos: {e}")
    conn.rollback()

# Mostrar algunos registros actualizados
cursor.execute("SELECT nombre, telefono, whatsapp_codigo_pais, whatsapp_numero FROM clientes LIMIT 5")
clientes = cursor.fetchall()
if clientes:
    print("\n📋 Primeros clientes actualizados:")
    for cliente in clientes:
        nombre, telefono, codigo, whatsapp = cliente
        print(f"   • {nombre}: Tel={telefono}, WhatsApp=+{codigo}{whatsapp}")

conn.close()
print("\n✅ Actualización completada")
print("📱 Ahora los clientes pueden tener números de WhatsApp internacionales")
