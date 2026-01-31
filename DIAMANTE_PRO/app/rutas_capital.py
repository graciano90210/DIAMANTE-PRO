from flask import Blueprint, request, jsonify
from app.models import db, AporteCapital, Sociedad
from datetime import datetime

# Definimos un "Blueprint" para organizar las rutas de finanzas
capital_bp = Blueprint('capital', __name__)

@capital_bp.route('/api/capital/nuevo', methods=['POST'])
def registrar_aporte():
    """
    Ruta para registrar un nuevo aporte de capital de un socio.
    Recibe un JSON con: sociedad_id, monto, nombre_aportante, usuario_id, etc.
    """
    try:
        datos = request.json
        
        # 1. Validaciones básicas (para que no nos metan datos vacíos)
        if not datos.get('sociedad_id') or not datos.get('monto'):
            return jsonify({'error': '¡Oye! Faltan datos obligatorios (sociedad o monto)'}), 400
            
        # 2. Crear el objeto AporteCapital
        nuevo_aporte = AporteCapital(
            sociedad_id=datos['sociedad_id'],
            nombre_aportante=datos['nombre_aportante'],
            monto=float(datos['monto']),
            moneda=datos.get('moneda', 'COP'),
            tipo_aporte=datos.get('tipo_aporte', 'EFECTIVO'),
            descripcion=datos.get('descripcion', ''),
            registrado_por_id=datos['usuario_id'], # El usuario que está logueado haciendo el registro
            fecha_aporte=datetime.utcnow()
        )

        # 3. Guardar en la Base de Datos
        db.session.add(nuevo_aporte)
        db.session.commit()

        return jsonify({
            'mensaje': '¡Aporte registrado con éxito, mi amor! 💎', 
            'id': nuevo_aporte.id,
            'monto': nuevo_aporte.monto
        }), 201

    except Exception as e:
        db.session.rollback() # Si algo falla, deshacemos para no dañar la BD
        print(f"❌ Error al registrar aporte: {e}")
        return jsonify({'error': str(e)}), 500

@capital_bp.route('/api/capital/listar/<int:sociedad_id>', methods=['GET'])
def listar_aportes(sociedad_id):
    """
    Muestra todos los aportes de una sociedad específica
    """
    try:
        aportes = AporteCapital.query.filter_by(sociedad_id=sociedad_id).all()
        lista_aportes = []
        
        total_invertido = 0
        
        for aporte in aportes:
            lista_aportes.append({
                'id': aporte.id,
                'nombre': aporte.nombre_aportante,
                'monto': aporte.monto,
                'fecha': aporte.fecha_aporte.strftime('%Y-%m-%d %H:%M'),
                'tipo': aporte.tipo_aporte
            })
            total_invertido += aporte.monto
            
        return jsonify({
            'sociedad_id': sociedad_id,
            'aportes': lista_aportes,
            'total_invertido': total_invertido
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500