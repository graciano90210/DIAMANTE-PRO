"""
Script rápido para registrar aportes de capital y activos
Personaliza los datos según tu caso
"""
from app import create_app
from app.models import db, AporteCapital, Activo, Sociedad
from datetime import datetime

app = create_app()

with app.app_context():
    print("\n" + "="*70)
    print("💰 REGISTRO DE APORTES Y ACTIVOS")
    print("="*70 + "\n")
    
    # Mostrar sociedades disponibles
    sociedades = Sociedad.query.filter_by(activo=True).all()
    if not sociedades:
        print("❌ No hay sociedades registradas.")
        print("   Primero crea una sociedad en: /sociedades/nueva")
        exit()
    
    print("📋 Sociedades disponibles:")
    for soc in sociedades:
        print(f"   ID {soc.id}: {soc.nombre}")
    print()
    
    # PERSONALIZA AQUÍ TUS DATOS
    SOCIEDAD_ID = 1  # <<< CAMBIA ESTO al ID de tu sociedad
    USUARIO_ADMIN_ID = 1  # ID del usuario que registra (admin)
    COBRADOR_RESPONSABLE_ID = 4  # ID de santiago
    
    # ============ REGISTRAR APORTES ============
    print("💵 Registrando aportes de capital...")
    
    aportes_data = [
        {"nombre": "Socio 1", "monto": 10000, "moneda": "BRL"},
        {"nombre": "Socio 2", "monto": 10000, "moneda": "BRL"},
        {"nombre": "Socio 3", "monto": 10000, "moneda": "BRL"},
    ]
    
    for aporte_data in aportes_data:
        # Verificar si ya existe
        existe = AporteCapital.query.filter_by(
            sociedad_id=SOCIEDAD_ID,
            nombre_aportante=aporte_data["nombre"],
            monto=aporte_data["monto"]
        ).first()
        
        if not existe:
            aporte = AporteCapital(
                sociedad_id=SOCIEDAD_ID,
                nombre_aportante=aporte_data["nombre"],
                monto=aporte_data["monto"],
                moneda=aporte_data["moneda"],
                tipo_aporte="EFECTIVO",
                descripcion="Aporte inicial de capital",
                registrado_por_id=USUARIO_ADMIN_ID
            )
            db.session.add(aporte)
            print(f"   ✅ Aporte registrado: {aporte_data['nombre']} - {aporte_data['monto']} {aporte_data['moneda']}")
        else:
            print(f"   ⚠️  Aporte ya existe: {aporte_data['nombre']}")
    
    db.session.commit()
    
    # Mostrar total
    total_aportes = db.session.query(db.func.sum(AporteCapital.monto)).filter_by(
        sociedad_id=SOCIEDAD_ID
    ).scalar() or 0
    print(f"\n   💰 TOTAL CAPITAL APORTADO: {total_aportes} BRL")
    
    # ============ REGISTRAR ACTIVO (MOTO) ============
    print("\n🏍️  Registrando activo fijo (moto)...")
    
    # Verificar si ya existe
    moto_existe = Activo.query.filter_by(
        nombre="Moto Honda Wave 110",
        sociedad_id=SOCIEDAD_ID
    ).first()
    
    if not moto_existe:
        moto = Activo(
            nombre="Moto Honda Wave 110",
            categoria="VEHICULO",
            descripcion="Moto para realizar cobros en la ruta",
            valor_compra=10000,
            moneda="BRL",
            sociedad_id=SOCIEDAD_ID,
            usuario_responsable_id=COBRADOR_RESPONSABLE_ID,
            marca="Honda",
            modelo="Wave 110",
            placa_serial="ABC-123",  # <<< CAMBIA ESTO a la placa real
            estado="ACTIVO",
            notas="Comprada con capital de la sociedad",
            registrado_por_id=USUARIO_ADMIN_ID
        )
        db.session.add(moto)
        db.session.commit()
        print("   ✅ Activo registrado: Moto Honda Wave 110 - 10,000 BRL")
    else:
        print("   ⚠️  Activo ya existe: Moto Honda Wave 110")
    
    # ============ RESUMEN FINAL ============
    print("\n" + "="*70)
    print("📊 RESUMEN FINANCIERO")
    print("="*70)
    
    total_activos = db.session.query(db.func.sum(Activo.valor_compra)).filter_by(
        sociedad_id=SOCIEDAD_ID,
        estado='ACTIVO'
    ).scalar() or 0
    
    capital_disponible = total_aportes - total_activos
    
    print(f"\n   💵 Capital Aportado:    {total_aportes:,.2f} BRL")
    print(f"   🏍️  Activos Comprados:   {total_activos:,.2f} BRL")
    print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   💰 Capital Disponible:  {capital_disponible:,.2f} BRL")
    print(f"\n   ✅ Este capital está disponible para dar préstamos\n")
    
    print("="*70 + "\n")
