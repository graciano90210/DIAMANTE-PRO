"""
Blueprint de Clientes - Diamante Pro
Maneja: CRUD de clientes
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from ..models import Cliente, Prestamo, Ruta, db

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')


def to_float(val):
    """Conversión segura a float"""
    try:
        return float(val) if val else None
    except ValueError:
        return None


def to_int(val):
    """Conversión segura a int"""
    try:
        return int(val) if val else None
    except ValueError:
        return None


@clientes_bp.route('/')
def lista():
    """Lista de clientes"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    rol = session.get('rol')
    usuario_id = session.get('usuario_id')
    page = request.args.get('page', 1, type=int)
    
    query = Cliente.query
    
    # Si es cobrador, solo ver sus clientes
    if rol == 'cobrador':
        clientes_ids = db.session.query(Prestamo.cliente_id).filter_by(cobrador_id=usuario_id).distinct()
        query = query.filter(Cliente.id.in_(clientes_ids))
    else:
        # Dueño, gerente y secretaria ven todos o filtrados por ruta
        ruta_seleccionada_id = session.get('ruta_seleccionada_id')
        if ruta_seleccionada_id:
            # Clientes asignados directamente a la ruta O que tienen préstamos en esa ruta
            clientes_con_prestamos = db.session.query(Prestamo.cliente_id).filter_by(ruta_id=ruta_seleccionada_id).distinct()
            query = query.filter(
                db.or_(
                    Cliente.ruta_id == ruta_seleccionada_id,
                    Cliente.id.in_(clientes_con_prestamos)
                )
            )
    
    clientes_paginados = query.order_by(Cliente.fecha_registro.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('clientes_lista.html',
                           clientes=clientes_paginados,
                           nombre=session.get('nombre'),
                           rol=session.get('rol'),
                           mensaje=request.args.get('mensaje'))


@clientes_bp.route('/nuevo')
def nuevo():
    """Formulario de nuevo cliente"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('clientes_nuevo.html',
                           nombre=session.get('nombre'),
                           rol=session.get('rol'))


@clientes_bp.route('/guardar', methods=['POST'])
def guardar():
    """Guardar nuevo cliente"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        documento = request.form.get('documento')
        
        if Cliente.query.filter_by(documento=documento).first():
            return render_template('clientes_nuevo.html',
                                   error='Ya existe un cliente con ese documento',
                                   nombre=session.get('nombre'),
                                   rol=session.get('rol'))
        
        # Validar fecha nacimiento
        fecha_nac = request.form.get('fecha_nacimiento')
        fecha_nacimiento = datetime.strptime(fecha_nac, '%Y-%m-%d').date() if fecha_nac else None
        
        nuevo_cliente = Cliente(
            nombre=request.form.get('nombre'),
            documento=documento,
            fecha_nacimiento=fecha_nacimiento,
            telefono=request.form.get('telefono'),
            whatsapp_codigo_pais=request.form.get('whatsapp_codigo_pais', '57'),
            whatsapp_numero=request.form.get('whatsapp_numero'),
            
            # Scoring personal
            estado_civil=request.form.get('estado_civil'),
            personas_a_cargo=to_int(request.form.get('personas_a_cargo')) or 0,
            
            # Datos Negocio
            documento_fiscal_negocio=request.form.get('documento_fiscal_negocio'),
            tipo_negocio=request.form.get('tipo_negocio'),
            direccion_negocio=request.form.get('direccion_negocio'),
            cep_negocio=request.form.get('cep_negocio'),
            antiguedad_negocio_meses=to_int(request.form.get('antiguedad_negocio_meses')),
            ingresos_diarios_estimados=to_float(request.form.get('ingresos_diarios_estimados')),
            gastos_mensuales_promedio=to_float(request.form.get('gastos_mensuales_promedio')),
            local_propio=bool(request.form.get('local_propio')),
            
            gps_latitud=to_float(request.form.get('gps_latitud')),
            gps_longitud=to_float(request.form.get('gps_longitud')),
            
            # Datos Residencia
            direccion_casa=request.form.get('direccion_casa'),
            cep_casa=request.form.get('cep_casa'),
            tiempo_residencia_meses=to_int(request.form.get('tiempo_residencia_meses')),
            tiene_comprobante_residencia=bool(request.form.get('tiene_comprobante_residencia')),
            comprobante_a_nombre_propio=bool(request.form.get('comprobante_a_nombre_propio')),
            
            es_vip=bool(request.form.get('es_vip'))
        )
        
        # Asignar ruta automáticamente si hay una seleccionada en el filtro
        ruta_seleccionada_id = session.get('ruta_seleccionada_id')
        if ruta_seleccionada_id:
            nuevo_cliente.ruta_id = ruta_seleccionada_id
        
        # Si tiene CNPJ, marcarlo como formalizado
        if nuevo_cliente.documento_fiscal_negocio:
            nuevo_cliente.negocio_formalizado = True
        
        db.session.add(nuevo_cliente)
        db.session.commit()
        
        return redirect(url_for('clientes.lista', mensaje='Cliente registrado exitosamente'))
    
    except Exception as e:
        db.session.rollback()
        return render_template('clientes_nuevo.html',
                               error=f'Error al guardar: {str(e)}',
                               nombre=session.get('nombre'),
                               rol=session.get('rol'))


@clientes_bp.route('/editar/<int:cliente_id>')
def editar(cliente_id):
    """Formulario de edición de cliente"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    cliente = Cliente.query.get_or_404(cliente_id)
    
    return render_template('clientes_editar.html',
                           cliente=cliente,
                           nombre=session.get('nombre'),
                           rol=session.get('rol'))


@clientes_bp.route('/actualizar/<int:cliente_id>', methods=['POST'])
def actualizar(cliente_id):
    """Actualizar datos de cliente"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        
        # Verificar si documento cambió y ya existe
        nuevo_documento = request.form.get('documento')
        if nuevo_documento != cliente.documento:
            if Cliente.query.filter_by(documento=nuevo_documento).first():
                return render_template('clientes_editar.html',
                                       cliente=cliente,
                                       error='Ya existe otro cliente con ese documento',
                                       nombre=session.get('nombre'),
                                       rol=session.get('rol'))
        
        # Procesar fecha nacimiento
        fecha_nac = request.form.get('fecha_nacimiento')
        cliente.fecha_nacimiento = datetime.strptime(fecha_nac, '%Y-%m-%d').date() if fecha_nac else None
        
        # Actualizar datos básicos
        cliente.nombre = request.form.get('nombre')
        cliente.documento = nuevo_documento
        cliente.telefono = request.form.get('telefono')
        cliente.whatsapp_codigo_pais = request.form.get('whatsapp_codigo_pais', '57')
        cliente.whatsapp_numero = request.form.get('whatsapp_numero')
        
        # Scoring personal
        cliente.estado_civil = request.form.get('estado_civil')
        cliente.personas_a_cargo = to_int(request.form.get('personas_a_cargo')) or 0
        
        # Datos Negocio
        cliente.documento_fiscal_negocio = request.form.get('documento_fiscal_negocio')
        cliente.tipo_negocio = request.form.get('tipo_negocio')
        cliente.direccion_negocio = request.form.get('direccion_negocio')
        cliente.cep_negocio = request.form.get('cep_negocio')
        cliente.antiguedad_negocio_meses = to_int(request.form.get('antiguedad_negocio_meses'))
        cliente.ingresos_diarios_estimados = to_float(request.form.get('ingresos_diarios_estimados'))
        cliente.gastos_mensuales_promedio = to_float(request.form.get('gastos_mensuales_promedio'))
        cliente.local_propio = bool(request.form.get('local_propio'))
        
        cliente.gps_latitud = to_float(request.form.get('gps_latitud'))
        cliente.gps_longitud = to_float(request.form.get('gps_longitud'))
        
        # Datos Residencia
        cliente.direccion_casa = request.form.get('direccion_casa')
        cliente.cep_casa = request.form.get('cep_casa')
        cliente.tiempo_residencia_meses = to_int(request.form.get('tiempo_residencia_meses'))
        cliente.tiene_comprobante_residencia = bool(request.form.get('tiene_comprobante_residencia'))
        cliente.comprobante_a_nombre_propio = bool(request.form.get('comprobante_a_nombre_propio'))
        
        cliente.es_vip = bool(request.form.get('es_vip'))
        
        # Actualización automática de estado formalizado
        if cliente.documento_fiscal_negocio and not cliente.negocio_formalizado:
            cliente.negocio_formalizado = True
        
        db.session.commit()
        
        return redirect(url_for('clientes.lista', mensaje='Cliente actualizado exitosamente'))
    
    except Exception as e:
        db.session.rollback()
        return render_template('clientes_editar.html',
                               cliente=cliente,
                               error=f'Error al actualizar: {str(e)}',
                               nombre=session.get('nombre'),
                               rol=session.get('rol'))
