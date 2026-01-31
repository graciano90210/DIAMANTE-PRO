import os
import sys
from sqlalchemy import create_engine, text, inspect

# Configurar para usar la base de datos de Heroku
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: No se encontró DATABASE_URL")
    sys.exit(1)

if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

print(f"Conectando a base de datos...")
engine = create_engine(database_url)

def add_column_if_not_exists(table_name, column_name, column_type):
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    
    if column_name not in columns:
        print(f"Agregando columna faltante: {column_name} a tabla {table_name}")
        with engine.connect() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
            conn.commit()
        print(f"Columna {column_name} agregada exitosamente.")
    else:
        print(f"La columna {column_name} ya existe en {table_name}.")

try:
    # Agregar columnas de GPS casa faltantes
    add_column_if_not_exists('clientes', 'gps_latitud_casa', 'FLOAT')
    add_column_if_not_exists('clientes', 'gps_longitud_casa', 'FLOAT')
    
    # Verificar columnas existentes para asegurarse
    add_column_if_not_exists('clientes', 'gps_latitud', 'FLOAT')
    add_column_if_not_exists('clientes', 'gps_longitud', 'FLOAT')

    print("Verificación de columnas GPS completada.")

except Exception as e:
    print(f"Error ejecutanado fix: {e}")
    sys.exit(1)
