"""
Crear todos los usuarios iniciales en Heroku
"""
from app import create_app
from app.models import db, Usuario

app = create_app()

usuarios_iniciales = [
    {'nombre': 'Administrador Principal', 'usuario': 'admin', 'password': '123', 'rol': 'dueno'},
    {'nombre': 'Luis Cardona', 'usuario': 'Lcardona', 'password': '5240', 'rol': 'gerente'},
    {'nombre': 'Cristian Vampi', 'usuario': 'cvampi', 'password': '1234', 'rol': 'cobrador'},
    {'nombre': 'Santiago', 'usuario': 'santiago', 'password': '1234', 'rol': 'cobrador'},
    {'nombre': 'Tasmania', 'usuario': 'tasmania', 'password': 'tasmania', 'rol': 'cobrador'},
]

with app.app_context():
    print("🔧 Creando usuarios en Heroku...\n")
    
    for user_data in usuarios_iniciales:
        existe = Usuario.query.filter_by(usuario=user_data['usuario']).first()
        
        if not existe:
            nuevo_usuario = Usuario(
                nombre=user_data['nombre'],
                usuario=user_data['usuario'],
                password=user_data['password'],
                rol=user_data['rol'],
                activo=True
            )
            db.session.add(nuevo_usuario)
            print(f"✅ {user_data['nombre']} ({user_data['usuario']}) - {user_data['rol']}")
        else:
            print(f"⚠️  {user_data['usuario']} ya existe")
    
    db.session.commit()
    print("\n🎉 ¡Usuarios creados exitosamente!")
    print("\n📋 Credenciales de acceso:")
    print("   admin / 123 (Dueño)")
    print("   Lcardona / 5240 (Gerente)")
    print("   cvampi / 1234 (Cobrador)")
    print("   santiago / 1234 (Cobrador)")
    print("   tasmania / tasmania (Cobrador)")
