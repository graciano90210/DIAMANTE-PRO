import os
from pathlib import Path
from flask import Flask, request, g
from flask_cors import CORS
from .extensions import db, login_manager, limiter

def create_app():
    app = Flask(__name__)

    # --- 1. CONFIGURACIÓN DE RUTA DE BASE DE DATOS ABSOLUTA ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    root_dir = os.path.dirname(basedir)  # Subir a la carpeta raíz DIAMANTE_PRO
    db_path = os.path.join(root_dir, 'diamante.db')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-secreta')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    print(f"DEBUG: Base de datos configurada en: {db_path}")

    # --- 2. INICIALIZACIÓN ---
    CORS(app)
    db.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # O 'main.login' según tu ruta

    # --- 3. USER LOADER (Modelo Usuario) ---
    from .models import Usuario
    @login_manager.user_loader
    def load_user(user_id):
        user = Usuario.query.get(int(user_id))
        if user:
            print(f"DEBUG: Usuario {user.usuario} cargado.")
        else:
            print(f"DEBUG: Usuario ID {user_id} NO encontrado.")
        return user

    # --- 4. REGISTRO DE BLUEPRINTS ---
    # Rutas principales
    from .routes import main as main_bp
    app.register_blueprint(main_bp)
    # Rutas modulares (Envolver en try/except para evitar roturas si falta alguno)
    try:
        from .rutas_admin import admin_bp
        app.register_blueprint(admin_bp)

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

        from .blueprints.oficinas import oficinas_bp
        app.register_blueprint(oficinas_bp)
        from .blueprints.sociedades import sociedades_bp
        app.register_blueprint(sociedades_bp)
        from .blueprints.finanzas import finanzas_bp
        app.register_blueprint(finanzas_bp, url_prefix='/finanzas')

        from .blueprints.reportes import reportes_bp
        app.register_blueprint(reportes_bp)
        # API
        from .api import api as api_bp
        app.register_blueprint(api_bp)

    except Exception as e:
        print(f"ALERTA: Error cargando algun blueprint: {e}")

    # Crear tablas al inicio
    with app.app_context():
        db.create_all()

        # Auto-crear cajas para dueños/gerentes y rutas activas
        try:
            from .services.caja_service import asegurar_cajas_dueno, asegurar_todas_las_cajas_ruta
            duenos = Usuario.query.filter(Usuario.rol.in_(['dueno', 'gerente'])).all()
            for dueno in duenos:
                asegurar_cajas_dueno(dueno.id)
            asegurar_todas_las_cajas_ruta()
            db.session.commit()
            print("DEBUG: Cajas auto-creadas correctamente")
        except Exception as e:
            print(f"ALERTA: Error auto-creando cajas: {e}")
            db.session.rollback()

    return app