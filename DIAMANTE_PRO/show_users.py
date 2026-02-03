"""Script para verificar y mostrar usuarios"""
from app import create_app
from app.models import Usuario, Ruta, Sociedad

app = create_app()

with app.app_context():
    print("=" * 60)
    print("USUARIOS REGISTRADOS")
    print("=" * 60)
    
    for u in Usuario.query.all():
        print(f"  ID: {u.id}")
        print(f"  Usuario: {u.usuario}")
        print(f"  Nombre: {u.nombre}")
        print(f"  Rol: {u.rol}")
        print(f"  Activo: {u.activo}")
        print(f"  Password: {u.password[:20]}..." if u.password else "  Password: None")
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print("RUTAS REGISTRADAS")
    print("=" * 60)
    
    for r in Ruta.query.all():
        cobrador = r.cobrador.nombre if r.cobrador else "Sin asignar"
        sociedad = r.sociedad.nombre if r.sociedad else "PROPIO"
        print(f"  ID: {r.id} | {r.nombre} | Cobrador: {cobrador} | Sociedad: {sociedad}")
    
    print("\n" + "=" * 60)
    print("SOCIEDADES REGISTRADAS")
    print("=" * 60)
    
    for s in Sociedad.query.all():
        print(f"  ID: {s.id} | {s.nombre} | Activo: {s.activo}")
