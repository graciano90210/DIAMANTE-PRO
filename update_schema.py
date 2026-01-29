import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'DIAMANTE_PRO', 'instance', 'diamante.db')
print(f"Opening DB at {db_path}")

try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    columns = [
        ('tipo_documento', 'TEXT DEFAULT "CPF"'),
        ('fecha_nacimiento', 'DATE'),
        ('email', 'TEXT'),
        ('cep_negocio', 'TEXT'),
        ('direccion_casa', 'TEXT'),
        ('cep_casa', 'TEXT')
    ]

    for col_def in columns:
        col_name = col_def[0].split()[0]
        try:
            sql = f"ALTER TABLE clientes ADD COLUMN {col_def[0]} {col_def[1]}" if len(col_def) > 1 else f"ALTER TABLE clientes ADD COLUMN {col_def[0]}"
            # Simpler approach:
            sql = f"ALTER TABLE clientes ADD COLUMN {col_def[0]}"
            print(f"Executing: {sql}")
            c.execute(sql)
            print(f"Added {col_name}")
        except sqlite3.OperationalError as e:
            print(f"Skipping {col_name}: {e}")

    conn.commit()
    conn.close()
    print("Schema update complete.")
except Exception as e:
    print(f"Error: {e}")
