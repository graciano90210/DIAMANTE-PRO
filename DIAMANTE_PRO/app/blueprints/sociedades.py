"""
Blueprint de Sociedades - Diamante Pro
Maneja: CRUD de sociedades/socios con modelo Many-to-Many
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from ..models import Sociedad, Ruta, Socio, db
from ..services import SociedadService

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
    """Formulario para nueva sociedad - Versión mejorada con socios dinámicos"""
    return render_template('sociedades_nueva_v2.html',
        nombre=session.get('nombre'),
        rol=session.get('rol'),
        fecha_hoy=datetime.now().strftime('%Y-%m-%d'))


@sociedades_bp.route('/guardar', methods=['POST'])
@login_required
@admin_required
def guardar():
    """Guardar nueva sociedad con múltiples socios"""
    try:
        # Obtener datos del formulario
        nombre_sociedad = request.form.get('nombre')
        notas = request.form.get('notas')
        porcentaje_dueno = float(request.form.get('porcentaje_dueno', 100))
        
        # Obtener arrays de socios
        nombres = request.form.getlist('socio_nombre[]')
        documentos = request.form.getlist('socio_documento[]')
        porcentajes = request.form.getlist('socio_porcentaje[]')
        telefonos = request.form.getlist('socio_telefono[]')
        emails = request.form.getlist('socio_email[]')
        tipos = request.form.getlist('socio_tipo[]')
        montos = request.form.getlist('socio_monto[]')
        bancos = request.form.getlist('socio_banco[]')
        
        # Validar porcentajes
        total_socios = sum(float(p) for p in porcentajes if p)
        if total_socios > 100:
            return render_template('sociedades_nueva_v2.html',
                error='La suma de los porcentajes no puede superar el 100%',
                nombre=session.get('nombre'),
                rol=session.get('rol'),
                fecha_hoy=datetime.now().strftime('%Y-%m-%d'))
        
        # Crear sociedad
        nueva_sociedad = Sociedad(
            nombre=nombre_sociedad,
            porcentaje_dueno=porcentaje_dueno,
            notas=notas,
            activo=True
        )
        db.session.add(nueva_sociedad)
        db.session.flush()  # Para obtener el ID
        
        # Crear socios
        for i, nombre_socio in enumerate(nombres):
            if nombre_socio:  # Solo si hay nombre
                socio = Socio(
                    sociedad_id=nueva_sociedad.id,
                    nombre=nombre_socio,
                    documento=documentos[i] if i < len(documentos) else None,
                    telefono=telefonos[i] if i < len(telefonos) else None,
                    email=emails[i] if i < len(emails) else None,
                    porcentaje=float(porcentajes[i]) if i < len(porcentajes) and porcentajes[i] else 0,
                    monto_aportado=float(montos[i]) if i < len(montos) and montos[i] else 0,
                    tipo_socio=tipos[i] if i < len(tipos) else 'INVERSIONISTA',
                    banco=bancos[i] if i < len(bancos) else None,
                    activo=True
                )
                db.session.add(socio)
        
        db.session.commit()
        return redirect(url_for('sociedades.lista'))
        
    except Exception as e:
        db.session.rollback()
        return render_template('sociedades_nueva_v2.html',
            error=f'Error al crear sociedad: {str(e)}',
            nombre=session.get('nombre'),
            rol=session.get('rol'),
            fecha_hoy=datetime.now().strftime('%Y-%m-%d'))


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


# ==================== RUTAS PARA GESTIÓN DE SOCIOS ====================

@sociedades_bp.route('/<int:sociedad_id>/socios')
@login_required
@admin_required
def ver_socios(sociedad_id):
    """Ver lista de socios de una sociedad"""
    sociedad = Sociedad.query.get_or_404(sociedad_id)
    socios = Socio.query.filter_by(sociedad_id=sociedad_id, activo=True).order_by(Socio.porcentaje.desc()).all()
    
    return render_template('sociedades_socios.html',
        sociedad=sociedad,
        socios=socios,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@sociedades_bp.route('/<int:sociedad_id>/socios/agregar', methods=['POST'])
@login_required
@admin_required
def agregar_socio(sociedad_id):
    """Agregar un nuevo socio a una sociedad existente"""
    sociedad = Sociedad.query.get_or_404(sociedad_id)
    
    try:
        datos_socio = {
            'nombre': request.form.get('nombre'),
            'documento': request.form.get('documento'),
            'telefono': request.form.get('telefono'),
            'email': request.form.get('email'),
            'porcentaje': float(request.form.get('porcentaje', 0)),
            'monto_aportado': float(request.form.get('monto_aportado', 0)),
            'tipo_socio': request.form.get('tipo_socio', 'INVERSIONISTA'),
            'banco': request.form.get('banco')
        }
        
        resultado = SociedadService.agregar_socio(sociedad_id, datos_socio)
        
        if resultado.get('error'):
            return jsonify({'error': resultado['error']}), 400
        
        return redirect(url_for('sociedades.ver_socios', sociedad_id=sociedad_id))
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@sociedades_bp.route('/socios/<int:socio_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_socio(socio_id):
    """Desactivar un socio (soft delete)"""
    socio = Socio.query.get_or_404(socio_id)
    sociedad_id = socio.sociedad_id
    
    try:
        resultado = SociedadService.eliminar_socio(socio_id)
        
        if resultado.get('error'):
            return jsonify({'error': resultado['error']}), 400
        
        return redirect(url_for('sociedades.ver_socios', sociedad_id=sociedad_id))
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@sociedades_bp.route('/socios/<int:socio_id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_socio(socio_id):
    """Editar datos de un socio"""
    socio = Socio.query.get_or_404(socio_id)
    
    try:
        socio.nombre = request.form.get('nombre', socio.nombre)
        socio.documento = request.form.get('documento', socio.documento)
        socio.telefono = request.form.get('telefono', socio.telefono)
        socio.email = request.form.get('email', socio.email)
        socio.porcentaje = float(request.form.get('porcentaje', socio.porcentaje))
        socio.monto_aportado = float(request.form.get('monto_aportado', socio.monto_aportado))
        socio.tipo_socio = request.form.get('tipo_socio', socio.tipo_socio)
        socio.banco = request.form.get('banco', socio.banco)
        
        db.session.commit()
        
        return redirect(url_for('sociedades.ver_socios', sociedad_id=socio.sociedad_id))
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@sociedades_bp.route('/<int:sociedad_id>/distribucion')
@login_required
@admin_required
def calcular_distribucion(sociedad_id):
    """Calcular distribución de ganancias para una sociedad"""
    ganancia_total = float(request.args.get('ganancia', 0))
    
    try:
        distribucion = SociedadService.calcular_distribucion_ganancias(sociedad_id, ganancia_total)
        
        if distribucion.get('error'):
            return jsonify({'error': distribucion['error']}), 400
        
        return jsonify(distribucion)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sociedades_bp.route('/<int:sociedad_id>/resumen')
@login_required
@admin_required
def resumen_sociedad(sociedad_id):
    """Obtener resumen completo de una sociedad"""
    try:
        resumen = SociedadService.get_resumen_sociedad(sociedad_id)
        
        if resumen.get('error'):
            return jsonify({'error': resumen['error']}), 400
        
        return jsonify(resumen)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
