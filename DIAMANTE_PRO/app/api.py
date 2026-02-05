"""
API REST para la aplicación móvil de cobradores
Endpoints JSON para sincronización con la app
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import Usuario, Cliente, Prestamo, Pago, Ruta, Transaccion, db
from .utils.pagination import paginate_query, paginated_response
from .extensions import limiter
from datetime import datetime, timedelta
import pytz
from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload

# Crear blueprint para la API
api = Blueprint('api', __name__, url_prefix='/api/v1')

# ==================== AUTENTICACIÓN ====================
@api.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Protección contra fuerza bruta: máx 5 intentos/min
def api_login():
    """
    Login para la app móvil
    Body: {"usuario": "username", "password": "password"}
    Returns: {"access_token": "JWT_TOKEN", "usuario": {...}}

    Rate Limit: 5 intentos por minuto por IP
    """
    data = request.get_json()
    
    if not data or not data.get('usuario') or not data.get('password'):
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
    
    usuario = Usuario.query.filter_by(usuario=data['usuario']).first()
    
    # Usar bcrypt para verificar contraseña de forma segura
    if not usuario or not usuario.check_password(data['password']):
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

@api.route('/cobrador/clientes', methods=['POST'])
@jwt_required()
def api_crear_cliente():
    """
    Crear nuevo cliente desde la app móvil
    Headers: Authorization: Bearer TOKEN
    Body: {"nombre": "Juan", "documento": "123", "telefono": "555", "direccion": "Calle 1"}
    Returns: {"id": 1, "nombre": "Juan", ...}
    """
    data = request.get_json()
    
    if not data or not data.get('nombre') or not data.get('documento') or not data.get('telefono'):
        return jsonify({'error': 'Faltan datos obligatorios (nombre, documento, telefono)'}), 400
        
    # Verificar si ya existe
    if Cliente.query.filter_by(documento=data['documento']).first():
        return jsonify({'error': 'Ya existe un cliente con este documento'}), 400
        
    fecha_nac = None
    if data.get('fecha_nacimiento'):
        try:
            # Espera formato YYYY-MM-DD
            fecha_nac = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
        except:
            pass # Ignorar si la fecha es invalida

    nuevo_cliente = Cliente(
        nombre=data['nombre'],
        documento=data['documento'],
        tipo_documento=data.get('tipo_documento', 'CPF'),
        fecha_nacimiento=fecha_nac,
        email=data.get('email'),
        telefono=data['telefono'],
        whatsapp_numero=data.get('whatsapp', data['telefono']), # Por defecto mismo telefono
        
        direccion_negocio=data.get('direccion_negocio', data.get('direccion', '')),
        cep_negocio=data.get('cep_negocio'),
        direccion_casa=data.get('direccion_casa'),
        cep_casa=data.get('cep_casa'),
        
        gps_latitud=data.get('gps_latitud'),
        gps_longitud=data.get('gps_longitud'),
        es_vip=False
    )
    
    try:
        db.session.add(nuevo_cliente)
        db.session.commit()
        return jsonify({
            'id': nuevo_cliente.id,
            'nombre': nuevo_cliente.nombre,
            'mensaje': 'Cliente creado exitosamente'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== PRÉSTAMOS ====================
@api.route('/cobrador/prestamos', methods=['POST'])
@jwt_required()
def api_crear_prestamo():
    """
    Crear nuevo préstamo desde la app móvil
    Headers: Authorization: Bearer TOKEN
    Body: {
        "cliente_id": 1, 
        "monto": 1000, 
        "interes": 20, 
        "cuotas": 24, 
        "frecuencia": "DIARIO",
        "ruta_id": 1
    }
    """
    usuario_id = int(get_jwt_identity())
    data = request.get_json()
    
    required_fields = ['cliente_id', 'monto', 'cuotas', 'frecuencia', 'ruta_id']
    if not all(k in data for k in required_fields):
        return jsonify({'error': f'Faltan campos requeridos: {required_fields}'}), 400
        
    try:
        cliente = Cliente.query.get_or_404(data['cliente_id'])
        ruta = Ruta.query.get_or_404(data['ruta_id'])
        
        # Verificar que la ruta pertenece al cobrador
        if ruta.cobrador_id != usuario_id:
            return jsonify({'error': 'No puedes crear préstamos en una ruta ajena'}), 403
            
        monto = float(data['monto'])
        interes_pct = float(data.get('interes', 20)) / 100.0
        num_cuotas = int(data['cuotas'])
        
        # Cálculos financieros
        total_pagar = monto * (1 + interes_pct)
        valor_cuota = total_pagar / num_cuotas
        
        nuevo_prestamo = Prestamo(
            cliente_id=cliente.id,
            ruta_id=ruta.id,
            cobrador_id=usuario_id,
            monto_prestado=monto,
            monto_a_pagar=total_pagar,
            saldo_actual=total_pagar,
            valor_cuota=valor_cuota,
            moneda=ruta.moneda, # Heredar moneda de la ruta
            frecuencia=data['frecuencia'],
            numero_cuotas=num_cuotas,
            tasa_interes=interes_pct,
            estado='ACTIVO',
            fecha_inicio=datetime.now()
        )
        
        db.session.add(nuevo_prestamo)
        db.session.commit()
        
        return jsonify({
            'id': nuevo_prestamo.id,
            'mensaje': 'Préstamo creado exitosamente',
            'saldo': total_pagar,
            'cuota': valor_cuota
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
    
    # Query base optimizada con eager loading para evitar N+1
    query = Prestamo.query.options(
        joinedload(Prestamo.cliente),
        joinedload(Prestamo.ruta)
    ).filter(
        Prestamo.cobrador_id == usuario_id,
        Prestamo.estado == 'ACTIVO'
    )
    
    # Filtrar por cliente si se especifica
    if cliente_id:
        query = query.filter_by(cliente_id=cliente_id)
    
    # Paginación - soporta ?page=1&per_page=20
    query = query.order_by(Prestamo.fecha_inicio.desc())
    result = paginate_query(query, default_per_page=50)
    
    # Serializar préstamos
    prestamos_data = [{
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
        'dias_atraso': 0,
        'fecha_inicio': prestamo.fecha_inicio.isoformat(),
        'fecha_ultimo_pago': prestamo.fecha_ultimo_pago.isoformat() if prestamo.fecha_ultimo_pago else None,
        'estado': prestamo.estado
    } for prestamo in result['items']]
    
    return jsonify(paginated_response(prestamos_data, result['pagination'])), 200

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
        'fecha': pago.fecha_pago.isoformat(),
        'metodo': pago.metodo_pago
    } for pago in pagos]), 200

# ==================== GASTOS ====================
@api.route('/cobrador/gastos', methods=['POST'])
@jwt_required()
def api_crear_gasto():
    """
    Registrar nuevo gasto
    Headers: Authorization: Bearer TOKEN
    Body: {
        "concepto": "Gasolina", 
        "descripcion": "Tanqueo moto", 
        "monto": 50000, 
        "fecha": "2023-10-27" (opcional, default hoy)
    }
    """
    usuario_id = int(get_jwt_identity())
    data = request.get_json()
    
    required_fields = ['concepto', 'monto']
    if not all(k in data for k in required_fields):
        return jsonify({'error': f'Faltan campos requeridos: {required_fields}'}), 400
        
    try:
        fecha = datetime.now()
        if data.get('fecha'):
            try:
                fecha = datetime.strptime(data['fecha'], '%Y-%m-%d')
            except:
                pass # Usar hoy si falla formato
                
        nuevo_gasto = Transaccion(
            naturaleza='EGRESO',
            # tipo_transaccion='GASTO_OPERATIVO', # Removed: Invalid field in model
            concepto=data['concepto'],
            descripcion=data.get('descripcion', ''),
            monto=float(data['monto']),
            fecha=fecha,
            usuario_origen_id=usuario_id,
            # transaccion_origen='MOVIL' # Removed: Invalid field in model (checked models.py)
        )
        
        db.session.add(nuevo_gasto)
        db.session.commit()
        
        return jsonify({
            'id': nuevo_gasto.id,
            'mensaje': 'Gasto registrado correctamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
@limiter.limit("30 per minute")  # Límite razonable para registros de pago
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

# Nuevo endpoint de estadísticas dashboard (zona horaria Brasil, datos en tiempo real)

@api.route('/dashboard_stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    from sqlalchemy import func
    from datetime import datetime, timedelta
    import pytz
    user_id = get_jwt_identity()
    tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(tz)
    today_start = datetime.combine(now.date(), datetime.min.time()).astimezone(pytz.utc)
    today_end = datetime.combine(now.date(), datetime.max.time()).astimezone(pytz.utc)

    print(f"🔍 DEBUG: Calculando para ID {user_id} | Fecha UTC: {today_start} a {today_end}")

    def filtrar_por_usuario(query, modelo):
        if hasattr(modelo, 'cobrador_id'):
            return query.filter(modelo.cobrador_id == user_id)
        elif hasattr(modelo, 'usuario_id'):
            return query.filter(modelo.usuario_id == user_id)
        else:
            print(f"⚠️ El modelo {modelo.__name__} no tiene cobrador_id ni usuario_id")
            return query.filter(False)

    try:
        # CLIENTES activos
        q_clientes = db.session.query(func.count(Cliente.id)).filter(Cliente.activo == True)
        total_clientes = filtrar_por_usuario(q_clientes, Cliente).scalar() or 0

        # POR COBRAR (suma de saldo_pendiente)
        q_cobrar = db.session.query(func.sum(Cliente.saldo_pendiente)).filter(Cliente.activo == True)
        total_cobrar = filtrar_por_usuario(q_cobrar, Cliente).scalar() or 0

        # RECAUDADO HOY (Pagos)
        q_pagos = db.session.query(func.sum(Pago.monto)).filter(
            Pago.fecha_pago >= today_start,
            Pago.fecha_pago <= today_end
        )
        recaudado_hoy = filtrar_por_usuario(q_pagos, Pago).scalar() or 0

        # GASTOS HOY (Transacciones tipo GASTO)
        q_gastos = db.session.query(func.sum(Transaccion.monto)).filter(
            Transaccion.fecha >= today_start,
            Transaccion.fecha <= today_end,
            (getattr(Transaccion, 'naturaleza', None) == 'EGRESO') | (getattr(Transaccion, 'tipo', None) == 'GASTO')
        )
        gastos_hoy = filtrar_por_usuario(q_gastos, Transaccion).scalar() or 0

        neto_hoy = float(recaudado_hoy) - float(gastos_hoy)

        print(f"✅ ÉXITO: Clientes={total_clientes} | Cobrado={recaudado_hoy} | Gastado={gastos_hoy}")

        return jsonify({
            "total_clientes": total_clientes,
            "total_cobrar": float(total_cobrar),
            "recaudado_hoy": float(recaudado_hoy),
            "gastos_hoy": float(gastos_hoy),
            "neto_hoy": float(neto_hoy)
        }), 200

    except Exception as e:
        print(f"❌ ERROR CRÍTICO (500): {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error calculando estadisticas', 'detalle': str(e)}), 500

# ==================== REGISTRAR PAGO ====================
@api.route('/cobros', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")  # Límite razonable para registros de cobro
def api_registrar_cobro():
    """
    Registrar un pago/abono a un préstamo
    Headers: Authorization: Bearer TOKEN
    Body: {
        "prestamo_id": 1,
        "monto_pagado": 50,
        "observaciones": "Pago parcial",
        "gps_latitud": "...",
        "gps_longitud": "..."
    }
    """
    usuario_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get('prestamo_id') or not data.get('monto_pagado'):
        return jsonify({'error': 'Faltan datos obligatorios (prestamo_id, monto_pagado)'}), 400
        
    try:
        prestamo = Prestamo.query.get_or_404(data['prestamo_id'])
        
        # Validación de derechos
        if prestamo.cobrador_id != usuario_id:
             return jsonify({'error': 'No tienes permiso para cobrar este préstamo'}), 403
             
        monto_pago = float(data['monto_pagado'])
        
        # Actualizar préstamo
        saldo_anterior = prestamo.saldo_actual
        prestamo.saldo_actual -= monto_pago
        
        # Actualizar estado si se pagó completo
        if prestamo.saldo_actual <= 0:
            prestamo.saldo_actual = 0
            prestamo.estado = 'PAGADO'
            prestamo.fecha_ultimo_pago = datetime.now()
        else:
            prestamo.fecha_ultimo_pago = datetime.now()
            
        # Calcular cuotas pagadas (aproximado, solo como referencia estadística)
        # cuotas_canceladas = int(monto_pago / prestamo.valor_cuota)
        # prestamo.cuotas_pagadas += cuotas_canceladas 
        
        # Registrar Pago
        nuevo_pago = Pago(
            prestamo_id=prestamo.id,
            cobrador_id=usuario_id,
            monto=monto_pago,
            # numero_cuotas_pagadas simplificado a 0 por ahora o cálculo simple
            numero_cuotas_pagadas=0, 
            saldo_anterior=saldo_anterior,
            saldo_nuevo=prestamo.saldo_actual,
            fecha_pago=datetime.now(),
            observaciones=data.get('observaciones', ''),
            tipo_pago='ABONO' if monto_pago < prestamo.valor_cuota else 'NORMAL'
        )
        
        db.session.add(nuevo_pago)
        
        # Registrar Transaccion (Entrada de dinero)
        nueva_transaccion = Transaccion(
            naturaleza='INGRESO',
            concepto='COBRO_PRESTAMO',
            descripcion=f"Cobro préstamo #{prestamo.id} - Cliente {prestamo.cliente.nombre}",
            monto=monto_pago,
            usuario_origen_id=usuario_id, # El cobrador recibe el dinero
            prestamo_id=prestamo.id
        )
        db.session.add(nueva_transaccion)
        
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Cobro registrado exitosamente',
            'nuevo_saldo': prestamo.saldo_actual,
            'estado_prestamo': prestamo.estado
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Forzando actualizacion