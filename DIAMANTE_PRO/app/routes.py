"""
Routes principales - Diamante Pro
Contiene solo rutas no migradas a blueprints:
- Dashboard
- Selección de ruta
- Gestión de usuarios
"""
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from flask import render_template, request, redirect, url_for, session, flash, Blueprint
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Usuario, Cliente, Prestamo, Pago, Transaccion, Sociedad, Ruta, AporteCapital, Activo, Oficina, db
from datetime import datetime, timedelta
from sqlalchemy import func
import os

main = Blueprint('main', __name__)


# ==================== DASHBOARD ====================

@main.route('/dashboard')
def dashboard():
    """Dashboard principal con estadísticas"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    usuario_id = session.get('usuario_id')
    rol = session.get('rol')
    ruta_seleccionada_id = session.get('ruta_seleccionada_id')
    oficina_seleccionada_id = session.get('oficina_seleccionada_id')

    # Variables base
    capital_total_aportado = db.session.query(func.sum(AporteCapital.monto)).scalar() or 0
    capital_invertido_activos = db.session.query(func.sum(Activo.valor_compra)).scalar() or 0
    capital_disponible = capital_total_aportado - capital_invertido_activos
    notificaciones = []
    mensajes_sin_leer = 0
    # Obtener IDs de rutas de la oficina seleccionada (si aplica)
    rutas_oficina_ids = []
    if oficina_seleccionada_id:
        rutas_oficina_ids = [r.id for r in Ruta.query.filter_by(oficina_id=oficina_seleccionada_id).all()]

    # Filtrar clientes por cobrador, oficina o ruta seleccionada
    if rol == 'cobrador':
        total_clientes = Cliente.query.join(Prestamo).filter(Prestamo.cobrador_id == usuario_id).distinct(Cliente.id).count()
        clientes_vip = Cliente.query.join(Prestamo).filter(Prestamo.cobrador_id == usuario_id, Cliente.es_vip == True).distinct(Cliente.id).count()
    elif oficina_seleccionada_id and rutas_oficina_ids:
        total_clientes = Cliente.query.filter(Cliente.ruta_id.in_(rutas_oficina_ids)).count()
        clientes_vip = Cliente.query.filter(Cliente.ruta_id.in_(rutas_oficina_ids), Cliente.es_vip == True).count()
    elif ruta_seleccionada_id:
        total_clientes = Cliente.query.filter_by(ruta_id=ruta_seleccionada_id).count()
        clientes_vip = Cliente.query.filter_by(ruta_id=ruta_seleccionada_id, es_vip=True).count()
    else:
        total_clientes = Cliente.query.count()
        clientes_vip = Cliente.query.filter_by(es_vip=True).count()
    solicitudes_pendientes = 0  # Para futuras solicitudes de préstamos pendientes
    
    # Cargar todas las rutas y oficinas para el filtro
    todas_las_rutas = Ruta.query.order_by(Ruta.nombre).all()
    todas_las_oficinas = Oficina.query.filter_by(activo=True).order_by(Oficina.nombre).all()

    # Cargar la ruta seleccionada
    ruta_seleccionada = None
    if ruta_seleccionada_id:
        ruta_seleccionada = Ruta.query.get(ruta_seleccionada_id)

    # Cargar la oficina seleccionada
    oficina_seleccionada = None
    if oficina_seleccionada_id:
        oficina_seleccionada = Oficina.query.get(oficina_seleccionada_id)
    
    # Estadísticas de los últimos 7 días
    fecha_inicio = datetime.now().date() - timedelta(days=6)
    cobros_ultimos_7_dias = []
    labels_7_dias = []
    
    for i in range(7):
        fecha = fecha_inicio + timedelta(days=i)
        if rol == 'cobrador':
            pagos_dia = Pago.query.join(Prestamo).filter(
                func.date(Pago.fecha_pago) == fecha,
                Prestamo.cobrador_id == usuario_id
            ).all()
        elif oficina_seleccionada_id and rutas_oficina_ids:
            pagos_dia = Pago.query.join(Prestamo).filter(
                func.date(Pago.fecha_pago) == fecha,
                Prestamo.ruta_id.in_(rutas_oficina_ids)
            ).all()
        elif ruta_seleccionada_id:
            pagos_dia = Pago.query.join(Prestamo).filter(
                func.date(Pago.fecha_pago) == fecha,
                Prestamo.ruta_id == ruta_seleccionada_id
            ).all()
        else:
            pagos_dia = Pago.query.filter(func.date(Pago.fecha_pago) == fecha).all()
        
        total_dia = sum(float(p.monto) for p in pagos_dia) if pagos_dia else 0
        cobros_ultimos_7_dias.append(total_dia)
        labels_7_dias.append(fecha.strftime('%d/%m'))
    
    # Distribución de préstamos por estado
    if rol == 'cobrador':
        prestamos_pagados = Prestamo.query.filter_by(estado='PAGADO', cobrador_id=usuario_id).count()
        prestamos_cancelados = Prestamo.query.filter_by(estado='CANCELADO', cobrador_id=usuario_id).count()
        riesgo_stats = db.session.query(
            Cliente.nivel_riesgo, func.count(Cliente.id)
        ).join(Prestamo).filter(
            Prestamo.cobrador_id == usuario_id,
            Prestamo.estado == 'ACTIVO'
        ).group_by(Cliente.nivel_riesgo).all()
        prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO', cobrador_id=usuario_id).all()
    elif oficina_seleccionada_id and rutas_oficina_ids:
        prestamos_pagados = Prestamo.query.filter(Prestamo.estado == 'PAGADO', Prestamo.ruta_id.in_(rutas_oficina_ids)).count()
        prestamos_cancelados = Prestamo.query.filter(Prestamo.estado == 'CANCELADO', Prestamo.ruta_id.in_(rutas_oficina_ids)).count()
        riesgo_stats = db.session.query(
            Cliente.nivel_riesgo, func.count(Cliente.id)
        ).join(Prestamo).filter(
            Prestamo.ruta_id.in_(rutas_oficina_ids),
            Prestamo.estado == 'ACTIVO'
        ).group_by(Cliente.nivel_riesgo).all()
        prestamos_activos = Prestamo.query.filter(Prestamo.estado == 'ACTIVO', Prestamo.ruta_id.in_(rutas_oficina_ids)).all()
    elif ruta_seleccionada_id:
        prestamos_pagados = Prestamo.query.filter_by(estado='PAGADO', ruta_id=ruta_seleccionada_id).count()
        prestamos_cancelados = Prestamo.query.filter_by(estado='CANCELADO', ruta_id=ruta_seleccionada_id).count()
        riesgo_stats = db.session.query(
            Cliente.nivel_riesgo, func.count(Cliente.id)
        ).join(Prestamo).filter(
            Prestamo.ruta_id == ruta_seleccionada_id,
            Prestamo.estado == 'ACTIVO'
        ).group_by(Cliente.nivel_riesgo).all()
        prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO', ruta_id=ruta_seleccionada_id).all()
    else:
        prestamos_pagados = Prestamo.query.filter_by(estado='PAGADO').count()
        prestamos_cancelados = Prestamo.query.filter_by(estado='CANCELADO').count()
        riesgo_stats = db.session.query(
            Cliente.nivel_riesgo, func.count(Cliente.id)
        ).group_by(Cliente.nivel_riesgo).all()
        prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO').all()
    
    total_prestamos_activos = len(prestamos_activos)
    # Filtrar totales por cobrador, oficina o ruta seleccionada
    if rol == 'cobrador':
        total_cartera = db.session.query(func.sum(Prestamo.saldo_actual)).filter(
            Prestamo.estado == 'ACTIVO',
            Prestamo.cobrador_id == usuario_id
        ).scalar()
        capital_prestado = db.session.query(func.sum(Prestamo.monto_prestado)).filter(
            Prestamo.estado == 'ACTIVO',
            Prestamo.cobrador_id == usuario_id
        ).scalar()
    elif oficina_seleccionada_id and rutas_oficina_ids:
        total_cartera = db.session.query(func.sum(Prestamo.saldo_actual)).filter(
            Prestamo.estado == 'ACTIVO',
            Prestamo.ruta_id.in_(rutas_oficina_ids)
        ).scalar()
        capital_prestado = db.session.query(func.sum(Prestamo.monto_prestado)).filter(
            Prestamo.estado == 'ACTIVO',
            Prestamo.ruta_id.in_(rutas_oficina_ids)
        ).scalar()
    elif ruta_seleccionada_id:
        total_cartera = db.session.query(func.sum(Prestamo.saldo_actual)).filter(
            Prestamo.estado == 'ACTIVO',
            Prestamo.ruta_id == ruta_seleccionada_id
        ).scalar()
        capital_prestado = db.session.query(func.sum(Prestamo.monto_prestado)).filter(
            Prestamo.estado == 'ACTIVO',
            Prestamo.ruta_id == ruta_seleccionada_id
        ).scalar()
    else:
        total_cartera = db.session.query(func.sum(Prestamo.saldo_actual)).filter_by(estado='ACTIVO').scalar()
        capital_prestado = db.session.query(func.sum(Prestamo.monto_prestado)).filter_by(estado='ACTIVO').scalar()
    total_cartera = float(total_cartera) if total_cartera else 0
    capital_prestado = float(capital_prestado) if capital_prestado else 0

    # ==================== TOTALES POR MONEDA (COP/BRL) ====================
    # Calcular cartera por moneda
    cartera_por_moneda_query = db.session.query(
        Prestamo.moneda,
        func.sum(Prestamo.saldo_actual).label('total')
    ).filter(Prestamo.estado == 'ACTIVO')

    if rol == 'cobrador':
        cartera_por_moneda_query = cartera_por_moneda_query.filter(Prestamo.cobrador_id == usuario_id)
    elif oficina_seleccionada_id and rutas_oficina_ids:
        cartera_por_moneda_query = cartera_por_moneda_query.filter(Prestamo.ruta_id.in_(rutas_oficina_ids))
    elif ruta_seleccionada_id:
        cartera_por_moneda_query = cartera_por_moneda_query.filter(Prestamo.ruta_id == ruta_seleccionada_id)

    cartera_por_moneda_result = cartera_por_moneda_query.group_by(Prestamo.moneda).all()
    cartera_por_moneda = {r[0] or 'COP': float(r[1] or 0) for r in cartera_por_moneda_result}

    # Calcular capital prestado por moneda
    capital_por_moneda_query = db.session.query(
        Prestamo.moneda,
        func.sum(Prestamo.monto_prestado).label('total')
    ).filter(Prestamo.estado == 'ACTIVO')

    if rol == 'cobrador':
        capital_por_moneda_query = capital_por_moneda_query.filter(Prestamo.cobrador_id == usuario_id)
    elif oficina_seleccionada_id and rutas_oficina_ids:
        capital_por_moneda_query = capital_por_moneda_query.filter(Prestamo.ruta_id.in_(rutas_oficina_ids))
    elif ruta_seleccionada_id:
        capital_por_moneda_query = capital_por_moneda_query.filter(Prestamo.ruta_id == ruta_seleccionada_id)

    capital_por_moneda_result = capital_por_moneda_query.group_by(Prestamo.moneda).all()
    capital_prestado_por_moneda = {r[0] or 'COP': float(r[1] or 0) for r in capital_por_moneda_result}

    # Calcular ganancia esperada por moneda (cartera - capital)
    ganancia_esperada_por_moneda = {}
    for moneda in set(list(cartera_por_moneda.keys()) + list(capital_prestado_por_moneda.keys())):
        cartera_m = cartera_por_moneda.get(moneda, 0)
        capital_m = capital_prestado_por_moneda.get(moneda, 0)
        ganancia_esperada_por_moneda[moneda] = cartera_m - capital_m

    hoy = datetime.now().date()
    pagos_hoy = Pago.query.filter(func.date(Pago.fecha_pago) == hoy).all()
    ultimos_pagos = Pago.query.order_by(Pago.fecha_pago.desc()).limit(10).all()
    # Filtrar préstamos recientes por cobrador, oficina o ruta
    if rol == 'cobrador':
        prestamos_recientes = Prestamo.query.filter_by(cobrador_id=usuario_id).order_by(Prestamo.fecha_inicio.desc()).limit(5).all()
    elif oficina_seleccionada_id and rutas_oficina_ids:
        prestamos_recientes = Prestamo.query.filter(Prestamo.ruta_id.in_(rutas_oficina_ids)).order_by(Prestamo.fecha_inicio.desc()).limit(5).all()
    elif ruta_seleccionada_id:
        prestamos_recientes = Prestamo.query.filter_by(ruta_id=ruta_seleccionada_id).order_by(Prestamo.fecha_inicio.desc()).limit(5).all()
    else:
        prestamos_recientes = Prestamo.query.order_by(Prestamo.fecha_inicio.desc()).limit(5).all()
    
    # Por cobrar hoy
    por_cobrar_hoy = 0
    dia_semana_hoy = datetime.now().weekday()

    # Calcular flujo de cobro por moneda (por cobrar hoy)
    flujo_cobro_por_moneda = {}
    for p in prestamos_activos:
        cobra_hoy_moneda = False
        if p.frecuencia == 'DIARIO' and dia_semana_hoy != 6:
            cobra_hoy_moneda = True
        elif p.frecuencia == 'DIARIO_LUNES_VIERNES' and dia_semana_hoy < 5:
            cobra_hoy_moneda = True
        elif p.frecuencia == 'BISEMANAL':
            cobra_hoy_moneda = True
        if cobra_hoy_moneda:
            moneda = p.moneda or 'COP'
            flujo_cobro_por_moneda[moneda] = flujo_cobro_por_moneda.get(moneda, 0) + float(p.valor_cuota)

    for p in prestamos_activos:
        cobra_hoy = False
        if p.frecuencia == 'DIARIO' and dia_semana_hoy != 6:
            cobra_hoy = True
        elif p.frecuencia == 'DIARIO_LUNES_VIERNES' and dia_semana_hoy < 5:
            cobra_hoy = True
        elif p.frecuencia == 'BISEMANAL':
            cobra_hoy = True
        if cobra_hoy:
            por_cobrar_hoy += float(p.valor_cuota)
    
    # Proyección mañana
    proyeccion_manana = 0
    dia_manana = (datetime.now() + timedelta(days=1)).weekday()
    for p in prestamos_activos:
        cobra_manana = False
        if p.frecuencia == 'DIARIO' and dia_manana != 6:
            cobra_manana = True
        elif p.frecuencia == 'DIARIO_LUNES_VIERNES' and dia_manana < 5:
            cobra_manana = True
        if cobra_manana:
            proyeccion_manana += float(p.valor_cuota)
    
    prestamos_al_dia = sum(1 for p in prestamos_activos if p.cuotas_atrasadas == 0)
    prestamos_atrasados = sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 0)
    prestamos_mora = sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 3)
    
    total_cobrado_hoy = sum(float(p.monto) for p in pagos_hoy) if pagos_hoy else 0
    num_pagos_hoy = len(pagos_hoy)
    
    ganancia_esperada = total_cartera - capital_prestado if capital_prestado > 0 else 0
    porcentaje_ganancia = (ganancia_esperada / capital_prestado * 100) if capital_prestado > 0 else 0
    tasa_cobro_diaria = (total_cobrado_hoy / por_cobrar_hoy * 100) if por_cobrar_hoy > 0 else 0
    
    riesgo_labels = [r[0] if r[0] else 'NUEVO' for r in riesgo_stats]
    riesgo_data = [r[1] for r in riesgo_stats]
    
    return render_template('dashboard_new.html',
        nombre=session.get('nombre'),
        rol=session.get('rol'),
        total_prestamos_activos=total_prestamos_activos,
        total_cartera=total_cartera,
        capital_prestado=capital_prestado,
        por_cobrar_hoy=por_cobrar_hoy,
        proyeccion_manana=proyeccion_manana,
        prestamos_al_dia=prestamos_al_dia,
        prestamos_atrasados=prestamos_atrasados,
        prestamos_mora=prestamos_mora,
        total_cobrado_hoy=total_cobrado_hoy,
        num_pagos_hoy=num_pagos_hoy,
        todas_las_rutas=todas_las_rutas,
        todas_las_oficinas=todas_las_oficinas,
        ruta_seleccionada=ruta_seleccionada,
        oficina_seleccionada=oficina_seleccionada,
        ganancia_esperada=ganancia_esperada,
        porcentaje_ganancia=porcentaje_ganancia,
        tasa_cobro_diaria=tasa_cobro_diaria,
        ultimos_pagos=ultimos_pagos,
        prestamos_recientes=prestamos_recientes,
        cobros_ultimos_7_dias=cobros_ultimos_7_dias,
        labels_7_dias=labels_7_dias,
        prestamos_pagados=prestamos_pagados,
        prestamos_cancelados=prestamos_cancelados,
        riesgo_labels=riesgo_labels,
        riesgo_data=riesgo_data,
        clientes_vip=clientes_vip,
        capital_total_aportado=capital_total_aportado,
        capital_invertido_activos=capital_invertido_activos,
        capital_disponible=capital_disponible,
        solicitudes_pendientes=solicitudes_pendientes,
        notificaciones=notificaciones,
        mensajes_sin_leer=mensajes_sin_leer,
        total_clientes=total_clientes,
        # Totales por moneda (COP = Pesos, BRL = Reales)
        cartera_por_moneda=cartera_por_moneda,
        capital_prestado_por_moneda=capital_prestado_por_moneda,
        ganancia_esperada_por_moneda=ganancia_esperada_por_moneda,
        flujo_cobro_por_moneda=flujo_cobro_por_moneda
    )


@main.route('/seleccionar-ruta/<int:ruta_id>')
def seleccionar_ruta(ruta_id):
    """Seleccionar una ruta para filtrar el dashboard"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('rol') not in ['dueno', 'gerente']:
        return redirect(url_for('main.dashboard'))
    session['ruta_seleccionada_id'] = ruta_id
    session.pop('oficina_seleccionada_id', None)  # Limpiar filtro de oficina
    return redirect(url_for('main.dashboard'))


