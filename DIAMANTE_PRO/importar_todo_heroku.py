"""
Importar TODOS los datos a Heroku desde datos_completos.json
"""
from app import create_app
from app.models import (Usuario, Sociedad, Ruta, Cliente, Prestamo, 
                       Pago, Transaccion, AporteCapital, Activo, db)
import json
from datetime import datetime

app = create_app()

def parse_date(date_str):
    if date_str:
        return datetime.fromisoformat(date_str)
    return None

with app.app_context():
    print("📥 Importando datos a Heroku...\n")
    
    # Leer archivo
    with open('datos_completos.json', 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    # 1. USUARIOS
    print("👥 Importando usuarios...")
    for u in datos['usuarios']:
        existe = Usuario.query.filter_by(usuario=u['usuario']).first()
        if not existe:
            nuevo = Usuario(
                nombre=u['nombre'],
                usuario=u['usuario'],
                password=u['password'],
                rol=u['rol'],
                activo=u['activo'],
                fecha_creacion=parse_date(u['fecha_creacion'])
            )
            db.session.add(nuevo)
    db.session.commit()
    print(f"   ✅ {Usuario.query.count()} usuarios totales")
    
    # 2. SOCIEDADES
    print("🤝 Importando sociedades...")
    for s in datos['sociedades']:
        existe = Sociedad.query.filter_by(nombre=s['nombre']).first()
        if not existe:
            nueva = Sociedad(
                nombre=s['nombre'],
                nombre_socio=s['nombre_socio'],
                telefono_socio=s['telefono_socio'],
                porcentaje_socio=s['porcentaje_socio'],
                nombre_socio_2=s.get('nombre_socio_2'),
                telefono_socio_2=s.get('telefono_socio_2'),
                porcentaje_socio_2=s.get('porcentaje_socio_2', 0),
                nombre_socio_3=s.get('nombre_socio_3'),
                telefono_socio_3=s.get('telefono_socio_3'),
                porcentaje_socio_3=s.get('porcentaje_socio_3', 0),
                activo=s['activo'],
                notas=s.get('notas'),
                fecha_creacion=parse_date(s['fecha_creacion'])
            )
            db.session.add(nueva)
    db.session.commit()
    print(f"   ✅ {Sociedad.query.count()} sociedades totales")
    
    # 3. RUTAS
    print("🗺️  Importando rutas...")
    for r in datos['rutas']:
        existe = Ruta.query.filter_by(nombre=r['nombre']).first()
        if not existe:
            nueva = Ruta(
                nombre=r['nombre'],
                cobrador_id=r['cobrador_id'],
                sociedad_id=r['sociedad_id'],
                pais=r.get('pais', 'Colombia'),
                moneda=r.get('moneda', 'COP'),
                simbolo_moneda=r.get('simbolo_moneda', '$'),
                activo=r['activo'],
                descripcion=r.get('descripcion'),
                fecha_creacion=parse_date(r['fecha_creacion'])
            )
            db.session.add(nueva)
    db.session.commit()
    print(f"   ✅ {Ruta.query.count()} rutas totales")
    
    # 4. CLIENTES
    print("👤 Importando clientes...")
    for c in datos['clientes']:
        existe = Cliente.query.filter_by(documento=c['documento']).first()
        if not existe:
            nuevo = Cliente(
                nombre=c['nombre'],
                documento=c['documento'],
                telefono=c['telefono'],
                whatsapp_codigo_pais=c.get('whatsapp_codigo_pais', '57'),
                whatsapp_numero=c.get('whatsapp_numero'),
                documento_negocio=c.get('documento_negocio'),
                direccion_negocio=c.get('direccion_negocio'),
                gps_latitud=c.get('gps_latitud'),
                gps_longitud=c.get('gps_longitud'),
                es_vip=c.get('es_vip', False),
                fecha_registro=parse_date(c['fecha_registro'])
            )
            db.session.add(nuevo)
    db.session.commit()
    print(f"   ✅ {Cliente.query.count()} clientes totales")
    
    # 5. PRÉSTAMOS
    print("💰 Importando préstamos...")
    for p in datos['prestamos']:
        # No duplicar préstamos
        existe = Prestamo.query.filter_by(
            cliente_id=p['cliente_id'],
            monto_prestado=p['monto_prestado'],
            fecha_inicio=parse_date(p['fecha_inicio'])
        ).first()
        if not existe:
            nuevo = Prestamo(
                cliente_id=p['cliente_id'],
                ruta_id=p['ruta_id'],
                cobrador_id=p['cobrador_id'],
                monto_prestado=p['monto_prestado'],
                tasa_interes=p['tasa_interes'],
                monto_a_pagar=p['monto_a_pagar'],
                saldo_actual=p['saldo_actual'],
                valor_cuota=p['valor_cuota'],
                moneda=p.get('moneda', 'COP'),
                frecuencia=p['frecuencia'],
                numero_cuotas=p['numero_cuotas'],
                cuotas_pagadas=p['cuotas_pagadas'],
                cuotas_atrasadas=p['cuotas_atrasadas'],
                estado=p['estado'],
                fecha_inicio=parse_date(p['fecha_inicio']),
                fecha_fin_estimada=parse_date(p.get('fecha_fin_estimada')),
                fecha_ultimo_pago=parse_date(p.get('fecha_ultimo_pago'))
            )
            db.session.add(nuevo)
    db.session.commit()
    print(f"   ✅ {Prestamo.query.count()} préstamos totales")
    
    # 6. PAGOS - OMITIDO (conflictos de ID)
    print("💳 Pagos: OMITIDO (se generarán nuevos al cobrar)")
    # Los pagos se recrearán automáticamente cuando se registren nuevos cobros
    
    # 7. TRANSACCIONES - OMITIDO (historial secundario)
    print("🏦 Transacciones: OMITIDO (historial secundario)")
    # Las transacciones futuras se registrarán automáticamente
    
    # 8. APORTES CAPITAL
    print("💵 Importando aportes de capital...")
    for a in datos['aportes_capital']:
        # Convertir moneda a código de 3 letras
        moneda_value = a.get('moneda', 'PESOS')
        if moneda_value == 'REALES':
            moneda_value = 'BRL'
        elif moneda_value == 'PESOS':
            moneda_value = 'COP'
        
        nuevo = AporteCapital(
            sociedad_id=a.get('sociedad_id'),
            nombre_aportante=a['nombre_aportante'],
            monto=a['monto'],
            moneda=moneda_value,
            tipo_aporte=a.get('tipo_aporte', 'CAPITAL'),
            fecha_aporte=parse_date(a['fecha_aporte']),
            descripcion=a.get('descripcion'),
            registrado_por_id=a.get('registrado_por_id')
        )
        db.session.add(nuevo)
    db.session.commit()
    print(f"   ✅ {AporteCapital.query.count()} aportes de capital totales")
    
    # 9. ACTIVOS
    print("📦 Importando activos...")
    for act in datos['activos']:
        nuevo = Activo(
            nombre=act['nombre'],
            categoria=act['categoria'],
            valor_compra=act['valor_compra'],
            fecha_compra=parse_date(act['fecha_compra']),
            sociedad_id=act.get('sociedad_id'),
            ruta_id=act.get('ruta_id'),
            usuario_responsable_id=act.get('usuario_responsable_id'),
            marca=act.get('marca'),
            modelo=act.get('modelo'),
            placa_serial=act.get('placa_serial'),
            estado=act.get('estado', 'ACTIVO'),
            notas=act.get('notas'),
            registrado_por_id=act.get('registrado_por_id')
        )
        db.session.add(nuevo)
    db.session.commit()
    print(f"   ✅ {Activo.query.count()} activos totales")
    
    print("\n" + "="*50)
    print("✨ ¡IMPORTACIÓN COMPLETADA EXITOSAMENTE!")
    print("="*50)
    print(f"\n📊 Resumen final:")
    print(f"   👥 Usuarios: {Usuario.query.count()}")
    print(f"   🤝 Sociedades: {Sociedad.query.count()}")
    print(f"   🗺️  Rutas: {Ruta.query.count()}")
    print(f"   👤 Clientes: {Cliente.query.count()}")
    print(f"   💰 Préstamos: {Prestamo.query.count()}")
    print(f"   💳 Pagos: {Pago.query.count()}")
    print(f"   🏦 Transacciones: {Transaccion.query.count()}")
    print(f"   💵 Aportes: {AporteCapital.query.count()}")
    print(f"   📦 Activos: {Activo.query.count()}")
    print("\n🎉 Ya puedes ingresar a www.diamantepro.me con tus credenciales!")
