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

# Columnas a agregar
columnas_agregar = [
    ("clientes", "tipo_documento", "VARCHAR(50)"),
]

with engine.connect() as conn:
    for tabla, columna, tipo in columnas_agregar:
        try:
            sql = f"ALTER TABLE {tabla} ADD COLUMN IF NOT EXISTS {columna} {tipo};"
            conn.execute(text(sql))
            conn.commit()
            print(f"✅ Columna {columna} agregada a {tabla}")
        except Exception as e:
            print(f"❌ Error agregando {columna}: {e}")

print("\n✅ Actualización completada")
