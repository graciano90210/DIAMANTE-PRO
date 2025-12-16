from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .models import db
import os

def create_app():
    app = Flask(__name__)
    
    # Configuración - Detectar entorno
    if os.environ.get('DATABASE_URL'):
        # Producción (Heroku) - PostgreSQL
        database_url = os.environ.get('DATABASE_URL')
        # Heroku usa postgres://, SQLAlchemy necesita postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Desarrollo local - SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diamante.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'diamante-pro-secret-2025')
    
    # Configuración JWT para API móvil
    app.config['JWT_SECRET_KEY'] = 'diamante-jwt-secret-2025-mobile'
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    
    # Inicializar extensiones
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Configurar CORS para la app móvil
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",  # En producción, especificar dominio de la app
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Solo crear tablas en desarrollo (SQLite)
    # En producción (PostgreSQL), usar init_db_heroku.py
    if not os.environ.get('DATABASE_URL'):
        with app.app_context():
            db.create_all()
    
    # Conectar rutas web
    from . import routes
    routes.init_routes(app)
    
    # Conectar API REST para app móvil
    from .api import api
    app.register_blueprint(api)

    return app