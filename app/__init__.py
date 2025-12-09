from flask import Flask
from .models import db

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diamante.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'diamante-pro-secret-2025'
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    # Conectamos las rutas DESPUÉS del app_context
    from . import routes
    routes.init_routes(app)

    return app