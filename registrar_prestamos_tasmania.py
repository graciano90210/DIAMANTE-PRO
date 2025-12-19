from app import create_app, db
from app.models import Cliente, Prestamo, Usuario, Ruta
from datetime import datetime
import random

app = create_app()

with app.app_context():
    # Buscar usuario Tasmania (cobrador)
    tasmania = Usuario.query.filter_by(usuario='tasmania').first()
    
    if not tasmania:
        print("❌ Error: No se encontró el usuario 'tasmania'")
        exit()
    
    # Buscar la ruta
    ruta = Ruta.query.filter_by(cobrador_id=tasmania.id).first()
    
    if not ruta:
        print("❌ Error: Tasmania no tiene ruta asignada")
        exit()
    
    print(f"✅ Usuario: {tasmania.nombre} (ID: {tasmania.id})")
    print(f"✅ Ruta: {ruta.nombre} (ID: {ruta.id})")
    
    # Buscar los 3 clientes recién creados
    clientes = Cliente.query.filter(
        Cliente.documento.in_(['43218765', '71234890', '39876543'])
    ).all()
    
    if len(clientes) != 3:
        print(f"❌ Error: Solo se encontraron {len(clientes)} clientes de 3 esperados")
        exit()
    
    print(f"\n📝 Registrando préstamos en REALES...\n")
    
    # Datos de préstamos (montos entre 1000 y 5000 reales)
    prestamos_data = [
        {'monto': 2500, 'frecuencia': 'DIARIO', 'cuotas': 30},
        {'monto': 4000, 'frecuencia': 'DIARIO', 'cuotas': 40},
        {'monto': 1500, 'frecuencia': 'BISEMANAL', 'cuotas': 15}
    ]
    
    for i, cliente in enumerate(clientes):
        data = prestamos_data[i]
        monto = data['monto']
        frecuencia = data['frecuencia']
        num_cuotas = data['cuotas']
        
        # Calcular tasa según si es VIP
        tasa_interes = 15.0 if cliente.es_vip else 20.0
        
        # Calcular monto a pagar (monto + interés)
        monto_a_pagar = monto * (1 + tasa_interes/100)
        
        # Calcular valor cuota
        valor_cuota = monto_a_pagar / num_cuotas
        
        # Crear préstamo
        nuevo_prestamo = Prestamo(
            cliente_id=cliente.id,
            cobrador_id=tasmania.id,
            ruta_id=ruta.id,
            monto_prestado=monto,
            tasa_interes=tasa_interes,
            monto_a_pagar=monto_a_pagar,
            numero_cuotas=num_cuotas,
            frecuencia=frecuencia,
            valor_cuota=valor_cuota,
            saldo_actual=monto_a_pagar,
            estado='ACTIVO',
            fecha_inicio=datetime.now(),
            moneda='BRL'  # IMPORTANTE: Préstamos en reales
        )
        
        db.session.add(nuevo_prestamo)
        
        vip_badge = "⭐ VIP" if cliente.es_vip else ""
        print(f"✅ {cliente.nombre} {vip_badge}")
        print(f"   💰 Monto: R$ {monto:,.2f}")
        print(f"   📊 Tasa: {tasa_interes}%")
        print(f"   💵 Total: R$ {monto_a_pagar:,.2f}")
        print(f"   📅 {num_cuotas} cuotas {frecuencia.lower()}")
        print(f"   💳 Cuota: R$ {valor_cuota:,.2f}")
        print()
    
    try:
        db.session.commit()
        print("💾 ¡Préstamos registrados exitosamente!")
        
        # Calcular totales reales
        prestamos_tasmania = Prestamo.query.filter_by(cobrador_id=tasmania.id, estado='ACTIVO').all()
        total_prestado = sum([p.monto_prestado for p in prestamos_tasmania])
        total_cobrar = sum([p.monto_a_pagar for p in prestamos_tasmania])
        
        print(f"\n📊 Resumen:")
        print(f"   💰 Capital entregado: R$ {total_prestado:,.2f}")
        print(f"   📈 Total a cobrar: R$ {total_cobrar:,.2f}")
        print(f"   🎯 Préstamos activos de Tasmania: {len(prestamos_tasmania)}")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al guardar: {str(e)}")
