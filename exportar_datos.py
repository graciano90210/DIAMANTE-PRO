"""
Script para migrar datos de SQLite local a PostgreSQL en Heroku
Exporta usuarios, clientes, préstamos, pagos, rutas y sociedades
"""
import json
from app import create_app
from app.models import Usuario, Cliente, Prestamo, Pago, Ruta, Sociedad, Transaccion, db
from datetime import datetime

app = create_app()

with app.app_context():
    print("📊 Exportando datos de SQLite local...")
    
    # Exportar usuarios
    usuarios = Usuario.query.all()
    usuarios_data = []
    for u in usuarios:
        usuarios_data.append({
            'nombre': u.nombre,
            'usuario': u.usuario,
            'password': u.password,
            'rol': u.rol,
            'activo': u.activo,
            'fecha_creacion': u.fecha_creacion.isoformat() if u.fecha_creacion else None
        })
    
    # Exportar sociedades
    sociedades = Sociedad.query.all()
    sociedades_data = []
    for s in sociedades:
        sociedades_data.append({
            'id': s.id,
            'nombre': s.nombre,
            'nombre_socio': s.nombre_socio,
            'telefono_socio': s.telefono_socio,
            'porcentaje_socio': float(s.porcentaje_socio) if s.porcentaje_socio else 50.0,
            'activo': s.activo,
            'notas': s.notas
        })
    
    # Exportar rutas
    rutas = Ruta.query.all()
    rutas_data = []
    for r in rutas:
        rutas_data.append({
            'id': r.id,
            'nombre': r.nombre,
            'descripcion': r.descripcion,
            'cobrador_id': r.cobrador_id,
            'sociedad_id': r.sociedad_id,
            'activo': r.activo
        })
    
    # Exportar clientes
    clientes = Cliente.query.all()
    clientes_data = []
    for c in clientes:
        clientes_data.append({
            'id': c.id,
            'nombre': c.nombre,
            'documento': c.documento,
            'telefono': c.telefono,
            'codigo_pais_whatsapp': c.codigo_pais_whatsapp,
            'numero_whatsapp': c.numero_whatsapp,
            'direccion_casa': c.direccion_casa,
            'direccion_negocio': c.direccion_negocio,
            'gps_latitud': float(c.gps_latitud) if c.gps_latitud else None,
            'gps_longitud': float(c.gps_longitud) if c.gps_longitud else None,
            'es_vip': c.es_vip,
            'notas': c.notas,
            'fecha_registro': c.fecha_registro.isoformat() if c.fecha_registro else None
        })
    
    # Exportar préstamos
    prestamos = Prestamo.query.all()
    prestamos_data = []
    for p in prestamos:
        prestamos_data.append({
            'id': p.id,
            'cliente_id': p.cliente_id,
            'cobrador_id': p.cobrador_id,
            'ruta_id': p.ruta_id,
            'monto_prestado': float(p.monto_prestado),
            'tasa_interes': float(p.tasa_interes) if p.tasa_interes else None,
            'monto_a_pagar': float(p.monto_a_pagar),
            'saldo_actual': float(p.saldo_actual),
            'valor_cuota': float(p.valor_cuota),
            'moneda': p.moneda,
            'frecuencia': p.frecuencia,
            'numero_cuotas': p.numero_cuotas,
            'cuotas_pagadas': p.cuotas_pagadas,
            'cuotas_atrasadas': p.cuotas_atrasadas,
            'estado': p.estado,
            'fecha_inicio': p.fecha_inicio.isoformat() if p.fecha_inicio else None,
            'fecha_fin_estimada': p.fecha_fin_estimada.isoformat() if p.fecha_fin_estimada else None,
            'fecha_ultimo_pago': p.fecha_ultimo_pago.isoformat() if p.fecha_ultimo_pago else None
        })
    
    # Exportar pagos
    pagos = Pago.query.all()
    pagos_data = []
    for pago in pagos:
        pagos_data.append({
            'prestamo_id': pago.prestamo_id,
            'cobrador_id': pago.cobrador_id,
            'monto': float(pago.monto),
            'numero_cuotas_pagadas': pago.numero_cuotas_pagadas,
            'saldo_anterior': float(pago.saldo_anterior),
            'saldo_nuevo': float(pago.saldo_nuevo),
            'fecha_pago': pago.fecha_pago.isoformat() if pago.fecha_pago else None,
            'observaciones': pago.observaciones,
            'tipo_pago': pago.tipo_pago
        })
    
    # Guardar en archivo JSON
    data = {
        'usuarios': usuarios_data,
        'sociedades': sociedades_data,
        'rutas': rutas_data,
        'clientes': clientes_data,
        'prestamos': prestamos_data,
        'pagos': pagos_data
    }
    
    with open('datos_exportados.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Datos exportados:")
    print(f"   - {len(usuarios_data)} usuarios")
    print(f"   - {len(sociedades_data)} sociedades")
    print(f"   - {len(rutas_data)} rutas")
    print(f"   - {len(clientes_data)} clientes")
    print(f"   - {len(prestamos_data)} préstamos")
    print(f"   - {len(pagos_data)} pagos")
    print(f"\n📁 Archivo creado: datos_exportados.json")
