
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Inicialización limpia de extensiones
db = SQLAlchemy()
login_manager = LoginManager()

# Rate limiter para protección contra ataques de fuerza bruta
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
