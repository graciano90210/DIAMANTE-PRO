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
    print("Iniciando verificación completa de columnas...")

    # Lista completa de columnas nuevas para Scoring
    columnas_nuevas = [
        ('gastos_mensuales_promedio', 'FLOAT'),
        ('personas_a_cargo', 'INTEGER DEFAULT 0'),
        ('estado_civil', 'VARCHAR(20)'),
        ('tiempo_residencia_meses', 'INTEGER'),
        ('tipo_negocio', 'VARCHAR(50)'),
        ('nombre_negocio', 'VARCHAR(100)'),
        ('antiguedad_negocio_meses', 'INTEGER'),
        ('local_propio', 'BOOLEAN DEFAULT FALSE'),
        ('dias_trabajo', 'VARCHAR(20)'),
        ('hora_cobro_preferida', 'VARCHAR(10)'),
        ('ingresos_diarios_estimados', 'FLOAT'),
        ('referido_por_cliente_id', 'INTEGER'),
        ('negocio_formalizado', 'BOOLEAN DEFAULT FALSE'),
        ('tipo_documento_fiscal', 'VARCHAR(20) DEFAULT \'CNPJ\''),
        ('documento_fiscal_negocio', 'VARCHAR(30)'),
        ('fecha_verificacion_fiscal', 'TIMESTAMP'),
        ('tiene_comprobante_residencia', 'BOOLEAN DEFAULT FALSE'),
        ('tipo_comprobante_residencia', 'VARCHAR(30)'),
        ('comprobante_a_nombre_propio', 'BOOLEAN DEFAULT FALSE'),
        ('nombre_titular_comprobante', 'VARCHAR(100)'),
        ('parentesco_titular', 'VARCHAR(30)'),
        ('fecha_comprobante', 'DATE'),
        ('foto_comprobante_residencia', 'VARCHAR(300)'),
        ('score_crediticio', 'INTEGER DEFAULT 500'),
        ('nivel_riesgo', 'VARCHAR(20) DEFAULT \'NUEVO\''),
        ('limite_credito_sugerido', 'FLOAT'),
        ('credito_bloqueado', 'BOOLEAN DEFAULT FALSE'),
        ('motivo_bloqueo', 'VARCHAR(200)'),
        ('fecha_ultimo_calculo_score', 'TIMESTAMP'),
        ('gps_latitud_casa', 'FLOAT'),
        ('gps_longitud_casa', 'FLOAT')
    ]

    for col_name, col_type in columnas_nuevas:
        add_column_if_not_exists('clientes', col_name, col_type)

    # Agregar ForeignKey manualmente si es necesario (referido_por)
    # Nota: Agregar FK en PostgreSQL requiere un paso extra, pero por ahora solo agregamos la columna INTEGER
    # Si quisieramos la restricción:
    # ALTER TABLE clientes ADD CONSTRAINT fk_referido FOREIGN KEY (referido_por_cliente_id) REFERENCES clientes(id)

    print("Verificación de TODAS las columnas completada.")

except Exception as e:
    print(f"Error ejecutanado fix completo: {e}")
    sys.exit(1)
