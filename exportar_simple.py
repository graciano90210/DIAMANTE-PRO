"""
Script SIMPLE para exportar datos de SQLite
Usa los nombres de columnas exactos que tiene la BD local
"""
import json
from app import create_app, db
from app.models import Usuario, Cliente, Prestamo, Pago, Ruta, Sociedad

app = create_app()

with app.app_context():
    print("📊 Exportando datos...")
    
    datos = {}
    
    # Usuarios
    usuarios = Usuario.query.all()
    datos['usuarios'] = [{
        'nombre': u.nombre,
        'usuario': u.usuario,
        'password': u.password,
        'rol': u.rol,
        'activo': u.activo
    } for u in usuarios]
    
    # Sociedades
    sociedades = Sociedad.query.all()
    datos['sociedades'] = [{
        'nombre': s.nombre,
        'capital': float(s.capital) if hasattr(s, 'capital') else 0
    } for s in sociedades]
    
    # Rutas  
    rutas = Ruta.query.all()
    datos['rutas'] = [{
        'nombre': r.nombre,
        'cobrador_id': r.cobrador_id,
        'sociedad_id': r.sociedad_id
    } for r in rutas]
    
    # Clientes (usando columnas reales)
    clientes = Cliente.query.all()
    datos['clientes'] = [{
        'nombre': c.nombre,
        'documento': c.documento,
        'documento_negocio': c.documento_negocio,
        'telefono': c.telefono,
        'whatsapp_codigo_pais': c.whatsapp_codigo_pais,
        'whatsapp_numero': c.whatsapp_numero,
        'direccion_negocio': c.direccion_negocio,
        'es_vip': c.es_vip
    } for c in clientes]
    
    # Préstamos
    prestamos = Prestamo.query.all()
    datos['prestamos'] = [{
        'cliente_id': p.cliente_id,
        'monto': float(p.monto),
        'tasa_interes': float(p.tasa_interes),
        'plazo': p.plazo,
        'cuota_diaria': float(p.cuota_diaria),
        'total_cuotas': p.total_cuotas,
        'cuotas_pagadas': p.cuotas_pagadas,
        'saldo_pendiente': float(p.saldo_pendiente),
        'estado': p.estado,
        'sociedad_id': p.sociedad_id,
        'cobrador_id': p.cobrador_id,
        'numero_recibo': p.numero_recibo
    } for p in prestamos]
    
    # Pagos
    pagos = Pago.query.all()
    datos['pagos'] = [{
        'prestamo_id': pg.prestamo_id,
        'monto': float(pg.monto),
        'cobrador_id': pg.cobrador_id,
        'metodo_pago': pg.metodo_pago,
        'numero_recibo': pg.numero_recibo
    } for pg in pagos]
    
    # Guardar
    with open('datos_local.json', 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    
    print("✅ Exportado:")
    print(f"  - {len(datos['usuarios'])} usuarios")
    print(f"  - {len(datos['sociedades'])} sociedades")
    print(f"  - {len(datos['rutas'])} rutas")
    print(f"  - {len(datos['clientes'])} clientes")
    print(f"  - {len(datos['prestamos'])} préstamos")
    print(f"  - {len(datos['pagos'])} pagos")
    print("\n📁 Archivo: datos_local.json")
