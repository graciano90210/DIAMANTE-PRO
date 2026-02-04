import os
from pathlib import Path

from flask import Flask, request, g
from flask_cors import CORS
from .extensions import db, login_manager

def create_app():
    app = Flask(__name__)

    # Cargar variables de entorno desde .env si existe
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
        except ImportError:
            pass  # python-dotenv no instalado, usar variables del sistema

    # ============================================================
    # LOGGING ESTRUCTURADO
    # ============================================================
    from .logging_config import setup_logging, get_logger
    logger = setup_logging(app)
    logger.info('Iniciando aplicación Diamante Pro')

    # ============================================================
    # CONFIGURACIÓN DE SEGURIDAD
    # ============================================================
    
    # SECRET_KEY - NUNCA usar valor por defecto en producción
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        if os.environ.get('FLASK_ENV') == 'production':
            raise RuntimeError('SECRET_KEY debe estar configurada en producción')
        secret_key = 'dev-key-solo-para-desarrollo-local'
    app.config['SECRET_KEY'] = secret_key
    
    # JWT para app móvil
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    
    # ============================================================
    # BASE DE DATOS
    # ============================================================
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        db_url = 'sqlite:///diamante.db'
    # Fix para Heroku Postgres (postgres:// -> postgresql://)
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # ============================================================
    # SERVICIOS EXTERNOS (Solo si están configurados)
    # ============================================================
    
    # Sentry - Monitoreo de errores
    sentry_dsn = os.environ.get('SENTRY_DSN')
    if sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[FlaskIntegration()],
                traces_sample_rate=0.1,
                environment=os.environ.get('FLASK_ENV', 'development')
            )
        except ImportError:
            pass
    
    # SendGrid - Configuración de email
    app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY')
    app.config['SENDGRID_FROM_EMAIL'] = os.environ.get('SENDGRID_FROM_EMAIL')
    
    # AWS S3 - Almacenamiento
    app.config['AWS_ACCESS_KEY_ID'] = os.environ.get('AWS_ACCESS_KEY_ID')
    app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY')
    app.config['AWS_S3_BUCKET'] = os.environ.get('AWS_S3_BUCKET')
    app.config['AWS_S3_REGION'] = os.environ.get('AWS_S3_REGION', 'us-east-1')

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
    
    from .blueprints.oficinas import oficinas_bp
    app.register_blueprint(oficinas_bp)
    
    from .blueprints.finanzas import finanzas_bp
    app.register_blueprint(finanzas_bp, url_prefix='/finanzas')
    
    from .blueprints.reportes import reportes_bp
    app.register_blueprint(reportes_bp)
    
    # Crear tablas
    with app.app_context():
        db.create_all()
    
    # ============================================================
    # REQUEST LOGGING MIDDLEWARE
    # ============================================================
    @app.before_request
    def log_request_info():
        """Registra información de cada request"""
        g.request_start_time = __import__('time').time()
    
    @app.after_request
    def log_response_info(response):
        """Registra información de cada response"""
        if hasattr(g, 'request_start_time'):
            duration_ms = ((__import__('time').time() - g.request_start_time) * 1000)
            if duration_ms > 1000:  # Solo loggear requests lentos (>1s)
                logger.warning(f'Slow request: {request.method} {request.path} - {duration_ms:.0f}ms')
        return response
    
    logger.info(f'Aplicación lista - Blueprints: {len(app.blueprints)}')
    
    return app