@main.route('/seleccionar-oficina/<int:oficina_id>')
def seleccionar_oficina(oficina_id):
    """Seleccionar una oficina para filtrar el dashboard"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('rol') not in ['dueno', 'gerente']:
        return redirect(url_for('main.dashboard'))
    session['oficina_seleccionada_id'] = oficina_id
    session.pop('ruta_seleccionada_id', None)  # Limpiar filtro de ruta
    return redirect(url_for('main.dashboard'))


@main.route('/ver-todas-rutas')
def ver_todas_rutas():
    """Limpiar filtro de ruta y oficina para ver todas"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    session.pop('ruta_seleccionada_id', None)
    session.pop('oficina_seleccionada_id', None)
    return redirect(url_for('main.dashboard'))


# ==================== GESTIÓN DE USUARIOS ====================

@main.route('/usuarios')
def usuarios_lista():
    """Lista de usuarios del sistema"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('rol') not in ['dueno', 'gerente']:
        flash('No tienes permisos para acceder a esta sección')
        return redirect(url_for('main.dashboard'))
    
    usuarios = Usuario.query.all()
    stats_usuarios = []
    for usuario in usuarios:
        num_cobros = Pago.query.filter_by(cobrador_id=usuario.id).count()
        total_cobrado = db.session.query(func.sum(Pago.monto)).filter_by(cobrador_id=usuario.id).scalar()
        total_cobrado = float(total_cobrado) if total_cobrado else 0
        stats_usuarios.append({
            'usuario': usuario,
            'num_cobros': num_cobros,
            'total_cobrado': total_cobrado
        })
    
    return render_template('usuarios_lista.html',
        stats_usuarios=stats_usuarios,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@main.route('/usuarios/nuevo')
def usuarios_nuevo():
    """Formulario para nuevo usuario"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('rol') not in ['dueno', 'gerente']:
        return redirect(url_for('main.dashboard'))
    return render_template('usuarios_nuevo.html',
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@main.route('/usuarios/guardar', methods=['POST'])
def usuarios_guardar():
    """Guardar nuevo usuario"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('rol') not in ['dueno', 'gerente']:
        return redirect(url_for('main.dashboard'))
    
    try:
        usuario = request.form.get('usuario')
        if Usuario.query.filter_by(usuario=usuario).first():
            return render_template('usuarios_nuevo.html',
                error='Ya existe un usuario con ese nombre',
                nombre=session.get('nombre'),
                rol=session.get('rol'))
        
        nuevo_usuario = Usuario(
            nombre=request.form.get('nombre'),
            usuario=usuario,
            password=generate_password_hash(request.form.get('password')),
            rol=request.form.get('rol'),
            activo=True
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('main.usuarios_lista'))
        
    except Exception as e:
        db.session.rollback()
        return render_template('usuarios_nuevo.html',
            error=f'Error al crear usuario: {str(e)}',
            nombre=session.get('nombre'),
            rol=session.get('rol'))


@main.route('/usuarios/editar/<int:usuario_id>')
def usuarios_editar(usuario_id):
    """Editar usuario existente"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('rol') not in ['dueno', 'gerente']:
        return redirect(url_for('main.dashboard'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template('usuarios_editar.html',
        usuario=usuario,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@main.route('/usuarios/actualizar/<int:usuario_id>', methods=['POST'])
def usuarios_actualizar(usuario_id):
    """Actualizar usuario existente"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('rol') not in ['dueno', 'gerente']:
        return redirect(url_for('main.dashboard'))
    
    try:
        usuario = Usuario.query.get_or_404(usuario_id)
        
        nuevo_usuario_nombre = request.form.get('usuario')
        if nuevo_usuario_nombre != usuario.usuario:
            if Usuario.query.filter_by(usuario=nuevo_usuario_nombre).first():
                return render_template('usuarios_editar.html',
                    usuario=usuario,
                    error='Ya existe otro usuario con ese nombre',
                    nombre=session.get('nombre'),
                    rol=session.get('rol'))
        
        usuario.nombre = request.form.get('nombre')
        usuario.usuario = nuevo_usuario_nombre
        usuario.rol = request.form.get('rol')
        
        nueva_password = request.form.get('password')
        if nueva_password and nueva_password.strip():
            usuario.password = generate_password_hash(nueva_password)
        
        activo = request.form.get('activo')
        usuario.activo = (activo == 'on')
        
        db.session.commit()
        return redirect(url_for('main.usuarios_lista'))
        
    except Exception as e:
        db.session.rollback()
        return render_template('usuarios_editar.html',
            usuario=usuario,
            error=f'Error al actualizar usuario: {str(e)}',
            nombre=session.get('nombre'),
            rol=session.get('rol'))
