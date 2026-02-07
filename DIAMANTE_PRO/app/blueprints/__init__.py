# Blueprints de Diamante Pro
# Este módulo contiene todos los blueprints organizados por funcionalidad

# Blueprints ACTIVOS (migrados)

from .auth import auth_bp
from .clientes import clientes_bp
from .prestamos import prestamos_bp

# Blueprints en PREPARACIÓN (aún no migrados - las rutas están en routes.py)
# from .prestamos import prestamos_bp
# from .cobros import cobros_bp
# from .rutas import rutas_bp
# from .sociedades import sociedades_bp
# from .finanzas import finanzas_bp
# from .reportes import reportes_bp

__all__ = [
    'auth_bp',
    'clientes_bp',
    'prestamos_bp',
    # Los siguientes se activarán cuando se migren:
    # 'cobros_bp',
    # 'rutas_bp',
    # 'sociedades_bp',
    # 'finanzas_bp',
    # 'reportes_bp'
]
