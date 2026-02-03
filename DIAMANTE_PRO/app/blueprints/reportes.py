"""
Blueprint de Reportes - Diamante Pro
Maneja: Dashboard, Reportes, PDFs
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
from ..models import Cliente, Prestamo, Pago, Transaccion, Ruta, Usuario, AporteCapital, db
from sqlalchemy import func

reportes_bp = Blueprint('reportes', __name__)


def login_required(f):
    """Decorador para requerir login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@reportes_bp.route('/reportes')
@login_required
def reportes():
    """Vista de reportes y estadísticas"""
    usuario_id = session.get('usuario_id')
    rol = session.get('rol')
    
    # Obtener fecha de inicio y fin (por defecto últimos 30 días)
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=30)
    
    if request.args.get('fecha_inicio'):
        fecha_inicio = datetime.strptime(request.args.get('fecha_inicio'), '%Y-%m-%d')
    if request.args.get('fecha_fin'):
        fecha_fin = datetime.strptime(request.args.get('fecha_fin'), '%Y-%m-%d')
        fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59)
    
    # Estadísticas generales
    total_clientes = Cliente.query.count()
    
    if rol == 'cobrador':
        total_prestamos = Prestamo.query.filter_by(cobrador_id=usuario_id).count()
        prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO', cobrador_id=usuario_id).count()
        prestamos_cancelados = Prestamo.query.filter_by(estado='CANCELADO', cobrador_id=usuario_id).count()
    else:
        total_prestamos = Prestamo.query.count()
        prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO').count()
        prestamos_cancelados = Prestamo.query.filter_by(estado='CANCELADO').count()
    
    # Datos financieros
    if rol == 'cobrador':
        prestamos_periodo = Prestamo.query.filter(
            Prestamo.fecha_inicio >= fecha_inicio,
            Prestamo.fecha_inicio <= fecha_fin,
            Prestamo.cobrador_id == usuario_id
        ).all()
        total_prestado_periodo = sum(p.monto_prestado for p in prestamos_periodo)
        
        pagos_periodo = Pago.query.join(Prestamo).filter(
            Pago.fecha_pago >= fecha_inicio,
            Pago.fecha_pago <= fecha_fin,
            Prestamo.cobrador_id == usuario_id
        ).all()
        total_cobrado_periodo = sum(p.monto for p in pagos_periodo)
        num_pagos_periodo = len(pagos_periodo)
        
        cartera_actual = db.session.query(func.sum(Prestamo.saldo_actual)).filter_by(
            estado='ACTIVO', cobrador_id=usuario_id).scalar()
        cartera_actual = float(cartera_actual) if cartera_actual else 0
        
        capital_circulacion = db.session.query(func.sum(Prestamo.monto_prestado)).filter_by(
            estado='ACTIVO', cobrador_id=usuario_id).scalar()
        capital_circulacion = float(capital_circulacion) if capital_circulacion else 0
    else:
        prestamos_periodo = Prestamo.query.filter(
            Prestamo.fecha_inicio >= fecha_inicio,
            Prestamo.fecha_inicio <= fecha_fin
        ).all()
        total_prestado_periodo = sum(p.monto_prestado for p in prestamos_periodo)
        
        pagos_periodo = Pago.query.filter(
            Pago.fecha_pago >= fecha_inicio,
            Pago.fecha_pago <= fecha_fin
        ).all()
        total_cobrado_periodo = sum(p.monto for p in pagos_periodo)
        num_pagos_periodo = len(pagos_periodo)
        
        cartera_actual = db.session.query(func.sum(Prestamo.saldo_actual)).filter_by(estado='ACTIVO').scalar()
        cartera_actual = float(cartera_actual) if cartera_actual else 0
        
        capital_circulacion = db.session.query(func.sum(Prestamo.monto_prestado)).filter_by(estado='ACTIVO').scalar()
        capital_circulacion = float(capital_circulacion) if capital_circulacion else 0
    
    # Datos para gráficos
    if rol == 'cobrador':
        pagos_por_dia = db.session.query(
            func.date(Pago.fecha_pago).label('fecha'),
            func.sum(Pago.monto).label('total')
        ).join(Prestamo).filter(
            Pago.fecha_pago >= fecha_inicio,
            Pago.fecha_pago <= fecha_fin,
            Prestamo.cobrador_id == usuario_id
        ).group_by(func.date(Pago.fecha_pago)).order_by('fecha').all()
        
        estados_prestamos = db.session.query(
            Prestamo.estado,
            func.count(Prestamo.id).label('cantidad')
        ).filter_by(cobrador_id=usuario_id).group_by(Prestamo.estado).all()
        
        top_deudores = db.session.query(
            Cliente.nombre,
            Prestamo.saldo_actual
        ).join(Prestamo).filter(
            Prestamo.estado == 'ACTIVO',
            Prestamo.cobrador_id == usuario_id
        ).order_by(Prestamo.saldo_actual.desc()).limit(5).all()
        
        prestamos_por_frecuencia = db.session.query(
            Prestamo.frecuencia,
            func.count(Prestamo.id).label('cantidad')
        ).filter_by(estado='ACTIVO', cobrador_id=usuario_id).group_by(Prestamo.frecuencia).all()
        
        cobros_por_cobrador = db.session.query(
            Usuario.nombre,
            func.count(Pago.id).label('num_pagos'),
            func.sum(Pago.monto).label('total_cobrado')
        ).join(Pago, Usuario.id == Pago.cobrador_id).filter(
            Pago.fecha_pago >= fecha_inicio,
            Pago.fecha_pago <= fecha_fin,
            Usuario.id == usuario_id
        ).group_by(Usuario.nombre).all()
    else:
        pagos_por_dia = db.session.query(
            func.date(Pago.fecha_pago).label('fecha'),
            func.sum(Pago.monto).label('total')
        ).filter(
            Pago.fecha_pago >= fecha_inicio,
            Pago.fecha_pago <= fecha_fin
        ).group_by(func.date(Pago.fecha_pago)).order_by('fecha').all()
        
        estados_prestamos = db.session.query(
            Prestamo.estado,
            func.count(Prestamo.id).label('cantidad')
        ).group_by(Prestamo.estado).all()
        
        top_deudores = db.session.query(
            Cliente.nombre,
            Prestamo.saldo_actual
        ).join(Prestamo).filter(
            Prestamo.estado == 'ACTIVO'
        ).order_by(Prestamo.saldo_actual.desc()).limit(5).all()
        
        prestamos_por_frecuencia = db.session.query(
            Prestamo.frecuencia,
            func.count(Prestamo.id).label('cantidad')
        ).filter_by(estado='ACTIVO').group_by(Prestamo.frecuencia).all()
        
        cobros_por_cobrador = db.session.query(
            Usuario.nombre,
            func.count(Pago.id).label('num_pagos'),
            func.sum(Pago.monto).label('total_cobrado')
        ).join(Pago, Usuario.id == Pago.cobrador_id).filter(
            Pago.fecha_pago >= fecha_inicio,
            Pago.fecha_pago <= fecha_fin
        ).group_by(Usuario.nombre).all()
    
    # Listas detalladas para cobradores
    if rol == 'cobrador':
        lista_pagos = Pago.query.join(Prestamo).join(Cliente).filter(
            Pago.fecha_pago >= fecha_inicio,
            Pago.fecha_pago <= fecha_fin,
            Prestamo.cobrador_id == usuario_id
        ).order_by(Pago.fecha_pago.desc()).all()
        
        lista_creditos = Prestamo.query.join(Cliente).filter(
            Prestamo.fecha_inicio >= fecha_inicio,
            Prestamo.fecha_inicio <= fecha_fin,
            Prestamo.cobrador_id == usuario_id
        ).order_by(Prestamo.fecha_inicio.desc()).all()
        
        lista_gastos = Transaccion.query.filter(
            Transaccion.fecha >= fecha_inicio,
            Transaccion.fecha <= fecha_fin,
            Transaccion.usuario_origen_id == usuario_id
        ).order_by(Transaccion.fecha.desc()).all()
        
        lista_movimientos = []
        for pago in lista_pagos:
            lista_movimientos.append({
                'tipo': 'PAGO',
                'fecha': pago.fecha_pago,
                'descripcion': f'Pago de {pago.prestamo.cliente.nombre} - Crédito #{pago.prestamo_id}',
                'monto': pago.monto,
                'icono': 'bi-cash-coin',
                'color': 'success'
            })
        for credito in lista_creditos:
            lista_movimientos.append({
                'tipo': 'CRÉDITO',
                'fecha': credito.fecha_inicio,
                'descripcion': f'Crédito creado para {credito.cliente.nombre} - #{credito.id}',
                'monto': credito.monto_prestado,
                'icono': 'bi-plus-circle',
                'color': 'primary'
            })
        for gasto in lista_gastos:
            lista_movimientos.append({
                'tipo': 'GASTO',
                'fecha': gasto.fecha,
                'descripcion': f'{gasto.concepto}: {gasto.descripcion}',
                'monto': gasto.monto,
                'icono': 'bi-arrow-down-circle',
                'color': 'danger'
            })
        lista_movimientos.sort(key=lambda x: x['fecha'], reverse=True)
    else:
        lista_pagos = []
        lista_creditos = []
        lista_gastos = []
        lista_movimientos = []
    
    return render_template('reportes.html',
        fecha_inicio=fecha_inicio.strftime('%Y-%m-%d'),
        fecha_fin=fecha_fin.strftime('%Y-%m-%d'),
        total_clientes=total_clientes,
        total_prestamos=total_prestamos,
        prestamos_activos=prestamos_activos,
        prestamos_cancelados=prestamos_cancelados,
        total_prestado_periodo=total_prestado_periodo,
        total_cobrado_periodo=total_cobrado_periodo,
        num_pagos_periodo=num_pagos_periodo,
        cartera_actual=cartera_actual,
        capital_circulacion=capital_circulacion,
        pagos_por_dia=pagos_por_dia,
        estados_prestamos=estados_prestamos,
        top_deudores=top_deudores,
        prestamos_por_frecuencia=prestamos_por_frecuencia,
        cobros_por_cobrador=cobros_por_cobrador,
        lista_pagos=lista_pagos,
        lista_creditos=lista_creditos,
        lista_gastos=lista_gastos,
        lista_movimientos=lista_movimientos,
        nombre=session.get('nombre'),
        rol=session.get('rol'))
