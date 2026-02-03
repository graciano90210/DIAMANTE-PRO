

from flask import Flask
from flask_cors import CORS
from .extensions import db, login_manager

def create_app():
    app = Flask(__name__)

    # Configuración
    import os
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-diamante-2026-change-in-prod'
    
    # Database URL - usar or en lugar de valor por defecto para manejar cadenas vacías
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        db_url = 'sqlite:///diamante.db'
    # Fix para Heroku Postgres (postgres:// -> postgresql://)
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones
    CORS(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # User Loader (Obligatorio)
    from .models import Usuario
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar Blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .rutas_admin import admin_bp
    app.register_blueprint(admin_bp)
    
    # Nuevos Blueprints modulares
    from .blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from .blueprints.clientes import clientes_bp
    app.register_blueprint(clientes_bp)
    
    from .blueprints.prestamos import prestamos_bp
    app.register_blueprint(prestamos_bp)
    
    from .blueprints.cobros import cobros_bp
    app.register_blueprint(cobros_bp)
    
    from .blueprints.rutas import rutas_bp
    app.register_blueprint(rutas_bp)
    
    from .blueprints.sociedades import sociedades_bp
    app.register_blueprint(sociedades_bp)
    
    from .blueprints.finanzas import finanzas_bp
    app.register_blueprint(finanzas_bp)
    
    from .blueprints.reportes import reportes_bp
    app.register_blueprint(reportes_bp)
    
    # Crear tablas
    with app.app_context():
        db.create_all()
    
    return app