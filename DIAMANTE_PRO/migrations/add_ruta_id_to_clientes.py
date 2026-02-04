"""
Migración: Agregar campo ruta_id a la tabla clientes
Permite asignar clientes directamente a una ruta cuando se registran
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def run_migration():
    app = create_app()
    with app.app_context():
        try:
            # Verificar si la columna ya existe
            result = db.session.execute(text("PRAGMA table_info(clientes)")).fetchall()
            columnas = [col[1] for col in result]
            
            if 'ruta_id' in columnas:
                print("✅ La columna 'ruta_id' ya existe en la tabla 'clientes'")
                return True
            
            # Agregar la columna
            db.session.execute(text("ALTER TABLE clientes ADD COLUMN ruta_id INTEGER REFERENCES rutas(id)"))
            db.session.commit()
            print("✅ Columna 'ruta_id' agregada exitosamente a la tabla 'clientes'")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error en migración: {str(e)}")
            return False

if __name__ == '__main__':
    run_migration()
