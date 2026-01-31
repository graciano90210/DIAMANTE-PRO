"""
Script para inicializar la base de datos en Heroku/PostgreSQL
"""
from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    # Eliminar todas las tablas si existen
    db.drop_all()
    
    # Crear todas las tablas de nuevo
    db.create_all()
    
    print("✅ Base de datos inicializada correctamente")
    print("Ahora ejecuta: heroku run python crear_admin.py -a diamante-pro")
