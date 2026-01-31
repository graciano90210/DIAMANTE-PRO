from app import create_app, db
from app.models import Prestamo, Usuario

app = create_app()

with app.app_context():
    tasmania = Usuario.query.filter_by(usuario='tasmania').first()
    
    if tasmania:
        prestamos = Prestamo.query.filter_by(cobrador_id=tasmania.id).all()
        print(f"\n📊 Préstamos de Tasmania: {len(prestamos)}\n")
        
        for p in prestamos:
            print(f"✅ Cliente: {p.cliente.nombre}")
            print(f"   💰 Monto: {p.moneda} {p.monto_prestado:,.2f}")
            print(f"   📈 A pagar: {p.moneda} {p.monto_a_pagar:,.2f}")
            print(f"   💳 Cuota: {p.moneda} {p.valor_cuota:,.2f}")
            print(f"   📅 {p.numero_cuotas} cuotas {p.frecuencia}")
            print()
    else:
        print("No se encontró Tasmania")
