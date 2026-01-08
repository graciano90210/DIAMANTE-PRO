"""
API REST para la aplicación móvil de cobradores
Endpoints JSON para sincronización con la app
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import Usuario, Cliente, Prestamo, Pago, Ruta, Transaccion, db
from datetime import datetime, timedelta
from sqlalchemy import func

# Crear blueprint para la API
api = Blueprint('api', __name__, url_prefix='/api/v1')

# ==================== AUTENTICACIÓN ====================
@api.route('/login', methods=['POST'])
def api_login():
    """
    Login para la app móvil
    Body: {"usuario": "username", "password": "password"}
    Returns: {"access_token": "JWT_TOKEN", "usuario": {...}}
    """
    data = request.get_json()
    
    if not data or not data.get('usuario') or not data.get('password'):
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
    
    usuario = Usuario.query.filter_by(usuario=data['usuario']).first()
    
    if not usuario or usuario.password != data['password']:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    if not usuario.activo:
        return jsonify({'error': 'Usuario inactivo'}), 401
    
    # Crear token JWT con duración de 30 días
    access_token = create_access_token(
        identity=str(usuario.id),
        expires_delta=timedelta(days=30),
        additional_claims={
            'rol': usuario.rol,
            'nombre': usuario.nombre
        }
    )
    
    return jsonify({
        'access_token': access_token,
        'usuario': {
            'id': usuario.id,
            'nombre': usuario.nombre,
            'usuario': usuario.usuario,
            'rol': usuario.rol
        }
    }), 200

# ==================== RUTAS DEL COBRADOR ====================
@api.route('/cobrador/rutas', methods=['GET'])
@jwt_required()
def api_obtener_rutas_cobrador():
    """
    Obtener las rutas asignadas al cobrador
    Headers: Authorization: Bearer TOKEN
    Returns: [{"id": 1, "nombre": "Ruta Centro", ...}]
    """
    usuario_id = int(get_jwt_identity())
    
    rutas = Ruta.query.filter_by(cobrador_id=usuario_id, activo=True).all()
    
    return jsonify([{
        'id': ruta.id,
        'nombre': ruta.nombre,
        'descripcion': ruta.descripcion,
        'es_sociedad': ruta.sociedad_id is not None,
        'sociedad_nombre': ruta.sociedad.nombre if ruta.sociedad else None
    } for ruta in rutas]), 200

# ==================== CLIENTES ====================
@api.route('/cobrador/clientes', methods=['GET'])
@jwt_required()
def api_obtener_clientes():
    """
    Obtener clientes del cobrador (con préstamos activos)
    Headers: Authorization: Bearer TOKEN
    Returns: [{"id": 1, "nombre": "Cliente", ...}]
    """
    usuario_id = int(get_jwt_identity())
    
    # Obtener clientes con préstamos activos del cobrador
    clientes_ids = db.session.query(Prestamo.cliente_id).filter(
        Prestamo.cobrador_id == usuario_id,
        Prestamo.estado == 'ACTIVO'
    ).distinct().all()
    
    clientes_ids = [c[0] for c in clientes_ids]
    clientes = Cliente.query.filter(Cliente.id.in_(clientes_ids)).all()
    
    return jsonify([{
        'id': cliente.id,
        'nombre': cliente.nombre,
        'documento': cliente.documento,
        'telefono': cliente.telefono,
        'whatsapp': cliente.whatsapp_completo,
        'direccion_negocio': cliente.direccion_negocio,
        'gps_latitud': cliente.gps_latitud,
        'gps_longitud': cliente.gps_longitud,
        'es_vip': cliente.es_vip
    } for cliente in clientes]), 200

# ==================== PRÉSTAMOS ====================
@api.route('/cobrador/prestamos', methods=['GET'])
@jwt_required()
def api_obtener_prestamos():
    """
    Obtener préstamos activos del cobrador
    Headers: Authorization: Bearer TOKEN
    Query params: ?cliente_id=1 (opcional)
    Returns: [{"id": 1, "cliente": {...}, ...}]
    """
    usuario_id = int(get_jwt_identity())
    cliente_id = request.args.get('cliente_id', type=int)
    
    # Query base - préstamos del cobrador
    query = Prestamo.query.filter(
        Prestamo.cobrador_id == usuario_id,
        Prestamo.estado == 'ACTIVO'
    )
    
    # Filtrar por cliente si se especifica
    if cliente_id:
        query = query.filter_by(cliente_id=cliente_id)
    
    prestamos = query.order_by(Prestamo.fecha_inicio.desc()).all()
    
    return jsonify([{
        'id': prestamo.id,
        'cliente': {
            'id': prestamo.cliente.id,
            'nombre': prestamo.cliente.nombre,
            'telefono': prestamo.cliente.telefono,
            'whatsapp': prestamo.cliente.whatsapp_completo
        },
        'monto_prestado': float(prestamo.monto_prestado),
        'monto_a_pagar': float(prestamo.monto_a_pagar),
        'saldo_actual': float(prestamo.saldo_actual),
        'valor_cuota': float(prestamo.valor_cuota),
        'moneda': prestamo.moneda,
        'frecuencia': prestamo.frecuencia,
        'numero_cuotas': prestamo.numero_cuotas,
        'cuotas_pagadas': prestamo.cuotas_pagadas,
        'cuotas_atrasadas': prestamo.cuotas_atrasadas,
        'fecha_inicio': prestamo.fecha_inicio.isoformat(),
        'fecha_ultimo_pago': prestamo.fecha_ultimo_pago.isoformat() if prestamo.fecha_ultimo_pago else None,
        'estado': prestamo.estado
    } for prestamo in prestamos]), 200

# ==================== PAGOS DE UN PRÉSTAMO ====================
@api.route('/cobrador/prestamos/<int:prestamo_id>/pagos', methods=['GET'])
@jwt_required()
def api_obtener_pagos_prestamo(prestamo_id):
    """
    Obtener historial de pagos de un préstamo
    Headers: Authorization: Bearer TOKEN
    Returns: [{"id": 1, "monto": 100, ...}]
    """
    usuario_id = int(get_jwt_identity())
    
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    
    # Verificar permisos (si es cobrador, debe ser SU préstamo o de su ruta)
    if prestamo.cobrador_id != usuario_id:
        return jsonify({'error': 'No tienes permiso para ver este préstamo'}), 403
        
    pagos = Pago.query.filter_by(prestamo_id=prestamo_id).order_by(Pago.fecha_pago.desc()).all()
    
    return jsonify([{
        'id': pago.id,
        'monto': float(pago.monto),
        'fecha_pago': pago.fecha_pago.isoformat(),
        'observaciones': pago.observaciones,
        'saldo_anterior': float(pago.saldo_anterior),
        'saldo_nuevo': float(pago.saldo_nuevo),
        'cuotas_pagadas': pago.numero_cuotas_pagadas
    } for pago in pagos]), 200

# ==================== RUTA DE COBRO DIARIA ====================
@api.route('/cobrador/ruta-cobro', methods=['GET'])
@jwt_required()
def api_ruta_cobro():
    """
    Obtener la lista de cobros del día (clientes que deben pagar hoy)
    Headers: Authorization: Bearer TOKEN
    Returns: [{"prestamo": {...}, "debe_pagar_hoy": true, ...}]
    """
    usuario_id = int(get_jwt_identity())
    
    # Obtener préstamos activos del cobrador
    prestamos_activos = Prestamo.query.filter(
        Prestamo.cobrador_id == usuario_id,
        Prestamo.estado == 'ACTIVO'
    ).all()
    
    # Filtrar los que NO han pagado hoy
    hoy = datetime.now().date()
    ruta_cobro = []
    
    for prestamo in prestamos_activos:
        # Verificar si ya pagó hoy
        pago_hoy = Pago.query.filter(
            Pago.prestamo_id == prestamo.id,
            func.date(Pago.fecha_pago) == hoy
        ).first()
        
        if not pago_hoy and prestamo.frecuencia in ['DIARIO', 'BISEMANAL']:
            ruta_cobro.append({
                'prestamo_id': prestamo.id,
                'cliente': {
                    'id': prestamo.cliente.id,
                    'nombre': prestamo.cliente.nombre,
                    'telefono': prestamo.cliente.telefono,
                    'whatsapp': prestamo.cliente.whatsapp_completo,
                    'direccion': prestamo.cliente.direccion_negocio,
                    'gps_latitud': prestamo.cliente.gps_latitud,
                    'gps_longitud': prestamo.cliente.gps_longitud
                },
                'valor_cuota': float(prestamo.valor_cuota),
                'saldo_actual': float(prestamo.saldo_actual),
                'moneda': prestamo.moneda,
                'cuotas_atrasadas': prestamo.cuotas_atrasadas,
                'estado_mora': 'GRAVE' if prestamo.cuotas_atrasadas > 3 else 'LEVE' if prestamo.cuotas_atrasadas > 0 else 'AL_DIA'
            })
    
    return jsonify({
        'total_cobros': len(ruta_cobro),
        'total_a_cobrar': sum(c['valor_cuota'] for c in ruta_cobro),
        'cobros': ruta_cobro
    }), 200

# ==================== REGISTRAR PAGO ====================
@api.route('/cobrador/registrar-pago', methods=['POST'])
@jwt_required()
def api_registrar_pago():
    """
    Registrar un pago desde la app móvil
    Headers: Authorization: Bearer TOKEN
    Body: {
        "prestamo_id": 1,
        "monto": 120.00,
        "observaciones": "Pago completo"
    }
    Returns: {"pago_id": 1, "saldo_nuevo": 2400, ...}
    """
    usuario_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get('prestamo_id') or not data.get('monto'):
        return jsonify({'error': 'prestamo_id y monto son requeridos'}), 400
    
    try:
        prestamo = Prestamo.query.get_or_404(data['prestamo_id'])
        
        # Verificar que el préstamo pertenece a una ruta del cobrador
        ruta = Ruta.query.get(prestamo.ruta_id)
        if not ruta or ruta.cobrador_id != usuario_id:
            return jsonify({'error': 'No tienes permiso para cobrar este préstamo'}), 403
        
        monto = float(data['monto'])
        observaciones = data.get('observaciones', '')
        
        # Calcular cuotas pagadas
        numero_cuotas_pagadas = int(monto / prestamo.valor_cuota)
        
        # Registrar el pago
        nuevo_pago = Pago(
            prestamo_id=prestamo.id,
            cobrador_id=usuario_id,
            monto=monto,
            numero_cuotas_pagadas=numero_cuotas_pagadas,
            saldo_anterior=prestamo.saldo_actual,
            saldo_nuevo=prestamo.saldo_actual - monto,
            fecha_pago=datetime.now(),
            observaciones=observaciones,
            tipo_pago='NORMAL'
        )
        
        # Actualizar préstamo
        prestamo.saldo_actual -= monto
        prestamo.cuotas_pagadas += numero_cuotas_pagadas
        prestamo.fecha_ultimo_pago = datetime.now()
        
        # Si cuotas atrasadas > 0, restarlas
        if prestamo.cuotas_atrasadas > 0:
            prestamo.cuotas_atrasadas = max(0, prestamo.cuotas_atrasadas - numero_cuotas_pagadas)
        
        # Si saldo llega a 0, marcar como cancelado
        if prestamo.saldo_actual <= 0:
            prestamo.estado = 'CANCELADO'
            prestamo.saldo_actual = 0
        
        db.session.add(nuevo_pago)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'pago_id': nuevo_pago.id,
            'monto_pagado': float(monto),
            'saldo_anterior': float(nuevo_pago.saldo_anterior),
            'saldo_nuevo': float(prestamo.saldo_actual),
            'cuotas_pagadas': numero_cuotas_pagadas,
            'prestamo_liquidado': prestamo.estado == 'CANCELADO',
            'fecha_pago': nuevo_pago.fecha_pago.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== ESTADÍSTICAS ====================
@api.route('/cobrador/estadisticas', methods=['GET'])
@jwt_required()
def api_estadisticas_cobrador():
    """
    Obtener estadísticas del cobrador
    Headers: Authorization: Bearer TOKEN
    Returns: {"total_cartera": 50000, "cobrado_hoy": 1200, ...}
    """
    usuario_id = int(get_jwt_identity())
    
    # Préstamos activos del cobrador (usando cobrador_id directamente)
    prestamos_activos = Prestamo.query.filter_by(
        cobrador_id=usuario_id,
        estado='ACTIVO'
    ).all()
    
    # Total cartera
    total_cartera = sum(float(p.saldo_actual) for p in prestamos_activos) if prestamos_activos else 0
    
    # Capital prestado
    capital_prestado = sum(float(p.monto_prestado) for p in prestamos_activos) if prestamos_activos else 0
    
    # Cobrado hoy
    hoy = datetime.now().date()
    pagos_hoy = Pago.query.join(Prestamo).filter(
        Prestamo.cobrador_id == usuario_id,
        func.date(Pago.fecha_pago) == hoy
    ).all()
    
    cobrado_hoy = sum(float(p.monto) for p in pagos_hoy) if pagos_hoy else 0
    
    # Por cobrar hoy
    por_cobrar_hoy = sum(float(p.valor_cuota) for p in prestamos_activos if p.frecuencia in ['DIARIO', 'BISEMANAL']) if prestamos_activos else 0
    
    return jsonify({
        'total_prestamos': len(prestamos_activos),
        'total_cartera': total_cartera,
        'capital_prestado': capital_prestado,
        'cobrado_hoy': cobrado_hoy,
        'numero_cobros_hoy': len(pagos_hoy),
        'por_cobrar_hoy': por_cobrar_hoy,
        'prestamos_al_dia': sum(1 for p in prestamos_activos if p.cuotas_atrasadas == 0),
        'prestamos_atrasados': sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 0),
        'prestamos_mora_grave': sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 3)
    }), 200
