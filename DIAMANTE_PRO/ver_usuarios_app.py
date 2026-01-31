from app import create_app, db
from app.models import Usuario, Ruta

app = create_app()

with app.app_context():
    print("\n=== USUARIOS DISPONIBLES ===\n")
    usuarios = Usuario.query.all()
    
    for u in usuarios:
        print(f"👤 Usuario: {u.usuario}")
        print(f"   Contraseña: {u.password}")
        print(f"   Rol: {u.rol}")
        print(f"   Nombre: {u.nombre}")
        
        # Ver si tiene rutas asignadas
        if u.rol == 'cobrador':
            rutas = Ruta.query.filter_by(cobrador_id=u.id).all()
            if rutas:
                print(f"   Rutas asignadas: {len(rutas)}")
                for r in rutas:
                    print(f"      - {r.nombre}")
            else:
                print(f"   ⚠️ No tiene rutas asignadas")
        print()
