"""
Script para importar datos a PostgreSQL en Heroku
Lee datos_completos.json y los importa
"""
import json
import os
from app import create_app, db
from app.models import Usuario, Cliente, Prestamo, Pago, Ruta, Sociedad
from datetime import datetime
from werkzeug.security import generate_password_hash

def parse_date(date_str):
    """Convierte string a datetime"""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        return datetime.now()

app = create_app()

with app.app_context():
    print("📥 Importando datos a PostgreSQL...")
    
    # Cargar JSON
    with open('datos_completos.json', 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    # 1. Usuarios (actualizar existentes o crear nuevos)
    print("\n👤 Importando usuarios...")
    for u_data in datos['usuarios']:
        usuario = Usuario.query.filter_by(usuario=u_data['usuario']).first()
        if not usuario:
            usuario = Usuario(
                nombre=u_data['nombre'],
                usuario=u_data['usuario'],
                password=u_data['password'],  # Ya está hasheado
                rol=u_data['rol'],
                activo=u_data.get('activo', True)
            )
            db.session.add(usuario)
    db.session.commit()
    print(f"  ✅ {len(datos['usuarios'])} usuarios")
    
    # 2. Sociedades
    print("\n🏢 Importando sociedades...")
    for s_data in datos['sociedades']:
        sociedad = Sociedad(
            nombre=s_data['nombre'],
            capital=s_data.get('capital', 0)
        )
        db.session.add(sociedad)
    if datos['sociedades']:
        db.session.commit()
        print(f"  ✅ {len(datos['sociedades'])} sociedades")
    else:
        print("  ℹ️  No hay sociedades para importar")
    
    # 3. Rutas
    print("\n🚗 Importando rutas...")
    id_mapping_rutas = {}
    for r_data in datos['rutas']:
        ruta = Ruta(
            nombre=r_data['nombre'],
            cobrador_id=r_data.get('cobrador_id'),
            sociedad_id=r_data.get('sociedad_id')
        )
        db.session.add(ruta)
        db.session.flush()
        id_mapping_rutas[r_data['id']] = ruta.id
    db.session.commit()
    print(f"  ✅ {len(datos['rutas'])} rutas")
    
    # 4. Clientes
    print("\n👥 Importando clientes...")
    id_mapping_clientes = {}
    for c_data in datos['clientes']:
        cliente = Cliente(
            nombre=c_data['nombre'],
            documento=c_data.get('documento'),
            documento_negocio=c_data.get('documento_negocio'),
            telefono=c_data.get('telefono'),
            whatsapp_codigo_pais=c_data.get('whatsapp_codigo_pais'),
            whatsapp_numero=c_data.get('whatsapp_numero'),
            direccion_negocio=c_data.get('direccion_negocio'),
            es_vip=c_data.get('es_vip', False)
        )
        db.session.add(cliente)
        db.session.flush()
        id_mapping_clientes[c_data['id']] = cliente.id
    db.session.commit()
    print(f"  ✅ {len(datos['clientes'])} clientes")
    
    # 5. Préstamos
    print("\n💰 Importando préstamos...")
    id_mapping_prestamos = {}
    for p_data in datos['prestamos']:
        # Mapear cliente_id
        cliente_id_nuevo = id_mapping_clientes.get(p_data.get('cliente_id'))
        ruta_id_nuevo = id_mapping_rutas.get(p_data.get('ruta_id'))
        
        prestamo = Prestamo(
            cliente_id=cliente_id_nuevo,
            ruta_id=ruta_id_nuevo,
            cobrador_id=p_data.get('cobrador_id'),
            monto_prestado=p_data.get('monto_prestado', 0),
            tasa_interes=p_data.get('tasa_interes', 0),
            monto_a_pagar=p_data.get('monto_a_pagar', 0),
            saldo_actual=p_data.get('saldo_actual', 0),
            valor_cuota=p_data.get('valor_cuota', 0),
            moneda=p_data.get('moneda', 'COP'),
            frecuencia=p_data.get('frecuencia', 'diaria'),
            numero_cuotas=p_data.get('numero_cuotas', 0),
            cuotas_pagadas=p_data.get('cuotas_pagadas', 0),
            cuotas_atrasadas=p_data.get('cuotas_atrasadas', 0),
            estado=p_data.get('estado', 'activo'),
            fecha_inicio=parse_date(p_data.get('fecha_inicio')),
            fecha_fin_estimada=parse_date(p_data.get('fecha_fin_estimada')),
            fecha_ultimo_pago=parse_date(p_data.get('fecha_ultimo_pago'))
        )
        db.session.add(prestamo)
        db.session.flush()
        id_mapping_prestamos[p_data['id']] = prestamo.id
    db.session.commit()
    print(f"  ✅ {len(datos['prestamos'])} préstamos")
    
    # 6. Pagos
    print("\n💵 Importando pagos...")
    for pg_data in datos['pagos']:
        # Mapear prestamo_id
        prestamo_id_nuevo = id_mapping_prestamos.get(pg_data.get('prestamo_id'))
        
        if prestamo_id_nuevo:
            pago = Pago(
                prestamo_id=prestamo_id_nuevo,
                fecha_pago=parse_date(pg_data.get('fecha_pago')),
                monto=pg_data.get('monto', 0),
                cobrador_id=pg_data.get('cobrador_id'),
                metodo_pago=pg_data.get('metodo_pago', 'efectivo'),
                numero_recibo=pg_data.get('numero_recibo')
            )
            db.session.add(pago)
    db.session.commit()
    print(f"  ✅ {len(datos['pagos'])} pagos")
    
    print("\n" + "="*50)
    print("✨ IMPORTACIÓN COMPLETADA")
    print("="*50)
