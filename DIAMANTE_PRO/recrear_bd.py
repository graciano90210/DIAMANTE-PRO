import os
import stat
from app import create_app
from app.models import db, Usuario
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash # <--- 🆕 Importamos check

app = create_app()

with app.app_context():
    print("🔄 Recreando base de datos...")
    
    # Asegurar carpeta instance
    if not os.path.exists('instance'):
        os.makedirs('instance')
        os.chmod('instance', 0o777)

    db_path = 'instance/diamante.db'
    
    # 1. Liberar archivo
    db.session.remove()
    db.engine.dispose()

    # 2. Borrado agresivo si existe
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("🗑️ Base de datos vieja eliminada.")
        except:
            print("⚠️ No se pudo borrar, intentando sobreescribir...")

    # 3. Crear tablas
    db.create_all()
    
    # 4. Permisos
    if os.path.exists(db_path):
        os.chmod(db_path, 0o777)
        print("🔓 Permisos 777 aplicados.")

    # --- 5. CREAR USUARIO CON AUTO-VERIFICACIÓN ---
    print("👤 Creando usuario admin...")
    
    # Usamos el método por defecto que es el más compatible
    password_hash = generate_password_hash('123')
    
    nuevo_admin = Usuario(
        usuario='admin',
        password=password_hash,
        nombre='Juan Gerente',
        rol='dueno',
        activo=True
    )
    
    db.session.add(nuevo_admin)
    db.session.commit()
    
    # --- 🕵️‍♂️ PRUEBA DE FUEGO: VERIFICAR INMEDIATAMENTE ---
    # Leemos de la base de datos para asegurar que se guardó bien
    usuario_prueba = Usuario.query.filter_by(usuario='admin').first()
    
    if usuario_prueba:
        print(f"✅ Usuario encontrado en BD: {usuario_prueba.usuario}")
        # Probamos la contraseña
        if check_password_hash(usuario_prueba.password, '123'):
            print("🔑 ¡VERIFICACIÓN DE PASSWORD EXITOSA! La clave '123' funciona.")
        else:
            print("❌ ERROR CRÍTICO: La contraseña no coincide al verificar.")
    else:
        print("❌ ERROR CRÍTICO: El usuario no se guardó en la base de datos.")

    # 6. Cierre final importante
    db.session.close()
    db.engine.dispose() # <--- Soltamos el archivo para que run.py lo pueda leer
    print("\n🚀 ¡Base de datos lista y desconectada!")