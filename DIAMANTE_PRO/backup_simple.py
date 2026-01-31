"""
Script simplificado para copiar base de datos SQLite a archivo SQL
"""
import sqlite3

# Conectar a la base de datos local
conn = sqlite3.connect('instance/diamante.db')
cursor = conn.cursor()

# Crear archivo SQL con las inserciones
with open('backup.sql', 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write('%s\n' % line)

conn.close()
print("✅ Backup SQL creado: backup.sql")
print("\nAhora ejecuta:")
print("1. heroku pg:psql -a diamante-pro < backup.sql")
print("O copia los datos manualmente desde el dashboard")
