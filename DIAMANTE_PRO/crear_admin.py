from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    username = 'admin_diamante'
    password = 'Diamante2026!'
    # El rol con todos los permisos debe ser 'dueno' según el sistema
    rol = 'dueno'

    # Verificar si ya existe
    admin = Usuario.query.filter_by(usuario=username).first()
    if admin:
        admin.rol = rol
        admin.password = generate_password_hash(password)
        admin.activo = True
        db.session.commit()
        print('El usuario administrador fue actualizado y ahora tiene todos los permisos (rol dueno).')
    else:
        nuevo_admin = Usuario(
            usuario=username,
            password=generate_password_hash(password),
            rol=rol,
            nombre='Administrador Diamante',
            activo=True
        )
        db.session.add(nuevo_admin)
        db.session.commit()
        print('¡Usuario Administrador creado con todos los permisos!')