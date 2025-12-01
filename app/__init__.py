from flask import Flask
from .models import db

def create_app():
    app = Flask(__name__)
    
    # Configuración de la Base de Datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diamante.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Aquí conectamos las rutas para que el servidor "hable"
        from . import routes

    return app  