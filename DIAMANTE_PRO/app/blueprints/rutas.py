"""
Blueprint de Rutas - Diamante Pro
Maneja: CRUD de rutas de cobro
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
from ..models import Ruta, Usuario, Sociedad, Prestamo, db
from sqlalchemy import func

rutas_bp = Blueprint('rutas', __name__, url_prefix='/rutas')


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


@rutas_bp.route('/')
@login_required
@admin_required
def lista():
    """Lista de rutas con estadísticas"""
    rutas = Ruta.query.order_by(Ruta.nombre).all()
    
    stats_rutas = []
    for ruta in rutas:
        num_prestamos = Prestamo.query.filter_by(ruta_id=ruta.id, estado='ACTIVO').count()
        total_cartera = db.session.query(func.sum(Prestamo.saldo_actual)).filter(
            Prestamo.ruta_id == ruta.id,
            Prestamo.estado == 'ACTIVO'
        ).scalar() or 0
        stats_rutas.append({
            'ruta': ruta,
            'num_prestamos': num_prestamos,
            'total_cartera': total_cartera
        })
    
    return render_template('rutas_lista.html',
        stats_rutas=stats_rutas,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@rutas_bp.route('/nueva')
@login_required
@admin_required
def nueva():
    """Formulario para nueva ruta"""
    cobradores = Usuario.query.filter_by(rol='cobrador', activo=True).all()
    sociedades = Sociedad.query.filter_by(activo=True).all()
    
    return render_template('rutas_nueva.html',
        cobradores=cobradores,
        sociedades=sociedades,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@rutas_bp.route('/guardar', methods=['POST'])
@login_required
@admin_required
def guardar():
    """Guardar nueva ruta"""
    try:
        cobrador_id = request.form.get('cobrador_id')
        sociedad_id = request.form.get('sociedad_id')
        pais_data = request.form.get('pais', 'Colombia|COP|$')
        
        # Parsear país, moneda y símbolo
        pais_parts = pais_data.split('|')
        pais = pais_parts[0] if len(pais_parts) > 0 else 'Colombia'
        moneda = pais_parts[1] if len(pais_parts) > 1 else 'COP'
        simbolo = pais_parts[2] if len(pais_parts) > 2 else '$'
        
        nueva_ruta = Ruta(
            nombre=request.form.get('nombre'),
            cobrador_id=int(cobrador_id) if cobrador_id else None,
            sociedad_id=int(sociedad_id) if sociedad_id and sociedad_id != '' else None,
            descripcion=request.form.get('descripcion'),
            pais=pais,
            moneda=moneda,
            simbolo_moneda=simbolo,
            activo=True
        )
        
        db.session.add(nueva_ruta)
        db.session.commit()
        
        return redirect(url_for('rutas.lista'))
        
    except Exception as e:
        db.session.rollback()
        cobradores = Usuario.query.filter_by(rol='cobrador', activo=True).all()
        sociedades = Sociedad.query.filter_by(activo=True).all()
        return render_template('rutas_nueva.html',
            cobradores=cobradores,
            sociedades=sociedades,
            error=f'Error al crear ruta: {str(e)}',
            nombre=session.get('nombre'),
            rol=session.get('rol'))


@rutas_bp.route('/editar/<int:ruta_id>')
@login_required
@admin_required
def editar(ruta_id):
    """Editar ruta existente"""
    ruta = Ruta.query.get_or_404(ruta_id)
    cobradores = Usuario.query.filter_by(rol='cobrador', activo=True).all()
    sociedades = Sociedad.query.filter_by(activo=True).all()
    
    return render_template('rutas_editar.html',
        ruta=ruta,
        cobradores=cobradores,
        sociedades=sociedades,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@rutas_bp.route('/actualizar/<int:ruta_id>', methods=['POST'])
@login_required
@admin_required
def actualizar(ruta_id):
    """Actualizar ruta existente"""
    ruta = Ruta.query.get_or_404(ruta_id)
    
    try:
        ruta.nombre = request.form.get('nombre')
        cobrador_id = request.form.get('cobrador_id')
        ruta.cobrador_id = int(cobrador_id) if cobrador_id else None
        sociedad_id = request.form.get('sociedad_id')
        ruta.sociedad_id = int(sociedad_id) if sociedad_id and sociedad_id != '' else None
        ruta.descripcion = request.form.get('descripcion')
        activo = request.form.get('activo')
        ruta.activo = (activo == 'on')
        
        db.session.commit()
        
        return redirect(url_for('rutas.lista'))
        
    except Exception as e:
        db.session.rollback()
        cobradores = Usuario.query.filter_by(rol='cobrador', activo=True).all()
        sociedades = Sociedad.query.filter_by(activo=True).all()
        return render_template('rutas_editar.html',
            ruta=ruta,
            cobradores=cobradores,
            sociedades=sociedades,
            error=f'Error al actualizar ruta: {str(e)}',
            nombre=session.get('nombre'),
            rol=session.get('rol'))
