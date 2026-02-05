"""
Routes principales - Diamante Pro
Contiene solo rutas no migradas a blueprints:
- Dashboard
- Selección de ruta
- Gestión de usuarios
"""
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from flask import render_template, request, redirect, url_for, session, flash, Blueprint, current_app
from werkzeug.utils import secure_filename
from .models import Usuario, Cliente, Prestamo, Pago, Transaccion, Sociedad, Ruta, AporteCapital, Activo, db
from datetime import datetime, timedelta
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload
from .services import DashboardService
import os

main = Blueprint('main', __name__)


# ==================== DASHBOARD ====================

@main.route('/dashboard')
def dashboard():
    """Dashboard principal con estadísticas - Refactorizado con DashboardService"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    usuario_id = session.get('usuario_id')
    rol = session.get('rol')
    ruta_seleccionada_id = session.get('ruta_seleccionada_id')
    
    # Usar DashboardService para obtener todos los datos
    data = DashboardService.get_dashboard_completo(
        usuario_id=usuario_id,
        rol=rol,
        ruta_id=ruta_seleccionada_id
    )
    
    # Cargar rutas para el selector
    todas_las_rutas = Ruta.query.order_by(Ruta.nombre).all()
    ruta_seleccionada = Ruta.query.get(ruta_seleccionada_id) if ruta_seleccionada_id else None
    
    # Eager load para actividad reciente
    ultimos_pagos = Pago.query.options(
        joinedload(Pago.prestamo).joinedload(Prestamo.cliente),
        joinedload(Pago.cobrador)
    ).order_by(Pago.fecha_pago.desc()).limit(10).all()
    
    prestamos_recientes = Prestamo.query.options(
        joinedload(Prestamo.cliente)
    ).order_by(Prestamo.fecha_inicio.desc()).limit(5).all()
    




    # CÁLCULO DE TOTALES (Blindado contra filtros de ruta y rol)
    from sqlalchemy import func  # Asegura el import
    print("--- DEBUG: Calculando Totales ---")
    if rol == 'dueno':
        # Dueño: suma todos los préstamos activos
        query_totales = db.session.query(
            Prestamo.moneda,
            func.sum(Prestamo.monto + Prestamo.interes).label('total_deuda')
        ).filter(
            Prestamo.estado == 'ACTIVO'
        ).group_by(Prestamo.moneda)
    elif rol == 'cobrador':
        # Cobrador: solo sus préstamos activos
        query_totales = db.session.query(
            Prestamo.moneda,
            func.sum(Prestamo.monto + Prestamo.interes).label('total_deuda')
        ).filter(
            Prestamo.usuario_id == usuario_id,
            Prestamo.estado == 'ACTIVO'
        ).group_by(Prestamo.moneda)
    else:
        # Otros roles: puedes ajustar según reglas de negocio
        query_totales = db.session.query(
            Prestamo.moneda,
            func.sum(Prestamo.monto + Prestamo.interes).label('total_deuda')
        ).filter(
            Prestamo.estado == 'ACTIVO'
        ).group_by(Prestamo.moneda)

    estadisticas_moneda = {row.moneda: float(row.total_deuda or 0) for row in query_totales.all()}
    print(f"--- DEBUG: Totales encontrados: {estadisticas_moneda} ---")

    # DEBUG: Imprimir los diccionarios por moneda
    current_app.logger.warning("=" * 60)
    current_app.logger.warning("DEBUG - Datos por moneda enviados al template:")
    current_app.logger.warning(f"cartera_por_moneda: {cartera_por_moneda}")
    current_app.logger.warning(f"capital_prestado_por_moneda: {capital_prestado_por_moneda}")
    current_app.logger.warning(f"flujo_cobro_por_moneda: {flujo_cobro_por_moneda}")
    current_app.logger.warning(f"ganancia_esperada_por_moneda: {ganancia_esperada_por_moneda}")
    current_app.logger.warning("=" * 60)

    return render_template('dashboard_new.html',
        nombre=session.get('nombre'),
        rol=rol,
        # Estadísticas de préstamos
        total_prestamos_activos=data['prestamos']['total_activos'],
        total_cartera=data['prestamos']['cartera_total'],
        estadisticas_moneda=estadisticas_moneda,
        prestamos_al_dia=data['prestamos']['al_dia'],
        prestamos_atrasados=data['prestamos']['atrasados'],
        prestamos_mora=data['prestamos']['en_mora'],
        prestamos_pagados=data['prestamos'].get('pagados', 0),
        prestamos_cancelados=data['prestamos'].get('cancelados', 0),
        # Estadísticas de cobros
        por_cobrar_hoy=data['cobros']['por_cobrar_hoy'],
        proyeccion_manana=data['cobros']['proyeccion_manana'],
        total_cobrado_hoy=data['cobros']['cobrado_hoy'],
        num_pagos_hoy=data['cobros']['num_pagos_hoy'],
        tasa_cobro_diaria=data['cobros']['tasa_cobro'],
        cobros_ultimos_7_dias=data['cobros']['ultimos_7_dias'],
        labels_7_dias=data['cobros']['labels_7_dias'],
        # Estadísticas de capital
        capital_total_aportado=data['capital']['total_aportado'],
        capital_invertido_activos=data['capital']['invertido_activos'],
        capital_disponible=data['capital']['disponible'],
        ganancia_esperada=data['capital']['ganancia_esperada'],
        porcentaje_ganancia=data['capital']['porcentaje_ganancia'],
        # Riesgo
        riesgo_labels=data['riesgo']['labels'],
        riesgo_data=data['riesgo']['data'],
        # Contadores
        total_clientes=data['contadores']['clientes'],
        clientes_vip=data['contadores']['clientes_vip'],
        solicitudes_pendientes=data['contadores']['solicitudes_pendientes'],
        mensajes_sin_leer=data['contadores']['mensajes_sin_leer'],
        # Rutas y actividad
        todas_las_rutas=todas_las_rutas,
        ruta_seleccionada=ruta_seleccionada,
        ultimos_pagos=ultimos_pagos,
        prestamos_recientes=prestamos_recientes,
        notificaciones=[]
    )


@main.route('/seleccionar-ruta/<int:ruta_id>')
def seleccionar_ruta(ruta_id):
    """Seleccionar una ruta para filtrar el dashboard"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('rol') not in ['dueno', 'gerente']:
        return redirect(url_for('main.dashboard'))
    session['ruta_seleccionada_id'] = ruta_id
    return redirect(url_for('main.dashboard'))


@main.route('/ver-todas-rutas')
def ver_todas_rutas():
    """Limpiar filtro de ruta para ver todas"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    session.pop('ruta_seleccionada_id', None)
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
            rol=request.form.get('rol'),
            activo=True
        )
        # Usar el método seguro del modelo para hashing con bcrypt
        nuevo_usuario.set_password(request.form.get('password'))
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
            # Usar el método seguro del modelo para hashing con bcrypt
            usuario.set_password(nueva_password)
        
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
