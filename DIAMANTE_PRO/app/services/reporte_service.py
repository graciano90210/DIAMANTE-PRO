"""
Reporte Service - Lógica de negocio para reportes y análisis

Contiene generación de reportes financieros y operativos.
"""
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from ..models import db, Prestamo, Pago, Cliente, Ruta, Transaccion, Sociedad


class ReporteService:
    """Servicio para generación de reportes"""
    
    @staticmethod
    def reporte_diario(fecha: datetime = None, ruta_id: int = None):
        """
        Genera reporte del día con cobros, préstamos y movimientos.
        """
        fecha = fecha or datetime.now().date()
        
        # Base queries
        pagos_query = Pago.query.filter(func.date(Pago.fecha_pago) == fecha)
        prestamos_query = Prestamo.query.filter(func.date(Prestamo.fecha_inicio) == fecha)
        
        if ruta_id:
            pagos_query = pagos_query.join(Prestamo).filter(Prestamo.ruta_id == ruta_id)
            prestamos_query = prestamos_query.filter(Prestamo.ruta_id == ruta_id)
        
        # Cobros del día
        cobros = pagos_query.all()
        total_cobrado = sum(p.monto for p in cobros)
        
        # Préstamos del día
        prestamos_nuevos = prestamos_query.all()
        total_prestado = sum(p.monto_prestado for p in prestamos_nuevos)
        
        # Gastos del día
        gastos = Transaccion.query.filter(
            func.date(Transaccion.fecha) == fecha,
            Transaccion.naturaleza == 'EGRESO'
        ).all()
        total_gastos = sum(g.monto for g in gastos)
        
        return {
            'fecha': fecha,
            'cobros': {
                'cantidad': len(cobros),
                'total': total_cobrado,
                'detalle': cobros
            },
            'prestamos': {
                'cantidad': len(prestamos_nuevos),
                'total': total_prestado,
                'detalle': prestamos_nuevos
            },
            'gastos': {
                'cantidad': len(gastos),
                'total': total_gastos,
                'detalle': gastos
            },
            'balance_dia': total_cobrado - total_prestado - total_gastos
        }
    
    @staticmethod
    def reporte_semanal(fecha_fin: datetime = None, ruta_id: int = None):
        """Genera reporte de la última semana"""
        fecha_fin = fecha_fin or datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=6)
        
        dias = []
        total_cobrado = 0
        total_prestado = 0
        
        for i in range(7):
            fecha = fecha_inicio + timedelta(days=i)
            reporte_dia = ReporteService.reporte_diario(fecha, ruta_id)
            
            dias.append({
                'fecha': fecha,
                'cobrado': reporte_dia['cobros']['total'],
                'prestado': reporte_dia['prestamos']['total'],
                'balance': reporte_dia['balance_dia']
            })
            
            total_cobrado += reporte_dia['cobros']['total']
            total_prestado += reporte_dia['prestamos']['total']
        
        return {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'dias': dias,
            'totales': {
                'cobrado': total_cobrado,
                'prestado': total_prestado,
                'balance': total_cobrado - total_prestado
            }
        }
    
    @staticmethod
    def reporte_mensual(anio: int = None, mes: int = None, ruta_id: int = None):
        """Genera reporte del mes"""
        ahora = datetime.now()
        anio = anio or ahora.year
        mes = mes or ahora.month
        
        # Cobros del mes
        cobros_query = db.session.query(
            func.sum(Pago.monto).label('total'),
            func.count(Pago.id).label('cantidad')
        ).filter(
            extract('year', Pago.fecha_pago) == anio,
            extract('month', Pago.fecha_pago) == mes
        )
        
        if ruta_id:
            cobros_query = cobros_query.join(Prestamo).filter(Prestamo.ruta_id == ruta_id)
        
        cobros = cobros_query.first()
        
        # Préstamos del mes
        prestamos_query = db.session.query(
            func.sum(Prestamo.monto_prestado).label('total'),
            func.count(Prestamo.id).label('cantidad')
        ).filter(
            extract('year', Prestamo.fecha_inicio) == anio,
            extract('month', Prestamo.fecha_inicio) == mes
        )
        
        if ruta_id:
            prestamos_query = prestamos_query.filter(Prestamo.ruta_id == ruta_id)
        
        prestamos = prestamos_query.first()
        
        # Clientes nuevos
        clientes_nuevos = Cliente.query.filter(
            extract('year', Cliente.fecha_registro) == anio,
            extract('month', Cliente.fecha_registro) == mes
        ).count()
        
        return {
            'anio': anio,
            'mes': mes,
            'cobros': {
                'total': float(cobros.total or 0),
                'cantidad': int(cobros.cantidad or 0)
            },
            'prestamos': {
                'total': float(prestamos.total or 0),
                'cantidad': int(prestamos.cantidad or 0)
            },
            'clientes_nuevos': clientes_nuevos,
            'balance': float((cobros.total or 0) - (prestamos.total or 0))
        }
    
    @staticmethod
    def reporte_cartera():
        """Genera reporte del estado de la cartera total"""
        # Por estado
        estados = db.session.query(
            Prestamo.estado,
            func.count(Prestamo.id).label('cantidad'),
            func.sum(Prestamo.saldo_actual).label('saldo')
        ).group_by(Prestamo.estado).all()
        
        # Por riesgo
        riesgos = db.session.query(
            Cliente.nivel_riesgo,
            func.count(Prestamo.id).label('cantidad'),
            func.sum(Prestamo.saldo_actual).label('saldo')
        ).join(Prestamo).filter(
            Prestamo.estado == 'ACTIVO'
        ).group_by(Cliente.nivel_riesgo).all()
        
        # Por ruta
        rutas = db.session.query(
            Ruta.nombre,
            func.count(Prestamo.id).label('cantidad'),
            func.sum(Prestamo.saldo_actual).label('saldo')
        ).join(Prestamo).filter(
            Prestamo.estado == 'ACTIVO'
        ).group_by(Ruta.id, Ruta.nombre).all()
        
        # Totales
        total_cartera = db.session.query(
            func.sum(Prestamo.saldo_actual)
        ).filter(Prestamo.estado == 'ACTIVO').scalar() or 0
        
        return {
            'por_estado': [
                {'estado': e[0], 'cantidad': e[1], 'saldo': float(e[2] or 0)} 
                for e in estados
            ],
            'por_riesgo': [
                {'riesgo': r[0] or 'NUEVO', 'cantidad': r[1], 'saldo': float(r[2] or 0)} 
                for r in riesgos
            ],
            'por_ruta': [
                {'ruta': r[0], 'cantidad': r[1], 'saldo': float(r[2] or 0)} 
                for r in rutas
            ],
            'total_cartera': float(total_cartera)
        }
    
    @staticmethod
    def reporte_cobradores(fecha_inicio: datetime = None, fecha_fin: datetime = None):
        """Genera reporte de rendimiento por cobrador"""
        fecha_fin = fecha_fin or datetime.now()
        fecha_inicio = fecha_inicio or (fecha_fin - timedelta(days=30))
        
        from ..models import Usuario
        
        cobradores = Usuario.query.filter_by(rol='cobrador', activo=True).all()
        resultados = []
        
        for cobrador in cobradores:
            # Cobros en el período
            cobros = db.session.query(
                func.sum(Pago.monto).label('total'),
                func.count(Pago.id).label('cantidad')
            ).filter(
                Pago.cobrador_id == cobrador.id,
                Pago.fecha_pago >= fecha_inicio,
                Pago.fecha_pago <= fecha_fin
            ).first()
            
            # Préstamos activos asignados
            prestamos_activos = Prestamo.query.filter_by(
                cobrador_id=cobrador.id,
                estado='ACTIVO'
            ).count()
            
            # Cartera asignada
            cartera = db.session.query(
                func.sum(Prestamo.saldo_actual)
            ).filter(
                Prestamo.cobrador_id == cobrador.id,
                Prestamo.estado == 'ACTIVO'
            ).scalar() or 0
            
            resultados.append({
                'cobrador': cobrador.nombre,
                'id': cobrador.id,
                'cobros_total': float(cobros.total or 0),
                'cobros_cantidad': int(cobros.cantidad or 0),
                'prestamos_activos': prestamos_activos,
                'cartera_asignada': float(cartera)
            })
        
        return {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'cobradores': resultados
        }
    
    @staticmethod
    def reporte_sociedades():
        """Genera reporte de rendimiento por sociedad"""
        sociedades = Sociedad.query.filter_by(activo=True).all()
        resultados = []
        
        for sociedad in sociedades:
            rutas = Ruta.query.filter_by(sociedad_id=sociedad.id).all()
            ruta_ids = [r.id for r in rutas]
            
            if ruta_ids:
                # Cartera
                cartera = db.session.query(
                    func.sum(Prestamo.saldo_actual)
                ).filter(
                    Prestamo.ruta_id.in_(ruta_ids),
                    Prestamo.estado == 'ACTIVO'
                ).scalar() or 0
                
                # Ganancias (préstamos pagados)
                ganancias = db.session.query(
                    func.sum(Prestamo.monto_a_pagar - Prestamo.monto_prestado)
                ).filter(
                    Prestamo.ruta_id.in_(ruta_ids),
                    Prestamo.estado == 'PAGADO'
                ).scalar() or 0
            else:
                cartera = 0
                ganancias = 0
            
            resultados.append({
                'sociedad': sociedad.nombre,
                'id': sociedad.id,
                'num_socios': sociedad.numero_socios,
                'porcentaje_dueno': sociedad.porcentaje_dueno,
                'num_rutas': len(rutas),
                'cartera_activa': float(cartera),
                'ganancias_realizadas': float(ganancias)
            })
        
        return {'sociedades': resultados}
