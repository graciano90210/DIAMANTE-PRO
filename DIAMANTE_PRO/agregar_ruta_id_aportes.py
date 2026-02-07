import sqlite3

# Cambia la ruta si tu base de datos está en otro lugar
DB_PATH = 'DIAMANTE_PRO/diamante.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE aportes_capital ADD COLUMN ruta_id INTEGER")
    print('Columna ruta_id agregada a aportes_capital.')
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e):
        print('La columna ruta_id ya existe.')
    else:
        print('Error:', e)

conn.commit()
conn.close()
