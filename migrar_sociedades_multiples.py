"""
Script para agregar soporte de múltiples socios a la tabla sociedades
"""
import sqlite3
import os

db_path = os.path.join('instance', 'diamante.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔧 Agregando columnas para socios adicionales...")
        
        # Agregar columnas para socio 2
        cursor.execute('ALTER TABLE sociedades ADD COLUMN nombre_socio_2 VARCHAR(100)')
        cursor.execute('ALTER TABLE sociedades ADD COLUMN telefono_socio_2 VARCHAR(20)')
        cursor.execute('ALTER TABLE sociedades ADD COLUMN porcentaje_socio_2 FLOAT DEFAULT 0.0')
        
        # Agregar columnas para socio 3
        cursor.execute('ALTER TABLE sociedades ADD COLUMN nombre_socio_3 VARCHAR(100)')
        cursor.execute('ALTER TABLE sociedades ADD COLUMN telefono_socio_3 VARCHAR(20)')
        cursor.execute('ALTER TABLE sociedades ADD COLUMN porcentaje_socio_3 FLOAT DEFAULT 0.0')
        
        conn.commit()
        print("✅ ¡Migración completada exitosamente!")
        print("   Ahora puedes crear sociedades con hasta 3 socios.")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️  Las columnas ya existen. Migración no necesaria.")
        else:
            print(f"❌ Error: {e}")
    finally:
        conn.close()
else:
    print(f"❌ No se encontró la base de datos en: {db_path}")
