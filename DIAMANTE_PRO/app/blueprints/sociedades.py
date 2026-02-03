"""
Blueprint de Sociedades - Diamante Pro
Maneja: CRUD de sociedades/socios
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime
from ..models import Sociedad, Ruta, db

sociedades_bp = Blueprint('sociedades', __name__, url_prefix='/sociedades')


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


@sociedades_bp.route('/')
@login_required
@admin_required
def lista():
    """Lista de sociedades con estadísticas"""
    sociedades = Sociedad.query.order_by(Sociedad.fecha_creacion.desc()).all()
    
    stats_sociedades = []
    for sociedad in sociedades:
        num_rutas = Ruta.query.filter_by(sociedad_id=sociedad.id, activo=True).count()
        stats_sociedades.append({
            'sociedad': sociedad,
            'num_rutas': num_rutas
        })
    
    return render_template('sociedades_lista.html',
        stats_sociedades=stats_sociedades,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@sociedades_bp.route('/nueva')
@login_required
@admin_required
def nueva():
    """Formulario para nueva sociedad"""
    return render_template('sociedades_nueva.html',
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@sociedades_bp.route('/guardar', methods=['POST'])
@login_required
@admin_required
def guardar():
    """Guardar nueva sociedad"""
    try:
        # Validar que la suma de porcentajes no supere 100%
        p1 = float(request.form.get('porcentaje_socio', 50))
        p2 = float(request.form.get('porcentaje_socio_2', 0))
        p3 = float(request.form.get('porcentaje_socio_3', 0))
        
        if (p1 + p2 + p3) > 100:
            return render_template('sociedades_nueva.html',
                error='La suma de los porcentajes no puede superar el 100%',
                nombre=session.get('nombre'),
                rol=session.get('rol'))
        
        nueva_sociedad = Sociedad(
            nombre=request.form.get('nombre'),
            nombre_socio=request.form.get('nombre_socio'),
            telefono_socio=request.form.get('telefono_socio'),
            porcentaje_socio=p1,
            nombre_socio_2=request.form.get('nombre_socio_2') or None,
            telefono_socio_2=request.form.get('telefono_socio_2') or None,
            porcentaje_socio_2=p2,
            nombre_socio_3=request.form.get('nombre_socio_3') or None,
            telefono_socio_3=request.form.get('telefono_socio_3') or None,
            porcentaje_socio_3=p3,
            notas=request.form.get('notas'),
            activo=True
        )
        
        db.session.add(nueva_sociedad)
        db.session.commit()
        
        return redirect(url_for('sociedades.lista'))
        
    except Exception as e:
        db.session.rollback()
        return render_template('sociedades_nueva.html',
            error=f'Error al crear sociedad: {str(e)}',
            nombre=session.get('nombre'),
            rol=session.get('rol'))


@sociedades_bp.route('/editar/<int:sociedad_id>')
@login_required
@admin_required
def editar(sociedad_id):
    """Editar sociedad existente"""
    sociedad = Sociedad.query.get_or_404(sociedad_id)
    
    return render_template('sociedades_editar.html',
        sociedad=sociedad,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@sociedades_bp.route('/actualizar/<int:sociedad_id>', methods=['POST'])
@login_required
@admin_required
def actualizar(sociedad_id):
    """Actualizar sociedad existente"""
    sociedad = Sociedad.query.get_or_404(sociedad_id)
    
    try:
        # Validar porcentajes
        p1 = float(request.form.get('porcentaje_socio', 50))
        p2 = float(request.form.get('porcentaje_socio_2', 0))
        p3 = float(request.form.get('porcentaje_socio_3', 0))
        
        if (p1 + p2 + p3) > 100:
            return render_template('sociedades_editar.html',
                sociedad=sociedad,
                error='La suma de los porcentajes no puede superar el 100%',
                nombre=session.get('nombre'),
                rol=session.get('rol'))
        
        sociedad.nombre = request.form.get('nombre')
        sociedad.nombre_socio = request.form.get('nombre_socio')
        sociedad.telefono_socio = request.form.get('telefono_socio')
        sociedad.porcentaje_socio = p1
        sociedad.nombre_socio_2 = request.form.get('nombre_socio_2') or None
        sociedad.telefono_socio_2 = request.form.get('telefono_socio_2') or None
        sociedad.porcentaje_socio_2 = p2
        sociedad.nombre_socio_3 = request.form.get('nombre_socio_3') or None
        sociedad.telefono_socio_3 = request.form.get('telefono_socio_3') or None
        sociedad.porcentaje_socio_3 = p3
        sociedad.notas = request.form.get('notas')
        activo = request.form.get('activo')
        sociedad.activo = (activo == 'on')
        
        db.session.commit()
        
        return redirect(url_for('sociedades.lista'))
        
    except Exception as e:
        db.session.rollback()
        return render_template('sociedades_editar.html',
            sociedad=sociedad,
            error=f'Error al actualizar sociedad: {str(e)}',
            nombre=session.get('nombre'),
            rol=session.get('rol'))
