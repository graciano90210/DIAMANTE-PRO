from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .models import db
import os
try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
except ImportError:
    pass # Managed in create_app
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Inicializar Sentry para monitoreo de errores (GitHub Student Pack)
    sentry_dsn = os.environ.get('SENTRY_DSN')
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        if sentry_dsn:
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[FlaskIntegration()],
                traces_sample_rate=1.0,  # 100% de transacciones en producción
                environment=os.environ.get('FLASK_ENV', 'production'),
                release=os.environ.get('HEROKU_SLUG_COMMIT', 'dev')
            )
            logger.info("✅ Sentry inicializado - Monitoreo activo")
        else:
            logger.info("⚠️ Sentry no configurado - Agregar SENTRY_DSN")
    except ImportError:
        logger.warning("⚠️ Sentry SDK no instalado - Se omite monitoreo")
    
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
    
    # Configurar CORS - Aceptar peticiones desde cualquier origen (localhost, web, etc.)
    CORS(app, 
         origins="*",
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=False)
    
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

    # NUEVO: Conectar Rutas de Capital (Inversiones) 💎
    # Esto permite guardar los aportes de dinero de los socios
    from .rutas_capital import capital_bp
    app.register_blueprint(capital_bp)

    return app