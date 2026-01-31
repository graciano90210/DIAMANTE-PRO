"""
Script para agregar columnas faltantes en la base de datos de Heroku
"""
import os
import sys

# Configurar para usar la base de datos de Heroku
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

if not database_url:
    print("ERROR: No se encontró DATABASE_URL")
    sys.exit(1)

from sqlalchemy import create_engine, text

engine = create_engine(database_url)

# Todas las columnas a agregar en la tabla clientes
columnas_clientes = [
    ("tipo_documento", "VARCHAR(20) DEFAULT 'CPF'"),
    ("fecha_nacimiento", "DATE"),
    ("documento_negocio", "VARCHAR(30)"),
    ("email", "VARCHAR(100)"),
    ("whatsapp_codigo_pais", "VARCHAR(5) DEFAULT '57'"),
    ("whatsapp_numero", "VARCHAR(20)"),
    ("direccion_negocio", "VARCHAR(200)"),
    ("cep_negocio", "VARCHAR(20)"),
    ("direccion_casa", "VARCHAR(200)"),
    ("cep_casa", "VARCHAR(20)"),
    ("gps_latitud", "FLOAT"),
    ("gps_longitud", "FLOAT"),
    ("es_vip", "BOOLEAN DEFAULT FALSE"),
    ("fecha_registro", "TIMESTAMP DEFAULT NOW()"),
]

# Columnas para rutas
columnas_rutas = [
    ("pais", "VARCHAR(50) DEFAULT 'Colombia'"),
    ("moneda", "VARCHAR(3) DEFAULT 'COP'"),
    ("simbolo_moneda", "VARCHAR(5) DEFAULT '$'"),
    ("descripcion", "VARCHAR(200)"),
]

# Columnas para sociedades  
columnas_sociedades = [
    ("nombre_socio_2", "VARCHAR(100)"),
    ("telefono_socio_2", "VARCHAR(20)"),
    ("porcentaje_socio_2", "FLOAT DEFAULT 0.0"),
    ("nombre_socio_3", "VARCHAR(100)"),
    ("telefono_socio_3", "VARCHAR(20)"),
    ("porcentaje_socio_3", "FLOAT DEFAULT 0.0"),
    ("notas", "VARCHAR(500)"),
]

with engine.connect() as conn:
    print("📋 Agregando columnas a CLIENTES...")
    for columna, tipo in columnas_clientes:
        try:
            sql = f"ALTER TABLE clientes ADD COLUMN IF NOT EXISTS {columna} {tipo};"
            conn.execute(text(sql))
            conn.commit()
            print(f"  ✅ {columna}")
        except Exception as e:
            print(f"  ⚠️ {columna}: {e}")
    
    print("\n📋 Agregando columnas a RUTAS...")
    for columna, tipo in columnas_rutas:
        try:
            sql = f"ALTER TABLE rutas ADD COLUMN IF NOT EXISTS {columna} {tipo};"
            conn.execute(text(sql))
            conn.commit()
            print(f"  ✅ {columna}")
        except Exception as e:
            print(f"  ⚠️ {columna}: {e}")
    
    print("\n📋 Agregando columnas a SOCIEDADES...")
    for columna, tipo in columnas_sociedades:
        try:
            sql = f"ALTER TABLE sociedades ADD COLUMN IF NOT EXISTS {columna} {tipo};"
            conn.execute(text(sql))
            conn.commit()
            print(f"  ✅ {columna}")
        except Exception as e:
            print(f"  ⚠️ {columna}: {e}")

print("\n✅ Actualización de base de datos completada")
