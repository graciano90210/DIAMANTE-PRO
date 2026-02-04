"""
Dashboard Service - Lógica de negocio del Dashboard

Contiene todas las consultas y cálculos para el dashboard,
separados de las rutas para mejor mantenibilidad.
"""
from datetime import datetime, timedelta
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload

from ..models import (
    db, Prestamo, Pago, Cliente, Ruta, 
    AporteCapital, Activo, Transaccion
)


class DashboardService:
    """Servicio para obtener estadísticas y datos del dashboard"""
    
    @staticmethod
    def get_capital_stats():
        """Obtiene estadísticas de capital"""
        capital_total_aportado = db.session.query(
            func.sum(AporteCapital.monto)
        ).scalar() or 0
        
        capital_invertido_activos = db.session.query(
            func.sum(Activo.valor_compra)
        ).scalar() or 0
        
        capital_disponible = capital_total_aportado - capital_invertido_activos
        
        return {
            'total_aportado': float(capital_total_aportado),
            'invertido_activos': float(capital_invertido_activos),
            'disponible': float(capital_disponible)
        }
    
    @staticmethod
    def get_prestamos_stats(usuario_id=None, ruta_id=None, rol='dueno'):
        """
        Obtiene estadísticas de préstamos filtradas por rol/ruta.
        
        Args:
            usuario_id: ID del usuario (para cobradores)
            ruta_id: ID de la ruta seleccionada
            rol: Rol del usuario
        """
        # Query base
        query = Prestamo.query.filter(Prestamo.estado == 'ACTIVO')
        
        # Aplicar filtros según rol
        if rol == 'cobrador' and usuario_id:
            query = query.filter(Prestamo.cobrador_id == usuario_id)
        elif ruta_id:
            query = query.filter(Prestamo.ruta_id == ruta_id)
        
        # Conteos y totales con agregaciones SQL
        totales = db.session.query(
            func.count(Prestamo.id).label('total'),
            func.sum(Prestamo.saldo_actual).label('cartera'),
            func.sum(Prestamo.monto_prestado).label('prestado'),
            func.sum(case((Prestamo.cuotas_atrasadas == 0, 1), else_=0)).label('al_dia'),
            func.sum(case((Prestamo.cuotas_atrasadas > 0, 1), else_=0)).label('atrasados'),
            func.sum(case((Prestamo.cuotas_atrasadas > 3, 1), else_=0)).label('mora')
        ).filter(Prestamo.estado == 'ACTIVO')
        
        if rol == 'cobrador' and usuario_id:
            totales = totales.filter(Prestamo.cobrador_id == usuario_id)
        elif ruta_id:
            totales = totales.filter(Prestamo.ruta_id == ruta_id)
        
        result = totales.first()
        
        total_cartera = float(result.cartera) if result.cartera else 0
        capital_prestado = float(result.prestado) if result.prestado else 0
        ganancia_esperada = total_cartera - capital_prestado
        porcentaje_ganancia = (ganancia_esperada / capital_prestado * 100) if capital_prestado > 0 else 0
        
        return {
            'total_activos': int(result.total) if result.total else 0,
            'total_cartera': total_cartera,
            'capital_prestado': capital_prestado,
            'al_dia': int(result.al_dia) if result.al_dia else 0,
            'atrasados': int(result.atrasados) if result.atrasados else 0,
            'en_mora': int(result.mora) if result.mora else 0,
            'ganancia_esperada': ganancia_esperada,
            'porcentaje_ganancia': porcentaje_ganancia
        }
    
    @staticmethod
    def get_cobros_stats(usuario_id=None, ruta_id=None, rol='dueno'):
        """Obtiene estadísticas de cobros para hoy y proyección mañana"""
        hoy = datetime.now().date()
        dia_semana_hoy = datetime.now().weekday()
        dia_manana = (datetime.now() + timedelta(days=1)).weekday()
        
        # Total cobrado hoy
        query_cobrado = db.session.query(
            func.sum(Pago.monto).label('total'),
            func.count(Pago.id).label('cantidad')
        ).filter(func.date(Pago.fecha_pago) == hoy)
        
        if rol == 'cobrador' and usuario_id:
            query_cobrado = query_cobrado.filter(Pago.cobrador_id == usuario_id)
        
        cobrado = query_cobrado.first()
        total_cobrado_hoy = float(cobrado.total) if cobrado.total else 0
        num_pagos_hoy = int(cobrado.cantidad) if cobrado.cantidad else 0
        
        # Por cobrar hoy (según frecuencia)
        por_cobrar_query = db.session.query(
            func.sum(Prestamo.valor_cuota)
        ).filter(Prestamo.estado == 'ACTIVO')
        
        if rol == 'cobrador' and usuario_id:
            por_cobrar_query = por_cobrar_query.filter(Prestamo.cobrador_id == usuario_id)
        elif ruta_id:
            por_cobrar_query = por_cobrar_query.filter(Prestamo.ruta_id == ruta_id)
        
        # Filtrar por día de la semana
        if dia_semana_hoy == 6:  # Domingo
            por_cobrar_query = por_cobrar_query.filter(Prestamo.frecuencia == 'BISEMANAL')
        elif dia_semana_hoy < 5:  # Lunes a Viernes
            por_cobrar_query = por_cobrar_query.filter(
                Prestamo.frecuencia.in_(['DIARIO', 'DIARIO_LUNES_VIERNES', 'BISEMANAL'])
            )
        else:  # Sábado
            por_cobrar_query = por_cobrar_query.filter(
                Prestamo.frecuencia.in_(['DIARIO', 'BISEMANAL'])
            )
        
        por_cobrar_hoy = float(por_cobrar_query.scalar() or 0)
        
        # Proyección mañana
        proyeccion_query = db.session.query(
            func.sum(Prestamo.valor_cuota)
        ).filter(Prestamo.estado == 'ACTIVO')
        
        if rol == 'cobrador' and usuario_id:
            proyeccion_query = proyeccion_query.filter(Prestamo.cobrador_id == usuario_id)
        elif ruta_id:
            proyeccion_query = proyeccion_query.filter(Prestamo.ruta_id == ruta_id)
        
        if dia_manana == 6:  # Domingo
            proyeccion_query = proyeccion_query.filter(Prestamo.frecuencia == 'BISEMANAL')
        elif dia_manana < 5:  # Lunes a Viernes
            proyeccion_query = proyeccion_query.filter(
                Prestamo.frecuencia.in_(['DIARIO', 'DIARIO_LUNES_VIERNES', 'BISEMANAL'])
            )
        else:  # Sábado
            proyeccion_query = proyeccion_query.filter(
                Prestamo.frecuencia.in_(['DIARIO', 'BISEMANAL'])
            )
        
        proyeccion_manana = float(proyeccion_query.scalar() or 0)
        
        # Tasa de cobro
        tasa_cobro = (total_cobrado_hoy / por_cobrar_hoy * 100) if por_cobrar_hoy > 0 else 0
        
        return {
            'total_cobrado_hoy': total_cobrado_hoy,
            'num_pagos_hoy': num_pagos_hoy,
            'por_cobrar_hoy': por_cobrar_hoy,
            'proyeccion_manana': proyeccion_manana,
            'tasa_cobro': tasa_cobro
        }
    
    @staticmethod
    def get_cobros_ultimos_7_dias(usuario_id=None, ruta_id=None, rol='dueno'):
        """Obtiene cobros de los últimos 7 días para gráfico"""
        fecha_inicio = datetime.now().date() - timedelta(days=6)
        cobros = []
        labels = []
        
        for i in range(7):
            fecha = fecha_inicio + timedelta(days=i)
            
            query = db.session.query(func.sum(Pago.monto)).join(Prestamo).filter(
                func.date(Pago.fecha_pago) == fecha
            )
            
            if rol == 'cobrador' and usuario_id:
                query = query.filter(Prestamo.cobrador_id == usuario_id)
            elif ruta_id:
                query = query.filter(Prestamo.ruta_id == ruta_id)
            
            total_dia = float(query.scalar() or 0)
            cobros.append(total_dia)
            labels.append(fecha.strftime('%d/%m'))
        
        return {'cobros': cobros, 'labels': labels}
    
    @staticmethod
    def get_riesgo_stats(usuario_id=None, ruta_id=None, rol='dueno'):
        """Obtiene distribución de clientes por nivel de riesgo"""
        query = db.session.query(
            Cliente.nivel_riesgo, func.count(Cliente.id)
        ).join(Prestamo).filter(Prestamo.estado == 'ACTIVO')
        
        if rol == 'cobrador' and usuario_id:
            query = query.filter(Prestamo.cobrador_id == usuario_id)
        elif ruta_id:
            query = query.filter(Prestamo.ruta_id == ruta_id)
        
        result = query.group_by(Cliente.nivel_riesgo).all()
        
        labels = [r[0] if r[0] else 'NUEVO' for r in result]
        data = [r[1] for r in result]
        
        return {'labels': labels, 'data': data}
    
    @staticmethod
    def get_ultimos_pagos(limit=10):
        """Obtiene los últimos pagos con eager loading"""
        return Pago.query.options(
            joinedload(Pago.prestamo).joinedload(Prestamo.cliente),
            joinedload(Pago.cobrador)
        ).order_by(Pago.fecha_pago.desc()).limit(limit).all()
    
    @staticmethod
    def get_prestamos_recientes(limit=5):
        """Obtiene los préstamos más recientes con eager loading"""
        return Prestamo.query.options(
            joinedload(Prestamo.cliente)
        ).order_by(Prestamo.fecha_inicio.desc()).limit(limit).all()
    
    @staticmethod
    def get_conteo_estados(usuario_id=None, ruta_id=None, rol='dueno'):
        """Obtiene conteo de préstamos por estado"""
        base_query = Prestamo.query
        
        if rol == 'cobrador' and usuario_id:
            base_query = base_query.filter(Prestamo.cobrador_id == usuario_id)
        elif ruta_id:
            base_query = base_query.filter(Prestamo.ruta_id == ruta_id)
        
        return {
            'pagados': base_query.filter_by(estado='PAGADO').count(),
            'cancelados': base_query.filter_by(estado='CANCELADO').count()
        }
    
    @classmethod
    def get_dashboard_completo(cls, usuario_id=None, ruta_id=None, rol='dueno'):
        """
        Obtiene todos los datos del dashboard en una sola llamada.
        Optimizado para reducir queries a la base de datos.
        """
        return {
            'capital': cls.get_capital_stats(),
            'prestamos': cls.get_prestamos_stats(usuario_id, ruta_id, rol),
            'cobros': cls.get_cobros_stats(usuario_id, ruta_id, rol),
            'cobros_7_dias': cls.get_cobros_ultimos_7_dias(usuario_id, ruta_id, rol),
            'riesgo': cls.get_riesgo_stats(usuario_id, ruta_id, rol),
            'estados': cls.get_conteo_estados(usuario_id, ruta_id, rol),
            'ultimos_pagos': cls.get_ultimos_pagos(),
            'prestamos_recientes': cls.get_prestamos_recientes(),
            'total_clientes': Cliente.query.count()
        }
