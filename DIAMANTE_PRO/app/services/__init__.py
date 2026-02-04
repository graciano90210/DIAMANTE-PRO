"""
Capa de Servicios - Diamante Pro

Esta capa contiene toda la lógica de negocio separada de las rutas.
Las rutas solo deben manejar HTTP requests/responses y llamar a estos servicios.

Beneficios:
- Código más limpio y mantenible
- Fácil de testear (unit tests)
- Reutilizable desde múltiples lugares (web, API, CLI)
- Separación de responsabilidades
"""

from .dashboard_service import DashboardService
from .prestamo_service import PrestamoService
from .cliente_service import ClienteService
from .sociedad_service import SociedadService
from .reporte_service import ReporteService
from .oficina_service import OficinaService

__all__ = [
    'DashboardService',
    'PrestamoService', 
    'ClienteService',
    'SociedadService',
    'ReporteService',
    'OficinaService'
]
