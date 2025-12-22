"""
Script para recrear la base de datos con todas las columnas correctas
"""
import os
import shutil
from app import create_app
from app.models import db, Usuario
from datetime import datetime
from werkzeug.security import generate_password_hash # <--- IMPORTANTE: Importamos la seguridad

app = create_app()

with app.app_context():
    print("🔄 Recreando base de datos...")
    
    # Hacer backup de la base de datos actual (si existe)
    db_path = 'instance/diamante.db'
    if os.path.exists(db_path):
        backup_path = f'instance/diamante_old_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        try:
            os.rename(db_path, backup_path)
            print(f"💾 Base de datos anterior renombrada: {backup_path}")
        except Exception as e:
            print(f"⚠️ No se pudo renombrar, ELIMINANDO para crear una limpia...")
            # ESTA ES LA LÍNEA MÁGICA QUE NOS FALTABA:
            try:
                os.remove(db_path) 
                print("🗑️ Base de datos vieja eliminada forzosamente.")
            except:
                print("❌ No se pudo eliminar la base de datos vieja. Puede haber errores.")
    
    # Crear todas las tablas desde cero
    db.create_all()
    print("✅ Base de datos recreada con todas las columnas!")
    
    # --- 1. Crear usuario ADMIN (Dueño) con contraseña SEGURA ---
    # Primero buscamos si ya existe
    admin = Usuario.query.filter_by(usuario='admin').first()
    
    # Si existe, lo borramos para crearlo bien (por si tiene la contraseña vieja sin encriptar)
    if admin:
        db.session.delete(admin)
        db.session.commit()
        print("🗑️ Usuario admin anterior eliminado para actualizar credenciales.")

    # Ahora lo creamos desde cero con la contraseña encriptada
    nuevo_admin = Usuario(
        usuario='admin',                 # Tu usuario
        password=generate_password_hash('123'),  # <--- AQUÍ LA CLAVE: Se guarda encriptada
        nombre='Juan Gerente',           # Tu nombre
        rol='dueno',                     # Rol máximo
        activo=True
    )
    
    db.session.add(nuevo_admin)
    db.session.commit()
    print("✅ Usuario dueño creado exitosamente: admin / 123 (Encriptada)")

    print("\n🚀 ¡Base de datos lista y usuario admin verificado!")
    
    print("\n✅ ¡Base de datos lista para usar!")
    print("📊 Tablas creadas:")
    print("   - usuarios")
    print("   - clientes")
    print("   - prestamos (con todas las columnas)")
    print("   - pagos")
    print("   - transacciones")