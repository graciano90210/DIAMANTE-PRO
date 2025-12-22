import os
import stat  # <--- 🆕 IMPORTANTE: Necesario para cambiar permisos
from app import create_app
from app.models import db, Usuario
from datetime import datetime
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("🔄 Recreando base de datos...")
    
    # Asegurar que la carpeta instance existe con permisos totales
    if not os.path.exists('instance'):
        os.makedirs('instance')
        os.chmod('instance', 0o777)

    db_path = 'instance/diamante.db'
    
    # 1. Eliminar cualquier conexión vieja que pueda bloquear el archivo
    db.engine.dispose() # <--- 🆕 TRUCO DE MAGIA: Libera el archivo antes de tocarlo

    # 2. Hacer backup o borrar lo viejo
    if os.path.exists(db_path):
        backup_path = f'instance/diamante_old_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        try:
            os.rename(db_path, backup_path)
            print(f"💾 Base de datos anterior renombrada: {backup_path}")
        except:
            if os.path.exists(db_path):
                os.remove(db_path)
                print("🗑️ Base de datos vieja eliminada forzosamente.")

    # 3. Crear las tablas
    db.create_all()
    
    # 4. 🔥 LA SOLUCIÓN DEFINITIVA: Dar permisos 777 AL ARCHIVO CREADO 🔥
    if os.path.exists(db_path):
        os.chmod(db_path, 0o777) # <--- 🆕 ESTO ES LO QUE NOS FALTABA
        print("🔓 Permisos de escritura otorgados al archivo de base de datos.")

    print("✅ Base de datos recreada con todas las columnas!")
    
    # --- Crear usuario ADMIN ---
    # (Ya no hace falta buscar si existe porque la acabamos de crear desde cero)
    
    nuevo_admin = Usuario(
        usuario='admin',
        password=generate_password_hash('123'),
        nombre='Juan Gerente',
        rol='dueno',
        activo=True
    )
    
    db.session.add(nuevo_admin)
    db.session.commit()
    print("✅ Usuario dueño creado exitosamente: admin / 123 (Encriptada)")

    print("\n🚀 ¡Base de datos lista y desbloqueada!")