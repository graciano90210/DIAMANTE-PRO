"""
Exportar TODOS los datos de la BD local a JSON
Compatible con el modelo actual
"""
from app import create_app
from app.models import (Usuario, Sociedad, Ruta, Cliente, Prestamo, 
                       Pago, Transaccion, AporteCapital, Activo)
import json
from datetime import datetime

app = create_app()

def serialize_date(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

with app.app_context():
    print("📊 Exportando datos completos...\n")
    
    datos = {
        'usuarios': [],
        'sociedades': [],
        'rutas': [],
        'clientes': [],
        'prestamos': [],
        'pagos': [],
        'transacciones': [],
        'aportes_capital': [],
        'activos': []
    }
    
    # USUARIOS
    for u in Usuario.query.all():
        datos['usuarios'].append({
            'id': u.id,
            'nombre': u.nombre,
            'usuario': u.usuario,
            'password': u.password,
            'rol': u.rol,
            'activo': u.activo,
            'fecha_creacion': serialize_date(u.fecha_creacion)
        })
    print(f"✅ {len(datos['usuarios'])} usuarios")
    
    # SOCIEDADES
    for s in Sociedad.query.all():
        datos['sociedades'].append({
            'id': s.id,
            'nombre': s.nombre,
            'nombre_socio': s.nombre_socio,
            'telefono_socio': s.telefono_socio,
            'porcentaje_socio': s.porcentaje_socio,
            'nombre_socio_2': s.nombre_socio_2,
            'telefono_socio_2': s.telefono_socio_2,
            'porcentaje_socio_2': s.porcentaje_socio_2,
            'nombre_socio_3': s.nombre_socio_3,
            'telefono_socio_3': s.telefono_socio_3,
            'porcentaje_socio_3': s.porcentaje_socio_3,
            'activo': s.activo,
            'notas': s.notas,
            'fecha_creacion': serialize_date(s.fecha_creacion)
        })
    print(f"✅ {len(datos['sociedades'])} sociedades")
    
    # RUTAS
    for r in Ruta.query.all():
        datos['rutas'].append({
            'id': r.id,
            'nombre': r.nombre,
            'cobrador_id': r.cobrador_id,
            'sociedad_id': r.sociedad_id,
            'pais': getattr(r, 'pais', 'Colombia'),
            'moneda': getattr(r, 'moneda', 'COP'),
            'simbolo_moneda': getattr(r, 'simbolo_moneda', '$'),
            'activo': r.activo,
            'descripcion': r.descripcion,
            'fecha_creacion': serialize_date(r.fecha_creacion)
        })
    print(f"✅ {len(datos['rutas'])} rutas")
    
    # CLIENTES
    for c in Cliente.query.all():
        datos['clientes'].append({
            'id': c.id,
            'nombre': c.nombre,
            'documento': c.documento,
            'telefono': c.telefono,
            'whatsapp_codigo_pais': c.whatsapp_codigo_pais,
            'whatsapp_numero': c.whatsapp_numero,
            'documento_negocio': c.documento_negocio,
            'direccion_negocio': c.direccion_negocio,
            'gps_latitud': c.gps_latitud,
            'gps_longitud': c.gps_longitud,
            'es_vip': c.es_vip,
            'fecha_registro': serialize_date(c.fecha_registro)
        })
    print(f"✅ {len(datos['clientes'])} clientes")
    
    # PRÉSTAMOS
    for p in Prestamo.query.all():
        datos['prestamos'].append({
            'id': p.id,
            'cliente_id': p.cliente_id,
            'ruta_id': p.ruta_id,
            'cobrador_id': p.cobrador_id,
            'monto_prestado': float(p.monto_prestado),
            'tasa_interes': float(p.tasa_interes),
            'monto_a_pagar': float(p.monto_a_pagar),
            'saldo_actual': float(p.saldo_actual),
            'valor_cuota': float(p.valor_cuota),
            'moneda': p.moneda,
            'frecuencia': p.frecuencia,
            'numero_cuotas': p.numero_cuotas,
            'cuotas_pagadas': p.cuotas_pagadas,
            'cuotas_atrasadas': p.cuotas_atrasadas,
            'estado': p.estado,
            'fecha_inicio': serialize_date(p.fecha_inicio),
            'fecha_fin_estimada': serialize_date(p.fecha_fin_estimada),
            'fecha_ultimo_pago': serialize_date(p.fecha_ultimo_pago)
        })
    print(f"✅ {len(datos['prestamos'])} préstamos")
    
    # PAGOS
    for pago in Pago.query.all():
        datos['pagos'].append({
            'id': pago.id,
            'prestamo_id': pago.prestamo_id,
            'monto': float(pago.monto),
            'fecha_pago': serialize_date(pago.fecha_pago),
            'cobrador_id': pago.cobrador_id,
            'numero_cuotas_pagadas': pago.numero_cuotas_pagadas,
            'saldo_anterior': float(pago.saldo_anterior),
            'saldo_nuevo': float(pago.saldo_nuevo),
            'tipo_pago': pago.tipo_pago,
            'observaciones': pago.observaciones
        })
    print(f"✅ {len(datos['pagos'])} pagos")
    
    # TRANSACCIONES
    for t in Transaccion.query.all():
        datos['transacciones'].append({
            'id': t.id,
            'naturaleza': t.naturaleza,
            'concepto': t.concepto,
            'descripcion': t.descripcion,
            'monto': float(t.monto),
            'fecha': serialize_date(t.fecha),
            'usuario_origen_id': t.usuario_origen_id,
            'usuario_destino_id': t.usuario_destino_id,
            'prestamo_id': t.prestamo_id,
            'foto_evidencia': t.foto_evidencia
        })
    print(f"✅ {len(datos['transacciones'])} transacciones")
    
    # APORTES CAPITAL
    for a in AporteCapital.query.all():
        datos['aportes_capital'].append({
            'id': a.id,
            'sociedad_id': a.sociedad_id,
            'nombre_aportante': a.nombre_aportante,
            'monto': float(a.monto),
            'moneda': a.moneda,
            'tipo_aporte': a.tipo_aporte,
            'fecha_aporte': serialize_date(a.fecha_aporte),
            'descripcion': a.descripcion,
            'registrado_por_id': a.registrado_por_id
        })
    print(f"✅ {len(datos['aportes_capital'])} aportes de capital")
    
    # ACTIVOS
    for act in Activo.query.all():
        datos['activos'].append({
            'id': act.id,
            'nombre': act.nombre,
            'categoria': act.categoria,
            'valor_compra': float(act.valor_compra),
            'fecha_compra': serialize_date(act.fecha_compra),
            'sociedad_id': act.sociedad_id,
            'ruta_id': act.ruta_id,
            'usuario_responsable_id': act.usuario_responsable_id,
            'marca': act.marca,
            'modelo': act.modelo,
            'placa_serial': act.placa_serial,
            'estado': act.estado,
            'notas': act.notas,
            'registrado_por_id': act.registrado_por_id
        })
    print(f"✅ {len(datos['activos'])} activos")
    
    # Guardar en JSON
    with open('datos_completos.json', 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Datos exportados a: datos_completos.json")
    print(f"📦 Tamaño total: {len(json.dumps(datos))} bytes")
