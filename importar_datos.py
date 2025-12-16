"""
Script para importar datos a PostgreSQL en Heroku
Lee el archivo JSON y crea los registros en la base de datos
"""
import json
from app import create_app
from app.models import Usuario, Cliente, Prestamo, Pago, Ruta, Sociedad, db
from datetime import datetime

app = create_app()

def parsear_fecha(fecha_str):
    """Convierte string ISO a datetime"""
    if not fecha_str:
        return None
    return datetime.fromisoformat(fecha_str)

with app.app_context():
    print("📥 Importando datos a PostgreSQL...")
    
    # Leer archivo JSON
    with open('datos_exportados.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Importar usuarios (excepto admin que ya existe)
    print("\n👥 Importando usuarios...")
    for u_data in data['usuarios']:
        if u_data['usuario'] != 'admin':  # No duplicar admin
            usuario = Usuario(
                nombre=u_data['nombre'],
                usuario=u_data['usuario'],
                password=u_data['password'],
                rol=u_data['rol'],
                activo=u_data['activo'],
                fecha_creacion=parsear_fecha(u_data.get('fecha_creacion'))
            )
            db.session.add(usuario)
    db.session.commit()
    print(f"✅ {len(data['usuarios'])} usuarios importados")
    
    # Importar sociedades
    print("\n🤝 Importando sociedades...")
    for s_data in data['sociedades']:
        sociedad = Sociedad(
            id=s_data['id'],
            nombre=s_data['nombre'],
            nombre_socio=s_data['nombre_socio'],
            telefono_socio=s_data.get('telefono_socio'),
            porcentaje_socio=s_data.get('porcentaje_socio', 50.0),
            activo=s_data.get('activo', True),
            notas=s_data.get('notas')
        )
        db.session.add(sociedad)
    db.session.commit()
    print(f"✅ {len(data['sociedades'])} sociedades importadas")
    
    # Importar rutas
    print("\n🗺️ Importando rutas...")
    for r_data in data['rutas']:
        ruta = Ruta(
            id=r_data['id'],
            nombre=r_data['nombre'],
            descripcion=r_data.get('descripcion'),
            cobrador_id=r_data.get('cobrador_id'),
            sociedad_id=r_data.get('sociedad_id'),
            activo=r_data.get('activo', True)
        )
        db.session.add(ruta)
    db.session.commit()
    print(f"✅ {len(data['rutas'])} rutas importadas")
    
    # Importar clientes
    print("\n👤 Importando clientes...")
    for c_data in data['clientes']:
        cliente = Cliente(
            id=c_data['id'],
            nombre=c_data['nombre'],
            documento=c_data.get('documento'),
            telefono=c_data.get('telefono'),
            codigo_pais_whatsapp=c_data.get('codigo_pais_whatsapp', '57'),
            numero_whatsapp=c_data.get('numero_whatsapp'),
            direccion_casa=c_data.get('direccion_casa'),
            direccion_negocio=c_data.get('direccion_negocio'),
            gps_latitud=c_data.get('gps_latitud'),
            gps_longitud=c_data.get('gps_longitud'),
            es_vip=c_data.get('es_vip', False),
            notas=c_data.get('notas'),
            fecha_registro=parsear_fecha(c_data.get('fecha_registro'))
        )
        db.session.add(cliente)
    db.session.commit()
    print(f"✅ {len(data['clientes'])} clientes importados")
    
    # Importar préstamos
    print("\n💰 Importando préstamos...")
    for p_data in data['prestamos']:
        prestamo = Prestamo(
            id=p_data['id'],
            cliente_id=p_data['cliente_id'],
            cobrador_id=p_data['cobrador_id'],
            ruta_id=p_data.get('ruta_id'),
            monto_prestado=p_data['monto_prestado'],
            tasa_interes=p_data.get('tasa_interes'),
            monto_a_pagar=p_data['monto_a_pagar'],
            saldo_actual=p_data['saldo_actual'],
            valor_cuota=p_data['valor_cuota'],
            moneda=p_data.get('moneda', 'COP'),
            frecuencia=p_data.get('frecuencia', 'DIARIO'),
            numero_cuotas=p_data['numero_cuotas'],
            cuotas_pagadas=p_data.get('cuotas_pagadas', 0),
            cuotas_atrasadas=p_data.get('cuotas_atrasadas', 0),
            estado=p_data.get('estado', 'ACTIVO'),
            fecha_inicio=parsear_fecha(p_data.get('fecha_inicio')),
            fecha_fin_estimada=parsear_fecha(p_data.get('fecha_fin_estimada')),
            fecha_ultimo_pago=parsear_fecha(p_data.get('fecha_ultimo_pago'))
        )
        db.session.add(prestamo)
    db.session.commit()
    print(f"✅ {len(data['prestamos'])} préstamos importados")
    
    # Importar pagos
    print("\n💵 Importando pagos...")
    for pago_data in data['pagos']:
        pago = Pago(
            prestamo_id=pago_data['prestamo_id'],
            cobrador_id=pago_data.get('cobrador_id'),
            monto=pago_data['monto'],
            numero_cuotas_pagadas=pago_data.get('numero_cuotas_pagadas', 1),
            saldo_anterior=pago_data['saldo_anterior'],
            saldo_nuevo=pago_data['saldo_nuevo'],
            fecha_pago=parsear_fecha(pago_data.get('fecha_pago')),
            observaciones=pago_data.get('observaciones'),
            tipo_pago=pago_data.get('tipo_pago', 'NORMAL')
        )
        db.session.add(pago)
    db.session.commit()
    print(f"✅ {len(data['pagos'])} pagos importados")
    
    print("\n✅ ¡Importación completada exitosamente!")
