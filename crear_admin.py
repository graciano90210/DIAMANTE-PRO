from app import create_app
from app.models import db, Usuario

app = create_app()

with app.app_context():
    # Verificamos si ya existe
    if not Usuario.query.filter_by(usuario='admin').first():
        nuevo_jefe = Usuario(
            nombre="Juan Gerente",
            usuario="admin",
            password="123",  # Contraseña temporal
            rol="dueno"
        )
        db.session.add(nuevo_jefe)
        db.session.commit()
        print("✅ ¡Usuario DUEÑO creado con éxito!")
    else:
        print("⚠️ El usuario ya existe.")