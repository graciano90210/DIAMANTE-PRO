from app import create_app
from app.models import db, Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Check if pablo exists
    pablo = Usuario.query.filter_by(usuario='pablo').first()
    if not pablo:
        nuevo_cobrador = Usuario(
            nombre="Pablo Cobrador",
            usuario="pablo",
            password="123",  # Assuming a simple password for testing
            rol="cobrador",
            activo=True
        )
        db.session.add(nuevo_cobrador)
        db.session.commit()
        print("✅ Usuario 'pablo' (cobrador) creado.")
    else:
        print("✅ Usuario 'pablo' ya existe.")
