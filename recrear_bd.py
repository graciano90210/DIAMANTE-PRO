"""
Script para recrear la base de datos con todas las columnas correctas
"""
import os
import shutil
from app import create_app
from app.models import db, Usuario
from datetime import datetime

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
            print(f"⚠️ No se pudo renombrar, creando nueva base de datos de todos modos...")
            # En GitHub Actions esto no importa mucho porque empieza limpio, 
            # pero es bueno mantenerlo para tu uso local.
    
    # Crear todas las tablas desde cero
    db.create_all()
    print("✅ Base de datos recreada con todas las columnas!")
    
   # --- 1. Crear SOLO el usuario ADMIN (Dueño) ---
    # Buscamos si ya existe para no duplicarlo
    admin = Usuario.query.filter_by(usuario='admin').first()
    
    if not admin:
        admin = Usuario(
            usuario='admin',    # Tu usuario para entrar
            password='123',     # Tu contraseña
            nombre='Juan Gerente', # El nombre que aparecerá
            rol='dueno',        # Rol principal con todos los permisos
            activo=True
        )
        db.session.add(admin)
        print("✅ Usuario dueño creado exitosamente: admin / 123")
    else:
        print("ℹ️ El usuario admin ya existe en la base de datos.")

    db.session.commit()
    print("\n🚀 ¡Base de datos lista y usuario admin verificado!")


    
    print("\n✅ ¡Base de datos lista para usar!")
    print("📊 Tablas creadas:")
    print("   - usuarios")
    print("   - clientes")
    print("   - prestamos (con todas las columnas)")
    print("   - pagos")
    print("   - transacciones")