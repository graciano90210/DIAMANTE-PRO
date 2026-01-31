from app import create_app, db
from app.models import Ruta

app = create_app()

with app.app_context():
    rutas = Ruta.query.filter_by(activo=True).all()
    
    print(f"\n📋 Rutas activas en la base de datos: {len(rutas)}\n")
    
    for r in rutas:
        cobrador = r.cobrador.nombre if r.cobrador else "Sin cobrador"
        tipo = r.sociedad.nombre if r.sociedad else "PROPIO"
        pais = getattr(r, 'pais', 'No definido')
        moneda = getattr(r, 'moneda', 'COP')
        
        print(f"  • {r.nombre}")
        print(f"    Cobrador: {cobrador}")
        print(f"    Tipo: {tipo}")
        print(f"    País: {pais} ({moneda})")
        print()
