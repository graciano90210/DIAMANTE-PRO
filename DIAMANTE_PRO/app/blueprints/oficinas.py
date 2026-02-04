"""
Blueprint de Oficinas - Diamante Pro
Gestión de oficinas para agrupar rutas por zona/región
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import datetime
from functools import wraps
from ..models import Oficina, Ruta, Usuario, Sociedad, db
from ..services import OficinaService

oficinas_bp = Blueprint('oficinas', __name__, url_prefix='/oficinas')


# Decoradores de autenticación
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('rol') not in ['dueno', 'gerente']:
            flash('No tienes permisos para esta acción')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@oficinas_bp.route('/')
@login_required
@admin_required
def lista():
    """Lista de oficinas con estadísticas"""
    sociedad_id = request.args.get('sociedad_id', type=int)
    
    resumen = OficinaService.get_resumen_por_oficinas(sociedad_id=sociedad_id)
    sociedades = Sociedad.query.filter_by(activo=True).all()
    
    return render_template('oficinas_lista.html',
        oficinas=resumen['oficinas'],
        rutas_sin_oficina=resumen['rutas_sin_oficina'],
        totales=resumen['totales'],
        sociedades=sociedades,
        sociedad_filtro=sociedad_id,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@oficinas_bp.route('/nueva')
@login_required
@admin_required
def nueva():
    """Formulario para nueva oficina"""
    sociedades = Sociedad.query.filter_by(activo=True).all()
    responsables = Usuario.query.filter(
        Usuario.rol.in_(['gerente', 'cobrador']),
        Usuario.activo == True
    ).all()
    
    return render_template('oficinas_nueva.html',
        sociedades=sociedades,
        responsables=responsables,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@oficinas_bp.route('/guardar', methods=['POST'])
@login_required
@admin_required
def guardar():
    """Guardar nueva oficina"""
    datos = {
        'nombre': request.form.get('nombre'),
        'codigo': request.form.get('codigo'),
        'descripcion': request.form.get('descripcion'),
        'direccion': request.form.get('direccion'),
        'ciudad': request.form.get('ciudad'),
        'estado': request.form.get('estado'),
        'pais': request.form.get('pais', 'Colombia'),
        'responsable_id': request.form.get('responsable_id') or None,
        'telefono_oficina': request.form.get('telefono_oficina'),
        'email_oficina': request.form.get('email_oficina'),
        'sociedad_id': request.form.get('sociedad_id') or None,
        'meta_cobro_diario': float(request.form.get('meta_cobro_diario', 0) or 0),
        'meta_prestamos_mes': float(request.form.get('meta_prestamos_mes', 0) or 0),
        'notas': request.form.get('notas')
    }
    
    resultado = OficinaService.crear_oficina(datos)
    
    if resultado.get('error'):
        flash(f'Error: {resultado["error"]}', 'danger')
        return redirect(url_for('oficinas.nueva'))
    
    flash(f'Oficina "{datos["nombre"]}" creada exitosamente', 'success')
    return redirect(url_for('oficinas.lista'))


@oficinas_bp.route('/<int:oficina_id>')
@login_required
@admin_required
def ver(oficina_id):
    """Ver detalle de una oficina con sus rutas"""
    resultado = OficinaService.get_oficina(oficina_id)
    
    if resultado.get('error'):
        flash(resultado['error'], 'danger')
        return redirect(url_for('oficinas.lista'))
    
    oficina = resultado['oficina']
    estadisticas = resultado['estadisticas']
    rutas = Ruta.query.filter_by(oficina_id=oficina_id, activo=True).order_by(Ruta.nombre).all()
    
    # Rutas disponibles para asignar (sin oficina o de esta sociedad)
    rutas_disponibles = Ruta.query.filter(
        Ruta.oficina_id.is_(None),
        Ruta.activo == True
    ).order_by(Ruta.nombre).all()
    
    return render_template('oficinas_detalle.html',
        oficina=oficina,
        estadisticas=estadisticas,
        rutas=rutas,
        rutas_disponibles=rutas_disponibles,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@oficinas_bp.route('/<int:oficina_id>/editar')
@login_required
@admin_required
def editar(oficina_id):
    """Formulario para editar oficina"""
    oficina = Oficina.query.get_or_404(oficina_id)
    sociedades = Sociedad.query.filter_by(activo=True).all()
    responsables = Usuario.query.filter(
        Usuario.rol.in_(['gerente', 'cobrador']),
        Usuario.activo == True
    ).all()
    
    return render_template('oficinas_editar.html',
        oficina=oficina,
        sociedades=sociedades,
        responsables=responsables,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@oficinas_bp.route('/<int:oficina_id>/actualizar', methods=['POST'])
@login_required
@admin_required
def actualizar(oficina_id):
    """Actualizar oficina existente"""
    datos = {
        'nombre': request.form.get('nombre'),
        'codigo': request.form.get('codigo'),
        'descripcion': request.form.get('descripcion'),
        'direccion': request.form.get('direccion'),
        'ciudad': request.form.get('ciudad'),
        'estado': request.form.get('estado'),
        'responsable_id': request.form.get('responsable_id') or None,
        'telefono_oficina': request.form.get('telefono_oficina'),
        'email_oficina': request.form.get('email_oficina'),
        'meta_cobro_diario': float(request.form.get('meta_cobro_diario', 0) or 0),
        'meta_prestamos_mes': float(request.form.get('meta_prestamos_mes', 0) or 0),
        'notas': request.form.get('notas'),
        'activo': request.form.get('activo') == 'on'
    }
    
    resultado = OficinaService.actualizar_oficina(oficina_id, datos)
    
    if resultado.get('error'):
        flash(f'Error: {resultado["error"]}', 'danger')
    else:
        flash('Oficina actualizada exitosamente', 'success')
    
    return redirect(url_for('oficinas.ver', oficina_id=oficina_id))


@oficinas_bp.route('/<int:oficina_id>/asignar-rutas', methods=['POST'])
@login_required
@admin_required
def asignar_rutas(oficina_id):
    """Asignar rutas a una oficina"""
    ruta_ids = request.form.getlist('ruta_ids[]')
    ruta_ids = [int(r) for r in ruta_ids if r]
    
    if not ruta_ids:
        flash('No se seleccionaron rutas', 'warning')
        return redirect(url_for('oficinas.ver', oficina_id=oficina_id))
    
    resultado = OficinaService.asignar_rutas(oficina_id, ruta_ids)
    
    if resultado.get('error'):
        flash(f'Error: {resultado["error"]}', 'danger')
    else:
        flash(resultado['mensaje'], 'success')
    
    return redirect(url_for('oficinas.ver', oficina_id=oficina_id))


@oficinas_bp.route('/quitar-ruta/<int:ruta_id>', methods=['POST'])
@login_required
@admin_required
def quitar_ruta(ruta_id):
    """Quitar una ruta de su oficina"""
    ruta = Ruta.query.get_or_404(ruta_id)
    oficina_id = ruta.oficina_id
    
    resultado = OficinaService.quitar_ruta(ruta_id)
    
    if resultado.get('error'):
        flash(f'Error: {resultado["error"]}', 'danger')
    else:
        flash(resultado['mensaje'], 'success')
    
    if oficina_id:
        return redirect(url_for('oficinas.ver', oficina_id=oficina_id))
    return redirect(url_for('oficinas.lista'))


@oficinas_bp.route('/<int:oficina_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar(oficina_id):
    """Eliminar (desactivar) una oficina"""
    reasignar_a = request.form.get('reasignar_a')
    reasignar_a = int(reasignar_a) if reasignar_a else None
    
    resultado = OficinaService.eliminar_oficina(oficina_id, reasignar_a)
    
    if resultado.get('error'):
        flash(f'Error: {resultado["error"]}', 'danger')
    else:
        flash(resultado['mensaje'], 'success')
    
    return redirect(url_for('oficinas.lista'))


# API endpoints para AJAX
@oficinas_bp.route('/api/<int:oficina_id>/estadisticas')
@login_required
def api_estadisticas(oficina_id):
    """API: Obtener estadísticas de una oficina"""
    estadisticas = OficinaService.get_estadisticas_oficina(oficina_id)
    return jsonify(estadisticas)


@oficinas_bp.route('/api/resumen')
@login_required
def api_resumen():
    """API: Resumen de todas las oficinas"""
    sociedad_id = request.args.get('sociedad_id', type=int)
    resumen = OficinaService.get_resumen_por_oficinas(sociedad_id=sociedad_id)
    
    # Serializar para JSON
    return jsonify({
        'oficinas': [{
            'id': o['oficina'].id,
            'nombre': o['oficina'].nombre,
            'num_rutas': o['num_rutas'],
            'cartera_total': o['cartera_total'],
            'cobrado_hoy': o['cobrado_hoy']
        } for o in resumen['oficinas']],
        'rutas_sin_oficina': len(resumen['rutas_sin_oficina']),
        'totales': resumen['totales']
    })
