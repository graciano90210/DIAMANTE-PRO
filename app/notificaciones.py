"""
API endpoints para notificaciones
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.twilio_service import twilio_service
from app.models import db, Cliente, Prestamo, User
from datetime import datetime, timedelta

notificaciones_bp = Blueprint('notificaciones', __name__, url_prefix='/api/v1/notificaciones')

@notificaciones_bp.route('/test-sms', methods=['POST'])
@jwt_required()
def test_sms():
    """Enviar SMS de prueba"""
    data = request.get_json()
    telefono = data.get('telefono')
    mensaje = data.get('mensaje', '✅ Mensaje de prueba desde DIAMANTE PRO')
    
    if not telefono:
        return jsonify({'error': 'Teléfono requerido'}), 400
    
    resultado = twilio_service.enviar_sms(telefono, mensaje)
    
    return jsonify({
        'success': resultado,
        'mensaje': 'SMS enviado' if resultado else 'Error al enviar SMS'
    })

@notificaciones_bp.route('/test-whatsapp', methods=['POST'])
@jwt_required()
def test_whatsapp():
    """Enviar WhatsApp de prueba"""
    data = request.get_json()
    telefono = data.get('telefono')
    mensaje = data.get('mensaje', '✅ Mensaje de prueba desde DIAMANTE PRO')
    
    if not telefono:
        return jsonify({'error': 'Teléfono requerido'}), 400
    
    resultado = twilio_service.enviar_whatsapp(telefono, mensaje)
    
    return jsonify({
        'success': resultado,
        'mensaje': 'WhatsApp enviado' if resultado else 'Error al enviar WhatsApp'
    })

@notificaciones_bp.route('/recordatorio-pago/<int:prestamo_id>', methods=['POST'])
@jwt_required()
def enviar_recordatorio_pago(prestamo_id):
    """Enviar recordatorio de pago a un cliente específico"""
    prestamo = Prestamo.query.get(prestamo_id)
    if not prestamo:
        return jsonify({'error': 'Préstamo no encontrado'}), 404
    
    cliente = Cliente.query.get(prestamo.cliente_id)
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    
    # Preparar mensaje
    mensaje = twilio_service.recordatorio_pago(
        cliente_nombre=cliente.nombre,
        monto=prestamo.valor_cuota,
        fecha_vencimiento='Próximamente'  # Puedes calcular la fecha real
    )
    
    # Enviar por el canal preferido
    canal = request.get_json().get('canal', 'sms')  # sms o whatsapp
    
    if canal == 'whatsapp' and cliente.whatsapp:
        resultado = twilio_service.enviar_whatsapp(cliente.whatsapp, mensaje)
    else:
        resultado = twilio_service.enviar_sms(cliente.telefono, mensaje)
    
    return jsonify({
        'success': resultado,
        'cliente': cliente.nombre,
        'canal': canal
    })

@notificaciones_bp.route('/cuotas-vencidas', methods=['POST'])
@jwt_required()
def notificar_cuotas_vencidas():
    """Enviar notificaciones masivas a clientes con cuotas vencidas"""
    
    # Buscar préstamos con mora
    prestamos_mora = Prestamo.query.filter(
        Prestamo.cuotas_atrasadas > 0,
        Prestamo.estado == 'ACTIVO'
    ).all()
    
    contactos = []
    for prestamo in prestamos_mora:
        cliente = Cliente.query.get(prestamo.cliente_id)
        if cliente:
            mensaje = twilio_service.cuota_vencida(
                cliente_nombre=cliente.nombre,
                monto=prestamo.valor_cuota,
                dias_mora=prestamo.dias_atraso
            )
            
            contactos.append({
                'telefono': cliente.whatsapp or cliente.telefono,
                'mensaje': mensaje
            })
    
    # Enviar masivo
    resultados = twilio_service.enviar_masivo_sms(contactos)
    
    return jsonify({
        'total_enviados': resultados['exitosos'],
        'total_fallidos': resultados['fallidos'],
        'clientes_notificados': len(contactos),
        'errores': resultados['errores']
    })

@notificaciones_bp.route('/confirmar-pago', methods=['POST'])
@jwt_required()
def confirmar_pago():
    """Enviar confirmación de pago recibido"""
    data = request.get_json()
    prestamo_id = data.get('prestamo_id')
    monto_pagado = data.get('monto')
    
    if not prestamo_id or not monto_pagado:
        return jsonify({'error': 'Datos incompletos'}), 400
    
    prestamo = Prestamo.query.get(prestamo_id)
    if not prestamo:
        return jsonify({'error': 'Préstamo no encontrado'}), 404
    
    cliente = Cliente.query.get(prestamo.cliente_id)
    
    mensaje = twilio_service.confirmacion_pago(
        cliente_nombre=cliente.nombre,
        monto=monto_pagado,
        saldo_restante=prestamo.saldo_actual
    )
    
    # Enviar por WhatsApp si está disponible
    if cliente.whatsapp:
        resultado = twilio_service.enviar_whatsapp(cliente.whatsapp, mensaje)
    else:
        resultado = twilio_service.enviar_sms(cliente.telefono, mensaje)
    
    return jsonify({
        'success': resultado,
        'mensaje': 'Confirmación enviada' if resultado else 'Error al enviar confirmación'
    })

@notificaciones_bp.route('/prestamo-aprobado/<int:prestamo_id>', methods=['POST'])
@jwt_required()
def notificar_prestamo_aprobado(prestamo_id):
    """Notificar aprobación de préstamo"""
    prestamo = Prestamo.query.get(prestamo_id)
    if not prestamo:
        return jsonify({'error': 'Préstamo no encontrado'}), 404
    
    cliente = Cliente.query.get(prestamo.cliente_id)
    
    mensaje = twilio_service.prestamo_aprobado(
        cliente_nombre=cliente.nombre,
        monto=prestamo.monto_prestado,
        cuotas=prestamo.numero_cuotas,
        valor_cuota=prestamo.valor_cuota
    )
    
    resultado = twilio_service.enviar_whatsapp(cliente.whatsapp, mensaje) if cliente.whatsapp else twilio_service.enviar_sms(cliente.telefono, mensaje)
    
    return jsonify({'success': resultado})

@notificaciones_bp.route('/estado', methods=['GET'])
@jwt_required()
def estado_twilio():
    """Verificar estado de Twilio"""
    return jsonify({
        'habilitado': twilio_service.enabled,
        'account_sid': twilio_service.account_sid[:10] + '...' if twilio_service.account_sid else None,
        'phone_number': twilio_service.phone_number,
        'whatsapp_number': twilio_service.whatsapp_number
    })
