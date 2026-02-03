"""
Blueprint de Finanzas - Diamante Pro
Maneja: Capital, Activos, Caja, Traslados
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime
from ..models import AporteCapital, Activo, Transaccion, Sociedad, Usuario, Ruta, Pago, Prestamo, db
from sqlalchemy import func

finanzas_bp = Blueprint('finanzas', __name__)


def login_required(f):
    """Decorador para requerir login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorador para requerir rol de dueño o gerente"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== CAPITAL ====================

@finanzas_bp.route('/capital/aportes')
@login_required
@admin_required
def capital_lista():
    """Lista de aportes de capital"""
    aportes = AporteCapital.query.order_by(AporteCapital.fecha_aporte.desc()).all()
    
    total_pesos = db.session.query(func.sum(AporteCapital.monto)).filter(
        AporteCapital.moneda == 'PESOS').scalar() or 0
    total_reales = db.session.query(func.sum(AporteCapital.monto)).filter(
        AporteCapital.moneda == 'REALES').scalar() or 0
    
    return render_template('capital_lista.html',
        aportes=aportes,
        total_pesos=total_pesos,
        total_reales=total_reales,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@finanzas_bp.route('/capital/nuevo')
@login_required
@admin_required
def capital_nuevo():
    """Formulario para nuevo aporte de capital"""
    sociedades = Sociedad.query.order_by(Sociedad.nombre).all()
    return render_template('capital_nuevo.html',
        sociedades=sociedades,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@finanzas_bp.route('/capital/guardar', methods=['POST'])
@login_required
@admin_required
def capital_guardar():
    """Guardar nuevo aporte de capital"""
    try:
        sociedad_id = request.form['sociedad_id']
        nombre_aportante = request.form['nombre_aportante']
        monto = float(request.form['monto'])
        moneda = request.form['moneda']
        fecha_aporte_str = request.form['fecha_aporte']
        descripcion = request.form.get('observaciones', '')
        
        fecha_aporte = datetime.strptime(fecha_aporte_str, '%Y-%m-%d')
        
        nuevo_aporte = AporteCapital(
            sociedad_id=sociedad_id,
            nombre_aportante=nombre_aportante,
            monto=monto,
            moneda=moneda,
            fecha_aporte=fecha_aporte,
            descripcion=descripcion,
            registrado_por_id=session.get('usuario_id')
        )
        db.session.add(nuevo_aporte)
        
        # Registrar en caja
        ingreso_caja = Transaccion(
            naturaleza='INGRESO',
            concepto='APORTE_CAPITAL',
            descripcion=f'Aporte Capital: {nombre_aportante} ({sociedad_id}) - {moneda}',
            monto=monto,
            fecha=fecha_aporte,
            usuario_origen_id=session.get('usuario_id'),
            usuario_destino_id=session.get('usuario_id'),
            prestamo_id=None
        )
        db.session.add(ingreso_caja)
        db.session.commit()
        
        return redirect(url_for('finanzas.capital_lista'))
        
    except Exception as e:
        db.session.rollback()
        sociedades = Sociedad.query.order_by(Sociedad.nombre).all()
        return render_template('capital_nuevo.html',
            sociedades=sociedades,
            error=f'Error al guardar aporte: {str(e)}',
            nombre=session.get('nombre'),
            rol=session.get('rol'))


# ==================== ACTIVOS ====================

@finanzas_bp.route('/activos')
@login_required
@admin_required
def activos_lista():
    """Lista de activos fijos"""
    activos = Activo.query.order_by(Activo.fecha_compra.desc()).all()
    total_valor = db.session.query(func.sum(Activo.valor_compra)).scalar() or 0
    
    return render_template('activos_lista.html',
        activos=activos,
        total_valor=total_valor,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@finanzas_bp.route('/activos/nuevo')
@login_required
@admin_required
def activos_nuevo():
    """Formulario para nuevo activo"""
    sociedades = Sociedad.query.order_by(Sociedad.nombre).all()
    rutas = Ruta.query.order_by(Ruta.nombre).all()
    usuarios = Usuario.query.order_by(Usuario.nombre).all()
    
    return render_template('activos_nuevo.html',
        sociedades=sociedades,
        rutas=rutas,
        usuarios=usuarios,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@finanzas_bp.route('/activos/guardar', methods=['POST'])
@login_required
@admin_required
def activos_guardar():
    """Guardar nuevo activo"""
    try:
        nombre = request.form['nombre']
        categoria = request.form['categoria']
        valor_compra = float(request.form['valor_compra'])
        fecha_compra_str = request.form['fecha_compra']
        sociedad_id = request.form.get('sociedad_id')
        ruta_id = request.form.get('ruta_id')
        usuario_responsable_id = request.form.get('usuario_responsable_id')
        marca = request.form.get('marca', '')
        modelo = request.form.get('modelo', '')
        placa_serial = request.form.get('placa_serial', '')
        estado = request.form['estado']
        notas = request.form.get('observaciones', '')
        
        fecha_compra = datetime.strptime(fecha_compra_str, '%Y-%m-%d')
        
        nuevo_activo = Activo(
            nombre=nombre,
            categoria=categoria,
            valor_compra=valor_compra,
            fecha_compra=fecha_compra,
            sociedad_id=sociedad_id if sociedad_id else None,
            ruta_id=ruta_id if ruta_id else None,
            usuario_responsable_id=usuario_responsable_id if usuario_responsable_id else None,
            marca=marca,
            modelo=modelo,
            placa_serial=placa_serial,
            estado=estado,
            notas=notas,
            registrado_por_id=session.get('usuario_id')
        )
        db.session.add(nuevo_activo)
        db.session.commit()
        
        return redirect(url_for('finanzas.activos_lista'))
        
    except Exception as e:
        db.session.rollback()
        sociedades = Sociedad.query.order_by(Sociedad.nombre).all()
        rutas = Ruta.query.order_by(Ruta.nombre).all()
        usuarios = Usuario.query.order_by(Usuario.nombre).all()
        return render_template('activos_nuevo.html',
            sociedades=sociedades,
            rutas=rutas,
            usuarios=usuarios,
            error=f'Error al guardar activo: {str(e)}',
            nombre=session.get('nombre'),
            rol=session.get('rol'))


# ==================== CAJA ====================

@finanzas_bp.route('/caja')
@login_required
def caja_inicio():
    """Vista principal de caja"""
    usuario_id = session.get('usuario_id')
    rol = session.get('rol')
    hoy = datetime.now().date()
    
    # Calcular ingresos del día
    if rol == 'cobrador':
        pagos_hoy = Pago.query.join(Prestamo).filter(
            func.date(Pago.fecha_pago) == hoy,
            Prestamo.cobrador_id == usuario_id
        ).all()
        traslados_recibidos_hoy = Transaccion.query.filter(
            func.date(Transaccion.fecha) == hoy,
            Transaccion.usuario_destino_id == usuario_id,
            Transaccion.naturaleza == 'TRASLADO'
        ).all()
    else:
        pagos_hoy = Pago.query.filter(func.date(Pago.fecha_pago) == hoy).all()
        traslados_recibidos_hoy = []
    
    total_cobrado_hoy = sum(p.monto for p in pagos_hoy)
    total_traslados_recibidos = sum(t.monto for t in traslados_recibidos_hoy)
    
    # Calcular gastos del día
    if rol == 'cobrador':
        gastos_hoy = Transaccion.query.filter(
            func.date(Transaccion.fecha) == hoy,
            Transaccion.usuario_origen_id == usuario_id
        ).all()
    else:
        gastos_hoy = Transaccion.query.filter(func.date(Transaccion.fecha) == hoy).all()
    
    total_gastos_hoy = sum(g.monto for g in gastos_hoy)
    balance_dia = total_cobrado_hoy + total_traslados_recibidos - total_gastos_hoy
    
    # Estadísticas del mes
    inicio_mes = datetime(hoy.year, hoy.month, 1)
    if rol == 'cobrador':
        pagos_mes = Pago.query.join(Prestamo).filter(
            Pago.fecha_pago >= inicio_mes,
            Prestamo.cobrador_id == usuario_id
        ).all()
        traslados_recibidos_mes = Transaccion.query.filter(
            Transaccion.fecha >= inicio_mes,
            Transaccion.usuario_destino_id == usuario_id,
            Transaccion.naturaleza == 'TRASLADO'
        ).all()
        gastos_mes = Transaccion.query.filter(
            Transaccion.fecha >= inicio_mes,
            Transaccion.usuario_origen_id == usuario_id
        ).all()
    else:
        pagos_mes = Pago.query.filter(Pago.fecha_pago >= inicio_mes).all()
        traslados_recibidos_mes = []
        gastos_mes = Transaccion.query.filter(Transaccion.fecha >= inicio_mes).all()
    
    total_cobrado_mes = sum(p.monto for p in pagos_mes)
    total_traslados_mes = sum(t.monto for t in traslados_recibidos_mes)
    total_gastos_mes = sum(g.monto for g in gastos_mes)
    balance_mes = total_cobrado_mes + total_traslados_mes - total_gastos_mes
    
    return render_template('caja_inicio.html',
        total_cobrado_hoy=total_cobrado_hoy,
        total_gastos_hoy=total_gastos_hoy,
        balance_dia=balance_dia,
        num_pagos_hoy=len(pagos_hoy),
        num_gastos_hoy=len(gastos_hoy),
        total_cobrado_mes=total_cobrado_mes,
        total_gastos_mes=total_gastos_mes,
        balance_mes=balance_mes,
        fecha_hoy=hoy.strftime('%d/%m/%Y'),
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@finanzas_bp.route('/caja/gastos')
@login_required
def caja_gastos():
    """Lista de gastos"""
    usuario_id = session.get('usuario_id')
    rol = session.get('rol')
    
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')
    
    query = Transaccion.query
    
    if rol == 'cobrador':
        query = query.filter_by(usuario_origen_id=usuario_id)
    
    if fecha_inicio_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            query = query.filter(Transaccion.fecha >= fecha_inicio)
        except ValueError:
            pass
    
    if fecha_fin_str:
        try:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
            fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59)
            query = query.filter(Transaccion.fecha <= fecha_fin)
        except ValueError:
            pass
    
    gastos = query.order_by(Transaccion.fecha.desc()).all()
    
    return render_template('caja_gastos.html',
        gastos=gastos,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@finanzas_bp.route('/caja/gastos/nuevo')
@login_required
def caja_gastos_nuevo():
    """Formulario para nuevo gasto"""
    return render_template('caja_gastos_nuevo.html',
        fecha_hoy=datetime.now().strftime('%Y-%m-%d'),
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@finanzas_bp.route('/caja/gastos/guardar', methods=['POST'])
@login_required
def caja_gastos_guardar():
    """Guardar nuevo gasto"""
    try:
        concepto = request.form.get('concepto')
        descripcion = request.form.get('descripcion', '')
        monto = float(request.form.get('monto'))
        fecha_str = request.form.get('fecha')
        
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d') if fecha_str else datetime.now()
        
        nuevo_gasto = Transaccion(
            naturaleza='EGRESO',
            concepto=concepto,
            descripcion=descripcion,
            monto=monto,
            fecha=fecha,
            usuario_origen_id=session.get('usuario_id'),
            usuario_destino_id=None,
            prestamo_id=None
        )
        
        db.session.add(nuevo_gasto)
        db.session.commit()
        
        return redirect(url_for('finanzas.caja_gastos'))
        
    except Exception as e:
        db.session.rollback()
        return render_template('caja_gastos_nuevo.html',
            fecha_hoy=datetime.now().strftime('%Y-%m-%d'),
            error=f'Error al guardar gasto: {str(e)}',
            nombre=session.get('nombre'),
            rol=session.get('rol'))

