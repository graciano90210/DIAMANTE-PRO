"""
Blueprint de Reportes - Diamante Pro
Dashboard de Inteligencia de Negocios
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, timedelta
from ..models import Cliente, Prestamo, Pago, Transaccion, Ruta, Usuario, AporteCapital, Oficina, db
from sqlalchemy import func, case, and_, or_
from decimal import Decimal

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


def calcular_metricas_bi(fecha_inicio, fecha_fin, usuario_id=None, rol='dueno', ruta_id=None, oficina_id=None):
    """
    Calcula todas las métricas de Business Intelligence para el dashboard.
    Retorna un diccionario con todas las métricas calculadas.
    """
    hoy = datetime.now().date()

    # ==================== FILTROS BASE ====================
    filtro_prestamos = [Prestamo.estado == 'ACTIVO']
    filtro_prestamos_todos = []
    filtro_pagos = []

    # Obtener IDs de rutas si hay oficina seleccionada
    rutas_oficina_ids = []
    if oficina_id:
        rutas_oficina_ids = [r.id for r in Ruta.query.filter_by(oficina_id=oficina_id).all()]

    if rol == 'cobrador':
        filtro_prestamos.append(Prestamo.cobrador_id == usuario_id)
        filtro_prestamos_todos.append(Prestamo.cobrador_id == usuario_id)
    elif oficina_id and rutas_oficina_ids:
        filtro_prestamos.append(Prestamo.ruta_id.in_(rutas_oficina_ids))
        filtro_prestamos_todos.append(Prestamo.ruta_id.in_(rutas_oficina_ids))
    elif ruta_id:
        filtro_prestamos.append(Prestamo.ruta_id == ruta_id)
        filtro_prestamos_todos.append(Prestamo.ruta_id == ruta_id)

    # ==================== MÉTRICAS DE CAPITAL ====================
    # Capital total prestado (préstamos activos)
    capital_prestado = db.session.query(
        func.coalesce(func.sum(Prestamo.monto_prestado), 0)
    ).filter(*filtro_prestamos).scalar() or 0

    # Cartera total (saldo pendiente por cobrar)
    cartera_total = db.session.query(
        func.coalesce(func.sum(Prestamo.saldo_actual), 0)
    ).filter(*filtro_prestamos).scalar() or 0

    # Capital recuperado (total cobrado histórico)
    capital_recuperado_query = db.session.query(
        func.coalesce(func.sum(Pago.monto), 0)
    )
    if rol == 'cobrador':
        capital_recuperado_query = capital_recuperado_query.join(Prestamo).filter(
            Prestamo.cobrador_id == usuario_id
        )
    elif oficina_id and rutas_oficina_ids:
        capital_recuperado_query = capital_recuperado_query.join(Prestamo).filter(
            Prestamo.ruta_id.in_(rutas_oficina_ids)
        )
    elif ruta_id:
        capital_recuperado_query = capital_recuperado_query.join(Prestamo).filter(
            Prestamo.ruta_id == ruta_id
        )
    capital_recuperado = capital_recuperado_query.scalar() or 0

    # ==================== GANANCIA NETA (Intereses) ====================
    # Ganancia = Cartera Total - Capital Prestado (lo que se gana por intereses)
    ganancia_esperada = float(cartera_total) - float(capital_prestado)

    # Ganancia cobrada en el período
    pagos_periodo_query = db.session.query(
        func.coalesce(func.sum(Pago.monto), 0)
    ).filter(
        Pago.fecha_pago >= fecha_inicio,
        Pago.fecha_pago <= fecha_fin
    )
    if rol == 'cobrador':
        pagos_periodo_query = pagos_periodo_query.join(Prestamo).filter(
            Prestamo.cobrador_id == usuario_id
        )
    elif oficina_id and rutas_oficina_ids:
        pagos_periodo_query = pagos_periodo_query.join(Prestamo).filter(
            Prestamo.ruta_id.in_(rutas_oficina_ids)
        )
    elif ruta_id:
        pagos_periodo_query = pagos_periodo_query.join(Prestamo).filter(
            Prestamo.ruta_id == ruta_id
        )
    cobrado_periodo = pagos_periodo_query.scalar() or 0

    # ==================== TASA DE MOROSIDAD ====================
    prestamos_activos = Prestamo.query.filter(*filtro_prestamos).all()
    total_prestamos_activos = len(prestamos_activos)

    prestamos_al_dia = sum(1 for p in prestamos_activos if p.cuotas_atrasadas == 0)
    prestamos_atrasados = sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 0)
    prestamos_mora_grave = sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 3)

    tasa_morosidad = (prestamos_atrasados / total_prestamos_activos * 100) if total_prestamos_activos > 0 else 0
    tasa_mora_grave = (prestamos_mora_grave / total_prestamos_activos * 100) if total_prestamos_activos > 0 else 0

    # Monto en mora
    monto_en_mora = sum(float(p.saldo_actual) for p in prestamos_activos if p.cuotas_atrasadas > 0)

    # ==================== FLUJO DE CAJA HOY ====================
    # Ingresos de hoy (pagos recibidos)
    ingresos_hoy_query = db.session.query(
        func.coalesce(func.sum(Pago.monto), 0)
    ).filter(func.date(Pago.fecha_pago) == hoy)
    if rol == 'cobrador':
        ingresos_hoy_query = ingresos_hoy_query.join(Prestamo).filter(
            Prestamo.cobrador_id == usuario_id
        )
    elif oficina_id and rutas_oficina_ids:
        ingresos_hoy_query = ingresos_hoy_query.join(Prestamo).filter(
            Prestamo.ruta_id.in_(rutas_oficina_ids)
        )
    elif ruta_id:
        ingresos_hoy_query = ingresos_hoy_query.join(Prestamo).filter(
            Prestamo.ruta_id == ruta_id
        )
    ingresos_hoy = ingresos_hoy_query.scalar() or 0

    # Egresos de hoy (préstamos desembolsados)
    egresos_hoy_query = db.session.query(
        func.coalesce(func.sum(Prestamo.monto_prestado), 0)
    ).filter(func.date(Prestamo.fecha_inicio) == hoy)
    if rol == 'cobrador':
        egresos_hoy_query = egresos_hoy_query.filter(Prestamo.cobrador_id == usuario_id)
    elif oficina_id and rutas_oficina_ids:
        egresos_hoy_query = egresos_hoy_query.filter(Prestamo.ruta_id.in_(rutas_oficina_ids))
    elif ruta_id:
        egresos_hoy_query = egresos_hoy_query.filter(Prestamo.ruta_id == ruta_id)
    egresos_hoy = egresos_hoy_query.scalar() or 0

    # Gastos operativos de hoy
    gastos_hoy_query = db.session.query(
        func.coalesce(func.sum(Transaccion.monto), 0)
    ).filter(
        func.date(Transaccion.fecha) == hoy,
        Transaccion.naturaleza == 'EGRESO'
    )
    if rol == 'cobrador':
        gastos_hoy_query = gastos_hoy_query.filter(Transaccion.usuario_origen_id == usuario_id)
    gastos_hoy = gastos_hoy_query.scalar() or 0

    flujo_caja_hoy = float(ingresos_hoy) - float(egresos_hoy) - float(gastos_hoy)

    # Por cobrar hoy (estimado según frecuencia)
    dia_semana = hoy.weekday()
    por_cobrar_hoy = 0
    for p in prestamos_activos:
        cobra_hoy = False
        if p.frecuencia == 'DIARIO' and dia_semana != 6:
            cobra_hoy = True
        elif p.frecuencia == 'DIARIO_LUNES_VIERNES' and dia_semana < 5:
            cobra_hoy = True
        elif p.frecuencia == 'BISEMANAL':
            cobra_hoy = True
        if cobra_hoy:
            por_cobrar_hoy += float(p.valor_cuota)

    tasa_cobro_hoy = (float(ingresos_hoy) / por_cobrar_hoy * 100) if por_cobrar_hoy > 0 else 0

    # ==================== TENDENCIAS (últimos 30 días) ====================
    tendencia_cobros = []
    tendencia_prestamos = []
    labels_tendencia = []

    for i in range(30):
        fecha = hoy - timedelta(days=29-i)
        labels_tendencia.append(fecha.strftime('%d/%m'))

        # Cobros del día
        cobros_dia_query = db.session.query(
            func.coalesce(func.sum(Pago.monto), 0)
        ).filter(func.date(Pago.fecha_pago) == fecha)
        if rol == 'cobrador':
            cobros_dia_query = cobros_dia_query.join(Prestamo).filter(Prestamo.cobrador_id == usuario_id)
        elif oficina_id and rutas_oficina_ids:
            cobros_dia_query = cobros_dia_query.join(Prestamo).filter(Prestamo.ruta_id.in_(rutas_oficina_ids))
        elif ruta_id:
            cobros_dia_query = cobros_dia_query.join(Prestamo).filter(Prestamo.ruta_id == ruta_id)
        tendencia_cobros.append(float(cobros_dia_query.scalar() or 0))

        # Préstamos del día
        prestamos_dia_query = db.session.query(
            func.coalesce(func.sum(Prestamo.monto_prestado), 0)
        ).filter(func.date(Prestamo.fecha_inicio) == fecha)
        if rol == 'cobrador':
            prestamos_dia_query = prestamos_dia_query.filter(Prestamo.cobrador_id == usuario_id)
        elif oficina_id and rutas_oficina_ids:
            prestamos_dia_query = prestamos_dia_query.filter(Prestamo.ruta_id.in_(rutas_oficina_ids))
        elif ruta_id:
            prestamos_dia_query = prestamos_dia_query.filter(Prestamo.ruta_id == ruta_id)
        tendencia_prestamos.append(float(prestamos_dia_query.scalar() or 0))

    # ==================== DISTRIBUCIÓN DE CARTERA ====================
    # Por estado de morosidad
    cartera_al_dia = sum(float(p.saldo_actual) for p in prestamos_activos if p.cuotas_atrasadas == 0)
    cartera_atraso_leve = sum(float(p.saldo_actual) for p in prestamos_activos if 0 < p.cuotas_atrasadas <= 3)
    cartera_mora_grave = sum(float(p.saldo_actual) for p in prestamos_activos if p.cuotas_atrasadas > 3)

    # Por frecuencia
    distribucion_frecuencia_query = db.session.query(
        Prestamo.frecuencia,
        func.count(Prestamo.id).label('cantidad'),
        func.sum(Prestamo.saldo_actual).label('monto')
    ).filter(*filtro_prestamos).group_by(Prestamo.frecuencia).all()

    distribucion_frecuencia = [
        {'frecuencia': f[0], 'cantidad': f[1], 'monto': float(f[2] or 0)}
        for f in distribucion_frecuencia_query
    ]

    # ==================== TOP MÉTRICAS ====================
    # Top 5 deudores
    top_deudores = db.session.query(
        Cliente.nombre,
        Prestamo.saldo_actual,
        Prestamo.cuotas_atrasadas
    ).join(Prestamo).filter(*filtro_prestamos).order_by(
        Prestamo.saldo_actual.desc()
    ).limit(5).all()

    # Cobros por cobrador (solo para admin)
    cobros_por_cobrador = []
    if rol in ['dueno', 'gerente']:
        cobros_por_cobrador = db.session.query(
            Usuario.nombre,
            func.count(Pago.id).label('num_pagos'),
            func.coalesce(func.sum(Pago.monto), 0).label('total_cobrado')
        ).join(Pago, Usuario.id == Pago.cobrador_id).filter(
            Pago.fecha_pago >= fecha_inicio,
            Pago.fecha_pago <= fecha_fin
        ).group_by(Usuario.nombre).order_by(func.sum(Pago.monto).desc()).all()

    # ==================== MÉTRICAS POR MONEDA ====================
    metricas_por_moneda = {}
    monedas = db.session.query(Prestamo.moneda).filter(*filtro_prestamos).distinct().all()
    for (moneda,) in monedas:
        moneda = moneda or 'COP'
        filtro_moneda = filtro_prestamos + [Prestamo.moneda == moneda]

        capital_m = db.session.query(func.coalesce(func.sum(Prestamo.monto_prestado), 0)).filter(*filtro_moneda).scalar() or 0
        cartera_m = db.session.query(func.coalesce(func.sum(Prestamo.saldo_actual), 0)).filter(*filtro_moneda).scalar() or 0

        # Cartera por estado de morosidad por moneda
        prestamos_moneda = [p for p in prestamos_activos if (p.moneda or 'COP') == moneda]
        cartera_al_dia_m = sum(float(p.saldo_actual) for p in prestamos_moneda if p.cuotas_atrasadas == 0)
        cartera_atraso_leve_m = sum(float(p.saldo_actual) for p in prestamos_moneda if 0 < p.cuotas_atrasadas <= 3)
        cartera_mora_grave_m = sum(float(p.saldo_actual) for p in prestamos_moneda if p.cuotas_atrasadas > 3)
        monto_en_mora_m = sum(float(p.saldo_actual) for p in prestamos_moneda if p.cuotas_atrasadas > 0)

        # Ingresos de hoy por moneda
        ingresos_hoy_m_query = db.session.query(
            func.coalesce(func.sum(Pago.monto), 0)
        ).join(Prestamo).filter(
            func.date(Pago.fecha_pago) == hoy,
            Prestamo.moneda == moneda
        )
        if rol == 'cobrador':
            ingresos_hoy_m_query = ingresos_hoy_m_query.filter(Prestamo.cobrador_id == usuario_id)
        elif oficina_id and rutas_oficina_ids:
            ingresos_hoy_m_query = ingresos_hoy_m_query.filter(Prestamo.ruta_id.in_(rutas_oficina_ids))
        elif ruta_id:
            ingresos_hoy_m_query = ingresos_hoy_m_query.filter(Prestamo.ruta_id == ruta_id)
        ingresos_hoy_m = ingresos_hoy_m_query.scalar() or 0

        # Egresos de hoy por moneda
        egresos_hoy_m_query = db.session.query(
            func.coalesce(func.sum(Prestamo.monto_prestado), 0)
        ).filter(
            func.date(Prestamo.fecha_inicio) == hoy,
            Prestamo.moneda == moneda
        )
        if rol == 'cobrador':
            egresos_hoy_m_query = egresos_hoy_m_query.filter(Prestamo.cobrador_id == usuario_id)
        elif oficina_id and rutas_oficina_ids:
            egresos_hoy_m_query = egresos_hoy_m_query.filter(Prestamo.ruta_id.in_(rutas_oficina_ids))
        elif ruta_id:
            egresos_hoy_m_query = egresos_hoy_m_query.filter(Prestamo.ruta_id == ruta_id)
        egresos_hoy_m = egresos_hoy_m_query.scalar() or 0

        metricas_por_moneda[moneda] = {
            'capital': float(capital_m),
            'cartera': float(cartera_m),
            'ganancia': float(cartera_m) - float(capital_m),
            'cartera_al_dia': cartera_al_dia_m,
            'cartera_atraso_leve': cartera_atraso_leve_m,
            'cartera_mora_grave': cartera_mora_grave_m,
            'monto_en_mora': monto_en_mora_m,
            'ingresos_hoy': float(ingresos_hoy_m),
            'egresos_hoy': float(egresos_hoy_m),
            'flujo_neto_hoy': float(ingresos_hoy_m) - float(egresos_hoy_m)
        }

    return {
        # Capital
        'capital_prestado': float(capital_prestado),
        'cartera_total': float(cartera_total),
        'capital_recuperado': float(capital_recuperado),
        'ganancia_esperada': ganancia_esperada,
        'cobrado_periodo': float(cobrado_periodo),

        # Morosidad
        'total_prestamos_activos': total_prestamos_activos,
        'prestamos_al_dia': prestamos_al_dia,
        'prestamos_atrasados': prestamos_atrasados,
        'prestamos_mora_grave': prestamos_mora_grave,
        'tasa_morosidad': round(tasa_morosidad, 1),
        'tasa_mora_grave': round(tasa_mora_grave, 1),
        'monto_en_mora': monto_en_mora,

        # Flujo de caja
        'ingresos_hoy': float(ingresos_hoy),
        'egresos_hoy': float(egresos_hoy),
        'gastos_hoy': float(gastos_hoy),
        'flujo_caja_hoy': flujo_caja_hoy,
        'por_cobrar_hoy': por_cobrar_hoy,
        'tasa_cobro_hoy': round(tasa_cobro_hoy, 1),

        # Tendencias
        'labels_tendencia': labels_tendencia,
        'tendencia_cobros': tendencia_cobros,
        'tendencia_prestamos': tendencia_prestamos,

        # Distribución
        'cartera_al_dia': cartera_al_dia,
        'cartera_atraso_leve': cartera_atraso_leve,
        'cartera_mora_grave': cartera_mora_grave,
        'distribucion_frecuencia': distribucion_frecuencia,

        # Top
        'top_deudores': [{'nombre': d[0], 'saldo': float(d[1]), 'atraso': d[2]} for d in top_deudores],
        'cobros_por_cobrador': [{'nombre': c[0], 'pagos': c[1], 'total': float(c[2])} for c in cobros_por_cobrador],

        # Por moneda
        'metricas_por_moneda': metricas_por_moneda
    }


@reportes_bp.route('/reportes')
@login_required
def reportes():
    """Dashboard de Inteligencia de Negocios"""
    usuario_id = session.get('usuario_id')
    rol = session.get('rol')

    # Obtener filtros de ruta y oficina (priorizar parámetros GET sobre sesión)
    ruta_seleccionada_id = request.args.get('ruta_id', type=int)
    oficina_seleccionada_id = request.args.get('oficina_id', type=int)

    # Si no hay parámetros GET, usar los de la sesión como fallback
    if ruta_seleccionada_id is None and oficina_seleccionada_id is None:
        ruta_seleccionada_id = session.get('ruta_seleccionada_id')
        oficina_seleccionada_id = session.get('oficina_seleccionada_id')

    # Obtener fecha de inicio y fin (por defecto últimos 30 días)
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=30)

    if request.args.get('fecha_inicio'):
        fecha_inicio = datetime.strptime(request.args.get('fecha_inicio'), '%Y-%m-%d')
    if request.args.get('fecha_fin'):
        fecha_fin = datetime.strptime(request.args.get('fecha_fin'), '%Y-%m-%d')
        fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59)
    
    # Calcular métricas de BI
    metricas = calcular_metricas_bi(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        usuario_id=usuario_id,
        rol=rol,
        ruta_id=ruta_seleccionada_id,
        oficina_id=oficina_seleccionada_id
    )

    # Estadísticas generales adicionales
    total_clientes = Cliente.query.count()
    total_prestamos = Prestamo.query.count()
    prestamos_cancelados = Prestamo.query.filter_by(estado='CANCELADO').count()

    # Cargar rutas y oficinas para filtros
    todas_las_rutas = Ruta.query.order_by(Ruta.nombre).all()
    todas_las_oficinas = Oficina.query.filter_by(activo=True).order_by(Oficina.nombre).all()

    ruta_seleccionada = None
    if ruta_seleccionada_id:
        ruta_seleccionada = Ruta.query.get(ruta_seleccionada_id)

    oficina_seleccionada = None
    if oficina_seleccionada_id:
        oficina_seleccionada = Oficina.query.get(oficina_seleccionada_id)

    return render_template('reportes_bi.html',
        fecha_inicio=fecha_inicio.strftime('%Y-%m-%d'),
        fecha_fin=fecha_fin.strftime('%Y-%m-%d'),
        metricas=metricas,
        total_clientes=total_clientes,
        total_prestamos=total_prestamos,
        prestamos_cancelados=prestamos_cancelados,
        todas_las_rutas=todas_las_rutas,
        todas_las_oficinas=todas_las_oficinas,
        ruta_seleccionada=ruta_seleccionada,
        oficina_seleccionada=oficina_seleccionada,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@reportes_bp.route('/api/reportes/metricas')
@login_required
def api_metricas():
    """API endpoint para obtener métricas en tiempo real (AJAX)"""
    usuario_id = session.get('usuario_id')
    rol = session.get('rol')
    ruta_id = session.get('ruta_seleccionada_id')
    oficina_id = session.get('oficina_seleccionada_id')

    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=30)

    metricas = calcular_metricas_bi(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        usuario_id=usuario_id,
        rol=rol,
        ruta_id=ruta_id,
        oficina_id=oficina_id
    )

    return jsonify(metricas)
