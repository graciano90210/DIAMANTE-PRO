"""
Utilidades de paginación y queries optimizadas para la API.
Mejora el rendimiento al manejar grandes volúmenes de datos.
"""
from flask import request, url_for


def paginate_query(query, default_per_page=20, max_per_page=100):
    """
    Pagina una query de SQLAlchemy basándose en parámetros GET.
    
    Parámetros URL soportados:
    - page: número de página (default 1)
    - per_page: items por página (default 20, max 100)
    
    Retorna:
    - dict con items, metadata de paginación
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', default_per_page, type=int)
    
    # Limitar per_page para evitar queries gigantes
    per_page = min(per_page, max_per_page)
    
    # Ejecutar paginación
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return {
        'items': pagination.items,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_items': pagination.total,
            'total_pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
            'next_page': pagination.next_num if pagination.has_next else None,
            'prev_page': pagination.prev_num if pagination.has_prev else None
        }
    }


def paginated_response(items_serialized, pagination_meta):
    """
    Crea respuesta JSON estándar para endpoints paginados.
    """
    return {
        'data': items_serialized,
        'pagination': pagination_meta
    }


# Constantes para optimización
PRESTAMO_EAGER_LOAD_FIELDS = [
    'cliente',
    'ruta',
    'cobrador'
]

PAGO_EAGER_LOAD_FIELDS = [
    'prestamo',
    'prestamo.cliente',
    'cobrador'
]
