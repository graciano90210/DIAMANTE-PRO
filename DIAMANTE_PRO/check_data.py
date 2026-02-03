"""Script para verificar datos en la base de datos"""
from app import create_app
from app.models import Sociedad, Cliente, Ruta, Usuario, Prestamo, Pago

app = create_app()

with app.app_context():
    print("=" * 50)
    print("DATOS EN LA BASE DE DATOS LOCAL")
    print("=" * 50)
    
    print(f"\n📊 Usuarios: {Usuario.query.count()}")
    for u in Usuario.query.all():
        print(f"   - {u.nombre} ({u.usuario}) - Rol: {u.rol}")
    
    print(f"\n🏢 Sociedades: {Sociedad.query.count()}")
    for s in Sociedad.query.all():
        print(f"   - {s.nombre}")
    
    print(f"\n🛣️ Rutas: {Ruta.query.count()}")
    for r in Ruta.query.all():
        print(f"   - {r.nombre}")
    
    print(f"\n👥 Clientes: {Cliente.query.count()}")
    for c in Cliente.query.limit(10).all():
        print(f"   - {c.nombre} - {c.telefono}")
    if Cliente.query.count() > 10:
        print(f"   ... y {Cliente.query.count() - 10} más")
    
    print(f"\n💰 Préstamos: {Prestamo.query.count()}")
    print(f"💵 Pagos: {Pago.query.count()}")
    
    print("\n" + "=" * 50)
